"""
Comprehensive test for all data source types with small test data

Run from the router directory:
    python -m tests.test_all_data_sources
"""

import os
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path so router can be imported as a package
router_dir = Path(__file__).parent.parent
sys.path.insert(0, str(router_dir))

from router import (
    Router,
    ModelConfig,
    ChunkingConfig,
    AggregationStrategy,
    DataSourceType,
    S3StoreConfig,
    MongoDBStoreConfig,
    RedisStoreConfig,
    PostgresStoreConfig,
    DynamoDBStoreConfig,
    GCSStoreConfig,
    JsonFileStoreConfig,
)


# Small test data for all sources
TEST_DATA = {
    "content": "This is a small test document about AI and machine learning. It contains basic information about neural networks and deep learning.",
    "json": {
        "title": "Test Document",
        "content": "This is test content for JSON file handler. It includes some sample data about testing.",
        "metadata": {
            "author": "Test Author",
            "date": "2024-01-01",
            "tags": ["test", "json", "sample"],
        },
    },
}


async def test_content_source(router: Router) -> Dict[str, Any]:
    """Test CONTENT data source type"""
    print("\n" + "=" * 60)
    print("Testing CONTENT Data Source")
    print("=" * 60)

    # CONTENT still needs to be connected, but config doesn't matter
    await router.connect_data_source(
        label="test_content",
        source_type=DataSourceType.CONTENT,
        store_config=JsonFileStoreConfig(),  # Dummy config, not used
    )

    # Use content directly as query
    response = await router.route(
        store_label="test_content",
        query=TEST_DATA["content"],
        rule_name="test_rule",
    )

    return {
        "type": "CONTENT",
        "success": True,
        "result_length": len(str(response.result)),
        "cost": response.metadata.get("total_cost", 0),
        "tokens": response.metadata.get("total_tokens", 0),
    }


async def test_json_file_source(router: Router) -> Dict[str, Any]:
    """Test JSON_FILE data source type"""
    print("\n" + "=" * 60)
    print("Testing JSON_FILE Data Source")
    print("=" * 60)

    # Create test JSON file
    test_data_dir = router_dir / "tests" / "test_data"
    test_data_dir.mkdir(parents=True, exist_ok=True)
    test_json_file = test_data_dir / "test_small.json"

    with open(test_json_file, "w", encoding="utf-8") as f:
        json.dump(TEST_DATA["json"], f, indent=2)

    print(f"Created test JSON file: {test_json_file}")

    # Connect JSON file source
    await router.connect_data_source(
        label="test_json",
        source_type=DataSourceType.JSON_FILE,
        store_config=JsonFileStoreConfig(base_path=str(test_data_dir)),
    )

    # Route
    response = await router.route(
        store_label="test_json",
        query=test_json_file.name,
        rule_name="test_rule",
    )

    return {
        "type": "JSON_FILE",
        "success": True,
        "result_length": len(str(response.result)),
        "cost": response.metadata.get("total_cost", 0),
        "tokens": response.metadata.get("total_tokens", 0),
    }


async def test_s3_source(router: Router) -> Dict[str, Any]:
    """Test S3 data source type"""
    print("\n" + "=" * 60)
    print("Testing S3 Data Source")
    print("=" * 60)

    # Check for S3 credentials
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    s3_bucket = os.getenv("S3_TEST_BUCKET")
    s3_region = os.getenv("AWS_REGION", "us-east-1")

    if not all([aws_access_key, aws_secret_key, s3_bucket]):
        print("⚠️  Skipping S3 test - missing credentials")
        print("   Set: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_TEST_BUCKET")
        return {"type": "S3", "success": False, "reason": "Missing credentials"}

    # Connect S3 source
    await router.connect_data_source(
        label="test_s3",
        source_type=DataSourceType.S3,
        store_config=S3StoreConfig(
            region=s3_region,
            bucket=s3_bucket,
            access_key=aws_access_key,
            secret_key=aws_secret_key,
        ),
    )

    # Create a test file path (you'd need to upload this first)
    test_file_path = "test/test_small.json"
    print(f"Testing with S3 path: {test_file_path}")

    try:
        response = await router.route(
            store_label="test_s3",
            query=test_file_path,
            rule_name="test_rule",
        )
        return {
            "type": "S3",
            "success": True,
            "result_length": len(str(response.result)),
            "cost": response.metadata.get("total_cost", 0),
            "tokens": response.metadata.get("total_tokens", 0),
        }
    except Exception as e:
        print(f"⚠️  S3 test failed: {e}")
        return {"type": "S3", "success": False, "reason": str(e)}


async def test_mongodb_source(router: Router) -> Dict[str, Any]:
    """Test MONGODB data source type"""
    print("\n" + "=" * 60)
    print("Testing MONGODB Data Source")
    print("=" * 60)

    mongodb_url = os.getenv("MONGODB_CONNECTION_STRING")
    mongodb_db = os.getenv("MONGODB_DATABASE", "test_db")

    if not mongodb_url:
        print("⚠️  Skipping MongoDB test - missing connection string")
        print("   Set: MONGODB_CONNECTION_STRING")
        return {"type": "MONGODB", "success": False, "reason": "Missing credentials"}

    # Connect MongoDB source
    await router.connect_data_source(
        label="test_mongodb",
        source_type=DataSourceType.MONGODB,
        store_config=MongoDBStoreConfig(
            connection_string=mongodb_url,
            database=mongodb_db,
        ),
    )

    # Test query
    test_query = "test"  # Simple query
    print(f"Testing with MongoDB query: {test_query}")

    try:
        response = await router.route(
            store_label="test_mongodb",
            query=test_query,
            rule_name="test_rule",
        )
        return {
            "type": "MONGODB",
            "success": True,
            "result_length": len(str(response.result)),
            "cost": response.metadata.get("total_cost", 0),
            "tokens": response.metadata.get("total_tokens", 0),
        }
    except Exception as e:
        print(f"⚠️  MongoDB test failed: {e}")
        return {"type": "MONGODB", "success": False, "reason": str(e)}


async def test_redis_source(router: Router) -> Dict[str, Any]:
    """Test REDIS data source type"""
    print("\n" + "=" * 60)
    print("Testing REDIS Data Source")
    print("=" * 60)

    # Check for full connection URL first (useful for Upstash, Redis Cloud, etc.)
    redis_url = os.getenv("REDIS_URL")

    if redis_url:
        # Use full connection URL (Upstash provides this format)
        print("Using REDIS_URL connection string")
        store_config = RedisStoreConfig(connection_url=redis_url)
    else:
        # Use individual connection parameters
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_password = os.getenv("REDIS_PASSWORD")
        redis_ssl = os.getenv("REDIS_SSL", "false").lower() == "true"

        store_config = RedisStoreConfig(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            ssl=redis_ssl,
        )
        print(f"Connecting to Redis at {redis_host}:{redis_port} (SSL: {redis_ssl})")

    # Connect Redis source
    await router.connect_data_source(
        label="test_redis",
        source_type=DataSourceType.REDIS,
        store_config=store_config,
    )

    # Test key (you'd need to set this in Redis first)
    test_key = "test:small:data"
    print(f"Testing with Redis key: {test_key}")

    try:
        response = await router.route(
            store_label="test_redis",
            query=test_key,
            rule_name="test_rule",
        )
        return {
            "type": "REDIS",
            "success": True,
            "result_length": len(str(response.result)),
            "cost": response.metadata.get("total_cost", 0),
            "tokens": response.metadata.get("total_tokens", 0),
        }
    except Exception as e:
        print(f"⚠️  Redis test failed: {e}")
        return {"type": "REDIS", "success": False, "reason": str(e)}


async def test_postgres_source(router: Router) -> Dict[str, Any]:
    """Test POSTGRES data source type"""
    print("\n" + "=" * 60)
    print("Testing POSTGRES Data Source")
    print("=" * 60)

    postgres_url = os.getenv("POSTGRES_CONNECTION_URL")

    if not postgres_url:
        print("⚠️  Skipping Postgres test - missing connection URL")
        print("   Set: POSTGRES_CONNECTION_URL")
        return {"type": "POSTGRES", "success": False, "reason": "Missing credentials"}

    # Connect Postgres source
    await router.connect_data_source(
        label="test_postgres",
        source_type=DataSourceType.POSTGRES,
        store_config=PostgresStoreConfig(
            connection_url=postgres_url,
        ),
    )

    # Test query
    test_query = "SELECT text_content FROM test"
    print(f"Testing with Postgres query: {test_query}")

    try:
        response = await router.route(
            store_label="test_postgres",
            query=test_query,
            rule_name="test_rule",
        )
        return {
            "type": "POSTGRES",
            "success": True,
            "result_length": len(str(response.result)),
            "cost": response.metadata.get("total_cost", 0),
            "tokens": response.metadata.get("total_tokens", 0),
        }
    except Exception as e:
        print(f"⚠️  Postgres test failed: {e}")
        return {"type": "POSTGRES", "success": False, "reason": str(e)}


async def test_dynamodb_source(router: Router) -> Dict[str, Any]:
    """Test DYNAMODB data source type"""
    print("\n" + "=" * 60)
    print("Testing DYNAMODB Data Source")
    print("=" * 60)

    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    dynamodb_table = os.getenv("DYNAMODB_TEST_TABLE")
    dynamodb_region = os.getenv("AWS_REGION", "us-east-1")

    if not all([aws_access_key, aws_secret_key, dynamodb_table]):
        print("⚠️  Skipping DynamoDB test - missing credentials")
        print("   Set: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DYNAMODB_TEST_TABLE")
        return {"type": "DYNAMODB", "success": False, "reason": "Missing credentials"}

    # Connect DynamoDB source
    await router.connect_data_source(
        label="test_dynamodb",
        source_type=DataSourceType.DYNAMODB,
        store_config=DynamoDBStoreConfig(
            region=dynamodb_region,
            table_name=dynamodb_table,
            access_key=aws_access_key,
            secret_key=aws_secret_key,
        ),
    )

    # Test query (DynamoDB query format)
    test_query = "{}"
    print(f"Testing with DynamoDB query: {test_query}")

    try:
        response = await router.route(
            store_label="test_dynamodb",
            query=test_query,
            rule_name="test_rule",
        )
        return {
            "type": "DYNAMODB",
            "success": True,
            "result_length": len(str(response.result)),
            "cost": response.metadata.get("total_cost", 0),
            "tokens": response.metadata.get("total_tokens", 0),
        }
    except Exception as e:
        print(f"⚠️  DynamoDB test failed: {e}")
        return {"type": "DYNAMODB", "success": False, "reason": str(e)}


async def test_gcs_source(router: Router) -> Dict[str, Any]:
    """Test GCS data source type"""
    print("\n" + "=" * 60)
    print("Testing GCS Data Source")
    print("=" * 60)

    gcs_project = os.getenv("GCS_PROJECT_ID")
    gcs_bucket = os.getenv("GCS_TEST_BUCKET")
    gcs_credentials = os.getenv("GCS_CREDENTIALS_PATH")

    if not all([gcs_project, gcs_bucket]):
        print("⚠️  Skipping GCS test - missing credentials")
        print("   Set: GCS_PROJECT_ID, GCS_TEST_BUCKET")
        return {"type": "GCS", "success": False, "reason": "Missing credentials"}

    # Connect GCS source
    await router.connect_data_source(
        label="test_gcs",
        source_type=DataSourceType.GCS,
        store_config=GCSStoreConfig(
            project_id=gcs_project,
            bucket=gcs_bucket,
            credentials_path=gcs_credentials,
        ),
    )

    # Test file path
    test_file_path = "test/test_small.json"
    print(f"Testing with GCS path: {test_file_path}")

    try:
        response = await router.route(
            store_label="test_gcs",
            query=test_file_path,
            rule_name="test_rule",
        )
        return {
            "type": "GCS",
            "success": True,
            "result_length": len(str(response.result)),
            "cost": response.metadata.get("total_cost", 0),
            "tokens": response.metadata.get("total_tokens", 0),
        }
    except Exception as e:
        print(f"⚠️  GCS test failed: {e}")
        return {"type": "GCS", "success": False, "reason": str(e)}


async def main():
    """Run tests for all data source types"""
    print("=" * 60)
    print("Testing All Data Source Types")
    print("=" * 60)

    # Get API key (required for all tests)
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ No API key found!")
        print("   Set either OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return

    # Determine provider
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "anthropic"
    model = "gpt-4o-mini" if provider == "openai" else "claude-3-haiku-20240307"

    print(f"\nUsing provider: {provider} with model: {model}")

    # Initialize router
    router = Router(
        config={
            "api_keys": {provider: api_key},
            "system_prompt": "You are a helpful assistant that summarizes text.",
            "prompt": "Summarize the following content in 2-3 sentences: {text}",
        }
    )

    # Add a simple test rule
    router.add_rule(
        name="test_rule",
        model_config=ModelConfig(
            provider=provider,
            model=model,
            temperature=0.3,
            max_tokens=500,
        ),
        chunking_config=ChunkingConfig(
            enabled=False,  # Disable chunking for small test data
        ),
    )

    # Run all tests
    results = []

    # Test CONTENT (always works, no setup needed)
    results.append(await test_content_source(router))

    # Test JSON_FILE (creates local file)
    results.append(await test_json_file_source(router))

    # Test cloud/external sources (may skip if credentials missing)
    results.append(await test_s3_source(router))
    results.append(await test_mongodb_source(router))
    results.append(await test_redis_source(router))
    results.append(await test_postgres_source(router))
    results.append(await test_dynamodb_source(router))
    results.append(await test_gcs_source(router))

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]

    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    for result in successful:
        print(
            f"   - {result['type']}: {result.get('tokens', 0)} tokens, ${result.get('cost', 0):.4f}"
        )

    if failed:
        print(f"\n⚠️  Skipped/Failed: {len(failed)}/{len(results)}")
        for result in failed:
            reason = result.get("reason", "Unknown")
            print(f"   - {result['type']}: {reason}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
