from datetime import UTC, datetime
from uuid import uuid7

import health_dashboard_service.features.strava.strava_mapper as mapper
from health_dashboard_service.features.strava.domain.strava_models import (
    StravaActivityModel,
    StravaActivitySummaryModel,
    StravaSessionStatusModel,
    StravaTokenModel,
)
from health_dashboard_service.features.strava.persistence.strava_entities import (
    StravaActivity,
    StravaActivityStatsRow,
    StravaToken,
)
from health_dashboard_service.infrastructure.strava.strava_client import StravaActivitySummaryDTO
from tests.builders.strava_builders import StravaAutoFixture


class StravaMapperTests:
    def test_can_map_from_persistence_StravaToken_to_domain_StravaTokenModel(self):
        token = StravaAutoFixture.generate(StravaToken)

        result = mapper.map_from_persistence_to_domain_token(token)

        assert result.id == token.Id
        assert result.access_token == token.AccessToken
        assert result.refresh_token == token.RefreshToken
        assert result.expires_at == token.ExpiresAt
        assert result.athlete_id == token.AthleteId
        assert result.scope == token.Scope
        assert result.created_timestamp == token.CreatedTimestamp
        assert result.updated_timestamp == token.UpdatedTimestamp

    def test_can_map_from_domain_StravaTokenModel_to_persistence_StravaToken(self):
        token_model = StravaAutoFixture.generate(StravaTokenModel)

        result = mapper.map_from_domain_to_persistence_token(token_model)

        assert result.Id == token_model.id
        assert result.AccessToken == token_model.access_token
        assert result.RefreshToken == token_model.refresh_token
        assert result.ExpiresAt == token_model.expires_at
        assert result.AthleteId == token_model.athlete_id
        assert result.Scope == token_model.scope
        assert result.CreatedTimestamp == token_model.created_timestamp
        assert result.UpdatedTimestamp == token_model.updated_timestamp

    def test_can_map_from_persistence_StravaToken_to_domain_StravaSessionStatusModel(self):
        token = StravaAutoFixture.generate(StravaToken)

        result = mapper.map_from_persistence_to_domain_session_status(token)

        assert result.connected is True
        assert result.athlete_id == token.AthleteId
        assert result.updated_timestamp == token.UpdatedTimestamp

    def test_can_map_from_persistence_no_token_to_domain_StravaSessionStatusModel(self):
        result = mapper.map_from_persistence_to_domain_session_status(None)

        assert result.connected is False
        assert result.athlete_id is None
        assert result.updated_timestamp is None

    def test_can_map_from_domain_StravaSessionStatusModel_to_response_StravaSessionResponse(self):
        status_model = StravaSessionStatusModel(
            connected=True,
            athlete_id=12345678,
            updated_timestamp=StravaAutoFixture.generate(StravaToken).UpdatedTimestamp,
        )

        result = mapper.map_from_domain_to_response_session_status(status_model)

        assert result.connected is True
        assert result.athlete_id == status_model.athlete_id
        assert result.updated_timestamp == status_model.updated_timestamp

    def test_can_map_from_domain_disconnected_StravaSessionStatusModel_to_response_StravaSessionResponse(  # noqa: E501
        self,
    ):
        status_model = StravaSessionStatusModel(
            connected=False, athlete_id=None, updated_timestamp=None
        )

        result = mapper.map_from_domain_to_response_session_status(status_model)

        assert result.connected is False
        assert result.athlete_id is None
        assert result.updated_timestamp is None

    def test_can_map_from_client_StravaActivitySummaryDTO_to_domain_StravaActivityModel(self):
        dto = StravaAutoFixture.generate(StravaActivitySummaryDTO)
        activity_id = uuid7()
        updated_timestamp = datetime.now(UTC)

        result = mapper.map_from_client_to_domain_activity(
            dto, activity_id=activity_id, updated_timestamp=updated_timestamp
        )

        assert result.id == activity_id
        assert result.updated_timestamp == updated_timestamp
        assert result.strava_activity_id == dto.id
        assert result.name == dto.name
        assert result.type == dto.type
        assert result.sport_type == dto.sport_type
        assert result.start_date == dto.start_date
        assert result.start_date_local == dto.start_date_local
        assert result.distance_metres == dto.distance
        assert result.moving_time_seconds == dto.moving_time
        assert result.elapsed_time_seconds == dto.elapsed_time
        assert result.total_elevation_gain_metres == dto.total_elevation_gain
        assert result.average_heartrate == dto.average_heartrate
        assert result.max_heartrate == dto.max_heartrate
        assert result.gear_id == dto.gear_id

    def test_can_map_from_persistence_StravaActivity_to_domain_StravaActivityModel(self):
        activity = StravaAutoFixture.generate(StravaActivity)

        result = mapper.map_from_persistence_to_domain_activity(activity)

        assert result.id == activity.Id
        assert result.strava_activity_id == activity.StravaActivityId
        assert result.name == activity.Name
        assert result.type == activity.Type
        assert result.sport_type == activity.SportType
        assert result.start_date == activity.StartDate
        assert result.start_date_local == activity.StartDateLocal
        assert result.distance_metres == activity.DistanceMetres
        assert result.moving_time_seconds == activity.MovingTimeSeconds
        assert result.elapsed_time_seconds == activity.ElapsedTimeSeconds
        assert result.total_elevation_gain_metres == activity.TotalElevationGainMetres
        assert result.average_heartrate == activity.AverageHeartrate
        assert result.max_heartrate == activity.MaxHeartrate
        assert result.gear_id == activity.GearId
        assert result.updated_timestamp == activity.UpdatedTimestamp

    def test_can_map_from_domain_StravaActivityModel_to_persistence_StravaActivity(self):
        activity_model = StravaAutoFixture.generate(StravaActivityModel)

        result = mapper.map_from_domain_to_persistence_activity(activity_model)

        assert result.Id == activity_model.id
        assert result.StravaActivityId == activity_model.strava_activity_id
        assert result.Name == activity_model.name
        assert result.Type == activity_model.type
        assert result.SportType == activity_model.sport_type
        assert result.StartDate == activity_model.start_date
        assert result.StartDateLocal == activity_model.start_date_local
        assert result.DistanceMetres == activity_model.distance_metres
        assert result.MovingTimeSeconds == activity_model.moving_time_seconds
        assert result.ElapsedTimeSeconds == activity_model.elapsed_time_seconds
        assert result.TotalElevationGainMetres == activity_model.total_elevation_gain_metres
        assert result.AverageHeartrate == activity_model.average_heartrate
        assert result.MaxHeartrate == activity_model.max_heartrate
        assert result.GearId == activity_model.gear_id
        assert result.UpdatedTimestamp == activity_model.updated_timestamp

    def test_can_map_from_domain_StravaActivityModel_to_response_StravaActivityResponse(self):
        activity_model = StravaAutoFixture.generate(StravaActivityModel)

        result = mapper.map_from_domain_to_response_activity(activity_model)

        assert result.strava_activity_id == activity_model.strava_activity_id
        assert result.name == activity_model.name
        assert result.type == activity_model.type
        assert result.sport_type == activity_model.sport_type
        assert result.start_date == activity_model.start_date
        assert result.start_date_local == activity_model.start_date_local
        assert result.distance_metres == activity_model.distance_metres
        assert result.moving_time_seconds == activity_model.moving_time_seconds
        assert result.elapsed_time_seconds == activity_model.elapsed_time_seconds
        assert result.total_elevation_gain_metres == activity_model.total_elevation_gain_metres
        assert result.average_heartrate == activity_model.average_heartrate
        assert result.max_heartrate == activity_model.max_heartrate
        assert result.gear_id == activity_model.gear_id

    def test_can_map_from_persistence_StravaActivityStatsRow_to_domain_StravaActivityStatsModel(
        self,
    ):
        stats_row = StravaAutoFixture.generate(StravaActivityStatsRow)

        result = mapper.map_from_persistence_to_domain_activity_stats(stats_row)

        assert result.total_activities == stats_row.TotalActivities
        assert result.total_run_distance_metres == stats_row.TotalRunDistanceMetres
        assert result.total_run_moving_time_seconds == stats_row.TotalRunMovingTimeSeconds

    def test_can_map_from_domain_StravaActivitySummaryModel_to_response_StravaActivitySummaryResponse(  # noqa: E501
        self,
    ):
        summary_model = StravaAutoFixture.generate(StravaActivitySummaryModel)

        result = mapper.map_from_domain_to_response_activity_summary(summary_model)

        assert (
            result.current_period.total_activities == summary_model.current_period.total_activities
        )
        assert (
            result.current_period.total_run_distance_metres
            == summary_model.current_period.total_run_distance_metres
        )
        assert (
            result.current_period.average_run_pace_seconds_per_km
            == summary_model.current_period.average_run_pace_seconds_per_km
        )
        assert result.prior_period.total_activities == summary_model.prior_period.total_activities
        assert (
            result.prior_period.total_run_distance_metres
            == summary_model.prior_period.total_run_distance_metres
        )
        assert (
            result.prior_period.average_run_pace_seconds_per_km
            == summary_model.prior_period.average_run_pace_seconds_per_km
        )

    def test_can_map_from_domain_counts_by_type_to_response_FetchStravaActivitiesResponse(self):
        counts_by_type = {"Run": 3, "WeightTraining": 1}

        result = mapper.map_from_domain_to_response_fetch_result(counts_by_type)

        assert result.counts_by_type == counts_by_type
