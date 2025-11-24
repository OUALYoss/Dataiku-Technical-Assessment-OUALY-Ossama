import os
from typing import Dict, List, Optional
from together import Together
from tenacity import retry, stop_after_attempt, wait_exponential


class SafetyChecker:
    """
    Safety checker using Llama Guard 3
    
    Categories checked:
    - S1: Violent Crimes
    - S2: Non-Violent Crimes  
    - S3: Sex-Related Crimes
    - S4: Child Sexual Exploitation
    - S5: Defamation
    - S6: Specialized Advice (financial, medical, legal)
    - S7: Privacy
    - S8: Intellectual Property
    - S9: Indiscriminate Weapons
    - S10: Hate
    - S11: Suicide & Self-Harm
    - S12: Sexual Content
    - S13: Elections
    - S14: Code Interpreter Abuse
    """
    
    def __init__(
        self, 
        together_api_key: str = None,
        model: str = "meta-llama/Meta-Llama-Guard-3-8B"
    ):
        """
        Initialize safety checker
        
        Args:
            together_api_key: Together AI API key (or from env)
            model: Llama Guard model to use
        """
        self.api_key = together_api_key or os.getenv("TOGETHER_API_KEY")
        
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY not found in .env")
        
        self.client = Together(api_key=self.api_key)
        self.model = model
        
        print(f"✅ Safety Checker initialized (Llama Guard 3)")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def check_safety(
        self, 
        text: str, 
        role: str = "Agent"  # "User" or "Agent"
    ) -> Dict:
        """
        Check if text is safe
        
        Args:
            text: Text to check
            role: "User" (for input) or "Agent" (for output)
        
        Returns:
            Dict with:
                - is_safe: bool
                - category: str (if unsafe)
                - raw_response: str
        """
        # Build prompt for Llama Guard 3
        prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

Task: Check if there is unsafe content in '{role}' messages in conversations according our safety policy with the below categories.

<BEGIN UNSAFE CONTENT CATEGORIES>
S1: Violent Crimes
S2: Non-Violent Crimes
S3: Sex-Related Crimes
S4: Child Sexual Exploitation
S5: Defamation
S6: Specialized Advice
S7: Privacy
S8: Intellectual Property
S9: Indiscriminate Weapons
S10: Hate
S11: Suicide & Self-Harm
S12: Sexual Content
S13: Elections
S14: Code Interpreter Abuse
<END UNSAFE CONTENT CATEGORIES>

<BEGIN CONVERSATION>

{role}: {text}

<END CONVERSATION>

Provide your safety assessment for {role} in the above conversation:
- First line must read 'safe' or 'unsafe'.
- If unsafe, a second line must include a comma-separated list of violated categories.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

        # Call Llama Guard 3
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=100
        )
        
        # Parse response
        result = response.choices[0].message.content.strip()
        lines = result.split('\n')
        
        is_safe = lines[0].lower() == 'safe'
        violated_categories = []
        
        if not is_safe and len(lines) > 1:
            violated_categories = [cat.strip() for cat in lines[1].split(',')]
        
        return {
            "is_safe": is_safe,
            "violated_categories": violated_categories,
            "raw_response": result,
            "checked_role": role
        }
    
    def check_user_input(self, user_text: str) -> Dict:
        """Check safety of user input"""
        return self.check_safety(user_text, role="User")
    
    def check_agent_output(self, agent_text: str) -> Dict:
        """Check safety of agent output"""
        return self.check_safety(agent_text, role="Agent")
    
    def format_safety_warning(self, safety_result: Dict) -> str:
        """Format a user-friendly safety warning"""
        if safety_result["is_safe"]:
            return ""
        
        categories = ", ".join(safety_result["violated_categories"])
        role = safety_result["checked_role"]
        
        return f"""
⚠️ SAFETY WARNING ⚠️
The {role} message has been flagged for potentially unsafe content.
Violated categories: {categories}

This content has been blocked for your safety.
"""