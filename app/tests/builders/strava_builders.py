from typing import Any, ClassVar, TypeVar

from polyfactory.factories import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory

from health_dashboard_service.contracts.strava import StravaSessionResponse
from health_dashboard_service.features.strava.domain.strava_models import (
    StravaSessionStatusModel,
    StravaTokenModel,
)
from health_dashboard_service.features.strava.persistence.strava_entities import StravaToken

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


class StravaAutoFixture:
    _factories: ClassVar[dict[type, Any]] = {
        StravaToken: _StravaTokenFactory,
        StravaTokenModel: _StravaTokenModelFactory,
        StravaSessionStatusModel: _StravaSessionStatusModelFactory,
        StravaSessionResponse: _StravaSessionResponseFactory,
    }

    @staticmethod
    def generate(model_type: type[T], **overrides: Any) -> T:
        """Build an instance with random values; `overrides` pin the fields a test cares about."""
        factory = StravaAutoFixture._factories.get(model_type)
        if factory is None:
            raise ValueError(f"No factory registered for {model_type!r}")
        return factory.build(**overrides)
