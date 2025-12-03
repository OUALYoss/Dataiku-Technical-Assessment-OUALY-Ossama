from typing import Dict, List, Optional
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from src.config import OPENAI_API_KEY, EMBEDDING_MODEL, SIMILARITY_THRESHOLD
from src.data.knowledge_base import KB_ARTICLES


class ChromaDBVectorKBSearcher:
    
    def __init__(self, chroma_path: str = "./chroma_db"):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.embedding_model = EMBEDDING_MODEL
        self.name = "search_knowledge_base"
        
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        self.collection = self.chroma_client.get_or_create_collection(name="kb_articles")
        
        if self.collection.count() == 0:
            self._populate()
    
    def _get_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(model=self.embedding_model, input=text)
        return response.data[0].embedding
    
    def _populate(self):
        ids, documents, metadatas, embeddings = [], [], [], []
        
        for article in KB_ARTICLES:
            text = f"{article['title']} {article['category']} {' '.join(article.get('keywords', []))} {article['content']}"
            
            ids.append(article["kb_id"])
            documents.append(article["content"])
            embeddings.append(self._get_embedding(text))
            metadatas.append({
                "kb_id": article["kb_id"],
                "title": article["title"],
                "category": article["category"],
                "keywords": ",".join(article.get("keywords", [])),
                "avg_resolution_time": article.get("avg_resolution_time", "N/A"),
                "success_rate": article.get("success_rate", "N/A")
            })
        
        self.collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    
    def execute(self, ticket_text: str, category: Optional[str] = None) -> Dict:
        results = self.collection.query(
            query_embeddings=[self._get_embedding(ticket_text)],
            n_results=10,
            where={"category": category} if category else None,
            include=["documents", "metadatas", "distances"]
        )
        
        articles = []
        for i in range(len(results['ids'][0])):
            similarity = 1 / (1 + results['distances'][0][i])
            if similarity < SIMILARITY_THRESHOLD:
                continue
                
            meta = results['metadatas'][0][i]
            articles.append({
                "kb_id": meta["kb_id"],
                "title": meta["title"],
                "category": meta["category"],
                "content": results['documents'][0][i],
                "keywords": meta.get("keywords", "").split(","),
                "avg_resolution_time": meta.get("avg_resolution_time", "N/A"),
                "success_rate": meta.get("success_rate", "N/A"),
                "similarity": similarity
            })
        
        return {
            "articles": articles[:3],
            "count": len(articles),
            "search_method": "chromadb_vector"
        }