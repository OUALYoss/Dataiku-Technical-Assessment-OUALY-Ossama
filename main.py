from dotenv import load_dotenv
load_dotenv()

from src.agent.react_agent import ITSupportReActAgent
from src.data.sample_tickets import SAMPLE_TICKETS

def main():
    print("""
    ********************************************************
    *      IT SUPPORT ADVISOR - ReAct Agent              *
    ********************************************************
    """)

    
    print("_" * 60)
    agent_verbose = ITSupportReActAgent(verbose=False)
    result = agent_verbose.analyze_ticket(SAMPLE_TICKETS[-1])  
    
    
    print("\n Analysis completed successfully!")
    print(f"Total reasoning steps: {result['total_steps']}")

if __name__ == "__main__":
    main()