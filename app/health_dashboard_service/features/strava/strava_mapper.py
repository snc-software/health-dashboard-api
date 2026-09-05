"""Mapping between Strava persistence rows, domain models, and contracts."""

from datetime import datetime
from uuid import UUID

from ...contracts.strava import (
    FetchStravaActivitiesResponse,
    StravaActivityPeriodStatsResponse,
    StravaActivityResponse,
    StravaActivitySummaryResponse,
    StravaSessionResponse,
)
from ...infrastructure.strava.strava_client import StravaActivitySummaryDTO
from .domain.strava_models import (
    StravaActivityModel,
    StravaActivityPeriodStatsModel,
    StravaActivityStatsModel,
    StravaActivitySummaryModel,
    StravaSessionStatusModel,
    StravaTokenModel,
)
from .persistence.strava_entities import StravaActivity, StravaActivityStatsRow, StravaToken


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


def map_from_client_to_domain_activity(
    dto: StravaActivitySummaryDTO, *, activity_id: UUID, updated_timestamp: datetime
) -> StravaActivityModel:
    """Map from Strava client StravaActivitySummaryDTO to domain StravaActivityModel"""
    return StravaActivityModel(
        id=activity_id,
        strava_activity_id=dto.id,
        name=dto.name,
        type=dto.type,
        sport_type=dto.sport_type,
        start_date=dto.start_date,
        start_date_local=dto.start_date_local,
        distance_metres=dto.distance,
        moving_time_seconds=dto.moving_time,
        elapsed_time_seconds=dto.elapsed_time,
        total_elevation_gain_metres=dto.total_elevation_gain,
        average_heartrate=dto.average_heartrate,
        max_heartrate=dto.max_heartrate,
        gear_id=dto.gear_id,
        updated_timestamp=updated_timestamp,
    )


def map_from_persistence_to_domain_activity(activity: StravaActivity) -> StravaActivityModel:
    """Map from persistence StravaActivity to domain StravaActivityModel"""
    return StravaActivityModel(
        id=activity.Id,
        strava_activity_id=activity.StravaActivityId,
        name=activity.Name,
        type=activity.Type,
        sport_type=activity.SportType,
        start_date=activity.StartDate,
        start_date_local=activity.StartDateLocal,
        distance_metres=activity.DistanceMetres,
        moving_time_seconds=activity.MovingTimeSeconds,
        elapsed_time_seconds=activity.ElapsedTimeSeconds,
        total_elevation_gain_metres=activity.TotalElevationGainMetres,
        average_heartrate=activity.AverageHeartrate,
        max_heartrate=activity.MaxHeartrate,
        gear_id=activity.GearId,
        updated_timestamp=activity.UpdatedTimestamp,
    )


def map_from_domain_to_persistence_activity(activity_model: StravaActivityModel) -> StravaActivity:
    """Map from domain StravaActivityModel to persistence StravaActivity"""
    return StravaActivity(
        Id=activity_model.id,
        StravaActivityId=activity_model.strava_activity_id,
        Name=activity_model.name,
        Type=activity_model.type,
        SportType=activity_model.sport_type,
        StartDate=activity_model.start_date,
        StartDateLocal=activity_model.start_date_local,
        DistanceMetres=activity_model.distance_metres,
        MovingTimeSeconds=activity_model.moving_time_seconds,
        ElapsedTimeSeconds=activity_model.elapsed_time_seconds,
        TotalElevationGainMetres=activity_model.total_elevation_gain_metres,
        AverageHeartrate=activity_model.average_heartrate,
        MaxHeartrate=activity_model.max_heartrate,
        GearId=activity_model.gear_id,
        UpdatedTimestamp=activity_model.updated_timestamp,
    )


def map_from_domain_to_response_activity(
    activity_model: StravaActivityModel,
) -> StravaActivityResponse:
    """Map from domain StravaActivityModel to response StravaActivityResponse"""
    return StravaActivityResponse(
        strava_activity_id=activity_model.strava_activity_id,
        name=activity_model.name,
        type=activity_model.type,
        sport_type=activity_model.sport_type,
        start_date=activity_model.start_date,
        start_date_local=activity_model.start_date_local,
        distance_metres=activity_model.distance_metres,
        moving_time_seconds=activity_model.moving_time_seconds,
        elapsed_time_seconds=activity_model.elapsed_time_seconds,
        total_elevation_gain_metres=activity_model.total_elevation_gain_metres,
        average_heartrate=activity_model.average_heartrate,
        max_heartrate=activity_model.max_heartrate,
        gear_id=activity_model.gear_id,
    )


def map_from_persistence_to_domain_activity_stats(
    stats_row: StravaActivityStatsRow,
) -> StravaActivityStatsModel:
    """Map from persistence StravaActivityStatsRow to domain StravaActivityStatsModel (raw,
    pre-pace; pace is computed by the domain service from these raw sums)"""
    return StravaActivityStatsModel(
        total_activities=stats_row.TotalActivities,
        total_run_distance_metres=stats_row.TotalRunDistanceMetres,
        total_run_moving_time_seconds=stats_row.TotalRunMovingTimeSeconds,
    )


def map_from_domain_to_response_activity_summary(
    summary_model: StravaActivitySummaryModel,
) -> StravaActivitySummaryResponse:
    """Map from domain StravaActivitySummaryModel to response StravaActivitySummaryResponse"""
    return StravaActivitySummaryResponse(
        current_period=_map_from_domain_to_response_period_stats(summary_model.current_period),
        prior_period=_map_from_domain_to_response_period_stats(summary_model.prior_period),
    )


def _map_from_domain_to_response_period_stats(
    period_model: StravaActivityPeriodStatsModel,
) -> StravaActivityPeriodStatsResponse:
    return StravaActivityPeriodStatsResponse(
        total_activities=period_model.total_activities,
        total_run_distance_metres=period_model.total_run_distance_metres,
        average_run_pace_seconds_per_km=period_model.average_run_pace_seconds_per_km,
    )


def map_from_domain_to_response_fetch_result(
    counts_by_type: dict[str, int],
) -> FetchStravaActivitiesResponse:
    """Map from the domain's counts-by-type dict to response FetchStravaActivitiesResponse"""
    return FetchStravaActivitiesResponse(counts_by_type=counts_by_type)
