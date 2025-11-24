from typing import Dict, List, Optional
from src.data.patterns import PRIORITY_KEYWORDS, PRIORITY_RULES

class PriorityScorer:
    
    def __init__(self):
        self.priority_keywords = PRIORITY_KEYWORDS
        self.priority_rules = PRIORITY_RULES
        self.name = "priority_scorer"
        
    def execute(self, ticket_text: str, category: Optional[str] = None) -> Dict:
        """
        Calcule la priorité du ticket
        
        Args:
            ticket_text: Le texte complet du ticket (subject + description)
            category: La catégorie du ticket (optionnel mais améliore la précision)
            
        Returns:
            Dict avec priorité, score, et justification
        """
        text_lower = ticket_text.lower()
        
        # 1. Analyser les mots-clés de priorité dans le texte
        keyword_matches = self._find_priority_keywords(text_lower)
        
        # 2. Obtenir la priorité de base selon la catégorie
        base_priority, category_factors = self._get_category_priority(text_lower, category)
        
        # 3. Calculer le score final
        final_priority, confidence = self._calculate_final_priority(
            keyword_matches, 
            base_priority, 
            category_factors
        )
        
        # 4. Déterminer le temps de réponse recommandé
        response_time = self._get_response_time(final_priority)
        
       
        return {
            "priority": final_priority,
            "confidence": confidence,
            "response_time": response_time,
            "keyword_matches": keyword_matches,
            "category_factors": category_factors,
            "base_priority": base_priority
        }
    
    def _find_priority_keywords(self, text_lower: str) -> Dict[str, List[str]]:
        """
        Trouve tous les mots-clés de priorité dans le texte
        """
        matches = {
            "HIGH": [],
            "MEDIUM": [],
            "LOW": []
        }
        # à optimiser 
        for priority_level, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matches[priority_level].append(keyword)
        
        return matches
    
    def _get_category_priority(self, text_lower: str, category: Optional[str]) -> tuple:
        """
        Détermine la priorité basée sur la catégorie et ses règles
        """
        if not category or category not in self.priority_rules:
            # Pas de catégorie ou catégorie inconnue
            return "MEDIUM", {"escalation": [], "deescalation": []}
        
        rule = self.priority_rules[category]
        base_priority = rule.get("base_priority", "MEDIUM")
        
        # Vérifier les facteurs d'escalade
        escalation_factors = []
        for trigger in rule.get("escalate_if", []):
            if trigger.lower() in text_lower:
                escalation_factors.append(trigger)
        
        # Vérifier les facteurs de désescalade
        deescalation_factors = []
        for trigger in rule.get("deescalate_if", []):
            if trigger.lower() in text_lower:
                deescalation_factors.append(trigger)
        
        return base_priority, {
            "escalation": escalation_factors,
            "deescalation": deescalation_factors
        }
    
    def _calculate_final_priority(self, keyword_matches: Dict, 
                                 base_priority: str, 
                                 category_factors: Dict) -> tuple:
        """
        Calcule la priorité finale basée sur tous les facteurs
        """
        # Système de points
        scores = {
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }
        
        # Points pour les mots-clés trouvés
        scores["HIGH"] += len(keyword_matches["HIGH"]) * 3
        scores["MEDIUM"] += len(keyword_matches["MEDIUM"]) * 2
        scores["LOW"] += len(keyword_matches["LOW"]) * 1
        
        # Points pour la priorité de base de la catégorie
        scores[base_priority] += 5
        
        # Points pour les facteurs d'escalade/désescalade
        if category_factors["escalation"]:
            scores["HIGH"] += len(category_factors["escalation"]) * 4
        if category_factors["deescalation"]:
            scores["LOW"] += len(category_factors["deescalation"]) * 3
        
        # Déterminer la priorité gagnante
        max_score = max(scores.values())
        
        # Si égalité, privilégier HIGH > MEDIUM > LOW
        if scores["HIGH"] == max_score:
            final_priority = "HIGH"
        elif scores["MEDIUM"] == max_score:
            final_priority = "MEDIUM"
        else:
            final_priority = "LOW"
        
        # Calculer la confiance (0-100%)
        total_score = sum(scores.values())
        if total_score > 0:
            confidence = int((scores[final_priority] / total_score) * 100)
        else:
            confidence = 50  # Confiance moyenne par défaut
        
        # Ajuster la confiance si très peu d'indices
        if total_score < 5:
            confidence = min(confidence, 60)
        
        return final_priority, confidence
    
    def _get_response_time(self, priority: str) -> str:
        """
        Retourne le temps de réponse recommandé
        """
        response_times = {
            "HIGH": "< 1 hour",
            "MEDIUM": "< 4 hours", 
            "LOW": "< 24 hours"
        }
        return response_times.get(priority, "< 4 hours")
    
    
    
    def format_output(self, result: Dict) -> str:
        """
        Formate le résultat pour un affichage clair
        """
        output_lines = []
        
        # Emoji selon la priorité
        priority_emojis = {
            "HIGH": "🔴",
            "MEDIUM": "🟡",
            "LOW": "🟢"
        }
        
        emoji = priority_emojis.get(result["priority"], "⚪")
        
        output_lines.append(f"{emoji} Priority: {result['priority']}")
        output_lines.append(f"Confidence: {result['confidence']}%")
        output_lines.append(f"  Response Time: {result['response_time']}")
        
        
        
        return "\n".join(output_lines)