from .base import DataSourceHandler
from ..types import PostgresStoreConfig, StoreConfig


class PostgresHandler(DataSourceHandler):
    """Handler for PostgreSQL data sources"""

    async def fetch(self, query: str, config: StoreConfig) -> str:
        """
        Fetch data from PostgreSQL

        Args:
            query: SQL query string
            config: PostgresStoreConfig instance

        Returns:
            Content from query results as string
        """
        if not isinstance(config, PostgresStoreConfig):
            raise ValueError("Config must be PostgresStoreConfig")

        try:
            import asyncpg
        except ImportError:
            raise ImportError(
                "asyncpg is required for PostgreSQL support. Install with: pip install asyncpg"
            )

        # Connect and execute query
        conn = await asyncpg.connect(config.connection_url)
        try:
            rows = await conn.fetch(query)

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
        finally:
            await conn.close()

    def validate_config(self, config: StoreConfig) -> bool:
        """Validate PostgresStoreConfig"""
        return isinstance(config, PostgresStoreConfig) and config.connection_url

