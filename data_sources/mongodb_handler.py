import json
from typing import Optional
from .base import DataSourceHandler
from ..types import MongoDBStoreConfig, StoreConfig


class MongoDBHandler(DataSourceHandler):
    """Handler for MongoDB data sources"""

    async def fetch(self, query: str, config: StoreConfig) -> str:
        """
        Fetch data from MongoDB

        Args:
            query: MongoDB query as JSON string or collection name
            config: MongoDBStoreConfig instance

        Returns:
            Content from MongoDB as string
        """
        if not isinstance(config, MongoDBStoreConfig):
            raise ValueError("Config must be MongoDBStoreConfig")

        try:
            from pymongo import MongoClient
        except ImportError:
            raise ImportError(
                "pymongo is required for MongoDB support. Install with: pip install pymongo"
            )

        # Connect to MongoDB
        client = MongoClient(config.connection_string)
        db = client[config.database]

        try:
            # Parse query - could be JSON string with collection, or just collection name
            # Format: "collection_name" or '{"collection": "name", "query": {...}}'
            try:
                query_data = json.loads(query)
                if isinstance(query_data, dict):
                    collection_name = query_data.get("collection")
                    query_dict = query_data.get("query", {})
                else:
                    # If parsed but not dict, treat as collection name
                    collection_name = query
                    query_dict = {}
            except (json.JSONDecodeError, TypeError):
                # Assume it's a collection name
                collection_name = query
                query_dict = {}

            if not collection_name:
                raise ValueError("MongoDB query must specify collection name")

            collection = db[collection_name]
            # Fetch documents
            documents = list(collection.find(query_dict))

            if not documents:
                return ""

            # Extract text content from documents
            # If single document, try to find content field
            if len(documents) == 1:
                doc = documents[0]
                for field in ["content", "text", "body", "message"]:
                    if field in doc:
                        return str(doc[field])
                return json.dumps(doc, indent=2, default=str)

            # Multiple documents - concatenate
            results = []
            for doc in documents:
                for field in ["content", "text", "body", "message"]:
                    if field in doc:
                        results.append(str(doc[field]))
                        break
                else:
                    results.append(json.dumps(doc, indent=2, default=str))

            return "\n\n".join(results)

        finally:
            client.close()

    def validate_config(self, config: StoreConfig) -> bool:
        """Validate MongoDBStoreConfig"""
        return (
            isinstance(config, MongoDBStoreConfig)
            and config.connection_string
            and config.database
        )

