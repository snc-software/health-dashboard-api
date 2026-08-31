from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class DailyHealthStatModel:
    stat_date: date
    steps: int | None
    resting_heart_rate: int | None
    sleep_seconds: int | None
    sleep_score: int | None
    peak_body_battery: int | None
    hrv_last_night_average: int | None
    hrv_status: str | None
    training_readiness_score: int | None
    training_status: str | None
    vo2_max: float | None
    fitness_age: float | None
    weight_grams: int | None
    intensity_minutes: int | None
    updated_timestamp: datetime
