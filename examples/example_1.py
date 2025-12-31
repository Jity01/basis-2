from metis_router import Router, ModelConfig, ChunkingConfig

# Initialize router
router = Router(config={
    "api_keys": {
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY")
    }
})

# Add rules
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

# Use router
response = await router.route({
    "content": "Very long agent interaction log...",
    "task_type": "evaluate"
})

print(f"Result: {response.result}")
print(f"Cost: ${response.metadata['total_cost']}")
print(f"Chunks processed: {response.metadata['chunks_processed']}")
