
from unittest.mock import Mock, patch

from src.dummyjson_client import DummyJSONClient


def create_mock_response(data):
    """Create a mock HTTP response."""
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = data
    return response


def test_get_categories():
    """Verify that product categories are retrieved correctly."""

    client = DummyJSONClient()

    expected_categories = [
        "smartphones",
        "laptops",
        "furniture"
    ]

    mock_response = create_mock_response(expected_categories)

    try:
        with patch.object(
            client.session,
            "get",
            return_value=mock_response
        ):
            categories = client.get_categories()

        assert categories == expected_categories
        assert len(categories) == 3

    finally:
        client.close()


def test_get_products_by_category_pagination():
    """Verify that product extraction handles multiple pages."""

    client = DummyJSONClient()

    first_page = {
        "products": [
            {"id": 1, "title": "Phone A"},
            {"id": 2, "title": "Phone B"}
        ],
        "total": 3,
        "skip": 0,
        "limit": 2
    }

    second_page = {
        "products": [
            {"id": 3, "title": "Phone C"}
        ],
        "total": 3,
        "skip": 2,
        "limit": 2
    }

    mock_responses = [
        create_mock_response(first_page),
        create_mock_response(second_page)
    ]

    try:
        with patch.object(
            client.session,
            "get",
            side_effect=mock_responses
        ) as mock_get:

            pages = list(
                client.get_products_by_category("smartphones")
            )

        assert len(pages) == 2

        all_products = [
            product
            for page in pages
            for product in page["products"]
        ]

        assert len(all_products) == 3

        product_ids = [
            product["id"]
            for product in all_products
        ]

        assert product_ids == [1, 2, 3]

        assert mock_get.call_count == 2

    finally:
        client.close()


def test_get_categories_rejects_invalid_response():
    """Verify that an unexpected category response raises an error."""

    client = DummyJSONClient()

    mock_response = create_mock_response(
        {"categories": ["smartphones"]}
    )

    try:
        with patch.object(
            client.session,
            "get",
            return_value=mock_response
        ):
            try:
                client.get_categories()
                assert False, "Expected ValueError was not raised"
            except ValueError:
                pass

    finally:
        client.close()
