import os
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client

load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"


def generate_embedding(text: str) -> list[float]:
    """Generate embedding vector using OpenAI API"""
    response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def prepare_text(article: dict) -> str:
    """Combine article fields for embedding"""
    keywords = ", ".join(article.get("keywords", []))
    return f"Title: {article['title']}\nCategory: {article['category']}\nContent: {article['content']}\nKeywords: {keywords}"


def seed_kb(articles: list[dict]):
    """Insert articles with embeddings into Supabase"""
    # Clear existing articles
    supabase.table("kb_articles").delete().neq("id", -1).execute()
    
    for article in articles:
        # Generate embedding
        embedding = generate_embedding(prepare_text(article))
        
        # Insert into Supabase
        record = {
            "kb_id": article["kb_id"],
            "title": article["title"],
            "category": article["category"],
            "content": article["content"],
            "keywords": article.get("keywords", []),
            "avg_resolution_time": article.get("avg_resolution_time"),
            "success_rate": article.get("success_rate"),
            "related_articles": article.get("related_articles", []),
            "embedding": embedding
        }
        supabase.table("kb_articles").insert(record).execute()


if __name__ == "__main__":
    from data.knowledge_base import KB_ARTICLES
    seed_kb(KB_ARTICLES)
    print(f"✅ Seeded {len(KB_ARTICLES)} articles")