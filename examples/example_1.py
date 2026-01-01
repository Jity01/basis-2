import os
from metis_router import (
    Router,
    ModelConfig,
    ChunkingConfig,
    DataSourceType,
    S3StoreConfig,
    MongoDBStoreConfig,
    PostgresStoreConfig,
)

# Setup Step #1: Initialize router
router = Router(
    config={
        "api_keys": {
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
        }
    }
)

# Setup Step #2: Connect data sources and use labels
router.connect_data_source(
    label="my_s3_bucket",
    source_type=DataSourceType.S3,
    store_config=S3StoreConfig(
        region="us-east-1",
        bucket="my-bucket",
        access_key=os.getenv("AWS_ACCESS_KEY"),
        secret_key=os.getenv("AWS_SECRET_KEY"),
    ),
)

router.connect_data_source(
    label="my_mongodb",
    source_type=DataSourceType.MONGODB,
    store_config=MongoDBStoreConfig(
        connection_string="mongodb://localhost:27017",
        database="mydb",
    ),
)

router.connect_data_source(
    label="my_postgres",
    source_type=DataSourceType.POSTGRES,
    store_config=PostgresStoreConfig(
        connection_url=os.getenv("POSTGRES_URL"),
    ),
)

# Setup Step #3: Add rules
router.add_rule(
    name="evaluate_agent",
    model_config=ModelConfig(
        provider="anthropic", model="claude-sonnet-4-20250514", temperature=0.2
    ),
    chunking_config=ChunkingConfig(
        enabled=True, chunk_size=8000, aggregation="concatenate"
    ),
)

router.add_rule(
    name="classify_cheap",
    model_config=ModelConfig(
        provider="anthropic", model="claude-haiku-4-20250101", temperature=0
    ),
    chunking_config=ChunkingConfig(enabled=True, aggregation="majority_vote"),
)

# Usage: Route using simple labels 🚀
response = await router.route(
    store_label="my_s3_bucket",
    query="logs/agent-interaction-123.json",
    rule_name="evaluate_agent",
)

response = await router.route(
    store_label="my_mongodb",
    query='{"agent_id": "123"}',  # MongoDB query as JSON string
    rule_name="classify_cheap",
)

response = await router.route(
    store_label="my_postgres",
    query="SELECT content FROM agent_logs WHERE id = 123",
    rule_name="evaluate_agent",
)

# Some basic metrics you can use
print(f"Result: {response.result}")
print(f"Cost: ${response.metadata['total_cost']}")
print(f"Chunks processed: {response.metadata['chunks_processed']}")
