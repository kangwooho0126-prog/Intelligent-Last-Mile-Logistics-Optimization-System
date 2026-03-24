from src.baseline_solver import solve_baseline_greedy, summarize_baseline_routes
from src.ortools_solver import solve_cvrp_ortools
from src.evaluator import evaluate_solution
from src.experiment_analysis import generate_comparison_summary


def run_capacity_scenario(
    depot_df,
    nodes_df,
    node_dict,
    distance_matrix,
    vehicle_capacity,
    fixed_vehicle_cost,
    cost_per_distance_unit,
    depot_id
):
    baseline_routes = solve_baseline_greedy(
        depot_df=depot_df,
        nodes_df=nodes_df,
        distance_matrix=distance_matrix,
        vehicle_capacity=vehicle_capacity
    )
    baseline_summary_df = summarize_baseline_routes(baseline_routes, distance_matrix)
    baseline_metrics = evaluate_solution(
        route_summary_df=baseline_summary_df,
        vehicle_capacity=vehicle_capacity,
        fixed_vehicle_cost=fixed_vehicle_cost,
        cost_per_distance_unit=cost_per_distance_unit
    )

    ortools_routes = solve_cvrp_ortools(
        node_dict=node_dict,
        distance_matrix=distance_matrix,
        vehicle_capacity=vehicle_capacity,
        depot_id=depot_id
    )
    ortools_summary_df = summarize_baseline_routes(ortools_routes, distance_matrix)
    ortools_metrics = evaluate_solution(
        route_summary_df=ortools_summary_df,
        vehicle_capacity=vehicle_capacity,
        fixed_vehicle_cost=fixed_vehicle_cost,
        cost_per_distance_unit=cost_per_distance_unit
    )

    comparison_df = baseline_summary_df.iloc[:0].copy()  # placeholder not used

    comparison_like_df = None

    import pandas as pd
    comparison_like_df = pd.DataFrame([
        {"method": "baseline", **baseline_metrics},
        {"method": "ortools", **ortools_metrics},
    ])

    summary_text = generate_comparison_summary(comparison_like_df)

    return {
        "baseline_metrics": baseline_metrics,
        "ortools_metrics": ortools_metrics,
        "summary_text": summary_text
    }