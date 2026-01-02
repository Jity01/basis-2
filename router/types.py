from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union, Literal
from enum import Enum


@dataclass
class RouterConfig:
    """Configuration for the Router instance"""

    api_keys: Dict[str, str] = field(
        default_factory=dict
    )  # {"anthropic": "...", "openai": "...", "gemini": "..."}
    default_chunk_size: int = 8000
    default_overlap: int = 500
    system_prompt: Optional[str] = None
    prompt: Optional[str] = (
        None  # Template string, e.g., "Evaluate the following text: {text}"
    )
    database_url: Optional[str] = (
        None  # PostgreSQL connection string, e.g., "postgresql://user:pass@host:port/db"
    )
    google_workspace: Optional[Dict[str, Any]] = (
        None  # Scaffold for Google Workspace connection
    )
    # Example: {"credentials_path": "...", "scopes": ["..."]}


@dataclass
class ModelConfig:
    """Configuration for model selection"""

    provider: str  # "anthropic" or "openai"
    model: str  # e.g., "claude-sonnet-4-20250514"
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: Optional[str] = None


class AggregationStrategy(Enum):
    """Aggregation strategies for combining chunk results"""

    CONCATENATE = "concatenate"
    MAJORITY_VOTE = "majority_vote"
    AVERAGE_SCORE = "average_score"


@dataclass
class ChunkingConfig:
    """Configuration for chunking behavior"""

    enabled: bool = True
    strategy: str = "fixed_size"  # "fixed_size", "semantic", "sliding_window"
    chunk_size: int = 8000  # in tokens
    overlap: int = 500  # tokens of overlap between chunks
    aggregation: AggregationStrategy = AggregationStrategy.CONCATENATE


@dataclass
class RouterResponse:
    """Response from router"""

    result: Any  # Could be str, dict, list depending on aggregation
    metadata: Dict[str, Any]
    chunks: Optional[List[Dict]] = None


# Data Source Types
@dataclass
class ContentData:
    """Direct content string data source"""

    content: str
    type: Literal["content"] = "content"
    task_type: Optional[str] = None  # e.g., "evaluate", "generate", "classify"
    metadata: Optional[Dict[str, Any]] = None  # Additional task-specific fields


@dataclass
class JsonPathData:
    """JSON file path data source"""

    path: str  # Path to JSON file
    type: Literal["json_path"] = "json_path"
    json_path: Optional[str] = (
        None  # JSONPath expression to extract specific field (e.g., "$.content")
    )
    task_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PostgresQueryData:
    """PostgreSQL query data source"""

    query: str  # SQL query to execute
    type: Literal["postgres_query"] = "postgres_query"
    column: Optional[str] = (
        None  # Column name to extract text from (defaults to first text column)
    )
    task_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    connection_url: Optional[str] = (
        None  # Override default database_url from RouterConfig
    )


@dataclass
class DataStoreData:
    """Data stored in a data store (S3, MongoDB, Postgres, etc.)"""

    store_type: str  # e.g., "s3", "mongodb", "postgres", "dynamodb"
    reference: str  # ID, key, path, or query to locate the data
    type: Literal["data_store"] = "data_store"
    # Examples:
    # - S3: reference = "bucket-name/path/to/file.json"
    # - MongoDB: reference = "collection_name" with query in store_config
    # - Postgres: reference = "table_name" with query in store_config
    store_config: Optional[Dict[str, Any]] = None  # Store-specific configuration
    # Examples:
    # - S3: {"region": "us-east-1", "access_key": "...", "secret_key": "..."}
    # - MongoDB: {"database": "mydb", "query": {"_id": "123"}, "field": "content"}
    # - Postgres: {"query": "SELECT content FROM table WHERE id = $1", "params": ["123"]}
    field: Optional[str] = (
        None  # Field/column name to extract text from (if data is structured)
    )
    task_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Union type for all data sources
DataSource = Union[ContentData, JsonPathData, PostgresQueryData, DataStoreData]


# Data Source Type Enum
class DataSourceType(Enum):
    """Supported data source types"""

    S3 = "s3"
    MONGODB = "mongodb"
    POSTGRES = "postgres"
    DYNAMODB = "dynamodb"
    JSON_FILE = "json_file"
    CONTENT = "content"  # Direct content (no connection needed)
    # Note: REDIS and GCS are not currently implemented but can be added in the future


# Store Configuration Types
@dataclass
class S3StoreConfig:
    """S3 store configuration"""

    region: str
    bucket: str
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    endpoint_url: Optional[str] = None  # For S3-compatible services


@dataclass
class MongoDBStoreConfig:
    """MongoDB store configuration"""

    connection_string: str
    database: str
    # Additional connection options can be added here


@dataclass
class PostgresStoreConfig:
    """PostgreSQL store configuration"""

    connection_url: str
    # Additional connection options can be added here


@dataclass
class DynamoDBStoreConfig:
    """DynamoDB store configuration"""

    region: str
    table_name: str
    access_key: Optional[str] = None
    secret_key: Optional[str] = None


@dataclass
class JsonFileStoreConfig:
    """JSON file store configuration"""

    base_path: Optional[str] = None  # Base directory for JSON files


# Union type for all store configs
StoreConfig = Union[
    S3StoreConfig,
    MongoDBStoreConfig,
    PostgresStoreConfig,
    DynamoDBStoreConfig,
    JsonFileStoreConfig,
]
