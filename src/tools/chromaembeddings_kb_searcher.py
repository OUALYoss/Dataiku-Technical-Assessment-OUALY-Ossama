from typing import Dict, List, Optional
from openai import OpenAI
from src.config import OPENAI_API_KEY, EMBEDDING_MODEL, SIMILARITY_THRESHOLD
from src.data.knowledge_base import KB_ARTICLES
import chromadb
from chromadb.config import Settings
from tenacity import retry, stop_after_attempt, wait_exponential


class ChromaDBVectorKBSearcher:
    
    def __init__(self, chroma_path: str = "./chroma_db"):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.embedding_model = EMBEDDING_MODEL
        self.name = "search_knowledge_base"
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="kb_articles",
            metadata={"description": "IT Support Knowledge Base"}
        )
        
        # Populate if empty
        if self.collection.count() == 0:
            print("📥 Populating ChromaDB...")
            self._populate_chromadb()
            print(f"✅ Loaded {self.collection.count()} articles")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _get_embedding(self, text: str) -> List[float]:
        """Obtient l'embedding d'un texte"""
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
    
    def _populate_chromadb(self):
        """Populate ChromaDB with KB articles"""
        ids = []
        documents = []
        metadatas = []
        embeddings = []
        
        for article in KB_ARTICLES:
            # Build representative text
            text = f"{article['title']} {article['category']} {' '.join(article.get('keywords', []))} {article['content']}"
            
            # Generate embedding
            embedding = self._get_embedding(text)
            
            ids.append(article["kb_id"])
            documents.append(article["content"])
            metadatas.append({
                "kb_id": article["kb_id"],
                "title": article["title"],
                "category": article["category"],
                "keywords": ",".join(article.get("keywords", [])),
                "avg_resolution_time": article.get("avg_resolution_time", "N/A"),
                "success_rate": article.get("success_rate", "N/A")
            })
            embeddings.append(embedding)
        
        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
    
    def execute(self, ticket_text: str, category: Optional[str] = None) -> Dict:
        """Retrieves the most relevant KB articles"""
        # Generate ticket embedding
        ticket_embedding = self._get_embedding(ticket_text)
        
        # Build category filter
        where_filter = {"category": category} if category else None
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[ticket_embedding],
            n_results=10,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        articles = []
        similarities = []
        
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                distance = results['distances'][0][i]
                similarity = 1 / (1 + distance)
                
                if similarity > SIMILARITY_THRESHOLD:
                    metadata = results['metadatas'][0][i]
                    
                    article = {
                        "kb_id": metadata["kb_id"],
                        "title": metadata["title"],
                        "category": metadata["category"],
                        "content": results['documents'][0][i],
                        "keywords": metadata.get("keywords", "").split(",") if metadata.get("keywords") else [],
                        "avg_resolution_time": metadata.get("avg_resolution_time", "N/A"),
                        "success_rate": metadata.get("success_rate", "N/A")
                    }
                    
                    articles.append(article)
                    similarities.append(similarity)
        
        # Return top 3
        top_results = list(zip(articles, similarities))[:3]
        
        return {
            "articles": [r[0] for r in top_results],
            "similarities": [r[1] for r in top_results],
            "total_found": len(articles),
            "search_method": "chromadb_vector"
        }