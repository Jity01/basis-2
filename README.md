# Basis Router

A flexible routing system for managing LLM requests across multiple providers (Anthropic, OpenAI, Gemini) with intelligent chunking and result aggregation.

## Features

- Route requests to different LLM providers based on configurable rules
- Automatic text chunking for large inputs
- Multiple aggregation strategies for chunk results
- Cost tracking and metadata collection

## Installation

### Basic Installation

```bash
pip install basis-router
```

## Quick Start

The router follows a simple setup-then-use pattern:

```python
from router import (
    Router,
    ModelConfig,
    ChunkingConfig,
    DataSourceType,
    S3StoreConfig,
    MongoDBStoreConfig,
    PostgresStoreConfig,
)
import os

# Setup Step #1: Initialize router
router = Router(
    config={
        "api_keys": {
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
        }
    }
)

# Setup Step #2: Connect data sources
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
        provider="anthropic",
        model="claude-sonnet-4-20250514",
        temperature=0.2
    ),
    chunking_config=ChunkingConfig(
        enabled=True,
        chunk_size=8000,
        aggregation="concatenate"
    )
)

# Usage: Route using simple labels
response = await router.route(
    store_label="my_s3_bucket",
    query="logs/agent-interaction-123.json",
    rule_name="evaluate_agent",
)

print(f"Result: {response.result}")
print(f"Cost: ${response.metadata['total_cost']}")
print(f"Chunks processed: {response.metadata['chunks_processed']}")
```

## Workflow

The router uses a three-step setup process:

1. **Initialize Router**: Configure API keys and default settings
2. **Connect Data Sources**: Register your data stores (S3, MongoDB, Postgres, etc.)
3. **Add Rules**: Define routing rules that specify which model to use for different tasks

Once setup is complete, routing is simple: just specify the data source label, query, and rule name.

## Configuration

### Router Config

```python
config = {
    "default_chunk_size": 8000,
    "default_overlap": 500,
    "api_keys": {
        "anthropic": "your-key",
        "openai": "your-key"
    },
    "system_prompt": "You are a helpful assistant.",
    "prompt": "Evaluate the following text: {text}"
}
```

### ModelConfig

```python
ModelConfig(
    provider="anthropic",  # or "openai", "gemini"
    model="claude-sonnet-4-20250514",
    temperature=0.7,
    max_tokens=4096,
    system_prompt="Optional system prompt"
)
```

### ChunkingConfig

```python
ChunkingConfig(
    enabled=True,
    strategy="fixed_size",  # "fixed_size", "semantic", "sliding_window"
    chunk_size=8000,
    overlap=500,
    aggregation="concatenate"  # "concatenate", "majority_vote", "average_score"
)
```

### Data Source Types

Connect data sources using `connect_data_source()`. Supported types:

- **S3**: Amazon S3 storage
- **MONGODB**: MongoDB database
- **REDIS**: Redis key-value store
- **POSTGRES**: PostgreSQL database
- **DYNAMODB**: Amazon DynamoDB
- **GCS**: Google Cloud Storage
- **JSON_FILE**: Local JSON files
- **CONTENT**: Direct content strings

#### Store Configurations

Each data source type has a corresponding store config class:

```python
from router import (
    DataSourceType,
    S3StoreConfig,
    MongoDBStoreConfig,
    RedisStoreConfig,
    PostgresStoreConfig,
    DynamoDBStoreConfig,
    GCSStoreConfig,
    JsonFileStoreConfig,
)

# S3
router.connect_data_source(
    label="my_s3",
    source_type=DataSourceType.S3,
    store_config=S3StoreConfig(
        region="us-east-1",
        bucket="my-bucket",
        access_key="...",
        secret_key="...",
    ),
)

# MongoDB
router.connect_data_source(
    label="my_mongodb",
    source_type=DataSourceType.MONGODB,
    store_config=MongoDBStoreConfig(
        connection_string="mongodb://localhost:27017",
        database="mydb",
    ),
)

# Redis
router.connect_data_source(
    label="my_redis",
    source_type=DataSourceType.REDIS,
    store_config=RedisStoreConfig(
        host="localhost",
        port=6379,
        db=0,
    ),
)

# Postgres
router.connect_data_source(
    label="my_postgres",
    source_type=DataSourceType.POSTGRES,
    store_config=PostgresStoreConfig(
        connection_url="postgresql://user:pass@host:port/db",
    ),
)
```

#### Query Format

The `query` parameter in `route()` varies by data source type:

- **S3**: File path in bucket (e.g., `"logs/agent-123.json"`)
- **MongoDB**: Query as JSON string (e.g., `'{"agent_id": "123"}'`) or collection name
- **Redis**: Key name (e.g., `"agent:log:123"`)
- **Postgres**: SQL query (e.g., `"SELECT content FROM logs WHERE id = 123"`)
- **JSON_FILE**: File path (e.g., `"data/logs.json"`)
- **CONTENT**: The content string itself

## Examples

### Complete Example

```python
from router import (
    Router,
    ModelConfig,
    ChunkingConfig,
    DataSourceType,
    S3StoreConfig,
    MongoDBStoreConfig,
    PostgresStoreConfig,
)
import os

# Setup Step #1: Initialize router
router = Router(
    config={
        "api_keys": {
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
        }
    }
)

# Setup Step #2: Connect data sources
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
        provider="anthropic",
        model="claude-sonnet-4-20250514",
        temperature=0.2
    ),
    chunking_config=ChunkingConfig(
        enabled=True,
        chunk_size=8000,
        aggregation="concatenate"
    )
)

router.add_rule(
    name="classify_cheap",
    model_config=ModelConfig(
        provider="anthropic",
        model="claude-haiku-4-20250101",
        temperature=0
    ),
    chunking_config=ChunkingConfig(
        enabled=True,
        aggregation="majority_vote"
    )
)

# Usage: Route using simple labels
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

print(f"Result: {response.result}")
print(f"Cost: ${response.metadata['total_cost']}")
print(f"Chunks processed: {response.metadata['chunks_processed']}")
```

## Response Format

The router returns a `RouterResponse` object:

```python
@dataclass
class RouterResponse:
    result: Any  # The aggregated result
    metadata: Dict[str, Any]  # Cost, tokens, latency, etc.
    chunks: Optional[List[Dict]]  # Individual chunk results
```

## Aggregation Strategies

- **concatenate**: Join all chunk results together
- **majority_vote**: Return the most common result across chunks
- **average_score**: Average numerical scores from chunks


