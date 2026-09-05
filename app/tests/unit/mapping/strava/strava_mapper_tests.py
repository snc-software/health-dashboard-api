import health_dashboard_service.features.strava.strava_mapper as mapper
from health_dashboard_service.features.strava.domain.strava_models import (
    StravaSessionStatusModel,
    StravaTokenModel,
)
from health_dashboard_service.features.strava.persistence.strava_entities import StravaToken
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
