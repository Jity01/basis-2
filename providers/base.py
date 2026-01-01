from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from ..types import ModelConfig


@dataclass
class ModelResponse:
    """Response from a model provider"""

    content: str
    tokens_used: int
    cost: float  # USD
    latency_ms: int
    model: str
    provider: str


class ModelProvider(ABC):
    """Abstract base class for model providers"""

    @abstractmethod
    async def call(
        self,
        content: str,
        config: ModelConfig,
        system_prompt: Optional[str] = None,
    ) -> ModelResponse:
        """
        Call the model API

        Args:
            content: Input text content
            config: Model configuration
            system_prompt: Optional system prompt

        Returns:
            ModelResponse with content, tokens, cost, and latency
        """
        pass

    @abstractmethod
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """
        Calculate cost based on token usage

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model name

        Returns:
            Cost in USD
        """
        pass

