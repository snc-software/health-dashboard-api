from template_service.contracts.template import TemplateResponse
from template_service.features.templates.domain.template_models import TemplateModel
from tests.builders.template_builders import TemplateAutoFixture


class ContractSerialisationTests:
    def test_responses_serialise_as_camel_case(self):
        model = TemplateAutoFixture.generate(TemplateModel)
        response = TemplateResponse(
            id=model.id,
            name=model.name,
            created_timestamp=model.created_timestamp,
            updated_timestamp=model.updated_timestamp,
        )

        payload = response.model_dump(by_alias=True)

        assert "createdTimestamp" in payload
        assert "updatedTimestamp" in payload

    def test_responses_accept_either_spelling_on_input(self):
        model = TemplateAutoFixture.generate(TemplateModel)

        by_alias = TemplateResponse(
            id=model.id,
            name=model.name,
            createdTimestamp=model.created_timestamp,
            updatedTimestamp=model.updated_timestamp,
        )

        assert by_alias.created_timestamp == model.created_timestamp
