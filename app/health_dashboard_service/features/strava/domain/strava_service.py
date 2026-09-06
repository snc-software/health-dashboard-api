from collections import Counter
from datetime import UTC, date, datetime, time, timedelta
from uuid import uuid7

from ....infrastructure.postgres.persistence_controller import PersistenceController
from ....infrastructure.postgres.persistence_controller_factory import (
    create_persistence_controller,
)
from ....infrastructure.strava import strava_client as client
from ....infrastructure.strava.strava_client import (
    StravaClientAuthenticationError,
    StravaClientConnectionError,
)
from .. import strava_mapper as mapper
from ..persistence import strava_reader as reader
from ..persistence import strava_writer as writer
from ..persistence.strava_entities import STRAVA_TOKEN_SINGLETON_ID
from .strava_models import (
    StravaActivityModel,
    StravaActivityPeriodStatsModel,
    StravaActivityStatsModel,
    StravaActivitySummaryModel,
    StravaSessionStatusModel,
    StravaTokenModel,
)

_TOKEN_REFRESH_LEEWAY = timedelta(minutes=5)


class StravaServiceError(Exception):
    """Strava is unreachable, or returned an unexpected error."""


class StravaAuthenticationError(StravaServiceError):
    """Strava rejected the authorization code or exchanged token, or the user denied consent."""


class StravaStateInvalidError(StravaServiceError):
    """The OAuth `state` is missing, unknown, or expired."""


class StravaSessionNotFoundError(StravaServiceError):
    """No Strava session has been established yet."""


def build_authorization_redirect_url() -> str:
    """Generate and store a pending CSRF state, and build Strava's authorization URL."""
    state = client.generate_pending_state()
    return client.build_authorize_url(state)


async def complete_authorization(
    code: str | None, state: str | None, error: str | None
) -> StravaTokenModel:
    """Validate the callback, exchange the code for tokens, verify the token works
    against Strava's /athlete endpoint, and persist the result."""
    if error is not None:
        raise StravaAuthenticationError(f"Strava returned an error: {error}")

    if not state or not client.consume_pending_state(state):
        raise StravaStateInvalidError("The OAuth state is missing, unknown, or expired.")

    if not code:
        raise StravaAuthenticationError("Strava callback is missing an authorization code.")

    try:
        exchange = await client.exchange_code_for_token(code)
    except StravaClientAuthenticationError as exc:
        raise StravaAuthenticationError(str(exc)) from exc
    except StravaClientConnectionError as exc:
        raise StravaServiceError(str(exc)) from exc

    try:
        await client.get_authenticated_athlete(exchange.access_token)
    except StravaClientAuthenticationError as exc:
        raise StravaAuthenticationError(str(exc)) from exc
    except StravaClientConnectionError as exc:
        raise StravaServiceError(str(exc)) from exc

    now = datetime.now(UTC)
    token_model = StravaTokenModel(
        id=STRAVA_TOKEN_SINGLETON_ID,
        access_token=exchange.access_token,
        refresh_token=exchange.refresh_token,
        expires_at=exchange.expires_at,
        athlete_id=exchange.athlete_id,
        scope=exchange.scope,
        created_timestamp=now,
        updated_timestamp=now,
    )

    async with create_persistence_controller() as pc:
        saved = await writer.upsert_token(
            pc, mapper.map_from_domain_to_persistence_token(token_model)
        )
        await pc.save_changes()
    return mapper.map_from_persistence_to_domain_token(saved)


async def get_session_status() -> StravaSessionStatusModel:
    """Report whether a Strava token is currently stored, without exposing the token."""
    async with create_persistence_controller() as pc:
        token = await reader.get_token(pc)
        return mapper.map_from_persistence_to_domain_session_status(token)


async def fetch_activities(start_date: date, end_date: date) -> dict[str, int]:
    """Use the stored Strava session (refreshing the access token if needed) to fetch
    activities covering the inclusive start_date/end_date range in UTC (start_date at
    00:00:00 UTC, end_date at 23:59:59 UTC), upsert them, and return a count of the synced
    activities by type."""
    async with create_persistence_controller() as pc:
        access_token = await _get_valid_access_token(pc)

        after = int(datetime.combine(start_date, time.min, tzinfo=UTC).timestamp())
        before = int(datetime.combine(end_date, time.max, tzinfo=UTC).timestamp())
        try:
            dtos = await client.list_activities(access_token, after=after, before=before)
        except StravaClientAuthenticationError as exc:
            raise StravaAuthenticationError(str(exc)) from exc
        except StravaClientConnectionError as exc:
            raise StravaServiceError(str(exc)) from exc

        in_range = [dto for dto in dtos if start_date <= dto.start_date.date() <= end_date]

        now = datetime.now(UTC)
        activity_models = [
            mapper.map_from_client_to_domain_activity(
                dto, activity_id=uuid7(), updated_timestamp=now
            )
            for dto in in_range
        ]
        rows = [mapper.map_from_domain_to_persistence_activity(model) for model in activity_models]
        saved = await writer.upsert_activities(pc, rows)
        await pc.save_changes()

    return dict(Counter(row.SportType for row in saved))


async def get_activities(start_date: date, end_date: date) -> list[StravaActivityModel]:
    """Return the stored activities whose local start date falls in the inclusive range."""
    async with create_persistence_controller() as pc:
        rows = await reader.get_activities_in_range(pc, start_date, end_date)
        return [mapper.map_from_persistence_to_domain_activity(row) for row in rows]


def compute_prior_period(start_date: date, end_date: date) -> tuple[date, date]:
    """Return the trailing period of equal length immediately preceding [start_date, end_date]."""
    period_length = (end_date - start_date) + timedelta(days=1)
    prior_end = start_date - timedelta(days=1)
    prior_start = prior_end - period_length + timedelta(days=1)
    return prior_start, prior_end


async def get_activity_summary(start_date: date, end_date: date) -> StravaActivitySummaryModel:
    """Compute current-vs-prior-period activity stats, matched against each activity's
    local start date."""
    prior_start, prior_end = compute_prior_period(start_date, end_date)

    async with create_persistence_controller() as pc:
        current_row = await reader.get_activity_stats_in_range(pc, start_date, end_date)
        prior_row = await reader.get_activity_stats_in_range(pc, prior_start, prior_end)

    current_raw = mapper.map_from_persistence_to_domain_activity_stats(current_row)
    prior_raw = mapper.map_from_persistence_to_domain_activity_stats(prior_row)
    return StravaActivitySummaryModel(
        current_period=_compute_period_stats(current_raw),
        prior_period=_compute_period_stats(prior_raw),
    )


def _compute_period_stats(raw: StravaActivityStatsModel) -> StravaActivityPeriodStatsModel:
    pace = (
        raw.total_run_moving_time_seconds / (raw.total_run_distance_metres / 1000)
        if raw.total_run_distance_metres > 0
        else None
    )
    return StravaActivityPeriodStatsModel(
        total_activities=raw.total_activities,
        total_run_distance_metres=raw.total_run_distance_metres,
        average_run_pace_seconds_per_km=pace,
    )


async def _get_valid_access_token(pc: PersistenceController) -> str:
    """Return a currently-valid Strava access token, refreshing and persisting a new one
    if the stored token has expired or is within `_TOKEN_REFRESH_LEEWAY` of expiring."""
    token = await reader.get_token(pc)
    if token is None:
        raise StravaSessionNotFoundError("No Strava session has been established yet.")

    token_model = mapper.map_from_persistence_to_domain_token(token)
    if token_model.expires_at > datetime.now(UTC) + _TOKEN_REFRESH_LEEWAY:
        return token_model.access_token

    try:
        refreshed = await client.refresh_access_token(token_model.refresh_token)
    except StravaClientAuthenticationError as exc:
        raise StravaAuthenticationError(str(exc)) from exc
    except StravaClientConnectionError as exc:
        raise StravaServiceError(str(exc)) from exc

    updated_model = StravaTokenModel(
        id=token_model.id,
        access_token=refreshed.access_token,
        refresh_token=refreshed.refresh_token,
        expires_at=refreshed.expires_at,
        athlete_id=token_model.athlete_id,
        scope=token_model.scope,
        created_timestamp=token_model.created_timestamp,
        updated_timestamp=datetime.now(UTC),
    )
    saved = await writer.upsert_token(
        pc, mapper.map_from_domain_to_persistence_token(updated_model)
    )
    return mapper.map_from_persistence_to_domain_token(saved).access_token
