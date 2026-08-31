import logging
from typing import Annotated

from fastapi import APIRouter, Path

from ..contracts.health_stats import DailyHealthStatResponse, GetDailyHealthStatsRequest
from ..features.health_stats import health_stats_mapper as mapper
from ..features.health_stats.domain import health_stats_service as service
from ..infrastructure.logging import values as log_values
from ..openapi import open_api_tags as OAPI
from ..openapi import responses as OAPIResponses

logger = logging.getLogger("health_stats")

router = APIRouter()


@router.get(
    "/start/{startDate}/end/{endDate}/health-stats",
    summary="Read stored daily health stats for a date range",
    description=(
        "Returns the daily health stat records stored for the inclusive start_date/end_date "
        "range, ordered ascending by date. Dates in the range with no stored row are simply "
        "omitted from the response."
    ),
    tags=OAPI.HEALTH_STATS,
    response_model=list[DailyHealthStatResponse],
    responses={**OAPIResponses.BAD_REQUEST, **OAPIResponses.SERVER_ERROR},
)
async def get_daily_health_stats(
    query: Annotated[GetDailyHealthStatsRequest, Path()],
) -> list[DailyHealthStatResponse]:
    logger.info(
        "get_daily_health_stats called",
        extra={log_values.START_DATE: query.start_date, log_values.END_DATE: query.end_date},
    )

    stats = await service.get_daily_health_stats(query.start_date, query.end_date)

    logger.info(
        "get_daily_health_stats succeeded",
        extra={log_values.START_DATE: query.start_date, log_values.END_DATE: query.end_date},
    )
    return [mapper.map_from_domain_to_response_daily_health_stat(stat) for stat in stats]
