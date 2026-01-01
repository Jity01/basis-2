from .base import DataSourceHandler
from ..types import StoreConfig


class ContentHandler(DataSourceHandler):
    """Handler for direct content strings"""

    async def fetch(self, query: str, config: StoreConfig) -> str:
        """
        Return content directly (no fetching needed)

        Args:
            query: The content string itself
            config: Not used for content handler

        Returns:
            The query string as-is
        """
        return query

    def validate_config(self, config: StoreConfig) -> bool:
        """Content handler doesn't need config validation"""
        return True

