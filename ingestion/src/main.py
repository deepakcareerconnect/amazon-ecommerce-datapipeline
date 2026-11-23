
import json
import logging
import uuid

from datetime import datetime, timezone

from src.config import (
    CATEGORIES,
    STORAGE_MODE
)

from src.dummyjson_client import DummyJSONClient
from src.storage import RawStorage


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)


def utc_now():
    return datetime.now(timezone.utc)


def run_ingestion():

    execution_id = f"exec_{uuid.uuid4().hex[:12]}"

    ingestion_date = utc_now().strftime("%Y-%m-%d")

    run_timestamp = utc_now().strftime("%Y%m%dT%H%M%SZ")

    client = DummyJSONClient()
    storage = RawStorage(mode=STORAGE_MODE)

    metadata = {
        "execution_id": execution_id,
        "source": "DummyJSON",
        "dataset": "products",
        "ingestion_date": ingestion_date,
        "started_at": utc_now().isoformat(),
        "status": "RUNNING",
        "categories": [],
        "total_records_extracted": 0,
        "total_files_uploaded": 0,
        "errors": []
    }

    try:

        # 1. Extract and save available categories
        categories = client.get_categories()

        category_key = (
            f"raw/categories/"
            f"ingestion_date={ingestion_date}/"
            f"run_id={execution_id}/"
            f"categories_{run_timestamp}.json"
        )

        storage.save_json(
            {"categories": categories},
            category_key
        )

        # 2. Extract products category-wise
        for category in CATEGORIES:

            logger.info(
                "Starting category: %s",
                category
            )

            category_records = 0
            category_files = 0

            category_result = {
                "category": category,
                "status": "SUCCESS",
                "records_extracted": 0,
                "files_uploaded": 0
            }

            try:

                pages = client.get_products_by_category(
                    category
                )

                for page_number, response in enumerate(
                    pages,
                    start=1
                ):

                    products = response.get("products", [])

                    category_records += len(products)

                    key = (
                        f"raw/products/"
                        f"ingestion_date={ingestion_date}/"
                        f"run_id={execution_id}/"
                        f"category={category}/"
                        f"page_{page_number:04d}.json"
                    )

                    storage.save_json(
                        response,
                        key
                    )

                    if STORAGE_MODE == "s3":
                        storage.verify_s3_object(key)

                    category_files += 1

                category_result["records_extracted"] = (
                    category_records
                )

                category_result["files_uploaded"] = (
                    category_files
                )

                metadata["total_records_extracted"] += (
                    category_records
                )

                metadata["total_files_uploaded"] += (
                    category_files
                )

                logger.info(
                    "Category completed: %s | records=%s | files=%s",
                    category,
                    category_records,
                    category_files
                )

            except Exception as error:

                category_result["status"] = "FAILED"

                category_result["error"] = str(error)

                metadata["errors"].append({
                    "category": category,
                    "error": str(error)
                })

                logger.exception(
                    "Category extraction failed: %s",
                    category
                )

            metadata["categories"].append(
                category_result
            )

        # 3. Determine overall execution status
        failed_categories = [
            item for item in metadata["categories"]
            if item["status"] == "FAILED"
        ]

        if failed_categories:
            metadata["status"] = (
                "PARTIAL" if metadata["total_files_uploaded"] > 0
                else "FAILED"
            )
        else:
            metadata["status"] = "SUCCESS"

    except Exception as error:

        metadata["status"] = (
            "PARTIAL" if metadata["total_files_uploaded"] > 0
            else "FAILED"
        )

        metadata["errors"].append({
            "error": str(error)
        })

        logger.exception("Ingestion execution failed")

    finally:

        metadata["finished_at"] = utc_now().isoformat()

        metadata_key = (
            f"logs/ingestion/"
            f"ingestion_date={ingestion_date}/"
            f"run_id={execution_id}/"
            f"metadata.json"
        )

        try:

            storage.save_json(
                metadata,
                metadata_key
            )

        except Exception:

            logger.exception(
                "Could not save ingestion metadata"
            )

        client.close()

    logger.info(
        "Ingestion completed: execution_id=%s status=%s",
        execution_id,
        metadata["status"]
    )

    print(json.dumps(metadata, indent=2))

    if metadata["status"] == "FAILED":
        raise RuntimeError("Ingestion failed")

    return metadata


if __name__ == "__main__":
    run_ingestion()
