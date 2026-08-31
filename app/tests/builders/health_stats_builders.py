from typing import Any, ClassVar, TypeVar

from polyfactory.factories import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import PostGenerated

from health_dashboard_service.contracts.health_stats import (
    DailyHealthStatResponse,
    GetDailyHealthStatsRequest,
)
from health_dashboard_service.features.health_stats.domain.health_stats_models import (
    DailyHealthStatModel,
)

__all__ = ["HealthStatsAutoFixture"]

T = TypeVar("T")


class _DailyHealthStatModelFactory(DataclassFactory[DailyHealthStatModel]):
    __model__ = DailyHealthStatModel


class _DailyHealthStatResponseFactory(ModelFactory[DailyHealthStatResponse]):
    __model__ = DailyHealthStatResponse


class _GetDailyHealthStatsRequestFactory(ModelFactory[GetDailyHealthStatsRequest]):
    __model__ = GetDailyHealthStatsRequest

    # end_date must not be before start_date; default to a same-day range so
    # random generation always satisfies the contract's model_validator.
    end_date = PostGenerated(lambda name, values: values["start_date"])


class HealthStatsAutoFixture:
    _factories: ClassVar[dict[type, Any]] = {
        DailyHealthStatModel: _DailyHealthStatModelFactory,
        DailyHealthStatResponse: _DailyHealthStatResponseFactory,
        GetDailyHealthStatsRequest: _GetDailyHealthStatsRequestFactory,
    }

    @staticmethod
    def generate(model_type: type[T], **overrides: Any) -> T:
        """Build an instance with random values; `overrides` pin the fields a test cares about."""
        factory = HealthStatsAutoFixture._factories.get(model_type)
        if factory is None:
            raise ValueError(f"No factory registered for {model_type!r}")
        return factory.build(**overrides)
