"""
Test script for processing large agent rollout data with OpenAI

Run from the router directory:
    python -m tests.test_agent_rollout
"""

import os
import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path so router can be imported as a package
router_dir = Path(__file__).parent.parent
sys.path.insert(0, str(router_dir))

from router import (
    Router,
    ModelConfig,
    ChunkingConfig,
    AggregationStrategy,
    DataSourceType,
    JsonFileStoreConfig,
)


async def main():
    """Test processing agent rollout data"""
    test_data_file = router_dir / "tests" / "test_data" / "agent_rollout_test_data.json"

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY not set!")
        print(
            f"   Checked environment variable: {os.getenv('OPENAI_API_KEY', 'NOT FOUND')}"
        )
        print("   Make sure to export it: export OPENAI_API_KEY='your-key'")
        return

    print("=" * 60)
    print("Agent Rollout Data Processing Test")
    print("=" * 60)

    # Initialize router
    print("\n[1/3] Initializing router...")
    router = Router(
        config={
            "api_keys": {"openai": openai_key},
            "system_prompt": "You are an expert at analyzing agent interactions. Provide detailed analysis.",
            "prompt": "Analyze this agent interaction data: {text}",
        }
    )

    # Connect data source
    print("[2/3] Connecting data source...")
    await router.connect_data_source(
        label="agent_data",
        source_type=DataSourceType.JSON_FILE,
        store_config=JsonFileStoreConfig(base_path=str(test_data_file.parent)),
    )

    # Add rule
    print("[3/3] Adding routing rule...")
    router.add_rule(
        name="analyze",
        model_config=ModelConfig(
            provider="openai",
            model="gpt-4o",
            temperature=0.3,
            max_tokens=4096,
        ),
        chunking_config=ChunkingConfig(
            enabled=True,
            chunk_size=8000,
            overlap=500,
            aggregation=AggregationStrategy.CONCATENATE,
        ),
    )

    # Load data info
    if not test_data_file.exists():
        print(f"❌ Test data file not found: {test_data_file}")
        print(f"   Run: python {router_dir / 'tests' / 'generate_test_data.py'}")
        return

    with open(test_data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    file_size_mb = test_data_file.stat().st_size / (1024 * 1024)
    print(
        f"\n✓ Data: {data['total_interactions']:,} interactions, {file_size_mb:.2f} MB"
    )

    # Process
    print("\n" + "=" * 60)
    print("Processing with OpenAI...")
    print("=" * 60)

    import time

    start = time.time()
    response = await router.route(
        store_label="agent_data",
        query=test_data_file.name,
        rule_name="analyze",
    )
    elapsed = time.time() - start

    # Results
    print("\n" + "=" * 60)
    print("Results")
    print("=" * 60)
    print(f"Time: {elapsed:.2f}s")
    print(f"Cost: ${response.metadata['total_cost']:.4f}")
    print(f"Tokens: {response.metadata['total_tokens']:,}")
    print(f"Chunks: {response.metadata['chunks_processed']}")

    print("\n" + "-" * 60)
    print("Analysis (first 1000 chars):")
    print("-" * 60)
    print(str(response.result)[:1000])
    if len(str(response.result)) > 1000:
        print(f"\n... (truncated, {len(str(response.result)):,} total chars)")

    # Save result
    output_file = f"tests/test_results/agent_rollout_analysis_result.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Processing Time: {elapsed:.2f}s\n")
        f.write(f"Cost: ${response.metadata['total_cost']:.4f}\n")
        f.write(f"Tokens: {response.metadata['total_tokens']:,}\n")
        f.write(f"Chunks: {response.metadata['chunks_processed']}\n\n")
        f.write("=" * 60 + "\n\n")
        f.write(str(response.result))

    print(f"\n✓ Full result saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
