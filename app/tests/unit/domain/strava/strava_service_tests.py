from datetime import date

from health_dashboard_service.features.strava.domain.strava_service import compute_prior_period


class StravaServiceTests:
    def test_compute_prior_period_should_return_equal_length_trailing_window_for_a_week_range(
        self,
    ):
        result = compute_prior_period(date(2026, 8, 20), date(2026, 8, 26))

        assert result == (date(2026, 8, 13), date(2026, 8, 19))

    def test_compute_prior_period_should_return_previous_day_for_a_single_day_range(self):
        result = compute_prior_period(date(2026, 8, 20), date(2026, 8, 20))

        assert result == (date(2026, 8, 19), date(2026, 8, 19))

    def test_compute_prior_period_should_return_equal_length_window_for_a_range_spanning_a_month_boundary(  # noqa: E501
        self,
    ):
        result = compute_prior_period(date(2026, 8, 25), date(2026, 9, 5))

        assert result == (date(2026, 8, 13), date(2026, 8, 24))
