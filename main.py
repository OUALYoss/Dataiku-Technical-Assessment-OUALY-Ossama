from dotenv import load_dotenv
load_dotenv()

from src.agent.react_agent import ITSupportReActAgent
from src.data.sample_tickets import SAMPLE_TICKETS

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     🤖 IT SUPPORT ADVISOR - ReAct Agent                 ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Test 1: Mode silencieux
    print("\n1️⃣ TEST SILENCIEUX (verbose=False)")
    print("-" * 60)
    agent_silent = ITSupportReActAgent(verbose=False)
    result = agent_silent.analyze_ticket(SAMPLE_TICKETS[-1])
    
    print(f"✅ Analysis complete!")
    print(f"   Category: {result['recommendation'].get('category')}")
    print(f"   Priority: {result['recommendation'].get('priority')}")
    print(f"   Steps taken: {result['total_steps']}")
    
    # Test 2: Mode verbose (affiche automatiquement tout)
    print("\n\n2️⃣ TEST AVEC AFFICHAGE DÉTAILLÉ (verbose=True)")
    print("-" * 60)
    agent_verbose = ITSupportReActAgent(verbose=True)
    result = agent_verbose.analyze_ticket(SAMPLE_TICKETS[-1])  # Ticket WiFi
    
    # ✅ PAS besoin d'afficher à nouveau, verbose=True le fait déjà !
    # Juste un résumé final si tu veux
    print("\n✅ Analysis completed successfully!")
    print(f"Total reasoning steps: {result['total_steps']}")

if __name__ == "__main__":
    main()