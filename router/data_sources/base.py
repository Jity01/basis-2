from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..types import StoreConfig


class DataSourceHandler(ABC):
    """Abstract base class for data source handlers"""

    def __init__(self):
        self._initialized = False
        self._config = None

    @abstractmethod
    async def initialize(self, config: StoreConfig) -> None:
        """
        Initialize connection to the data source (called once during connect_data_source)

        Args:
            config: Store configuration for this data source
        """
        pass

    @abstractmethod
    async def fetch(self, query: str) -> str:
        """
        Fetch data from the data source based on query

        Args:
            query: Query/reference string specific to the data source type

        Returns:
            Extracted text content as string
        """
        pass

    @abstractmethod
    def validate_config(self, config: StoreConfig) -> bool:
        """
        Validate that the config is correct for this handler type

        Args:
            config: Store configuration to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    async def close(self) -> None:
        """
        Close connection to the data source (optional, for cleanup)
        """
        pass

