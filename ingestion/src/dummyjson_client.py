
import logging
import time
from urllib.parse import quote

import requests

from src.config import (
    API_BASE_URL,
    API_PAGE_SIZE,
    API_TIMEOUT,
    MAX_RETRIES,
)

logger = logging.getLogger(__name__)


class DummyJSONClient:

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": "EcommerceDataEngineeringProject/1.0",
            "Accept": "application/json",
        })

    def _get(self, endpoint, params=None):

        url = f"{API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"

        for attempt in range(1, MAX_RETRIES + 1):

            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=API_TIMEOUT,
                )

                response.raise_for_status()

                return response.json()

            except requests.RequestException as error:

                logger.warning(
                    "API request failed. Attempt %s/%s: %s",
                    attempt,
                    MAX_RETRIES,
                    error,
                )

                if attempt == MAX_RETRIES:
                    raise

                time.sleep(min(2 ** (attempt - 1), 8))

        raise RuntimeError("API request failed")

    def get_categories(self):

        logger.info("Retrieving product categories")

        data = self._get("/products/category-list")

        if not isinstance(data, list):
            raise ValueError("Unexpected category response")

        logger.info("Retrieved %s categories", len(data))

        return data

    def get_products_by_category(self, category):

        encoded_category = quote(category, safe="")

        endpoint = f"/products/category/{encoded_category}"

        skip = 0
        total = None

        while total is None or skip < total:

            params = {
                "limit": API_PAGE_SIZE,
                "skip": skip,
            }

            logger.info(
                "Extracting category=%s skip=%s limit=%s",
                category,
                skip,
                API_PAGE_SIZE,
            )

            response = self._get(endpoint, params=params)

            products = response.get("products", [])

            if total is None:
                total = int(response.get("total", 0))

            yield response

            if not products:
                break

            skip += len(products)

        logger.info(
            "Completed category extraction: %s",
            category,
        )

    def close(self):
        self.session.close()
