import time
from typing import Optional
from .base import ModelProvider, ModelResponse
from ..types import ModelConfig


class GeminiProvider(ModelProvider):
    """Provider for Google Gemini models"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def call(
        self,
        content: str,
        config: ModelConfig,
        system_prompt: Optional[str] = None,
    ) -> ModelResponse:
        """Call Gemini API"""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai is required for Gemini support. Install with: pip install google-generativeai"
            )

        genai.configure(api_key=self.api_key)

        start_time = time.time()

        try:
            model = genai.GenerativeModel(
                model_name=config.model,
                generation_config={
                    "temperature": config.temperature,
                    "max_output_tokens": config.max_tokens,
                },
            )

            # Combine system prompt and content
            prompt = content
            if system_prompt or config.system_prompt:
                sys_prompt = system_prompt or config.system_prompt
                prompt = f"{sys_prompt}\n\n{prompt}"

            response = await model.generate_content_async(prompt)

            latency_ms = int((time.time() - start_time) * 1000)

            # Extract response content
            response_text = response.text if hasattr(response, "text") else ""

            # Estimate token usage (Gemini API doesn't always provide this)
            # Rough estimate: ~4 characters per token
            input_tokens = len(prompt) // 4
            output_tokens = len(response_text) // 4
            total_tokens = input_tokens + output_tokens

            # Calculate cost
            cost = self.calculate_cost(input_tokens, output_tokens, config.model)

            return ModelResponse(
                content=response_text,
                tokens_used=total_tokens,
                cost=cost,
                latency_ms=latency_ms,
                model=config.model,
                provider="gemini",
            )
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate Gemini pricing"""
        # Pricing as of 2024 (approximate, update as needed)
        pricing = {
            "gemini-1.5-pro": {"input": 1.25 / 1_000_000, "output": 5.00 / 1_000_000},
            "gemini-1.5-flash": {"input": 0.075 / 1_000_000, "output": 0.30 / 1_000_000},
        }

        # Default pricing if model not found
        default = {"input": 1.25 / 1_000_000, "output": 5.00 / 1_000_000}
        rates = pricing.get(model, default)

        return (input_tokens * rates["input"]) + (output_tokens * rates["output"])

