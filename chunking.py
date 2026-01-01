from typing import List
from .types import ChunkingConfig


class ChunkingEngine:
    """Handles splitting large text into chunks"""

    def chunk_text(self, text: str, config: ChunkingConfig) -> List[str]:
        """
        Split text into chunks based on configuration

        Args:
            text: Input text to chunk
            config: Chunking configuration

        Returns:
            List of text chunks
        """
        if not config.enabled:
            return [text]

        if config.strategy == "fixed_size":
            return self._fixed_size_chunk(text, config)
        elif config.strategy == "semantic":
            return self._semantic_chunk(text, config)
        elif config.strategy == "sliding_window":
            return self._sliding_window_chunk(text, config)
        else:
            # Default to fixed_size
            return self._fixed_size_chunk(text, config)

    def _fixed_size_chunk(self, text: str, config: ChunkingConfig) -> List[str]:
        """Split text into fixed-size chunks"""
        chunks = []
        estimated_chunk_size = config.chunk_size * 4  # Approximate chars per token

        start = 0
        while start < len(text):
            end = start + estimated_chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for punct in [". ", "! ", "? ", "\n\n", "\n"]:
                    last_punct = chunk.rfind(punct)
                    if last_punct > estimated_chunk_size * 0.7:  # Don't break too early
                        chunk = chunk[: last_punct + len(punct)]
                        end = start + len(chunk)
                        break

            chunks.append(chunk.strip())
            start = end - config.overlap * 4  # Account for overlap

        return [c for c in chunks if c]  # Remove empty chunks

    def _semantic_chunk(self, text: str, config: ChunkingConfig) -> List[str]:
        """Split text using semantic boundaries (paragraphs, sections)"""
        # For now, use paragraph-based chunking
        # Could be enhanced with actual semantic analysis
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []

        for para in paragraphs:
            para_tokens = self.estimate_tokens(para)
            current_tokens = sum(self.estimate_tokens(p) for p in current_chunk)

            if current_tokens + para_tokens > config.chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                # Keep last paragraph for overlap
                current_chunk = current_chunk[-1:] if current_chunk else []

            current_chunk.append(para)

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def _sliding_window_chunk(self, text: str, config: ChunkingConfig) -> List[str]:
        """Split text with sliding window overlap"""
        return self._fixed_size_chunk(text, config)  # Same as fixed_size for now

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (simplified)
        Can use tiktoken or approximate as len(text) / 4
        """
        try:
            import tiktoken
            # Use cl100k_base encoding (used by GPT models)
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            # Fallback: approximate 4 characters per token
            return len(text) // 4