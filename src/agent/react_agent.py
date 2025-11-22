from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from config import OPENAI_API_KEY, MODEL_NAME
from tools import TicketCategorizer, EmbeddingKBSearcher, PriorityScorer
from utils.logger import ReActLogger

@dataclass
class ReActStep:
    """Une étape dans la chaîne ReAct"""
    step_number: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict] = None
    observation: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    
class ITSupportReActAgent: 
    
    def __init__(self, verbose: bool = True):
        """Initialise l'agent ReAct"""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = MODEL_NAME
        self.verbose = verbose
        self.logger = ReActLogger(verbose)
        
        # Initialiser les tools
        self.tools = {
            "ticket_categorizer": TicketCategorizer(),
            "search_knowledge_base": EmbeddingKBSearcher(),
            "calculate_priority": PriorityScorer()
        }
        
        # État de l'agent
        self.reset()
        
        
    def reset(self):
        """Reset l'état pour un nouveau ticket"""
        self.reasoning_chain: List[ReActStep] = []
        self.context = {}
        self.observations = {}
        self.current_step = 0
        
        
    def analyze_ticket(self, ticket: Dict) -> Dict:
        """
        Analyse principale d'un ticket avec ReAct loop
        """
        self.reset()
        self.context['ticket'] = ticket
        ticket_text = f"{ticket['subject']}\n{ticket['description']}"
        
        self.logger.log_start(ticket)
        
        # ReAct Loop
        for step in range(7):  # Max 7 steps
            self.current_step = step + 1
            
            # 1. THINK - Générer une pensée
            thought = self._generate_thought(ticket_text)
            
            if "FINISH" in thought or self._has_enough_info():
                # On a assez d'info, générer la recommandation finale
                self.logger.log_thought(thought, is_final=True)
                break
            
            # 2. ACT - Décider quelle action prendre
            action, action_input = self._decide_action(thought, ticket_text)
            
            # 3. OBSERVE - Exécuter l'action et observer
            observation = self._execute_tool(action, action_input)
            
            # Enregistrer l'étape
            react_step = ReActStep(
                step_number=self.current_step,
                thought=thought,
                action=action,
                action_input=action_input,
                observation=observation
            )
            
            self.reasoning_chain.append(react_step)
            self.observations[action] = observation
            
            # Logger l'étape
            self.logger.log_step(react_step)
        
        # Générer la recommandation finale
        recommendation = self._generate_final_recommendation(ticket)
        
        self.logger.log_recommendation(recommendation)
        
        return {
            "ticket": ticket,
            "reasoning_chain": self.reasoning_chain,
            "recommendation": recommendation,
            "total_steps": self.current_step
        }
    
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _generate_thought(self, ticket_text: str) -> str:
        """
        Génère une pensée basée sur le contexte actuel
        Utilise GPT-4o-mini
        """
        # Construire le contexte pour GPT
        context_prompt = self._build_thought_prompt(ticket_text)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": """You are a ReAct agent analyzing IT support tickets.
                Generate a SINGLE thought about what you need to know next.
                Be concise and specific.
                If you have enough information, say 'FINISH: I have enough information to provide recommendations.'"""},
                {"role": "user", "content": context_prompt}
            ],
            temperature=0.1,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    
    def _build_thought_prompt(self, ticket_text: str) -> str:
        """Construit le prompt pour la génération de pensée"""
        prompt = f"Ticket:\n{ticket_text}\n\n"
        
        if self.observations:
            prompt += "Previous observations:\n"
            for tool, obs in self.observations.items():
                prompt += f"- {tool}: {obs}\n"
            prompt += "\n"
        
        prompt += "What do you need to know next to solve this ticket?"
        return prompt
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _decide_action(self, thought: str, ticket_text: str) -> tuple:
        """
        Décide quelle action prendre basée sur la pensée
        Utilise GPT-4o-mini
        """
        tools_desc = """
        Available tools:
        1. categorize_ticket: Categorizes the ticket type (password, network, software, etc.)
        2. search_knowledge_base: Searches for relevant KB articles using embeddings
        3. calculate_priority: Calculates ticket priority (HIGH, MEDIUM, LOW)
        """
        
        prompt = f"""
        Based on this thought: "{thought}"
        
        For this ticket:
        {ticket_text}
        
        {tools_desc}
        
        Which tool should be used? Respond in JSON format:
        {{
            "tool": "tool_name",
            "reason": "why this tool"
        }}
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a tool selector. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=100,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        tool_name = result.get("tool", "categorize_ticket")
        
        # Préparer les inputs pour chaque tool
        if tool_name == "categorize_ticket":
            action_input = {"ticket_text": ticket_text}
        elif tool_name == "search_knowledge_base":
            action_input = {
                "ticket_text": ticket_text,
                "category": self.observations.get("categorize_ticket", {}).get("category")
            }
        elif tool_name == "calculate_priority":
            action_input = {
                "ticket_text": ticket_text,
                "category": self.observations.get("categorize_ticket", {}).get("category")
            }
        else:
            action_input = {"ticket_text": ticket_text}
        
        return tool_name, action_input
    
    def _execute_tool(self, tool_name: str, tool_input: Dict) -> Dict:
        """Exécute un tool et retourne l'observation"""
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        tool = self.tools[tool_name]
        return tool.execute(**tool_input)
    
    def _has_enough_info(self) -> bool:
        """Vérifie si on a assez d'info pour faire une recommandation"""
        required_tools = ["categorize_ticket", "search_knowledge_base", "calculate_priority"]
        return all(tool in self.observations for tool in required_tools)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _generate_final_recommendation(self, ticket: Dict) -> Dict:
        """
        Génère la recommandation finale avec GPT-4o-mini
        """
        # Construire le contexte complet
        context = self._build_recommendation_context(ticket)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": """You are an expert IT support advisor.
                Based on the analysis, provide a structured recommendation.
                Include: immediate actions, tools needed, estimated time, and preventive measures.
                Be specific and actionable. Format as JSON."""},
                {"role": "user", "content": context}
            ],
            temperature=0.2,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        recommendation = json.loads(response.choices[0].message.content)
        
        # Enrichir avec nos observations
        recommendation.update({
            "category": self.observations.get("categorize_ticket", {}).get("category"),
            "priority": self.observations.get("calculate_priority", {}).get("priority"),
            "kb_articles": self.observations.get("search_knowledge_base", {}).get("articles", [])
        })
        
        return recommendation
    
    def _build_recommendation_context(self, ticket: Dict) -> str:
        """Construit le contexte pour la recommandation finale"""
        context = f"""
        TICKET ANALYSIS COMPLETE
        
        Ticket ID: {ticket['id']}
        Subject: {ticket['subject']}
        Description: {ticket['description']}
        
        ANALYSIS RESULTS:
        """
        
        if "categorize_ticket" in self.observations:
            cat = self.observations["categorize_ticket"]
            context += f"\nCategory: {cat.get('category')} (Confidence: {cat.get('confidence')}%)"
        
        if "calculate_priority" in self.observations:
            pri = self.observations["calculate_priority"]
            context += f"\nPriority: {pri.get('priority')}"
            context += f"\nResponse Time: {pri.get('response_time')}"
        
        if "search_knowledge_base" in self.observations:
            kb = self.observations["search_knowledge_base"]
            context += f"\nRelevant KB Articles Found: {len(kb.get('articles', []))}"
            for article in kb.get('articles', [])[:3]:
                context += f"\n- {article.get('kb_id')}: {article.get('title')}"
        
        context += """
        
        Please provide a comprehensive recommendation including:
        1. immediate_actions: List of steps to resolve
        2. tools_required: IT tools needed
        3. estimated_time: Time to resolution
        4. preventive_measures: How to prevent this in future
        5. escalation_needed: true/false
        6. notes: Additional important notes
        """
        
        return context