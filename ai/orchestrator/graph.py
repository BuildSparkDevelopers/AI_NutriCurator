from langgraph.graph import StateGraph, START, END

# Import the standardized state schema
from ai.state.schema import overallState

# Import Agents
from ai.orchestrator.policy import RouterLogic
from ai.agents.user_agent_node import ProfileRetrieval
from ai.agents.chat_core_agent import EvidenceGeneration
from ai.agents.reco_agent import Recommendation
from ai.agents.sub_reco_agent import SubstitutionReco
from ai.agents.composer_agent import ResponseGeneration

orchagent = RouterLogic()


def orch_node(state: dict) -> dict:
    next_step = orchagent.run(state)
    return {"next_step": next_step}

def create_workflow(*, products_db: dict, final_profiles: dict | None = None) -> StateGraph:
    workflow = StateGraph(overallState)
    final_profiles = final_profiles or {}

    # Nodes with runtime-injected data source
    useragent = ProfileRetrieval(model=None)
    chatagent = EvidenceGeneration(
        model=None,
        tokenizer=None,
        final_profiles=final_profiles,
        products=products_db,
    )
    recoagent = Recommendation(products_db=products_db)
    subsagent = SubstitutionReco(products_db=products_db, final_profiles=final_profiles)
    respagent = ResponseGeneration()

    # 1. Add Nodes
    workflow.add_node("orch_agent", orch_node)
    workflow.add_node("user_agent", useragent.run)
    workflow.add_node("chat_agent", chatagent.evaluate_threshold)
    workflow.add_node("reco_agent", recoagent.run)
    workflow.add_node("sub_reco_agent", subsagent.run)
    workflow.add_node("resp_agent", respagent.run)

    # 2. Add Normal Edges
    workflow.add_edge(START, "orch_agent")
    workflow.add_edge("user_agent", "orch_agent")
    workflow.add_edge("chat_agent", "orch_agent")
    workflow.add_edge("reco_agent", "sub_reco_agent")
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
    workflow.add_edge("resp_agent", END)

    return workflow

# For standalone execution / testing
def compile_graph(*, products_db: dict, final_profiles: dict | None = None):
    workflow = create_workflow(products_db=products_db, final_profiles=final_profiles)
    return workflow.compile()

if __name__ == "__main__":
    app = compile_graph(products_db={})
    print("LangGraph Compiled Successfully!")
