import time
from typing import Optional
from .base import ModelProvider, ModelResponse
from ..types import ModelConfig


class AnthropicProvider(ModelProvider):
    """Provider for Anthropic Claude models"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def call(
        self,
        content: str,
        config: ModelConfig,
        system_prompt: Optional[str] = None,
    ) -> ModelResponse:
        """Call Anthropic API"""
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ImportError(
                "anthropic is required for Anthropic support. Install with: pip install anthropic"
            )

        client = AsyncAnthropic(api_key=self.api_key)

        # Use system prompt from config or parameter
        sys_prompt = system_prompt or config.system_prompt

        start_time = time.time()

        try:
            message = await client.messages.create(
                model=config.model,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                system=sys_prompt,
                messages=[
                    {"role": "user", "content": content}
                ],
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Extract response content
            response_text = ""
            if message.content:
                for block in message.content:
                    if hasattr(block, "text"):
                        response_text += block.text
                    elif isinstance(block, str):
                        response_text += block

            # Get token usage
            input_tokens = message.usage.input_tokens if hasattr(message, "usage") else 0
            output_tokens = message.usage.output_tokens if hasattr(message, "usage") else 0
            total_tokens = input_tokens + output_tokens

            # Calculate cost
            cost = self.calculate_cost(input_tokens, output_tokens, config.model)

            return ModelResponse(
                content=response_text,
                tokens_used=total_tokens,
                cost=cost,
                latency_ms=latency_ms,
                model=config.model,
                provider="anthropic",
            )
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate Anthropic pricing"""
        # Pricing as of 2024 (approximate, update as needed)
        pricing = {
            "claude-3-5-sonnet-20241022": {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
            "claude-3-5-sonnet-20240620": {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
            "claude-sonnet-4-20250514": {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
            "claude-3-opus-20240229": {"input": 15.00 / 1_000_000, "output": 75.00 / 1_000_000},
            "claude-3-haiku-20240307": {"input": 0.25 / 1_000_000, "output": 1.25 / 1_000_000},
            "claude-haiku-4-20250101": {"input": 0.25 / 1_000_000, "output": 1.25 / 1_000_000},
        }

        # Default pricing if model not found
        default = {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000}
        rates = pricing.get(model, default)

        return (input_tokens * rates["input"]) + (output_tokens * rates["output"])

