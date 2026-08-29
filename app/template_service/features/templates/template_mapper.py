from datetime import UTC, datetime
from uuid import uuid4

from ...contracts.template import CreateTemplateRequest, TemplateResponse
from .domain.template_models import TemplateModel
from .persistence.template_entities import Template


def map_from_persistence_to_domain(template: Template) -> TemplateModel:
    """Map from persistence Template to domain TemplateModel"""
    return TemplateModel(
        id=template.Id,
        name=template.Name,
        created_timestamp=template.CreatedTimestamp,
        updated_timestamp=template.UpdatedTimestamp,
    )


def map_from_domain_to_persistence(
    template_model: TemplateModel, deleted: bool = False
) -> Template:
    """Map from domain TemplateModel to persistence Template"""
    return Template(
        Id=template_model.id,
        Name=template_model.name,
        CreatedTimestamp=template_model.created_timestamp,
        UpdatedTimestamp=template_model.updated_timestamp,
        Deleted=deleted,
    )


def map_from_contract_to_domain(create_template_request: CreateTemplateRequest) -> TemplateModel:
    """Map from request contract CreateTemplateRequest to domain TemplateModel"""
    now = datetime.now(UTC)
    return TemplateModel(
        id=uuid4(),
        name=create_template_request.name,
        created_timestamp=now,
        updated_timestamp=now,
    )


def map_from_domain_to_response(template_model: TemplateModel) -> TemplateResponse:
    """Map from domain TemplateModel to response contract TemplateResponse"""
    return TemplateResponse(
        id=template_model.id,
        name=template_model.name,
        created_timestamp=template_model.created_timestamp,
        updated_timestamp=template_model.updated_timestamp,
    )
