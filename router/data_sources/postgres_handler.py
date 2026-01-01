import asyncpg
from .base import DataSourceHandler
from ..types import PostgresStoreConfig, StoreConfig


class PostgresHandler(DataSourceHandler):
    """Handler for PostgreSQL data sources"""

    async def initialize(self, config: StoreConfig) -> None:
        """Initialize PostgreSQL connection pool"""
        if not isinstance(config, PostgresStoreConfig):
            raise ValueError("Config must be PostgresStoreConfig")

        self._config = config
        self.conn = await asyncpg.connect(config.connection_url)
        self._initialized = True

    async def fetch(self, query: str) -> str:
        """
        Fetch data from PostgreSQL

        Args:
            query: SQL query string

        Returns:
            Content from query results as string
        """
        if not self._initialized:
            raise RuntimeError("Handler not initialized. Call initialize() first.")

        rows = await self.conn.fetch(query)

        if not rows:
            return ""

        # Extract text content from rows
        # Try to find a text column, or concatenate all columns
        results = []
        for row in rows:
            # Look for common content column names
            row_dict = dict(row)
            for field in ["content", "text", "body", "message"]:
                if field in row_dict:
                    results.append(str(row_dict[field]))
                    break
            else:
                # No common field, join all values
                results.append(" | ".join(str(v) for v in row_dict.values()))

        return "\n\n".join(results)

    async def close(self) -> None:
        """Close PostgreSQL connection"""
        if self._initialized and self.conn:
            await self.conn.close()

    def validate_config(self, config: StoreConfig) -> bool:
        """Validate PostgresStoreConfig"""
        return isinstance(config, PostgresStoreConfig) and config.connection_url
