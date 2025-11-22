from openai import OpenAI
import json
from config import OPENAI_API_KEY, MODEL_NAME


class TicketCategorizer:
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = MODEL_NAME
        self.name = "ticket_categorizer"
        
        self.categories = [
            "PASSWORD_ACCESS",
            "SOFTWARE_ISSUES",
            "NETWORK_CONNECTIVITY",
            "HARDWARE_PROBLEMS",
            "EMAIL_ISSUES"
        ]
        
    def execute(self, ticket_text: str) -> Dict:
        """
        Classifies the ticket using a LLM : GPT-4o-mini
        """
        prompt = f"""
        Categorize this IT support ticket into ONE of these categories:
        {', '.join(self.categories)}
        
        Ticket:
        {ticket_text}
        
        Respond with JSON:
        {{
            "category": "CATEGORY_NAME",
            "confidence": 0-100,
            "reasoning": "brief explanation",
            "keywords_detected": ["keyword1", "keyword2"]
        }}
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an IT ticket categorizer. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)