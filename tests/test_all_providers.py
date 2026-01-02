"""
Test all three LLM providers (Anthropic, OpenAI, Gemini) with CONTENT data source

Run from the router directory:
    python -m tests.test_all_providers
"""

import os
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path so router can be imported as a package
router_dir = Path(__file__).parent.parent
sys.path.insert(0, str(router_dir))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    env_path = router_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded environment variables from {env_path}")
    else:
        print(f"⚠️  No .env file found at {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Or manually export environment variables before running tests.")

from router import (
    Router,
    ModelConfig,
    ChunkingConfig,
    DataSourceType,
    JsonFileStoreConfig,
)

# Small test content
TEST_CONTENT = (
    "Artificial intelligence is transforming how we interact with technology. "
    "Machine learning algorithms can now recognize patterns in data that humans might miss. "
    "Deep learning, a subset of machine learning, uses neural networks to process information. "
    "These technologies are being applied across various industries including healthcare, finance, and transportation."
)


async def test_provider(
    router: Router, provider: str, model: str, rule_name: str
) -> Optional[Dict[str, Any]]:
    """Test a single provider with CONTENT data source"""
    print(f"\n{'=' * 60}")
    print(f"Testing {provider.upper()} Provider")
    print(f"{'=' * 60}")
    print(f"Model: {model}")

    try:
        response = await router.route(
            store_label="test_content",
            query=TEST_CONTENT,
            rule_name=rule_name,
        )

        result_length = len(str(response.result))
        cost = response.metadata.get("total_cost", 0)
        tokens = response.metadata.get("total_tokens", 0)
        latency = response.metadata.get("total_latency_ms", 0)

        print(f"✓ Success!")
        print(f"  Result length: {result_length:,} characters")
        print(f"  Tokens used: {tokens:,}")
        print(f"  Cost: ${cost:.6f}")
        print(f"  Latency: {latency:.0f}ms")
        print(f"\n  Result preview:")
        result_preview = str(response.result)[:200]
        print(f"  {result_preview}...")

        return {
            "provider": provider,
            "model": model,
            "success": True,
            "result_length": result_length,
            "tokens": tokens,
            "cost": cost,
            "latency_ms": latency,
            "result": str(response.result),
        }
    except Exception as e:
        print(f"❌ Failed: {e}")
        return {
            "provider": provider,
            "model": model,
            "success": False,
            "error": str(e),
        }


async def main():
    """Test all three providers with CONTENT data source"""
    print("=" * 60)
    print("Testing All LLM Providers with CONTENT Data Source")
    print("=" * 60)

    # Get API keys
    api_keys = {
        # "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        # "openai": os.getenv("OPENAI_API_KEY"),
        "gemini": os.getenv("GEMINI_API_KEY"),
    }

    # Check which providers are available
    available_providers = {name: key for name, key in api_keys.items() if key}

    if not available_providers:
        print("\n❌ No API keys found!")
        print("   Set at least one of:")
        print("   - ANTHROPIC_API_KEY")
        print("   - OPENAI_API_KEY")
        print("   - GEMINI_API_KEY")
        return

    print(
        f"\n✓ Found {len(available_providers)} provider(s): {', '.join(available_providers.keys())}"
    )

    # Initialize router with available API keys
    router = Router(
        config={
            "api_keys": available_providers,
            "system_prompt": "You are a helpful assistant that summarizes text concisely.",
            "prompt": "Summarize the following text in 2-3 sentences: {text}",
        }
    )

    # Connect CONTENT data source
    await router.connect_data_source(
        label="test_content",
        source_type=DataSourceType.CONTENT,
        store_config=JsonFileStoreConfig(),  # Dummy config, not used
    )

    # Define provider configurations
    provider_configs = {
        "anthropic": {
            "model": "claude-3-haiku-20240307",
            "rule_name": "test_anthropic",
        },
        "openai": {
            "model": "gpt-4o-mini",
            "rule_name": "test_openai",
        },
        "gemini": {
            "model": "gemini-3-flash-preview",
            "rule_name": "test_gemini",
        },
    }

    # Add rules for available providers
    for provider, config in provider_configs.items():
        if provider in available_providers:
            router.add_rule(
                name=config["rule_name"],
                model_config=ModelConfig(
                    provider=provider,
                    model=config["model"],
                    temperature=0.3,
                    max_tokens=500,
                ),
                chunking_config=ChunkingConfig(
                    enabled=False,  # No chunking for small test data
                ),
            )

    # Test each available provider
    results = []
    for provider, config in provider_configs.items():
        if provider in available_providers:
            result = await test_provider(
                router, provider, config["model"], config["rule_name"]
            )
            if result:
                results.append(result)
        else:
            print(f"\n{'=' * 60}")
            print(f"Skipping {provider.upper()} - API key not set")
            print(f"{'=' * 60}")

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]

    if successful:
        print(f"\n✅ Successful: {len(successful)}/{len(results)}")
        print("\nProvider Comparison:")
        print(
            f"{'Provider':<12} {'Model':<25} {'Tokens':<10} {'Cost':<12} {'Latency':<10}"
        )
        print("-" * 70)
        for result in successful:
            print(
                f"{result['provider']:<12} "
                f"{result['model']:<25} "
                f"{result.get('tokens', 0):<10,} "
                f"${result.get('cost', 0):<11.6f} "
                f"{result.get('latency_ms', 0):<10.0f}ms"
            )

    if failed:
        print(f"\n❌ Failed: {len(failed)}/{len(results)}")
        for result in failed:
            print(f"   - {result['provider']}: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
