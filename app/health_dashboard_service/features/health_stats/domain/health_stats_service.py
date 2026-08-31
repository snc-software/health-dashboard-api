from datetime import date

from ....infrastructure.postgres.persistence_controller_factory import (
    create_persistence_controller,
)
from ...garmin.persistence import garmin_reader as reader
from .. import health_stats_mapper as mapper
from .health_stats_models import DailyHealthStatModel


async def get_daily_health_stats(start_date: date, end_date: date) -> list[DailyHealthStatModel]:
    """Read every stored daily stat row in the inclusive range, ascending by date."""
    async with create_persistence_controller() as pc:
        stats = await reader.get_daily_stats_in_range(pc, start_date, end_date)
        return [mapper.map_from_persistence_to_domain_daily_health_stat(stat) for stat in stats]
