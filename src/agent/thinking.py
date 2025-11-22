from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME

class ThinkingEngine:
    """
    Moteur de pensée utilisant GPT-4o-mini
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = MODEL_NAME
    
    def generate_thought(self, context: Dict) -> str:
        """
        Génère une pensée basée sur le contexte
        """
        system_prompt = """
        You are the thinking component of a ReAct agent.
        Analyze the current situation and generate a single, clear thought about:
        - What information is missing
        - What should be investigated next
        - Whether you have enough info to make a recommendation
        
        Be concise and specific.
        """
        
        user_prompt = self._format_context(context)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    
    def _format_context(self, context: Dict) -> str:
        """Formate le contexte pour GPT"""
        formatted = f"Ticket: {context.get('ticket', {})}\n"
        
        if context.get('observations'):
            formatted += "\nObservations so far:\n"
            for key, value in context['observations'].items():
                formatted += f"- {key}: {value}\n"
        
        formatted += "\nWhat should we think about next?"
        return formatted