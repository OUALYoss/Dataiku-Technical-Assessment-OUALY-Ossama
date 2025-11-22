from   typing import Dict, List
import numpy as np
from openai import OpenAI
from config import OPENAI_API_KEY, EMBEDDING_MODEL, SIMILARITY_THRESHOLD
from data.knowledge_base import KB_ARTICLES

class EmbeddingsKBSearcher:
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.embedding_model = EMBEDDING_MODEL
        self.name = "embedding_kb_searcher"
        self.kb_articles = KB_ARTICLES
        
        #  Precompute embeddings for the knowledge bas
        self._precompute_kb_embeddings()
        
        
    def _get_embedding(self, text: str) -> List[float]:
        """
        Obtient l'embedding d'un texte
        """
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
    
    def _precompute_kb_embeddings(self):
        """
        Precomputes embeddings for all knowledge-base articles
        """
        self.kb_embeddings = []
        
        for article in self.kb_articles:
            # Build a representative text for the article
            article_text = f"{article['title']} {article['category']} {' '.join(article['keywords'])} {article['content']}"
            
            # Obtenir l'embedding
            embedding = self._get_embedding(article_text)
            
            # Store the article and its embedding : our vector store
            self.kb_embeddings.append({
                "article": article,
                "embedding": embedding
            })
            
            
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """
        Computes the cosine similarity between two vectors
        """
        # My two vetors
        a_array = np.array(a)
        b_array = np.array(b)
        
        dot_product = np.dot(a_array, b_array)
        norm_a = np.linalg.norm(a_array)
        norm_b = np.linalg.norm(b_array)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0 # raise exception : devide by 0
        
        return dot_product / (norm_a * norm_b)
    
    
    # Main function : 
    
    def execute(self, ticket_text: str, category: str = None) -> Dict:
        """
        Retrieves the most relevant knowledge-base articles based on semantic similarity
        """
        # Get the embedding of the ticket
        ticket_embedding = self._get_embedding(ticket_text)
        
        # Compute semantic similarities
        results = []
        for kb_item in self.kb_embeddings:
            article = kb_item["article"]
            
            # Bonus if the categories match
            category_bonus = 0.2 if category and article["category"] == category else 0
            
            # Compute similarity
            similarity = self._cosine_similarity(ticket_embedding, kb_item["embedding"])
            final_score = similarity + category_bonus
            
            if similarity > SIMILARITY_THRESHOLD or (category and article["category"] == category):
                results.append({
                    "article": article,
                    "similarity": similarity,
                    "final_score": final_score
                })
        
        # sort by highest   score
        results.sort(key=lambda x: x["final_score"], reverse=True)
        
        #  top 3
        top_results = results[:3]
        
        return {
            "articles": [tr["article"] for tr in top_results],
            "similarities": [tr["similarity"] for tr in top_results],
            "total_found": len(results),
            "search_method": "semantic_embedding"
        }