from collections import Counter

class ResultAggregator:
    """Aggregates results from multiple chunks"""
    
    def aggregate(
        self,
        chunk_results: List[ModelResponse],
        strategy: str
    ) -> str:
        """
        Combine multiple chunk results into single output
        
        Args:
            chunk_results: List of responses from processing chunks
            strategy: How to combine ("concatenate", "majority_vote", "average_score")
            
        Returns:
            Aggregated result
        """
        votes = [r.content for r in chunk_results]
        return Counter(votes).most_common(1)[0][0]