"""Mapping between Garmin persistence rows, domain models, and contracts."""

from datetime import date

from ...contracts.garmin import (
    AuthenticateGarminRequest,
    BatchUpsertGarminDailyStatsResponse,
    GarminAuthenticateResponse,
    GarminDailyStatResponse,
    GarminSessionResponse,
    SubmitGarminMfaRequest,
)
from .domain.garmin_models import (
    GarminAuthenticationResultModel,
    GarminCredentialsModel,
    GarminDailyStatModel,
    GarminMfaSubmissionModel,
    GarminSessionStatusModel,
    GarminTokenModel,
)
from .persistence.garmin_entities import GarminDailyStat, GarminToken


def map_from_contract_to_domain_credentials(
    request: AuthenticateGarminRequest,
) -> GarminCredentialsModel:
    """Map from request contract AuthenticateGarminRequest to domain GarminCredentialsModel"""
    return GarminCredentialsModel(email=request.email, password=request.password)


def map_from_domain_to_response_authentication_result(
    result: GarminAuthenticationResultModel,
) -> GarminAuthenticateResponse:
    """Map from domain GarminAuthenticationResultModel to response GarminAuthenticateResponse"""
    return GarminAuthenticateResponse(status=result.status, mfa_session_id=result.mfa_session_id)


def map_from_contract_to_domain_mfa_submission(
    request: SubmitGarminMfaRequest,
) -> GarminMfaSubmissionModel:
    """Map from request contract SubmitGarminMfaRequest to domain GarminMfaSubmissionModel"""
    return GarminMfaSubmissionModel(mfa_session_id=request.mfa_session_id, code=request.code)


def map_from_persistence_to_domain_token(token: GarminToken) -> GarminTokenModel:
    """Map from persistence GarminToken to domain GarminTokenModel"""
    return GarminTokenModel(
        id=token.Id,
        token_data=token.TokenData,
        created_timestamp=token.CreatedTimestamp,
        updated_timestamp=token.UpdatedTimestamp,
    )


def map_from_domain_to_persistence_token(token_model: GarminTokenModel) -> GarminToken:
    """Map from domain GarminTokenModel to persistence GarminToken"""
    return GarminToken(
        Id=token_model.id,
        TokenData=token_model.token_data,
        CreatedTimestamp=token_model.created_timestamp,
        UpdatedTimestamp=token_model.updated_timestamp,
    )


def map_from_persistence_to_domain_session_status(
    token: GarminToken | None,
) -> GarminSessionStatusModel:
    """Map from persistence GarminToken (or absence of one) to domain GarminSessionStatusModel"""
    if token is None:
        return GarminSessionStatusModel(authenticated=False, authenticated_at=None)
    return GarminSessionStatusModel(authenticated=True, authenticated_at=token.UpdatedTimestamp)


def map_from_domain_to_response_session_status(
    status_model: GarminSessionStatusModel,
) -> GarminSessionResponse:
    """Map from domain GarminSessionStatusModel to response GarminSessionResponse"""
    return GarminSessionResponse(
        status="authenticated" if status_model.authenticated else "unauthenticated",
        authenticated_at=status_model.authenticated_at,
    )


def map_from_persistence_to_domain_daily_stat(stat: GarminDailyStat) -> GarminDailyStatModel:
    """Map from persistence GarminDailyStat to domain GarminDailyStatModel"""
    return GarminDailyStatModel(
        id=stat.Id,
        stat_date=stat.StatDate,
        steps=stat.Steps,
        resting_heart_rate=stat.RestingHeartRate,
        sleep_seconds=stat.SleepSeconds,
        peak_body_battery=stat.PeakBodyBattery,
        sleep_score=stat.SleepScore,
        hrv_last_night_average=stat.HrvLastNightAverage,
        hrv_status=stat.HrvStatus,
        training_readiness_score=stat.TrainingReadinessScore,
        training_status=stat.TrainingStatus,
        vo2_max=stat.Vo2Max,
        fitness_age=stat.FitnessAge,
        weight_grams=stat.WeightGrams,
        intensity_minutes=stat.IntensityMinutes,
        updated_timestamp=stat.UpdatedTimestamp,
    )


def map_from_domain_to_persistence_daily_stat(stat_model: GarminDailyStatModel) -> GarminDailyStat:
    """Map from domain GarminDailyStatModel to persistence GarminDailyStat"""
    return GarminDailyStat(
        Id=stat_model.id,
        StatDate=stat_model.stat_date,
        Steps=stat_model.steps,
        RestingHeartRate=stat_model.resting_heart_rate,
        SleepSeconds=stat_model.sleep_seconds,
        PeakBodyBattery=stat_model.peak_body_battery,
        SleepScore=stat_model.sleep_score,
        HrvLastNightAverage=stat_model.hrv_last_night_average,
        HrvStatus=stat_model.hrv_status,
        TrainingReadinessScore=stat_model.training_readiness_score,
        TrainingStatus=stat_model.training_status,
        Vo2Max=stat_model.vo2_max,
        FitnessAge=stat_model.fitness_age,
        WeightGrams=stat_model.weight_grams,
        IntensityMinutes=stat_model.intensity_minutes,
        UpdatedTimestamp=stat_model.updated_timestamp,
    )


def map_from_domain_to_response_daily_stat(
    stat_model: GarminDailyStatModel,
) -> GarminDailyStatResponse:
    """Map from domain GarminDailyStatModel to response contract GarminDailyStatResponse"""
    return GarminDailyStatResponse(
        stat_date=stat_model.stat_date,
        steps=stat_model.steps,
        resting_heart_rate=stat_model.resting_heart_rate,
        sleep_seconds=stat_model.sleep_seconds,
        peak_body_battery=stat_model.peak_body_battery,
        sleep_score=stat_model.sleep_score,
        hrv_last_night_average=stat_model.hrv_last_night_average,
        hrv_status=stat_model.hrv_status,
        training_readiness_score=stat_model.training_readiness_score,
        training_status=stat_model.training_status,
        vo2_max=stat_model.vo2_max,
        fitness_age=stat_model.fitness_age,
        weight_grams=stat_model.weight_grams,
        intensity_minutes=stat_model.intensity_minutes,
        updated_timestamp=stat_model.updated_timestamp,
    )


def map_from_domain_to_response_batch_upsert_result(
    failed_dates: list[date],
) -> BatchUpsertGarminDailyStatsResponse:
    """Map from the domain's list of failed dates to response BatchUpsertGarminDailyStatsResponse"""
    return BatchUpsertGarminDailyStatsResponse(failed_dates=failed_dates)
