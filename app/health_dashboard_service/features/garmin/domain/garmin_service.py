from datetime import UTC, date, datetime
from uuid import uuid7

from ....infrastructure.garmin import garmin_client_factory as client_factory
from ....infrastructure.garmin.garmin_client_factory import (
    GarminClientAuthenticationError,
    GarminClientConnectionError,
    GarminClientMfaSessionNotFoundError,
)
from ....infrastructure.postgres.persistence_controller_factory import (
    create_scoped_persistence_controller,
)
from .. import garmin_mapper as mapper
from ..persistence import garmin_reader as reader
from ..persistence import garmin_writer as writer
from ..persistence.garmin_entities import GARMIN_TOKEN_SINGLETON_ID
from .garmin_models import (
    GarminAuthenticationResultModel,
    GarminCredentialsModel,
    GarminDailyStatModel,
    GarminMfaSubmissionModel,
    GarminTokenModel,
)


class GarminServiceError(Exception):
    """Garmin Connect is unreachable, or returned an unexpected error."""


class GarminAuthenticationError(GarminServiceError):
    """Garmin Connect rejected the supplied credentials."""


class GarminSessionNotFoundError(GarminServiceError):
    """No Garmin session has been established yet."""


class GarminMfaSessionNotFoundError(GarminServiceError):
    """The Garmin MFA session is unknown or has expired."""


async def authenticate(credentials: GarminCredentialsModel) -> GarminAuthenticationResultModel:
    """Start a Garmin login. If Garmin challenges for an MFA code, returns an
    mfa_required result instead of persisting a token."""
    try:
        result = client_factory.start_login(credentials.email, credentials.password)
    except GarminClientAuthenticationError as exc:
        raise GarminAuthenticationError(str(exc)) from exc
    except GarminClientConnectionError as exc:
        raise GarminServiceError(str(exc)) from exc

    if result.mfa_required:
        return GarminAuthenticationResultModel(
            status="mfa_required", mfa_session_id=result.mfa_session_id
        )

    assert result.token_data is not None
    await _persist_token(result.token_data)
    return GarminAuthenticationResultModel(status="authenticated", mfa_session_id=None)


async def complete_mfa(submission: GarminMfaSubmissionModel) -> None:
    """Submit an MFA code for a pending login and persist the resulting session token."""
    try:
        token_data = client_factory.complete_mfa_login(submission.mfa_session_id, submission.code)
    except GarminClientMfaSessionNotFoundError as exc:
        raise GarminMfaSessionNotFoundError(str(exc)) from exc
    except GarminClientAuthenticationError as exc:
        raise GarminAuthenticationError(str(exc)) from exc
    except GarminClientConnectionError as exc:
        raise GarminServiceError(str(exc)) from exc

    await _persist_token(token_data)


async def _persist_token(token_data: str) -> None:
    now = datetime.now(UTC)
    token_model = GarminTokenModel(
        id=GARMIN_TOKEN_SINGLETON_ID,
        token_data=token_data,
        created_timestamp=now,
        updated_timestamp=now,
    )

    async with create_scoped_persistence_controller() as pc:
        await writer.upsert_token(pc, mapper.map_from_domain_to_persistence_token(token_model))
        await pc.save_changes()


async def refresh_daily_stats(stat_date: date) -> GarminDailyStatModel:
    """Pull the day's summary stats from Garmin using the stored session, and upsert them."""
    async with create_scoped_persistence_controller() as pc:
        token = await reader.get_token(pc)
        if token is None:
            raise GarminSessionNotFoundError("No Garmin session has been established yet.")

        try:
            snapshot = client_factory.fetch_daily_snapshot(token.TokenData, stat_date)
        except (GarminClientAuthenticationError, GarminClientConnectionError) as exc:
            # Both a rejected stored session and an unreachable Garmin surface as
            # 502 here (only the initial `authenticate` call distinguishes 401).
            raise GarminServiceError(str(exc)) from exc

        stat_model = GarminDailyStatModel(
            id=uuid7(),
            stat_date=stat_date,
            steps=snapshot.steps,
            resting_heart_rate=snapshot.resting_heart_rate,
            sleep_seconds=snapshot.sleep_seconds,
            body_battery=snapshot.body_battery,
            updated_timestamp=datetime.now(UTC),
        )
        saved = await writer.upsert_daily_stat(
            pc, mapper.map_from_domain_to_persistence_daily_stat(stat_model)
        )
        await pc.save_changes()
        return mapper.map_from_persistence_to_domain_daily_stat(saved)
