from typing import Dict, List, Optional, TypedDict
import os
import json

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()



LANGFUSE_ENABLED = os.getenv("LANGFUSE_PUBLIC_KEY") 


from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langfuse.openai import openai as langfuse_openai
    
langfuse = get_client()
langfuse_handler = CallbackHandler()


    


@tool
def ticket_categorizer(ticket_text: str) -> dict:
    """Categorize an IT support ticket into: PASSWORD_ACCESS, SOFTWARE_ISSUES, NETWORK_CONNECTIVITY, HARDWARE_PROBLEMS, EMAIL_ISSUES"""
    categories = ["PASSWORD_ACCESS", "SOFTWARE_ISSUES", "NETWORK_CONNECTIVITY", "HARDWARE_PROBLEMS", "EMAIL_ISSUES"]
    
    response = langfuse_openai.chat.completions.create(
        model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "You are an IT ticket categorizer. Respond only with valid JSON."},
            {"role": "user", "content": f"""
                Categorize this IT support ticket into ONE of these categories: {', '.join(categories)}
                
                Ticket: {ticket_text}
                
                Respond with JSON:
                {{"category": "CATEGORY_NAME", "confidence": 0-100, "keywords": ["keyword1", "keyword2"]}}
            """}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)


@tool  
def search_knowledge_base(ticket_text: str, category: Optional[str] = None) -> dict:
    """Search the knowledge base for relevant articles based on ticket content"""
    from supabase import create_client
    
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    embedding_response = langfuse_openai.embeddings.create(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        input=ticket_text
    )
    query_embedding = embedding_response.data[0].embedding
    
    result = supabase.rpc(
        "match_kb_articles",
        {"query_embedding": query_embedding, "match_threshold": 0.5, "match_count": 5, "filter_category": category}
    ).execute()
    
    articles = [
        {"kb_id": a["kb_id"], "title": a["title"], "category": a["category"], 
         "content": a["content"][:200] + "...", "similarity": float(a["similarity"])}
        for a in result.data[:3]
    ]
    return {"articles": articles, "count": len(articles)}


@tool
def calculate_priority(ticket_text: str, category: Optional[str] = None) -> dict:
    """Calculate the priority level of an IT support ticket"""
    prompt = f"[Category: {category}]\n{ticket_text}" if category else ticket_text
    
    response = langfuse_openai.chat.completions.create(
        model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": """Analyze IT ticket priority. Return JSON:
                {"priority": "CRITICAL|HIGH|MEDIUM|LOW", "confidence": 0-100, "response_time": "< 15 min|< 1 hour|< 4 hours|< 24 hours", "factors": ["factor1"]}
                CRITICAL: System down, multiple users blocked. HIGH: User blocked, deadline. MEDIUM: Degraded performance. LOW: Questions, feature requests."""},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)




class AgentState(TypedDict):
    ticket: Dict
    messages: List
    category: Optional[str]
    priority: Optional[str]
    kb_articles: Optional[List]
    observations: Dict
    used_tools: List[str]
    final_recommendation: Optional[Dict]
    step_count: int




class ITSupportLangGraphAgent:
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.llm = ChatOpenAI(
            model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.tools = [ticket_categorizer, search_knowledge_base, calculate_priority]
        self.tool_map = {t.name: t for t in self.tools}
        self.graph = self._build_graph()
        
        self.enable_safety = os.getenv("ENABLE_SAFETY_CHECK", "true").lower() == "true"
        if self.enable_safety:
            from together import Together
            self.together_client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        workflow.add_node("think", self._think_node)
        workflow.add_node("act", self._act_node)
        workflow.add_node("recommend", self._recommend_node)
        
        workflow.set_entry_point("think")
        workflow.add_conditional_edges("think", self._should_continue, {"act": "act", "recommend": "recommend"})
        workflow.add_edge("act", "think")
        workflow.add_edge("recommend", END)
        
        return workflow.compile()
    
    def _think_node(self, state: AgentState) -> AgentState:
        used = state.get("used_tools", [])
        available = [t for t in ["ticket_categorizer", "search_knowledge_base", "calculate_priority"] if t not in used]
        
        if self.verbose:
            print(f"\n[Step {state['step_count'] + 1}] Thinking... Available tools: {available}")
        
        obs_summary = ""
        if state.get("observations"):
            for tool_name, obs in state["observations"].items():
                if "category" in obs:
                    obs_summary += f"- Category: {obs.get('category')} ({obs.get('confidence')}%)\n"
                elif "priority" in obs:
                    obs_summary += f"- Priority: {obs.get('priority')} (response: {obs.get('response_time')})\n"
                elif "articles" in obs:
                    obs_summary += f"- KB: Found {len(obs.get('articles', []))} articles\n"
        
        state["step_count"] = state.get("step_count", 0) + 1
        state["messages"].append(AIMessage(content=f"Analyzed ticket. Available: {available}. Gathered:\n{obs_summary}"))
        return state
    
    def _should_continue(self, state: AgentState) -> str:
        used = set(state.get("used_tools", []))
        required = {"ticket_categorizer", "search_knowledge_base", "calculate_priority"}
        
        if required.issubset(used) or state["step_count"] >= 7:
            return "recommend"
        return "act"
    
    def _act_node(self, state: AgentState) -> AgentState:
        ticket_text = f"{state['ticket']['subject']}\n{state['ticket']['description']}"
        used = state.get("used_tools", [])
        available = [t for t in ["ticket_categorizer", "search_knowledge_base", "calculate_priority"] if t not in used]
        
        if not available:
            return state
        
        if "ticket_categorizer" not in used:
            tool_name = "ticket_categorizer"
        elif "search_knowledge_base" not in used:
            tool_name = "search_knowledge_base"
        else:
            tool_name = "calculate_priority"
        
        if self.verbose:
            print(f"  → Action: {tool_name}")
        
        tool = self.tool_map[tool_name]
        category = state.get("observations", {}).get("ticket_categorizer", {}).get("category")
        
        if tool_name == "ticket_categorizer":
            result = tool.invoke({"ticket_text": ticket_text})
        else:
            result = tool.invoke({"ticket_text": ticket_text, "category": category})
        
        state["used_tools"] = used + [tool_name]
        state["observations"] = state.get("observations", {})
        state["observations"][tool_name] = result
        
        if tool_name == "ticket_categorizer":
            state["category"] = result.get("category")
        elif tool_name == "calculate_priority":
            state["priority"] = result.get("priority")
        elif tool_name == "search_knowledge_base":
            state["kb_articles"] = result.get("articles", [])
        
        if self.verbose:
            print(f"  ← Observation: {json.dumps(result, indent=2)[:200]}...")
        
        return state
    
    def _recommend_node(self, state: AgentState) -> AgentState:
        if self.verbose:
            print("\n[Generating final recommendation...]")
        
        ticket = state["ticket"]
        obs = state.get("observations", {})
        
        context = f"""
TICKET: {ticket['subject']}
{ticket['description']}

ANALYSIS:
- Category: {obs.get('ticket_categorizer', {}).get('category', 'Unknown')} ({obs.get('ticket_categorizer', {}).get('confidence', 0)}%)
- Priority: {obs.get('calculate_priority', {}).get('priority', 'Unknown')} (Response: {obs.get('calculate_priority', {}).get('response_time', 'N/A')})
- KB Articles: {len(obs.get('search_knowledge_base', {}).get('articles', []))} found

Provide recommendation as JSON with: immediate_actions (list), tools_required (list), estimated_time (string), escalation_needed (boolean)
"""
        
        response = self.llm.invoke(
            [
                SystemMessage(content="You are an IT support advisor. Provide structured recommendations in JSON. Stay within IT support scope only."),
                HumanMessage(content=context)
            ],
            config={"callbacks": [langfuse_handler]} if langfuse_handler else {}
        )
        
        try:
            recommendation = json.loads(response.content)
        except:
            recommendation = {"immediate_actions": [response.content], "tools_required": [], "estimated_time": "Varies", "escalation_needed": False}
        
        if self.enable_safety:
            safety_result = self._check_safety(response.content)
            if not safety_result["is_safe"]:
                if self.verbose:
                    print(f"   Safety violation: {safety_result['violated_categories']}")
                recommendation = {
                    "immediate_actions": ["Please contact IT support directly."],
                    "tools_required": ["IT Support Portal"],
                    "estimated_time": "Varies",
                    "escalation_needed": True,
                    "safety_flagged": True,
                    "safety_categories": safety_result["violated_categories"]
                }
        
        recommendation.update({
            "category": state.get("category"),
            "category_confidence": obs.get("ticket_categorizer", {}).get("confidence"),
            "priority": state.get("priority"),
            "response_time": obs.get("calculate_priority", {}).get("response_time"),
            "kb_articles": state.get("kb_articles", [])[:3]
        })
        
        state["final_recommendation"] = recommendation
        return state
    
    def _check_safety(self, text: str) -> dict:
        prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>
Task: Check if there is unsafe content in 'Agent' messages according to safety policy.
<BEGIN UNSAFE CONTENT CATEGORIES>
S1: Violent Crimes, S2: Non-Violent Crimes, S3: Sex-Related Crimes, S4: Child Sexual Exploitation,
S5: Defamation, S6: Specialized Advice, S7: Privacy, S8: Intellectual Property,
S9: Indiscriminate Weapons, S10: Hate, S11: Suicide & Self-Harm, S12: Sexual Content,
S13: Elections, S14: Code Interpreter Abuse
<END UNSAFE CONTENT CATEGORIES>
<BEGIN CONVERSATION>
Agent: {text}
<END CONVERSATION>
Provide safety assessment: First line 'safe' or 'unsafe'. If unsafe, second line lists violated categories.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

        response = self.together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-Guard-3-8B",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=100
        )
        
        result = response.choices[0].message.content.strip()
        lines = result.split('\n')
        is_safe = lines[0].lower() == 'safe'
        violated = [c.strip() for c in lines[1].split(',')] if not is_safe and len(lines) > 1 else []
        
        return {"is_safe": is_safe, "violated_categories": violated, "raw_response": result}
    
    def analyze_ticket(self, ticket: Dict) -> Dict:
        print(f"\n{'='*60}")
        print(f"Analyzing ticket: {ticket['id']}")
        print(f"Subject: {ticket['subject']}")
        print(f"{'='*60}")
        
        initial_state: AgentState = {
            "ticket": ticket,
            "messages": [HumanMessage(content=f"{ticket['subject']}\n{ticket['description']}")],
            "category": None,
            "priority": None,
            "kb_articles": None,
            "observations": {},
            "used_tools": [],
            "final_recommendation": None,
            "step_count": 0
        }
        
        # Run graph with Langfuse callback if enabled
        config = {"callbacks": [langfuse_handler]} if langfuse_handler else {}
        final_state = self.graph.invoke(initial_state, config=config)
        
        self._print_recommendation(final_state["final_recommendation"])
        
        return {
            "ticket_id": ticket["id"],
            "recommendation": final_state["final_recommendation"],
            "total_steps": final_state["step_count"]
        }
    
    def _print_recommendation(self, rec: Dict):sss
        print(f"\n{'='*50}")
        print(" FINAL RECOMMENDATION")
        print(f"{'='*50}")
        
        if rec.get("safety_flagged"):
            print(f"\n Safety flagged: {rec.get('safety_categories', [])}")
        
        print(f"\n {rec.get('category')} ({rec.get('category_confidence')}%) |  {rec.get('priority')} |  {rec.get('estimated_time')}")
        
        if actions := rec.get("immediate_actions"):
            print(f"\n Actions:")
            for i, action in enumerate(actions, 1):
                # Clean action text
                clean = action.strip().lstrip('0123456789.) ')
                print(f"  {i}. {clean}")
        
        if tools := rec.get("tools_required"):
            print(f"\n Tools: {', '.join(tools)}")
        
        if articles := rec.get("kb_articles"):
            print(f"\n KB: {', '.join(a.get('kb_id', '') for a in articles[:3])}")
        
        print(f"{'='*50}\n")


#MAIN

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.data.sample_tickets import SAMPLE_TICKETS
    
    agent = ITSupportLangGraphAgent(verbose=False)
    
    test_tickets = SAMPLE_TICKETS[1:3]
    for ticket in test_tickets:
        result = agent.analyze_ticket(ticket)