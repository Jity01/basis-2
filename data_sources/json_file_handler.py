import json
import os
from pathlib import Path
from .base import DataSourceHandler
from ..types import JsonFileStoreConfig, StoreConfig


class JsonFileHandler(DataSourceHandler):
    """Handler for JSON file data sources"""

    async def initialize(self, config: StoreConfig) -> None:
        """Initialize JSON file handler (stores base_path)"""
        if not isinstance(config, JsonFileStoreConfig):
            raise ValueError("Config must be JsonFileStoreConfig")

        self._config = config
        self._initialized = True

    async def fetch(self, query: str) -> str:
        """
        Fetch data from JSON file

        Args:
            query: File path to JSON file

        Returns:
            Content from JSON file as string
        """
        if not self._initialized:
            raise RuntimeError("Handler not initialized. Call initialize() first.")

        # Resolve path (with optional base_path)
        if self._config.base_path:
            file_path = Path(self._config.base_path) / query
        else:
            file_path = Path(query)

        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")

        # Read and parse JSON
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract text content
        if isinstance(data, dict):
            # Look for common content fields
            for field in ["content", "text", "body", "message"]:
                if field in data:
                    return str(data[field])
            # If no common field, return JSON string
            return json.dumps(data, indent=2)
        elif isinstance(data, list):
            # If list, try to extract content from each item
            results = []
            for item in data:
                if isinstance(item, dict):
                    for field in ["content", "text", "body", "message"]:
                        if field in item:
                            results.append(str(item[field]))
                            break
                    else:
                        results.append(json.dumps(item, indent=2))
                else:
                    results.append(str(item))
            return "\n\n".join(results)
        else:
            return str(data)

    def validate_config(self, config: StoreConfig) -> bool:
        """Validate JsonFileStoreConfig"""
        return isinstance(config, JsonFileStoreConfig)

