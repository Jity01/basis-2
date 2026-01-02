import time
from typing import Optional
import google.generativeai as genai
from .base import ModelProvider, ModelResponse
from ..types import ModelConfig


class GeminiProvider(ModelProvider):
    """Provider for Google Gemini models"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)

    async def call(
        self,
        content: str,
        config: ModelConfig,
        system_prompt: Optional[str] = None,
    ) -> ModelResponse:
        """Call Gemini API"""

        start_time = time.time()

        try:
            # Configure safety settings to allow more content through
            # BLOCK_ONLY_HIGH blocks only high-probability unsafe content
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH",
                },
            ]

            model = genai.GenerativeModel(
                model_name=config.model,
                generation_config={
                    "temperature": config.temperature,
                    "max_output_tokens": config.max_tokens,
                },
                safety_settings=safety_settings,
            )

            # Combine system prompt and content
            prompt = content
            if system_prompt or config.system_prompt:
                sys_prompt = system_prompt or config.system_prompt
                prompt = f"{sys_prompt}\n\n{prompt}"

            response = await model.generate_content_async(prompt)

            latency_ms = int((time.time() - start_time) * 1000)

            # Check if response has valid content
            if not response.candidates or not response.candidates[0].content:
                finish_reason = (
                    response.candidates[0].finish_reason
                    if response.candidates
                    else None
                )
                if finish_reason == 2:  # SAFETY - content filtered
                    raise RuntimeError(
                        "Gemini API: Content was filtered/blocked for safety reasons. "
                        "Try adjusting your prompt or safety settings."
                    )
                else:
                    raise RuntimeError(
                        f"Gemini API: No content returned (finish_reason: {finish_reason})"
                    )

            # Extract response content safely
            try:
                response_text = response.text
            except ValueError as e:
                # Handle case where .text accessor fails
                raise RuntimeError(f"Gemini API: {e}")

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

    def calculate_cost(
        self, input_tokens: int, output_tokens: int, model: str
    ) -> float:
        """Calculate Gemini pricing"""
        # Pricing as of 2024 (approximate, update as needed)
        pricing = {
            "gemini-1.5-pro": {"input": 1.25 / 1_000_000, "output": 5.00 / 1_000_000},
            "gemini-1.5-flash": {
                "input": 0.075 / 1_000_000,
                "output": 0.30 / 1_000_000,
            },
        }

        # Default pricing if model not found
        default = {"input": 1.25 / 1_000_000, "output": 5.00 / 1_000_000}
        rates = pricing.get(model, default)

        return (input_tokens * rates["input"]) + (output_tokens * rates["output"])
