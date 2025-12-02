from typing import Dict, List, Optional
import os
from openai import OpenAI
from supabase import create_client
from tenacity import retry, stop_after_attempt, wait_exponential
from src.tools.reranker import Reranker  


class SupabaseVectorKBSearcher:
    """Knowledge Base searcher with reranking"""
    
    def __init__(
        self, 
        supabase_url: str = None,
        supabase_key: str = None,
        openai_api_key: str = None,
        embedding_model: str = None,
        use_reranking: bool = True  
    ):
        """Initialize Supabase vector searcher with reranking"""
        self.name = "search_knowledge_base"
        
        # Get credentials from env if not provided
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.embedding_model = embedding_model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

        
        # Initialize clients
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
     
        
        # Initialize reranker
        self.use_reranking = use_reranking
        if self.use_reranking:
            self.reranker = Reranker()
        
        print(f" Supabase Vector KB Searcher initialized")
        print(f"   Model: {self.embedding_model}")
        print(f"   Reranking: {' Enabled' if self.use_reranking else 'Disabled'}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using OpenAI API
        """
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
    
    def search(
        self,
        query: str,
        top_k: int = 3, 
        category: Optional[str] = None,
        min_similarity: float = 0.5
    ) -> List[Dict]:
        """
        Search KB with reranking
        
        Args:
            query: Search query
            top_k: Number of results to return
            category: Category to filter by
            min_similarity: Minimum similarity score to return
        
        Returns:
            List of articles"""
        
        # Step 1: Get more results from Supabase for reranking
        initial_k = top_k * 3 if self.use_reranking else top_k  
        
        # Generate query embedding
        query_embedding = self._get_embedding(query)
        
        # Call Supabase
        result = self.supabase.rpc(
            "match_kb_articles",
            {
                "query_embedding": query_embedding,
                "match_threshold": min_similarity,
                "match_count": initial_k,  
                "filter_category": category
            }
        ).execute()
        
        # Format results
        articles = []
        for article in result.data:
            articles.append({
                "kb_id": article["kb_id"],
                "title": article["title"],
                "category": article["category"],
                "content": article["content"][:200] + "...",
                "full_content": article["content"],
                "similarity_score": float(article["similarity"]),
                "keywords": article.get("keywords", []),
                "avg_resolution_time": article.get("avg_resolution_time", "N/A"),
                "success_rate": article.get("success_rate", "N/A"),
                "related_articles": article.get("related_articles", [])
            })
        
        # Step 2: Rerank 
        if self.use_reranking and articles:
            articles = self.reranker.rerank(query, articles, top_k=top_k)
        else:
            articles = articles[:top_k]
        
        return articles
    
    def execute(self, ticket_text: str, category: Optional[str] = None) -> Dict:
        """Execute search with reranking"""
        results = self.search(ticket_text, top_k=3, category=category)
        
        return {
            "articles": results,
            "count": len(results),
            "search_method": "supabase_vector_reranked" if self.use_reranking else "supabase_vector",
            "embedding_model": self.embedding_model,
            "reranking": self.use_reranking
        }