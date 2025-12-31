class Router:
    """
    Main routing engine that manages rules and dispatches requests
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize router with optional configuration
        
        Args:
            config: Optional dict with default settings
                {
                    "default_chunk_size": 8000,
                    "default_overlap": 500,
                    "api_keys": {
                        "anthropic": "...",
                        "openai": "..."
                    },
                    "system_prompt": "You are a helpful assistant that can answer questions and help with tasks."
                    "prompt": "Evalutate the following text: {text}"
                }
        """
        
    def add_rule(
        self,
        name: str,
        condition: Callable[[Dict], bool],
        model_config: ModelConfig,
        chunking_config: Optional[ChunkingConfig] = None
    ) -> None:
        """
        Add a routing rule
        
        Args:
            name: Unique identifier for the rule
            condition: Function that takes data dict and returns True if rule matches
            model_config: Configuration for which model to use
            chunking_config: Optional chunking configuration
        """
        
    async def route(
        self,
        data: Dict[str, Any],
        metadata: Optional[Dict] = None
    ) -> RouterResponse:
        """
        Main routing method - routes data to appropriate model
        
        Args:
            data: Input data containing:
                - content: str (the text to process)
                - task_type: str (e.g., "evaluate", "generate", "classify")
                - Any other task-specific fields
            metadata: Optional metadata for logging/tracking
            
        Returns:
            RouterResponse with model output and routing metadata
        """