
import json
import logging
from pathlib import Path

import boto3

from src.config import (
    AWS_REGION,
    S3_BUCKET,
    DATA_DIR
)

logger = logging.getLogger(__name__)


class RawStorage:

    def __init__(self, mode="local"):

        self.mode = mode

        if self.mode == "s3":

            if not S3_BUCKET:
                raise ValueError(
                    "S3_BUCKET is missing in .env"
                )

            self.s3 = boto3.client(
                "s3",
                region_name=AWS_REGION
            )

        else:
            self.s3 = None

    def save_json(self, data, key):

        json_content = json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        )

        if self.mode == "local":

            file_path = DATA_DIR / key

            file_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            file_path.write_text(
                json_content,
                encoding="utf-8"
            )

            logger.info(
                "Saved local JSON: %s",
                file_path
            )

            return str(file_path)

        elif self.mode == "s3":

            self.s3.put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=json_content.encode("utf-8"),
                ContentType="application/json"
            )

            logger.info(
                "Uploaded to S3: s3://%s/%s",
                S3_BUCKET,
                key
            )

            return f"s3://{S3_BUCKET}/{key}"

        else:
            raise ValueError(
                f"Unsupported storage mode: {self.mode}"
            )

    def verify_s3_object(self, key):

        if self.mode != "s3":
            return True

        self.s3.head_object(
            Bucket=S3_BUCKET,
            Key=key
        )

        return True
