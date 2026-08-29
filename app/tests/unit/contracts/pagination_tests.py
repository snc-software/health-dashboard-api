import pytest
from pydantic import ValidationError

from health_dashboard_service.contracts.pagination import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    PaginationParameters,
)


class PaginationParameterTests:
    def test_defaults(self):
        parameters = PaginationParameters()

        assert parameters.page == 1
        assert parameters.page_size == DEFAULT_PAGE_SIZE
        assert parameters.offset == 0

    @pytest.mark.parametrize(
        ("page", "page_size", "expected"),
        [(1, 20, 0), (2, 20, 20), (3, 50, 100)],
    )
    def test_offset(self, page, page_size, expected):
        assert PaginationParameters(page=page, page_size=page_size).offset == expected

    def test_rejects_a_page_size_above_the_ceiling(self):
        with pytest.raises(ValidationError):
            PaginationParameters(page_size=MAX_PAGE_SIZE + 1)

    def test_rejects_a_non_positive_page_size(self):
        with pytest.raises(ValidationError):
            PaginationParameters(page_size=0)

    def test_rejects_a_non_positive_page(self):
        with pytest.raises(ValidationError):
            PaginationParameters(page=0)
