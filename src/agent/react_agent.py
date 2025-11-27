from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import OPENAI_API_KEY, MODEL_NAME
from src.tools import TicketCategorizer, ChromaDBVectorKBSearcher, PriorityScorer, SupabaseVectorKBSearcher, SafetyChecker


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
    
    def __init__(self, verbose: bool = False, max_steps: int = 7):
        """
        Initialise agent ReAct
        Args:
            verbose: if True, print all the steps 
            max_steps:  maximum of steps (default: 6)
        """
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = MODEL_NAME
        self.verbose = verbose
        self.max_steps = max_steps
        
        # Initialise tools
        self.tools = {
            "ticket_categorizer": TicketCategorizer(),
            "search_knowledge_base": SupabaseVectorKBSearcher(),
            "calculate_priority": PriorityScorer()
        }
        
        # Initialize safety checker 
        self.enable_safety = os.getenv("ENABLE_SAFETY_CHECK", "true").lower() == "true"
        if self.enable_safety:
            try:
                self.safety_checker = SafetyChecker()
                print("Safety checking enabled  using Llama Guard 3")
            except Exception as e:
                print(f"Safety checker disabled: {e}")
                self.enable_safety = False
        
        # reset the agent
        self.reset()
        
        
    def reset(self):
        """Reset l'état pour un nouveau ticket"""
        self.reasoning_chain: List[ReActStep] = []
        self.context = {}
        self.observations = {}
        self.current_step = 0
        self.used_tools = set()  # Track 
        
        
    def analyze_ticket(self, ticket: Dict) -> Dict:
        """
        Analyse principale d'un ticket avec ReAct loop
        
        Le cycle ReAct:
        1. THOUGHT: Le LLM réfléchit à ce qu'il faut faire
        2. ACTION: Le LLM choisit un outil à utiliser
        3. OBSERVATION: L'outil est exécuté et retourne un résultat
        4. Répéter jusqu'à avoir assez d'information
        """
        self.reset()
        self.context['ticket'] = ticket
        ticket_text = f"{ticket['subject']}\n{ticket['description']}"
        
        if self.verbose:
            print(f"\n{'*'*60}")
            print(f"Start analyzing the ticket: {ticket['id']}")
            print(f"Subject: {ticket['subject']}")
            print(f"{'*'*60}\n")
        
        # ReAct Loop Principal
        for step in range(1, self.max_steps + 1):
            self.current_step = step
            
            
            # Step 1: THOUGHT about the user query
            
            thought = self._generate_thought(ticket_text)
            
            if self.verbose:
                print(f"Step N°{self.current_step}: {thought}")
            
            # Vérifier si le LLM veut terminer
            if "FINISH" in thought.upper() or self._has_enough_info():
                if self.verbose:
                    print("\n => Agent has gathered sufficient information!")
                    print("\n => Ready to answer")
                break
            
           
            # Step 2: ACTION to choose
          
            action, action_input = self._decide_action(thought, ticket_text)
            
            if action == "FINISH" or action is None:
                if self.verbose:
                    print("\n All tools have been used!")
                break
            
            if self.verbose:
                print(f"🎯 Action: {action}")
            
            
            # Step 3: OBSERVATION Execute the action
         
            observation = self._execute_tool(action, action_input)
            self.used_tools.add(action) # in order to not use a tool more than one time
            
            if self.verbose:
                self._print_observation(action, observation)
            
            # save the step 
            react_step = ReActStep(
                step_number=self.current_step,
                thought=thought,
                action=action,
                action_input=action_input,
                observation=observation
            )
            
            self.reasoning_chain.append(react_step)
            self.observations[action] = observation
        
        
        # FINAL RECOMMANDATION 
       
        if self.verbose:
            print(f"\n => Generating final recommendation based on gathered information")
        
        recommendation = self._generate_final_recommendation(ticket)
        
        if self.verbose:
            self._print_final_recommendation(recommendation)
        
        return {
            "ticket_id": ticket['id'],
            "reasoning_chain": self.reasoning_chain,
            "recommendation": recommendation,
            "total_steps": self.current_step
        }
    
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _generate_thought(self, ticket_text: str) -> str:
        """
        Generate a thought based on the current context.
        The LLM decides what it should do next.
        """
        prompt = self._build_thought_prompt(ticket_text)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_thought_system_prompt()},  # system message for the llm
                {"role": "user", "content": prompt} # user message 
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    
    def _get_thought_system_prompt(self) -> str:
        """
        System Prompt thought generation
        """
        return """ You are a ReAct reasoning agent for IT support ticket analysis.

            Your goal: Analyze the ticket by gathering information using available tools.

            Available tools:
            1. ticket_categorizer :Identify the ticket category (use this FIRST)
            2. search_knowledge_base : Find relevant solutions (use AFTER categorization)
            3. calculate_priority : Assess urgency level (use to determine response time)

            Rules:
            - Think step by step about what information you need
            - Use each tool only ONCE
            - After using all 3 tools, say "FINISH: I have all the information needed"
            - Be concise and specific in your thoughts
            - Don't repeat yourself

            Format your response as a single clear thought about what you need to do next."""
    
    
    def _build_thought_prompt(self, ticket_text: str) -> str:
        """Build the contextual prompt for thought generation."""
        
        # used tools
        used_tools_str = ", ".join(self.used_tools) if self.used_tools else "None"
        
        # available tools
        available_tools = [tool for tool in self.tools.keys() if tool not in self.used_tools]
        available_tools_str = ", ".join(available_tools) if available_tools else "None"
        
        prompt = f"""
                TICKET TO ANALYZE:
                    {ticket_text}

                    TOOLS ALREADY USED: {used_tools_str}
                    TOOLS STILL AVAILABLE: {available_tools_str}
                    """
        
        # Ajouter les observations précédentes
        if self.observations:
            prompt += "INFORMATION GATHERED SO FAR:\n"
            for tool_name, obs in self.observations.items():
                if isinstance(obs, dict):
                    if 'category' in obs:
                        prompt += f"- Category: {obs.get('category')} (confidence: {obs.get('confidence')}%)\n"
                    elif 'priority' in obs:
                        prompt += f"- Priority: {obs.get('priority')} (response time: {obs.get('response_time')})\n"
                    elif 'articles' in obs:
                        prompt += f"- KB Articles: Found {len(obs.get('articles', []))} relevant articles\n"
            prompt += "\n"
        
        prompt += "What should you do next? (If you have all information, say 'FINISH')"
        
        return prompt
    
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _decide_action(self, thought: str, ticket_text: str) -> Tuple[Optional[str], Dict]:
        """
        Le LLM décide quelle action prendre basée sur sa pensée
        Returns: (tool_name, tool_input)
        """
        
        # Si tous les outils ont été utilisés, terminer
        if len(self.used_tools) >= 3:
            return None, {}
        
        # Outils disponibles
        available_tools = [tool for tool in self.tools.keys() if tool not in self.used_tools]
        
        if not available_tools:
            return None, {}
        
        prompt = f"""Based on this thought: "{thought}"

                Available tools you haven't used yet:
                {json.dumps(available_tools, indent=2)}

                Tools already used: {list(self.used_tools)}

                Which tool should you use NEXT? Choose ONE tool from the available list.

                Respond in JSON format:
                {{
                    "tool": "exact_tool_name_from_list",
                    "reason": "brief reason why"
                }}
                """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a tool selector. Return only valid JSON with one tool from the available list."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=100,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        tool_name = result.get("tool")
        
        # Validation: le tool doit être dans la liste disponible
        if tool_name not in available_tools:
            # Fallback: prendre le premier outil disponible
            tool_name = available_tools[0] if available_tools else None
        
        if tool_name is None:
            return None, {}
        
        # Préparer les inputs pour le tool
        action_input = self._prepare_tool_input(tool_name, ticket_text)
        
        return tool_name, action_input
    
    
    def _prepare_tool_input(self, tool_name: str, ticket_text: str) -> Dict:
        """Prépare les inputs appropriés pour chaque tool"""
        
        base_input = {"ticket_text": ticket_text}
        
        # Ajouter la catégorie si elle est disponible
        if "ticket_categorizer" in self.observations:
            category = self.observations["ticket_categorizer"].get("category")
            if category and tool_name in ["search_knowledge_base", "calculate_priority"]:
                base_input["category"] = category
        
        return base_input
    
    
    def _execute_tool(self, tool_name: str, tool_input: Dict) -> Dict:
        """Exécute un tool et retourne l'observation"""
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            tool = self.tools[tool_name]
            return tool.execute(**tool_input)
        except Exception as e:
            return {"error": str(e)}
    
    
    def _has_enough_info(self) -> bool:
        """Vérifie si tous les outils requis ont été utilisés"""
        required_tools = {"ticket_categorizer", "search_knowledge_base", "calculate_priority"}
        return required_tools.issubset(self.used_tools)
    
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _generate_final_recommendation(self, ticket: Dict) -> Dict:
        """Generate final recommendation with safety check"""
        context = self._build_recommendation_context(ticket)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": """You are an IT support advisor.

    CRITICAL: You can ONLY provide IT technical support.

    FORBIDDEN TOPICS (You MUST refuse these):
    - Financial advice (investments, stocks, crypto, trading, portfolios)
    - Medical advice (diagnosis, symptoms, treatment, medications)
    - Legal advice (liability, lawsuits, legal rights, contracts)
    - Any specialized professional advice outside IT

    If a ticket requests forbidden topics:
    1. Immediately recognize it's outside IT scope
    2. State: "This request is outside IT support scope"
    3. Provide: "immediate_actions": ["Please contact [appropriate professional]"]
    4. Set: "escalation_needed": true
    5. DO NOT provide analysis, research, tools, or strategies for non-IT topics
    6. DO NOT add disclaimers while still providing the forbidden advice

    For legitimate IT support issues only, provide structured recommendations in JSON format:
    - immediate_actions: Specific IT troubleshooting steps
    - tools_required: IT tools and software only
    - estimated_time: Realistic time estimate
    - preventive_measures: IT security and maintenance steps
    - escalation_needed: Boolean
    - notes: Additional IT-related information

    Return your response as valid JSON with these exact fields.
    Stay strictly within IT technical support domain."""},
                {"role": "user", "content": context}
            ],
            temperature=0.2,
            max_tokens=600,
            response_format={"type": "json_object"}
        )
        
        recommendation_text = response.choices[0].message.content
        
        # Debug
        # if self.verbose:
        #     print("\n" + "="*80)
        #     print("🔍 DEBUG: LLM Response")
        #     print("="*80)
        #     print(recommendation_text[:500] + "..." if len(recommendation_text) > 500 else recommendation_text)
        #     print("="*80)
        
        # Safety check
        if self.enable_safety:
            print(f"\n{'#'*50}")
            print(" Llama Guard")
            print(f"{'#'*50}")
            
            print("\n Running safety check :")
            safety_result = self.safety_checker.check_agent_output(recommendation_text)
            
            print(f"   Is safe: {safety_result['is_safe']}")
            print(f"   Raw response: {safety_result['raw_response']}")
            
            if not safety_result["is_safe"]:
                print(" SAFETY VIOLATION DETECTED ")
                print(f"Categories: {safety_result['violated_categories']}")
                
                return {
                    "category": self.observations.get("ticket_categorizer", {}).get("category"),
                    "category_confidence": self.observations.get("ticket_categorizer", {}).get("confidence"),
                    "priority": self.observations.get("calculate_priority", {}).get("priority"),
                    "response_time": self.observations.get("calculate_priority", {}).get("response_time"),
                    "immediate_actions": ["Please contact IT support directly for assistance with this issue."],
                    "tools_required": ["IT Support Portal"],
                    "estimated_time": "Varies",
                    "preventive_measures": [],
                    "escalation_needed": True,
                    "notes": "For safety reasons, automated recommendation was not provided. Please contact support.",
                    "kb_articles": [],
                    "safety_flagged": True,
                    "safety_categories": safety_result['violated_categories']
                }
            else:
                print(" safety check : Done")
        
        # Parse recommendation
        recommendation = json.loads(recommendation_text)
        
        recommendation.update({
            "category": self.observations.get("ticket_categorizer", {}).get("category"),
            "category_confidence": self.observations.get("ticket_categorizer", {}).get("confidence"),
            "priority": self.observations.get("calculate_priority", {}).get("priority"),
            "response_time": self.observations.get("calculate_priority", {}).get("response_time"),
            "kb_articles": self.observations.get("search_knowledge_base", {}).get("articles", [])[:3],
            "safety_flagged": False
        })
        
        return recommendation
    
    
    def _build_recommendation_context(self, ticket: Dict) -> str:
        """Construit le contexte complet pour la recommandation finale"""
        
        context = f"""COMPLETE TICKET ANALYSIS

TICKET DETAILS:
- ID: {ticket['id']}
- Subject: {ticket['subject']}
- Description: {ticket['description']}

ANALYSIS RESULTS:
"""
        
        # Catégorisation
        if "ticket_categorizer" in self.observations:
            cat = self.observations["ticket_categorizer"]
            context += f"\n CATEGORY: {cat.get('category')} (Confidence: {cat.get('confidence')}%)"
            if cat.get('keywords'):
                context += f"\n  Keywords detected: {', '.join(cat.get('keywords', []))}"
        
        # Priorité
        if "calculate_priority" in self.observations:
            pri = self.observations["calculate_priority"]
            context += f"\n\n PRIORITY: {pri.get('priority')}"
            context += f"\n  Response Time: {pri.get('response_time')}"
            context += f"\n  Score: {pri.get('score')}"
            if pri.get('factors'):
                context += f"\n  Key factors: {', '.join(pri.get('factors', []))}"
        
        # Articles KB
        if "search_knowledge_base" in self.observations:
            kb = self.observations["search_knowledge_base"]
            articles = kb.get('articles', [])
            context += f"\n\n KNOWLEDGE BASE: Found {len(articles)} relevant articles"
            
            if articles:
                context += "\n  Top solutions:"
                for i, article in enumerate(articles[:3], 1):
                    context += f"\n  {i}. {article.get('title')}"
                    content = article.get('content', '')
                    if content:
                        context += f"\n     {content[:150]}..."
        
        context += """

TASK: Based on this complete analysis, provide a comprehensive recommendation.
Focus on immediate actionable steps, required tools, realistic time estimates, and preventive measures."""
        
        return context
    
    
    def _print_observation(self, action: str, observation: Dict):
        """Affiche l'observation de manière formatée"""
        if isinstance(observation, dict):
            if 'category' in observation:
                print(f"   → Category: {observation.get('category')} ({observation.get('confidence')}% confidence)")
            elif 'priority' in observation:
                print(f"   → Priority: {observation.get('priority')} | Response: {observation.get('response_time')}")
            elif 'articles' in observation:
                articles = observation.get('articles', [])
                print(f"   → Found {len(articles)} KB articles")
                if articles:
                    for i, article in enumerate(articles[:2], 1):
                        print(f"      • {article.get('title', 'Unknown')}")
            else:
                print(f"   → {str(observation)[:100]}...")
        else:
            print(f"   → {str(observation)[:100]}...")
    
    
    def _print_final_recommendation(self, recommendation: Dict):
        """Affiche la recommandation finale de manière compacte"""
        print(f"\n{'='*50}")
        print(" FINAL RECOMMENDATION")
        print(f"{'='*50}")
        
        # Safety warning
        if recommendation.get("safety_flagged"):
            print(f"\n Safety flagged: {', '.join(recommendation.get('safety_categories', []))}")
            print(f"    Safe fallback provided")
        
        # Header info
        category = recommendation.get('category', 'Unknown')
        priority = recommendation.get('priority', 'Unknown')
        est_time = recommendation.get('estimated_time', 'N/A')
        
        print(f"\n🏷️  {category} | ⚡ {priority} | ⏱️  {est_time}")
        
        # Immediate actions
        if actions := recommendation.get('immediate_actions'):
            print(f"\n🔧 Actions:")
            for i, action in enumerate(actions, 1):
                # Clean action text
                clean = action.strip().lstrip('0123456789.) ')
                print(f"  {i}. {clean}")
        
        # Tools
        if tools := recommendation.get('tools_required'):
            print(f"\n ✓  Tools: {', '.join(tools)}")
        
        # KB articles (compact)
        if articles := recommendation.get('kb_articles'):
            print(f"\n ✓   KB: {', '.join(a.get('kb_id', '') for a in articles[:3])}")
        
        # Escalation flag
        if recommendation.get('escalation_needed'):
            print(f"\n⚠️  Escalation required")
        
        
        print(f"{'='*80}\n")
    
    
    
    
    
    