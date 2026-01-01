import time
from typing import Optional
from openai import AsyncOpenAI
from .base import ModelProvider, ModelResponse
from ..types import ModelConfig


class OpenAIProvider(ModelProvider):
    """Provider for OpenAI models"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def call(
        self,
        content: str,
        config: ModelConfig,
        system_prompt: Optional[str] = None,
    ) -> ModelResponse:
        """Call OpenAI API"""

        # Use system prompt from config or parameter
        sys_prompt = system_prompt or config.system_prompt

        start_time = time.time()

        try:
            messages = []
            if sys_prompt:
                messages.append({"role": "system", "content": sys_prompt})
            messages.append({"role": "user", "content": content})

            response = await self.client.chat.completions.create(
                model=config.model,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Extract response content
            response_text = response.choices[0].message.content or ""

            # Get token usage
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            total_tokens = input_tokens + output_tokens

            # Calculate cost
            cost = self.calculate_cost(input_tokens, output_tokens, config.model)

            return ModelResponse(
                content=response_text,
                tokens_used=total_tokens,
                cost=cost,
                latency_ms=latency_ms,
                model=config.model,
                provider="openai",
            )
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate OpenAI pricing"""
        # Pricing as of 2024 (approximate, update as needed)
        pricing = {
            "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
            "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
            "gpt-4-turbo": {"input": 10.00 / 1_000_000, "output": 30.00 / 1_000_000},
            "gpt-4": {"input": 30.00 / 1_000_000, "output": 60.00 / 1_000_000},
            "gpt-3.5-turbo": {"input": 0.50 / 1_000_000, "output": 1.50 / 1_000_000},
        }

        # Default pricing if model not found
        default = {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000}
        rates = pricing.get(model, default)

        return (input_tokens * rates["input"]) + (output_tokens * rates["output"])

