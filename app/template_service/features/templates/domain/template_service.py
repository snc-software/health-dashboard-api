from uuid import UUID

from ....infrastructure.postgres.persistence_controller_factory import (
    create_persistence_controller,
)
from .. import template_mapper as mapper
from ..persistence import template_reader as reader
from ..persistence import template_writer as writer
from .template_models import TemplateModel


async def get_by_id(template_id: UUID) -> TemplateModel | None:
    """Fetch a template by its unique identifier."""
    async with create_persistence_controller() as pc:
        template = await reader.get_by_id(pc, template_id)
        return mapper.map_from_persistence_to_domain(template) if template else None


async def get_page(page: int, page_size: int) -> tuple[list[TemplateModel], int]:
    """Get a page of templates along with the total available count."""
    offset = (page - 1) * page_size
    async with create_persistence_controller() as pc:
        templates = await reader.get_page(pc, limit=page_size, offset=offset)
        total = await reader.count(pc)
        return [mapper.map_from_persistence_to_domain(t) for t in templates], total


async def create(template: TemplateModel) -> TemplateModel:
    """Create a new template."""
    async with create_persistence_controller() as pc:
        persistence_template = mapper.map_from_domain_to_persistence(template, False)
        created = await writer.create(pc, persistence_template)
        await pc.save_changes()
        return mapper.map_from_persistence_to_domain(created)
