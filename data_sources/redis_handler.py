from .base import DataSourceHandler
from ..types import RedisStoreConfig, StoreConfig


class RedisHandler(DataSourceHandler):
    """Handler for Redis data sources"""

    async def fetch(self, query: str, config: StoreConfig) -> str:
        """
        Fetch data from Redis

        Args:
            query: Redis key name
            config: RedisStoreConfig instance

        Returns:
            Content from Redis key as string
        """
        if not isinstance(config, RedisStoreConfig):
            raise ValueError("Config must be RedisStoreConfig")

        try:
            import redis.asyncio as redis
        except ImportError:
            try:
                import redis
            except ImportError:
                raise ImportError(
                    "redis is required for Redis support. Install with: pip install redis"
                )

        # Create Redis client
        if hasattr(redis, "from_url"):
            # Async redis
            client = redis.from_url(
                f"redis://{config.host}:{config.port}/{config.db}",
                password=config.password,
                ssl=config.ssl,
            )
            try:
                value = await client.get(query)
                if value is None:
                    return ""
                return value.decode("utf-8") if isinstance(value, bytes) else str(value)
            finally:
                await client.aclose()
        else:
            # Sync redis
            client = redis.Redis(
                host=config.host,
                port=config.port,
                db=config.db,
                password=config.password,
                ssl=config.ssl,
            )
            value = client.get(query)
            if value is None:
                return ""
            return value.decode("utf-8") if isinstance(value, bytes) else str(value)

    def validate_config(self, config: StoreConfig) -> bool:
        """Validate RedisStoreConfig"""
        return isinstance(config, RedisStoreConfig)

