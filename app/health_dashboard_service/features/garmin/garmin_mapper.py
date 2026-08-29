"""Mapping between Garmin persistence rows, domain models, and contracts."""

from ...contracts.garmin import (
    AuthenticateGarminRequest,
    GarminAuthenticateResponse,
    GarminDailyStatResponse,
    SubmitGarminMfaRequest,
)
from .domain.garmin_models import (
    GarminAuthenticationResultModel,
    GarminCredentialsModel,
    GarminDailyStatModel,
    GarminMfaSubmissionModel,
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


def map_from_persistence_to_domain_daily_stat(stat: GarminDailyStat) -> GarminDailyStatModel:
    """Map from persistence GarminDailyStat to domain GarminDailyStatModel"""
    return GarminDailyStatModel(
        id=stat.Id,
        stat_date=stat.StatDate,
        steps=stat.Steps,
        resting_heart_rate=stat.RestingHeartRate,
        sleep_seconds=stat.SleepSeconds,
        body_battery=stat.BodyBattery,
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
        BodyBattery=stat_model.body_battery,
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
        body_battery=stat_model.body_battery,
        updated_timestamp=stat_model.updated_timestamp,
    )
