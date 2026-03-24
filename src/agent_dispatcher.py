import re

from src.llm_copilot import load_text_file
from src.scenario_manager import run_capacity_scenario


def detect_intent(user_query: str) -> str:
    q = user_query.lower()

    if any(keyword in q for keyword in ["summary", "summarize", "dispatch summary"]):
        return "summary"

    if any(keyword in q for keyword in ["compare", "improvement", "difference"]):
        return "compare"

    if any(keyword in q for keyword in ["replan", "rerun", "capacity"]):
        return "replan"

    return "unknown"


def extract_capacity(user_query: str):
    match = re.search(r"(\d+)", user_query)
    if match:
        return int(match.group(1))
    return None


def dispatch_agent(
    user_query: str,
    comparison_summary_path: str,
    llm_analysis_path: str,
    depot_df=None,
    nodes_df=None,
    node_dict=None,
    distance_matrix=None,
    fixed_vehicle_cost=None,
    cost_per_distance_unit=None,
    depot_id=None
) -> str:
    intent = detect_intent(user_query)

    if intent == "summary":
        return load_text_file(llm_analysis_path)

    if intent == "compare":
        return load_text_file(comparison_summary_path)

    if intent == "replan":
        new_capacity = extract_capacity(user_query)
        if new_capacity is None:
            return "Capacity value not found in the request."

        scenario_result = run_capacity_scenario(
            depot_df=depot_df,
            nodes_df=nodes_df,
            node_dict=node_dict,
            distance_matrix=distance_matrix,
            vehicle_capacity=new_capacity,
            fixed_vehicle_cost=fixed_vehicle_cost,
            cost_per_distance_unit=cost_per_distance_unit,
            depot_id=depot_id
        )

        return (
            f"Scenario rerun completed with vehicle capacity = {new_capacity}.\n\n"
            f"{scenario_result['summary_text']}"
        )

    return "Intent not recognized. Supported intents: summary, compare, replan."