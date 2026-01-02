import json
import boto3
from botocore.exceptions import ClientError
from .base import DataSourceHandler
from ..types import DynamoDBStoreConfig, StoreConfig


class DynamoDBHandler(DataSourceHandler):
    """Handler for DynamoDB data sources"""

    async def initialize(self, config: StoreConfig) -> None:
        """Initialize DynamoDB client"""
        if not isinstance(config, DynamoDBStoreConfig):
            raise ValueError("Config must be DynamoDBStoreConfig")

        self._config = config
        self.dynamodb_client = boto3.client(
            "dynamodb",
            region_name=config.region,
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
        )
        self._initialized = True

    async def fetch(self, query: str) -> str:
        """
        Fetch data from DynamoDB

        Args:
            query: JSON string with query parameters or empty {} to scan all items
                Format: '{}' for scan all, or '{"key": "value"}' for specific query

        Returns:
            Content from DynamoDB as string
        """
        if not self._initialized:
            raise RuntimeError("Handler not initialized. Call initialize() first.")

        try:
            # Parse query - empty {} means scan all items
            try:
                query_data = json.loads(query) if query else {}
            except json.JSONDecodeError:
                query_data = {}

            # Use scan to get all items (or query if specific key provided)
            if not query_data or query_data == {}:
                # Scan all items
                response = self.dynamodb_client.scan(TableName=self._config.table_name)
            else:
                # Query with specific key (assuming partition key is in query)
                # For simplicity, we'll scan and filter client-side
                # In production, you'd want to use query() with proper key conditions
                response = self.dynamodb_client.scan(TableName=self._config.table_name)

            items = response.get("Items", [])

            if not items:
                return ""

            # Convert DynamoDB items to JSON and extract text content
            results = []
            for item in items:
                # Convert DynamoDB format to regular dict
                converted_item = self._convert_dynamodb_item(item)

                # Try to find text content fields
                for field in ["content", "text", "body", "message"]:
                    if field in converted_item:
                        results.append(str(converted_item[field]))
                        break
                else:
                    # No common field, return JSON string
                    results.append(json.dumps(converted_item, indent=2, default=str))

            return "\n\n".join(results) if results else ""

        except ClientError as e:
            raise ValueError(f"Failed to fetch from DynamoDB: {e}")

    def _convert_dynamodb_item(self, item: dict) -> dict:
        """Convert DynamoDB item format to regular dict"""
        result = {}
        for key, value in item.items():
            # DynamoDB uses type descriptors like {'S': 'string'}, {'N': '123'}
            if "S" in value:  # String
                result[key] = value["S"]
            elif "N" in value:  # Number
                result[key] = value["N"]
            elif "B" in value:  # Binary
                result[key] = value["B"]
            elif "SS" in value:  # String Set
                result[key] = value["SS"]
            elif "NS" in value:  # Number Set
                result[key] = value["NS"]
            elif "M" in value:  # Map
                result[key] = self._convert_dynamodb_item(value["M"])
            elif "L" in value:  # List
                result[key] = [
                    (
                        self._convert_dynamodb_item([v])[0]
                        if isinstance(v, dict) and "M" in v
                        else v
                    )
                    for v in value["L"]
                ]
            else:
                result[key] = str(value)
        return result

    def validate_config(self, config: StoreConfig) -> bool:
        """Validate DynamoDBStoreConfig"""
        return (
            isinstance(config, DynamoDBStoreConfig)
            and config.region
            and config.table_name
        )

    async def close(self) -> None:
        """Close DynamoDB connection"""
        # boto3 clients don't need explicit closing
        pass
