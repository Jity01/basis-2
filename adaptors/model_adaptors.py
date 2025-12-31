class ModelAdapter(ABC):
    """Abstract base class for model providers"""
    
    @abstractmethod
    async def call(
        self,
        content: str,
        config: ModelConfig
    ) -> ModelResponse:
        """Call the model API"""
        pass
        
@dataclass
class ModelResponse:
    """Response from a model"""
    content: str
    tokens_used: int
    cost: float  # USD
    latency_ms: int
    

class AnthropicAdapter(ModelAdapter):
    """Adapter for Anthropic API"""
    
    async def call(self, content: str, config: ModelConfig) -> ModelResponse:
        # Use Anthropic SDK
        # Calculate cost based on token usage
        # Return standardized response
        pass
        

class OpenAIAdapter(ModelAdapter):
    """Adapter for OpenAI API"""
    
    async def call(self, content: str, config: ModelConfig) -> ModelResponse:
        # Use OpenAI SDK
        # Calculate cost based on token usage
        # Return standardized response
        pass