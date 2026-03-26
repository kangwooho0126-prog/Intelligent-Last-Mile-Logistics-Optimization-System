from src.config import (
    RAW_VRP_FILE,
    DEPOT_CSV,
    NODES_CSV,
    META_JSON,
    NODE_MAP_PNG,
    BASELINE_ROUTE_PNG,
    BASELINE_ROUTE_PLAN_JSON,
    BASELINE_ROUTE_SUMMARY_CSV,
    BASELINE_METRICS_JSON,
    BASELINE_METRICS_CSV,
    ORTOOLS_ROUTE_PLAN_JSON,
    ORTOOLS_ROUTE_SUMMARY_CSV,
    ORTOOLS_METRICS_JSON,
    ORTOOLS_METRICS_CSV,
    ORTOOLS_ROUTE_PNG,
    COMPARISON_METRICS_CSV,
    COMPARISON_SUMMARY_TXT,
    DISTANCE_COMPARISON_PNG,
    COST_COMPARISON_PNG,
    UTILIZATION_COMPARISON_PNG,
    LLM_ANALYSIS_TXT,
    AGENT_RESPONSE_TXT,
    FIXED_VEHICLE_COST,
    COST_PER_DISTANCE_UNIT,
    LLM_MODE,
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL_NAME,
    ensure_directories
)

from src.data_loader import parse_cvrp_file, save_meta_json
from src.scenario_builder import build_logistics_tables, save_tables
from src.visualization import plot_node_map
from src.distance_utils import build_node_dict, build_distance_matrix
from src.baseline_solver import (
    solve_baseline_greedy,
    summarize_baseline_routes,
    save_route_plan_json,
    plot_baseline_routes
)
from src.evaluator import (
    evaluate_solution,
    save_metrics_json,
    save_route_summary_csv,
    save_metrics_csv
)
from src.ortools_solver import solve_cvrp_ortools
from src.experiment_analysis import (
    build_comparison_table,
    save_comparison_table,
    plot_metric_comparison,
    generate_comparison_summary,
    save_summary_text
)
from src.llm_copilot import (
    generate_dispatch_analysis,
    save_analysis_text
)
from src.agent_dispatcher import dispatch_agent

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    ensure_directories()

    logging.info("Loading data...")
    parsed_data = parse_cvrp_file(str(RAW_VRP_FILE))

    meta_info = {
        "instance_name": parsed_data["name"],
        "vehicle_capacity": parsed_data["capacity"],
        "dimension": parsed_data["dimension"],
        "depot_id": parsed_data["depot_id"],
        "num_service_points": parsed_data["dimension"] - 1
    }
    save_meta_json(meta_info, str(META_JSON))

    depot_df, nodes_df = build_logistics_tables(parsed_data)

    save_tables(
        depot_df=depot_df,
        nodes_df=nodes_df,
        depot_path=str(DEPOT_CSV),
        nodes_path=str(NODES_CSV)
    )

    plot_node_map(depot_df, nodes_df, str(NODE_MAP_PNG))

    node_dict = build_node_dict(depot_df, nodes_df)
    distance_matrix = build_distance_matrix(node_dict)

    logging.info("Running baseline solver...")
    baseline_routes = solve_baseline_greedy(
        depot_df=depot_df,
        nodes_df=nodes_df,
        distance_matrix=distance_matrix,
        vehicle_capacity=parsed_data["capacity"]
    )

    baseline_summary_df = summarize_baseline_routes(baseline_routes, distance_matrix)

    baseline_metrics = evaluate_solution(
        route_summary_df=baseline_summary_df,
        vehicle_capacity=parsed_data["capacity"],
        fixed_vehicle_cost=FIXED_VEHICLE_COST,
        cost_per_distance_unit=COST_PER_DISTANCE_UNIT
    )

    save_route_plan_json(baseline_routes, str(BASELINE_ROUTE_PLAN_JSON))
    save_route_summary_csv(baseline_summary_df, str(BASELINE_ROUTE_SUMMARY_CSV))
    save_metrics_json(baseline_metrics, str(BASELINE_METRICS_JSON))
    save_metrics_csv(baseline_metrics, str(BASELINE_METRICS_CSV))

    plot_baseline_routes(
        depot_df=depot_df,
        nodes_df=nodes_df,
        routes=baseline_routes,
        node_dict=node_dict,
        save_path=str(BASELINE_ROUTE_PNG)
    )

    logging.info("Running OR-Tools solver...")
    ortools_routes = solve_cvrp_ortools(
        node_dict=node_dict,
        distance_matrix=distance_matrix,
        vehicle_capacity=parsed_data["capacity"],
        depot_id=parsed_data["depot_id"]
    )

    ortools_summary_df = summarize_baseline_routes(ortools_routes, distance_matrix)

    ortools_metrics = evaluate_solution(
        route_summary_df=ortools_summary_df,
        vehicle_capacity=parsed_data["capacity"],
        fixed_vehicle_cost=FIXED_VEHICLE_COST,
        cost_per_distance_unit=COST_PER_DISTANCE_UNIT
    )

    save_route_plan_json(ortools_routes, str(ORTOOLS_ROUTE_PLAN_JSON))
    save_route_summary_csv(ortools_summary_df, str(ORTOOLS_ROUTE_SUMMARY_CSV))
    save_metrics_json(ortools_metrics, str(ORTOOLS_METRICS_JSON))
    save_metrics_csv(ortools_metrics, str(ORTOOLS_METRICS_CSV))

    plot_baseline_routes(
        depot_df=depot_df,
        nodes_df=nodes_df,
        routes=ortools_routes,
        node_dict=node_dict,
        save_path=str(ORTOOLS_ROUTE_PNG)
    )

    logging.info("Running experiment analysis...")
    comparison_df = build_comparison_table(
        baseline_metrics_path=str(BASELINE_METRICS_CSV),
        ortools_metrics_path=str(ORTOOLS_METRICS_CSV)
    )

    save_comparison_table(comparison_df, str(COMPARISON_METRICS_CSV))

    plot_metric_comparison(
        comparison_df,
        "total_distance",
        "Total Distance Comparison",
        "Distance",
        str(DISTANCE_COMPARISON_PNG)
    )

    plot_metric_comparison(
        comparison_df,
        "total_cost",
        "Total Cost Comparison",
        "Cost",
        str(COST_COMPARISON_PNG)
    )

    plot_metric_comparison(
        comparison_df,
        "avg_load_utilization",
        "Load Utilization Comparison",
        "Utilization",
        str(UTILIZATION_COMPARISON_PNG)
    )

    summary_text = generate_comparison_summary(comparison_df)
    save_summary_text(summary_text, str(COMPARISON_SUMMARY_TXT))

    logging.info("Generating LLM analysis...")
    llm_analysis = generate_dispatch_analysis(
        str(COMPARISON_SUMMARY_TXT),
        LLM_MODE,
        LLM_API_KEY,
        LLM_BASE_URL,
        LLM_MODEL_NAME
    )
    save_analysis_text(llm_analysis, str(LLM_ANALYSIS_TXT))

    logging.info("Running agent...")
    user_query = input("Enter your query (e.g., 'replan with capacity 120'): ")

    agent_response = dispatch_agent(
        user_query=user_query,
        comparison_summary_path=str(COMPARISON_SUMMARY_TXT),
        llm_analysis_path=str(LLM_ANALYSIS_TXT),
        depot_df=depot_df,
        nodes_df=nodes_df,
        node_dict=node_dict,
        distance_matrix=distance_matrix,
        fixed_vehicle_cost=FIXED_VEHICLE_COST,
        cost_per_distance_unit=COST_PER_DISTANCE_UNIT,
        depot_id=parsed_data["depot_id"]
    )

    with open(str(AGENT_RESPONSE_TXT), "w", encoding="utf-8") as f:
        f.write(agent_response)

    print("\n=== Agent Response ===\n")
    print(agent_response)


if __name__ == "__main__":
    main()