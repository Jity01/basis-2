import json
from typing import Optional
from .base import DataSourceHandler
from ..types import S3StoreConfig, StoreConfig


class S3Handler(DataSourceHandler):
    """Handler for S3 data sources"""

    async def fetch(self, query: str, config: StoreConfig) -> str:
        """
        Fetch data from S3

        Args:
            query: S3 object key/path (e.g., "logs/agent-123.json")
            config: S3StoreConfig instance

        Returns:
            Content from S3 object as string
        """
        if not isinstance(config, S3StoreConfig):
            raise ValueError("Config must be S3StoreConfig")

        try:
            import boto3
            from botocore.exceptions import ClientError
        except ImportError:
            raise ImportError(
                "boto3 is required for S3 support. Install with: pip install boto3"
            )

        # Create S3 client
        s3_client = boto3.client(
            "s3",
            region_name=config.region,
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
            endpoint_url=config.endpoint_url,
        )

        try:
            # Download object
            response = s3_client.get_object(Bucket=config.bucket, Key=query)
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

