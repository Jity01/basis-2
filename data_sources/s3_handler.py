import json
import boto3
from botocore.exceptions import ClientError
from .base import DataSourceHandler
from ..types import S3StoreConfig, StoreConfig


class S3Handler(DataSourceHandler):
    """Handler for S3 data sources"""

    async def initialize(self, config: StoreConfig) -> None:
        """Initialize S3 client"""
        if not isinstance(config, S3StoreConfig):
            raise ValueError("Config must be S3StoreConfig")

        self._config = config
        self.s3_client = boto3.client(
            "s3",
            region_name=config.region,
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
            endpoint_url=config.endpoint_url,
        )
        self._initialized = True

    async def fetch(self, query: str) -> str:
        """
        Fetch data from S3

        Args:
            query: S3 object key/path (e.g., "logs/agent-123.json")

        Returns:
            Content from S3 object as string
        """
        if not self._initialized:
            raise RuntimeError("Handler not initialized. Call initialize() first.")

        try:
            # Download object
            response = self.s3_client.get_object(Bucket=self._config.bucket, Key=query)
            content = response["Body"].read().decode("utf-8")

            # If JSON, try to extract text content
            try:
                data = json.loads(content)
                # If it's a dict, try to find common text fields
                if isinstance(data, dict):
                    # Look for common content fields
                    for field in ["content", "text", "body", "message"]:
                        if field in data:
                            return str(data[field])
                    # If no common field, return JSON string
                    return json.dumps(data, indent=2)
                return str(data)
            except (json.JSONDecodeError, TypeError):
                # Not JSON, return as-is
                return content

        except ClientError as e:
            raise ValueError(f"Failed to fetch from S3: {e}")

    def validate_config(self, config: StoreConfig) -> bool:
        """Validate S3StoreConfig"""
        return isinstance(config, S3StoreConfig) and config.region and config.bucket

