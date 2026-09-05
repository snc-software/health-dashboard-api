from datetime import UTC, datetime

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
from .strava_models import StravaSessionStatusModel, StravaTokenModel


class StravaServiceError(Exception):
    """Strava is unreachable, or returned an unexpected error."""


class StravaAuthenticationError(StravaServiceError):
    """Strava rejected the authorization code or exchanged token, or the user denied consent."""


class StravaStateInvalidError(StravaServiceError):
    """The OAuth `state` is missing, unknown, or expired."""


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
