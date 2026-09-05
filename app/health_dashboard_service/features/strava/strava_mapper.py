"""Mapping between Strava persistence rows, domain models, and contracts."""

from ...contracts.strava import StravaSessionResponse
from .domain.strava_models import StravaSessionStatusModel, StravaTokenModel
from .persistence.strava_entities import StravaToken


def map_from_persistence_to_domain_token(token: StravaToken) -> StravaTokenModel:
    """Map from persistence StravaToken to domain StravaTokenModel"""
    return StravaTokenModel(
        id=token.Id,
        access_token=token.AccessToken,
        refresh_token=token.RefreshToken,
        expires_at=token.ExpiresAt,
        athlete_id=token.AthleteId,
        scope=token.Scope,
        created_timestamp=token.CreatedTimestamp,
        updated_timestamp=token.UpdatedTimestamp,
    )


def map_from_domain_to_persistence_token(token_model: StravaTokenModel) -> StravaToken:
    """Map from domain StravaTokenModel to persistence StravaToken"""
    return StravaToken(
        Id=token_model.id,
        AccessToken=token_model.access_token,
        RefreshToken=token_model.refresh_token,
        ExpiresAt=token_model.expires_at,
        AthleteId=token_model.athlete_id,
        Scope=token_model.scope,
        CreatedTimestamp=token_model.created_timestamp,
        UpdatedTimestamp=token_model.updated_timestamp,
    )


def map_from_persistence_to_domain_session_status(
    token: StravaToken | None,
) -> StravaSessionStatusModel:
    """Map from persistence StravaToken (or absence of one) to domain StravaSessionStatusModel"""
    if token is None:
        return StravaSessionStatusModel(connected=False, athlete_id=None, updated_timestamp=None)
    return StravaSessionStatusModel(
        connected=True, athlete_id=token.AthleteId, updated_timestamp=token.UpdatedTimestamp
    )


def map_from_domain_to_response_session_status(
    status_model: StravaSessionStatusModel,
) -> StravaSessionResponse:
    """Map from domain StravaSessionStatusModel to response StravaSessionResponse"""
    return StravaSessionResponse(
        connected=status_model.connected,
        athlete_id=status_model.athlete_id,
        updated_timestamp=status_model.updated_timestamp,
    )
