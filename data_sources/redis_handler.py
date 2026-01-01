import redis.asyncio as redis
from .base import DataSourceHandler
from ..types import RedisStoreConfig, StoreConfig


class RedisHandler(DataSourceHandler):
    """Handler for Redis data sources"""

    async def initialize(self, config: StoreConfig) -> None:
        """Initialize Redis client"""
        if not isinstance(config, RedisStoreConfig):
            raise ValueError("Config must be RedisStoreConfig")

        self._config = config
        self.client = redis.from_url(
            f"redis://{config.host}:{config.port}/{config.db}",
            password=config.password,
            ssl=config.ssl,
        )
        self._initialized = True

    async def fetch(self, query: str) -> str:
        """
        Fetch data from Redis

        Args:
            query: Redis key name

        Returns:
            Content from Redis key as string
        """
        if not self._initialized:
            raise RuntimeError("Handler not initialized. Call initialize() first.")

        value = await self.client.get(query)
        if value is None:
            return ""
        return value.decode("utf-8") if isinstance(value, bytes) else str(value)

    async def close(self) -> None:
        """Close Redis connection"""
        if self._initialized and self.client:
            await self.client.aclose()

    def validate_config(self, config: StoreConfig) -> bool:
        """Validate RedisStoreConfig"""
        return isinstance(config, RedisStoreConfig)
