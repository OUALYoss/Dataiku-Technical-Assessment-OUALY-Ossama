import os
import json
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are an IT Support Priority Analyzer. Analyze the ticket and return JSON only:

{
  "priority": "CRITICAL|HIGH|MEDIUM|LOW",
  "confidence": 0-100,
  "response_time": "< 15 min|< 1 hour|< 4 hours|< 24 hours",
  "reasoning": "brief explanation"
}

Guidelines:
- CRITICAL: System down, multiple users blocked, security breach
- HIGH: User blocked, deadline mentioned, client impact
- MEDIUM: Degraded performance, workaround exists
- LOW: Questions, feature requests, "when you have time"

Return valid JSON only."""


class PriorityScorer:
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.name = "priority_scorer"
    
    def execute(self, ticket_text: str, category: Optional[str] = None) -> Dict:
        prompt = f"[Category: {category}]\n{ticket_text}" if category else ticket_text
        
        response = self.client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        
        result = json.loads(response.choices[0].message.content)
       
        return {
            "priority": result.get("priority", "MEDIUM"),
            "confidence": result.get("confidence", 50),
            "response_time": result.get("response_time", "< 4 hours"),
            "reasoning": result.get("reasoning", "")
        }
    
    def format_output(self, result: Dict) -> str:
        return f"Priority: {result['priority']} | Response: {result['response_time']}"