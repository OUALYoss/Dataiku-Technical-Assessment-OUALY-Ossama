"""
Cross-Encoder Reranker
----------------------
Reranks search results using cross-encoder for better relevance
"""

from typing import List, Dict
from sentence_transformers import CrossEncoder
import numpy as np


class Reranker:
    """Reranks search results using cross-encoder"""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize reranker
        
        Args:
            model_name: Cross-encoder model to use
                - ms-marco-MiniLM-L-6-v2: Fast, good quality (default)
                - ms-marco-MiniLM-L-12-v2: Slower, better quality
        """
        print(f"📥 Loading reranker model: {model_name}...")
        self.model = CrossEncoder(model_name)
        print(f"✅ Reranker loaded!")
    
    def rerank(
        self, 
        query: str, 
        articles: List[Dict], 
        top_k: int = 3
    ) -> List[Dict]:
        """
        Rerank articles based on query
        
        Args:
            query: Search query
            articles: List of articles from initial search
            top_k: Number of results to return after reranking
        
        Returns:
            Reranked articles with new scores
        """
        if not articles:
            return []
        
        # Prepare pairs (query, document) for cross-encoder
        pairs = []
        for article in articles:
            # Use title + content for reranking
            doc_text = f"{article['title']}. {article.get('full_content', article['content'])}"
            pairs.append([query, doc_text])
        
        # Get reranking scores
        scores = self.model.predict(pairs)
        
        # Add rerank scores to articles
        for i, article in enumerate(articles):
            article['rerank_score'] = float(scores[i])
            article['original_similarity'] = article.get('similarity_score', 0.0)
        
        # Sort by rerank score
        reranked = sorted(articles, key=lambda x: x['rerank_score'], reverse=True)
        
        # Return top_k
        return reranked[:top_k]