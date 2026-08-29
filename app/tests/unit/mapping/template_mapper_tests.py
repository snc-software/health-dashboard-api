import template_service.features.templates.template_mapper as mapper
from template_service.contracts.template import CreateTemplateRequest
from template_service.features.templates.domain.template_models import TemplateModel
from template_service.features.templates.persistence.template_entities import Template
from tests.builders.template_builders import TemplateAutoFixture


class TemplateMapperTests:
    def test_can_map_from_persistence_template_to_domain_template_model(self):
        template = TemplateAutoFixture.generate(Template)

        result = mapper.map_from_persistence_to_domain(template)

        assert result.id == template.Id
        assert result.name == template.Name
        assert result.created_timestamp == template.CreatedTimestamp
        assert result.updated_timestamp == template.UpdatedTimestamp

    def test_can_map_from_domain_template_model_to_persistence_template(self):
        deleted = False
        template_model = TemplateAutoFixture.generate(TemplateModel)

        template = mapper.map_from_domain_to_persistence(template_model, deleted)

        assert template.Id == template_model.id
        assert template.Name == template_model.name
        assert template.CreatedTimestamp == template_model.created_timestamp
        assert template.UpdatedTimestamp == template_model.updated_timestamp
        assert template.Deleted == deleted

    def test_can_map_from_request_contract_create_template_request_to_domain_template_model(self):
        request = TemplateAutoFixture.generate(CreateTemplateRequest)

        template_model = mapper.map_from_contract_to_domain(request)

        assert template_model.name == request.name
        assert template_model.id is not None

    def test_can_map_from_domain_template_model_to_response_template_response(self):
        template_model = TemplateAutoFixture.generate(TemplateModel)

        template_response = mapper.map_from_domain_to_response(template_model)

        assert template_response.id == template_model.id
        assert template_response.name == template_model.name
        assert template_response.created_timestamp == template_model.created_timestamp
        assert template_response.updated_timestamp == template_model.updated_timestamp
