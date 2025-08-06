from langgraph.graph import StateGraph, END
from langchain_core.tools import Tool
from tools.segment_insight_tool import segment_insight
from tools.performance_analysis_tool import performance_analysis
from agents.strategy_generator_agent import generate_strategy
from typing import TypedDict

class FlowState(TypedDict):
    query: str
    segment_insight: str
    performance_analysis: str
    strategy_generator: str

workflow = StateGraph(FlowState)

def segment_node_func(state):
    result = segment_insight.invoke({"query": state["query"]})
    if isinstance(result, dict):
        segment_data = result.get("segment_insight", result.get("segment_json", "[]"))
    else:
        segment_data = result

    print("\n🎯 Matched Campaign Segment:")
    print(segment_data)
    return {"segment_insight": segment_data}

def performance_node_func(state):
    result = performance_analysis.invoke({
        "query": state["query"],
        "segment_json": state["segment_insight"]
    })

    if isinstance(result, dict):
        performance_data = result.get("roi_summary", str(result))
    else:
        performance_data = result
    return {"performance_analysis": performance_data}

def strategy_node_func(state):
    
    print("\n📈 Performance Analysis:")
    print(state["performance_analysis"])

    result = generate_strategy(
        query=state["query"],
        performance_analysis=state["performance_analysis"]
    )

    return {"strategy_generator": result}

workflow.add_node("segment_insight", segment_node_func)
workflow.add_node("performance_analysis", performance_node_func)
workflow.add_node("strategy_generator", strategy_node_func)

workflow.set_entry_point("segment_insight")
workflow.add_edge("segment_insight", "performance_analysis")
workflow.add_edge("performance_analysis", "strategy_generator")
workflow.set_finish_point("strategy_generator")

graph_app = workflow.compile()