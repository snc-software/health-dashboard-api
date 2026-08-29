from typing import Any, ClassVar, TypeVar

from polyfactory.factories import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory

from health_dashboard_service.contracts.garmin import (
    AuthenticateGarminRequest,
    GarminDailyStatResponse,
)
from health_dashboard_service.features.garmin.domain.garmin_models import (
    GarminCredentialsModel,
    GarminDailyStatModel,
    GarminTokenModel,
)
from health_dashboard_service.features.garmin.persistence.garmin_entities import (
    GarminDailyStat,
    GarminToken,
)

__all__ = ["GarminAutoFixture"]

T = TypeVar("T")


class _GarminTokenFactory(DataclassFactory[GarminToken]):
    __model__ = GarminToken


class _GarminDailyStatFactory(DataclassFactory[GarminDailyStat]):
    __model__ = GarminDailyStat


class _GarminTokenModelFactory(DataclassFactory[GarminTokenModel]):
    __model__ = GarminTokenModel


class _GarminDailyStatModelFactory(DataclassFactory[GarminDailyStatModel]):
    __model__ = GarminDailyStatModel


class _GarminCredentialsModelFactory(DataclassFactory[GarminCredentialsModel]):
    __model__ = GarminCredentialsModel


class _AuthenticateGarminRequestFactory(ModelFactory[AuthenticateGarminRequest]):
    __model__ = AuthenticateGarminRequest


class _GarminDailyStatResponseFactory(ModelFactory[GarminDailyStatResponse]):
    __model__ = GarminDailyStatResponse


class GarminAutoFixture:
    _factories: ClassVar[dict[type, Any]] = {
        GarminToken: _GarminTokenFactory,
        GarminDailyStat: _GarminDailyStatFactory,
        GarminTokenModel: _GarminTokenModelFactory,
        GarminDailyStatModel: _GarminDailyStatModelFactory,
        GarminCredentialsModel: _GarminCredentialsModelFactory,
        AuthenticateGarminRequest: _AuthenticateGarminRequestFactory,
        GarminDailyStatResponse: _GarminDailyStatResponseFactory,
    }

    @staticmethod
    def generate(model_type: type[T], **overrides: Any) -> T:
        """Build an instance with random values; `overrides` pin the fields a test cares about."""
        factory = GarminAutoFixture._factories.get(model_type)
        if factory is None:
            raise ValueError(f"No factory registered for {model_type!r}")
        return factory.build(**overrides)
