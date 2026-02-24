from langgraph.graph import StateGraph, START, END

# Import the standardized state schema
from ai.state.schema import overallState

# Import Agents
from ai.orchestrator.policy import RouterLogic
from ai.agents.user_agent import ProfileRetrieval
from ai.agents.chat_core_agent import EvidenceGeneration
from ai.agents.reco_agent import Recommendation
from ai.agents.sub_reco_agent import SubstitutionReco
from ai.agents.composer_agent import ResponseGeneration

# Instantiate agents
# Note: For production, you may need to pass actual LLM objects to these initializations.
# Following the structure from langgrapharchitecture.py, these should receive their respective models.
# Since this file serves as the graph definition, ensure models are initialized either here or passed via a config.
orchagent = RouterLogic()

# Assuming models are passed or initialized inside the classes for this generic setup
# In a real app/main.py, you would inject the llm instances here.
useragent = ProfileRetrieval(model=None)  
chatagent = EvidenceGeneration(model=None, tokenizer=None)
recoagent = Recommendation() # Assuming defaults
subsagent = SubstitutionReco() # Assuming defaults
respagent = ResponseGeneration() # Assuming defaults

def create_workflow() -> StateGraph:
    workflow = StateGraph(overallState)

    # 1. Add Nodes
    workflow.add_node("orch_agent", orchagent.run)
    workflow.add_node("user_agent", useragent.run)
    workflow.add_node("chat_agent", chatagent.evaluate_threshold)
    workflow.add_node("reco_agent", recoagent.run if hasattr(recoagent, 'run') else lambda state: state)
    workflow.add_node("sub_reco_agent", subsagent.run if hasattr(subsagent, 'run') else lambda state: state)
    workflow.add_node("resp_agent", respagent.run if hasattr(respagent, 'run') else lambda state: state)

    # 2. Add Normal Edges
    workflow.add_edge(START, "orch_agent")
    workflow.add_edge("orch_agent", "user_agent")
    workflow.add_edge("user_agent", "orch_agent")
    
    workflow.add_edge("orch_agent", "chat_agent")
    workflow.add_edge("chat_agent", "orch_agent")
    
    workflow.add_edge("chat_agent", "reco_agent")
    
    workflow.add_edge("orch_agent", "reco_agent")
    workflow.add_edge("reco_agent", "sub_reco_agent")
    workflow.add_edge("sub_reco_agent", "reco_agent")
    workflow.add_edge("sub_reco_agent", "resp_agent")

    # 3. Add Conditional Edges from Router
    workflow.add_conditional_edges(
        "orch_agent",
        lambda x: x.get("next_step", "end"),
        {
            "user_agent": "user_agent",
            "chat_agent": "chat_agent",
            "reco_agent": "reco_agent",
            "sub_reco_agent": "sub_reco_agent",
            "resp_agent": "resp_agent",
            "end": END
        }
    )

    # 4. Explicit Ends
    workflow.add_edge("orch_agent", END)
    workflow.add_edge("resp_agent", END)

    return workflow

# For standalone execution / testing
def compile_graph():
    workflow = create_workflow()
    return workflow.compile()

if __name__ == "__main__":
    app = compile_graph()
    print("LangGraph Compiled Successfully!")
