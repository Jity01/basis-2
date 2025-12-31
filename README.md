# Router

A flexible routing system for managing LLM requests across multiple providers (Anthropic, OpenAI, Gemini) with intelligent chunking and result aggregation.

## Features

- Route requests to different LLM providers based on configurable rules
- Automatic text chunking for large inputs
- Multiple aggregation strategies for chunk results
- Cost tracking and metadata collection

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from router import Router, ModelConfig, ChunkingConfig
import os

# Initialize router with API keys
router = Router(config={
    "api_keys": {
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY")
    }
})

# Add a routing rule
router.add_rule(
    name="evaluate_agent",
    condition=lambda data: data.get("task_type") == "evaluate",
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

# Route a request
response = await router.route({
    "content": "Your text content here...",
    "task_type": "evaluate"
})

print(f"Result: {response.result}")
print(f"Cost: ${response.metadata['total_cost']}")
```

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

## Examples

### Example 1: Basic Routing

```python
router.add_rule(
    name="evaluate_agent",
    condition=lambda data: data.get("task_type") == "evaluate",
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
```

### Example 2: Cost-Effective Classification

```python
router.add_rule(
    name="classify_cheap",
    condition=lambda data: data.get("task_type") == "classify",
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
```

### Example 3: Using the Router

```python
response = await router.route({
    "content": "Very long agent interaction log...",
    "task_type": "evaluate"
})

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

## License

MIT

