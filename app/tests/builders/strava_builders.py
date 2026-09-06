from typing import Any, ClassVar, TypeVar

from polyfactory.factories import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory

from health_dashboard_service.contracts.strava import (
    FetchStravaActivitiesResponse,
    StravaActivityResponse,
    StravaActivitySummaryResponse,
    StravaSessionResponse,
)
from health_dashboard_service.features.strava.domain.strava_models import (
    StravaActivityModel,
    StravaActivityPeriodStatsModel,
    StravaActivityStatsModel,
    StravaActivitySummaryModel,
    StravaSessionStatusModel,
    StravaTokenModel,
)
from health_dashboard_service.features.strava.persistence.strava_entities import (
    StravaActivity,
    StravaActivityStatsRow,
    StravaToken,
)
from health_dashboard_service.infrastructure.strava.strava_client import StravaActivitySummary

__all__ = ["StravaAutoFixture"]

T = TypeVar("T")


class _StravaTokenFactory(DataclassFactory[StravaToken]):
    __model__ = StravaToken


class _StravaTokenModelFactory(DataclassFactory[StravaTokenModel]):
    __model__ = StravaTokenModel


class _StravaSessionStatusModelFactory(DataclassFactory[StravaSessionStatusModel]):
    __model__ = StravaSessionStatusModel


class _StravaSessionResponseFactory(ModelFactory[StravaSessionResponse]):
    __model__ = StravaSessionResponse


class _StravaActivityFactory(DataclassFactory[StravaActivity]):
    __model__ = StravaActivity


class _StravaActivityModelFactory(DataclassFactory[StravaActivityModel]):
    __model__ = StravaActivityModel


class _StravaActivityStatsRowFactory(DataclassFactory[StravaActivityStatsRow]):
    __model__ = StravaActivityStatsRow


class _StravaActivityStatsModelFactory(DataclassFactory[StravaActivityStatsModel]):
    __model__ = StravaActivityStatsModel


class _StravaActivityPeriodStatsModelFactory(DataclassFactory[StravaActivityPeriodStatsModel]):
    __model__ = StravaActivityPeriodStatsModel


class _StravaActivitySummaryModelFactory(DataclassFactory[StravaActivitySummaryModel]):
    __model__ = StravaActivitySummaryModel


class _StravaActivityResponseFactory(ModelFactory[StravaActivityResponse]):
    __model__ = StravaActivityResponse


class _FetchStravaActivitiesResponseFactory(ModelFactory[FetchStravaActivitiesResponse]):
    __model__ = FetchStravaActivitiesResponse


class _StravaActivitySummaryResponseFactory(ModelFactory[StravaActivitySummaryResponse]):
    __model__ = StravaActivitySummaryResponse


class _StravaActivitySummaryFactory(DataclassFactory[StravaActivitySummary]):
    __model__ = StravaActivitySummary


class StravaAutoFixture:
    _factories: ClassVar[dict[type, Any]] = {
        StravaToken: _StravaTokenFactory,
        StravaTokenModel: _StravaTokenModelFactory,
        StravaSessionStatusModel: _StravaSessionStatusModelFactory,
        StravaSessionResponse: _StravaSessionResponseFactory,
        StravaActivity: _StravaActivityFactory,
        StravaActivityModel: _StravaActivityModelFactory,
        StravaActivityStatsRow: _StravaActivityStatsRowFactory,
        StravaActivityStatsModel: _StravaActivityStatsModelFactory,
        StravaActivityPeriodStatsModel: _StravaActivityPeriodStatsModelFactory,
        StravaActivitySummaryModel: _StravaActivitySummaryModelFactory,
        StravaActivityResponse: _StravaActivityResponseFactory,
        FetchStravaActivitiesResponse: _FetchStravaActivitiesResponseFactory,
        StravaActivitySummaryResponse: _StravaActivitySummaryResponseFactory,
        StravaActivitySummary: _StravaActivitySummaryFactory,
    }

    @staticmethod
    def generate(model_type: type[T], **overrides: Any) -> T:
        """Build an instance with random values; `overrides` pin the fields a test cares about."""
        factory = StravaAutoFixture._factories.get(model_type)
        if factory is None:
            raise ValueError(f"No factory registered for {model_type!r}")
        return factory.build(**overrides)
