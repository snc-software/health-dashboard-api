from health_dashboard_service.contracts.strava import StravaSessionResponse
from tests.builders.strava_builders import StravaAutoFixture


class StravaContractTests:
    def test_strava_session_response_should_serialise_as_camel_case(self):
        response = StravaAutoFixture.generate(StravaSessionResponse)

        payload = response.model_dump(by_alias=True)

        assert "athleteId" in payload
        assert "updatedTimestamp" in payload
