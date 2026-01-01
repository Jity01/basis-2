from typing import Optional, Dict, Any, Union, List
from .types import (
    RouterConfig,
    ModelConfig,
    ChunkingConfig,
    RouterResponse,
    DataSource,
    ContentData,
    JsonPathData,
    PostgresQueryData,
    DataStoreData,
    DataSourceType,
    StoreConfig,
)
from .data_sources import (
    S3Handler,
    MongoDBHandler,
    RedisHandler,
    PostgresHandler,
    JsonFileHandler,
    ContentHandler,
)
from .providers import (
    AnthropicProvider,
    OpenAIProvider,
    GeminiProvider,
    ModelResponse as ProviderResponse,
)
from .chunking import ChunkingEngine
from .aggregator import ResultAggregator


class Router:
    """
    Main routing engine that manages rules and dispatches requests.

    Workflow:
    1. Initialize router with config
    2. Connect data sources using connect_data_source()
    3. Add routing rules using add_rule()
    4. Route requests using route() with store labels and rule names
    """

    def __init__(self, config: Optional[Union[RouterConfig, Dict]] = None):
        """
        Initialize router with optional configuration

        Args:
            config: Optional RouterConfig instance or dict with default settings.
                If dict, will be converted to RouterConfig.
                {
                    "default_chunk_size": 8000,
                    "default_overlap": 500,
                    "api_keys": {
                        "anthropic": "...",
                        "openai": "..."
                    },
                    "system_prompt": "You are a helpful assistant that can answer questions and help with tasks.",
                    "prompt": "Evaluate the following text: {text}",
                    "database_url": "postgresql://user:pass@host:port/db",
                    "google_workspace": {"credentials_path": "...", "scopes": ["..."]}
                }
        """
        # Convert dict to RouterConfig if needed
        if isinstance(config, dict):
            self.config = RouterConfig(**config)
        else:
            self.config = config or RouterConfig()

        self._data_sources: Dict[str, Dict[str, Any]] = {}
        self._rules: Dict[str, Dict[str, Any]] = {}
        self._chunking_engine = ChunkingEngine()
        self._aggregator = ResultAggregator()

        # Initialize providers
        self._providers: Dict[str, Any] = {}
        if "anthropic" in self.config.api_keys:
            self._providers["anthropic"] = AnthropicProvider(
                self.config.api_keys["anthropic"]
            )
        if "openai" in self.config.api_keys:
            self._providers["openai"] = OpenAIProvider(self.config.api_keys["openai"])
        if "gemini" in self.config.api_keys:
            self._providers["gemini"] = GeminiProvider(self.config.api_keys["gemini"])

    def _get_data_source_handler(self, source_type: DataSourceType):
        """Get the appropriate data source handler"""
        handlers = {
            DataSourceType.S3: S3Handler(),
            DataSourceType.MONGODB: MongoDBHandler(),
            DataSourceType.REDIS: RedisHandler(),
            DataSourceType.POSTGRES: PostgresHandler(),
            DataSourceType.JSON_FILE: JsonFileHandler(),
            DataSourceType.CONTENT: ContentHandler(),
        }
        handler = handlers.get(source_type)
        if not handler:
            raise ValueError(
                f"No handler available for data source type: {source_type}"
            )
        return handler

    def _get_model_provider(self, provider_name: str):
        """Get the appropriate model provider"""
        provider = self._providers.get(provider_name)
        if not provider:
            raise ValueError(
                f"Provider '{provider_name}' not configured. Add API key to RouterConfig."
            )
        return provider

    def add_rule(
        self,
        name: str,
        model_config: ModelConfig,
        chunking_config: Optional[ChunkingConfig] = None,
    ) -> None:
        """
        Add a routing rule (Setup Step #3).

        Define which model and chunking strategy to use for processing requests.

        Args:
            name: Unique identifier for the rule (used in route() calls)
            model_config: Configuration for which model to use
            chunking_config: Optional chunking configuration
        """
        self._rules[name] = {
            "model_config": model_config,
            "chunking_config": chunking_config,
        }

    def connect_data_source(
        self,
        label: str,
        source_type: DataSourceType,
        store_config: StoreConfig,
    ) -> None:
        """
        Connect to a data source for later use (Setup Step #2).

        Register data sources that can be referenced by label in route() calls.

        Args:
            label: Unique identifier for this data source connection
            source_type: Type of data source (from DataSourceType enum)
            store_config: Store-specific configuration matching the source_type
                - S3StoreConfig for DataSourceType.S3
                - MongoDBStoreConfig for DataSourceType.MONGODB
                - RedisStoreConfig for DataSourceType.REDIS
                - PostgresStoreConfig for DataSourceType.POSTGRES
                - etc.
        """
        self._data_sources[label] = {
            "type": source_type,
            "config": store_config,
        }

    async def route(
        self,
        store_label: str,
        query: str,
        rule_name: str,
        metadata: Optional[Dict] = None,
    ) -> RouterResponse:
        """
        Route a request using connected data sources and rules.

        This is the main usage method after setup is complete.

        Args:
            store_label: Label of connected data source (from connect_data_source)
            query: Query/reference to get data from the store. Format depends on source type:
                - S3: File path in bucket (e.g., "logs/agent-123.json")
                - MongoDB: Query as JSON string (e.g., '{"agent_id": "123"}') or collection name
                - Redis: Key name (e.g., "agent:log:123")
                - Postgres: SQL query (e.g., "SELECT content FROM logs WHERE id = 123")
                - JSON_FILE: File path (e.g., "data/logs.json")
                - CONTENT: The content string itself
            rule_name: Name of routing rule to use (from add_rule)
            metadata: Optional metadata for logging/tracking

        Returns:
            RouterResponse with model output and routing metadata

        Raises:
            ValueError: If store_label or rule_name not found
        """
        if store_label not in self._data_sources:
            raise ValueError(
                f"Data source '{store_label}' not found. Use connect_data_source() first."
            )
        if rule_name not in self._rules:
            raise ValueError(f"Rule '{rule_name}' not found. Use add_rule() first.")

        # Get the connected data source and rule
        data_source_info = self._data_sources[store_label]
        rule_info = self._rules[rule_name]

        source_type = data_source_info["type"]
        store_config = data_source_info["config"]
        model_config = rule_info["model_config"]
        chunking_config = rule_info.get("chunking_config") or ChunkingConfig()

        # Step 1: Fetch data from data source
        handler = self._get_data_source_handler(source_type)
        if not handler.validate_config(store_config):
            raise ValueError(f"Invalid config for data source '{store_label}'")

        content = await handler.fetch(query, store_config)

        # Step 2: Chunk the content if needed
        chunks = self._chunking_engine.chunk_text(content, chunking_config)

        # Step 3: Process each chunk with the model
        chunk_responses: List[ProviderResponse] = []
        total_cost = 0.0
        total_tokens = 0
        total_latency = 0

        provider = self._get_model_provider(model_config.provider)

        # Use system prompt from config or router config
        system_prompt = (
            model_config.system_prompt
            or self.config.system_prompt
            or "You are a helpful assistant."
        )

        # Apply prompt template if provided
        if self.config.prompt:
            # Format prompt template with content
            formatted_prompts = [
                self.config.prompt.format(text=chunk) for chunk in chunks
            ]
        else:
            formatted_prompts = chunks

        for chunk_prompt in formatted_prompts:
            response = await provider.call(chunk_prompt, model_config, system_prompt)
            chunk_responses.append(response)
            total_cost += response.cost
            total_tokens += response.tokens_used
            total_latency += response.latency_ms

        # Step 4: Aggregate results
        aggregated_result = self._aggregator.aggregate(
            chunk_responses, chunking_config.aggregation
        )

        # Step 5: Build response
        return RouterResponse(
            result=aggregated_result,
            metadata={
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "total_latency_ms": total_latency,
                "chunks_processed": len(chunks),
                "model": model_config.model,
                "provider": model_config.provider,
                "store_label": store_label,
                "rule_name": rule_name,
            },
            chunks=[
                {
                    "content": r.content,
                    "tokens": r.tokens_used,
                    "cost": r.cost,
                    "latency_ms": r.latency_ms,
                }
                for r in chunk_responses
            ],
        )
