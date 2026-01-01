from collections import Counter
from typing import List, Any
from .providers.base import ModelResponse
from .types import AggregationStrategy


class ResultAggregator:
    """Aggregates results from multiple chunks"""

    def aggregate(
        self, chunk_results: List[ModelResponse], strategy: AggregationStrategy
    ) -> Any:
        """
        Combine multiple chunk results into single output

        Args:
            chunk_results: List of responses from processing chunks
            strategy: How to combine (AggregationStrategy enum)

        Returns:
            Aggregated result (str, float, or other depending on strategy)
        """
        if not chunk_results:
            return ""

        if strategy == AggregationStrategy.CONCATENATE:
            return "\n\n".join(r.content for r in chunk_results)

        elif strategy == AggregationStrategy.MAJORITY_VOTE:
            votes = [r.content.strip() for r in chunk_results]
            if not votes:
                return ""
            counter = Counter(votes)
            return counter.most_common(1)[0][0]

        elif strategy == AggregationStrategy.AVERAGE_SCORE:
            # Try to extract numeric scores
            scores = []
            for result in chunk_results:
                try:
                    # Try to parse as float
                    score = float(result.content.strip())
                    scores.append(score)
                except (ValueError, AttributeError):
                    # If not a number, skip
                    continue

            if scores:
                return sum(scores) / len(scores)
            else:
                # Fallback to concatenate if no scores found
                return "\n\n".join(r.content for r in chunk_results)

        else:
            # Default to concatenate
            return "\n\n".join(r.content for r in chunk_results)