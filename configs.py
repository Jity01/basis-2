@dataclass
class ModelConfig:
    """Configuration for model selection"""
    provider: str  # "anthropic" or "openai"
    model: str  # e.g., "claude-sonnet-4-20250514"
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: Optional[str] = None
    
@dataclass
class ChunkingConfig:
    """Configuration for chunking behavior"""
    enabled: bool = True
    strategy: str = "fixed_size"  # "fixed_size", "semantic", "sliding_window"
    chunk_size: int = 8000  # in tokens
    overlap: int = 500  # tokens of overlap between chunks
    aggregation: str = "concatenate"  # "concatenate", "majority_vote", "average_score"
    
@dataclass
class RouterResponse:
    """Response from router"""
    result: Any  # Could be str, dict, list depending on aggregation
    metadata: Dict[str, Any]
    chunks: Optional[List[Dict]] = None