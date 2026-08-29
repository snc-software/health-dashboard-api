import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ..contracts.pagination import PagedResponse, Pagination, PaginationParameters
from ..contracts.template import CreateTemplateRequest, TemplateResponse
from ..features.templates import template_mapper as mapper
from ..features.templates.domain import template_service as service
from ..infrastructure.logging import values as log_values
from ..openapi import open_api_tags as OAPI
from ..openapi import responses as OAPIResponses

logger = logging.getLogger("templates")

router = APIRouter()


@router.get(
    "/templates/{template_id}",
    summary="Retrieve a template by its ID",
    tags=OAPI.TEMPLATES,
    response_model=TemplateResponse,
    responses={
        **OAPIResponses.BAD_REQUEST,
        **OAPIResponses.NOT_FOUND,
        **OAPIResponses.SERVER_ERROR,
    },
)
async def get_template(template_id: UUID) -> TemplateResponse:
    logger.info("get_template called", extra={log_values.TEMPLATE_ID: template_id})

    template = await service.get_by_id(template_id)
    if not template:
        logger.info("get_template not found", extra={log_values.TEMPLATE_ID: template_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    logger.info("get_template succeeded", extra={log_values.TEMPLATE_ID: template_id})
    return mapper.map_from_domain_to_response(template)


@router.get(
    "/templates",
    summary="List templates",
    tags=OAPI.TEMPLATES,
    response_model=PagedResponse[TemplateResponse],
    responses={**OAPIResponses.BAD_REQUEST, **OAPIResponses.SERVER_ERROR},
)
async def list_templates(
    pagination: Annotated[PaginationParameters, Depends()],
) -> PagedResponse[TemplateResponse]:
    logger.info(
        "list_templates called",
        extra={
            log_values.PAGE: pagination.page,
            log_values.PAGE_SIZE: pagination.page_size,
        },
    )

    templates, total = await service.get_page(pagination.page, pagination.page_size)

    logger.info(
        "list_templates succeeded",
        extra={
            log_values.PAGE: pagination.page,
            log_values.PAGE_SIZE: pagination.page_size,
            log_values.TOTAL: total,
        },
    )
    return PagedResponse(
        items=[mapper.map_from_domain_to_response(t) for t in templates],
        pagination=Pagination(
            total=total,
            page=pagination.page,
            size=len(templates),
        ),
    )


@router.post(
    "/templates",
    summary="Create a template",
    tags=OAPI.TEMPLATES,
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={**OAPIResponses.BAD_REQUEST, **OAPIResponses.SERVER_ERROR},
)
async def create_template(body: CreateTemplateRequest) -> TemplateResponse:
    logger.info("create_template called", extra={log_values.TEMPLATE_NAME: body.name})

    template = mapper.map_from_contract_to_domain(body)
    created = await service.create(template)

    logger.info(
        "create_template succeeded",
        extra={log_values.TEMPLATE_ID: created.id, log_values.TEMPLATE_NAME: created.name},
    )
    return mapper.map_from_domain_to_response(created)
