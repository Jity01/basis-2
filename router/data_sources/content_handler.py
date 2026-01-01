from .base import DataSourceHandler
from ..types import StoreConfig


class ContentHandler(DataSourceHandler):
    """Handler for direct content strings"""

    async def initialize(self, config: StoreConfig) -> None:
        """Initialize content handler (no-op)"""
        self._config = config
        self._initialized = True

    async def fetch(self, query: str) -> str:
        """
        Return content directly (no fetching needed)

        Args:
            query: The content string itself

        Returns:
            The query string as-is
        """
        if not self._initialized:
            raise RuntimeError("Handler not initialized. Call initialize() first.")
        return query

    def validate_config(self, config: StoreConfig) -> bool:
        """Content handler doesn't need config validation"""
        return True

