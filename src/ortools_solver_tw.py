from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.dist((x1, y1), (x2, y2))


def load_instance_data(instance_name: str, scenario_name: str = "medium") -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    base_dir = PROJECT_ROOT / "data" / "processed" / instance_name

    depot_path = base_dir / "depot.csv"
    nodes_path = base_dir / f"nodes_tw_{scenario_name}.csv"
    meta_path = base_dir / "meta.json"

    if not depot_path.exists():
        raise FileNotFoundError(f"Depot file not found: {depot_path}")
    if not nodes_path.exists():
        raise FileNotFoundError(f"Time-window node file not found: {nodes_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Meta file not found: {meta_path}")

    depot_df = pd.read_csv(depot_path)
    nodes_df = pd.read_csv(nodes_path)

    meta = pd.read_json(meta_path, typ="series").to_dict()

    return depot_df, nodes_df, meta


def build_combined_dataframe(depot_df: pd.DataFrame, nodes_df: pd.DataFrame) -> pd.DataFrame:
    depot_row = depot_df.iloc[0].to_dict()
    depot_row["distance_to_depot"] = 0.0
    depot_row["service_time"] = 0
    depot_row["ready_time"] = 0
    depot_row["due_time"] = 480

    all_rows = [depot_row] + nodes_df.to_dict(orient="records")
    df = pd.DataFrame(all_rows).reset_index(drop=True)

    return df


def build_distance_matrix(df: pd.DataFrame) -> List[List[int]]:
    coords = list(zip(df["x"], df["y"]))
    n = len(coords)

    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            dist = euclidean_distance(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
            row.append(int(round(dist)))
        matrix.append(row)

    return matrix


def build_time_matrix(df: pd.DataFrame) -> List[List[int]]:
    """
    Travel time matrix.
    Here we use rounded Euclidean distance as travel time.
    """
    return build_distance_matrix(df)


def create_data_model(instance_name: str, scenario_name: str = "medium") -> Dict:
    depot_df, nodes_df, meta = load_instance_data(instance_name, scenario_name)
    df = build_combined_dataframe(depot_df, nodes_df)

    vehicle_capacity = int(meta["vehicle_capacity"])
    depot_time_window = meta.get("depot_time_window", [0, 480])

    total_demand = int(df["demand"].sum())
    min_vehicles = math.ceil(total_demand / vehicle_capacity)
    num_vehicles = min_vehicles + 2

    data = {
        "instance_name": instance_name,
        "scenario_name": scenario_name,
        "df": df,
        "distance_matrix": build_distance_matrix(df),
        "time_matrix": build_time_matrix(df),
        "demands": df["demand"].astype(int).tolist(),
        "vehicle_capacities": [vehicle_capacity] * num_vehicles,
        "num_vehicles": num_vehicles,
        "depot": 0,
        "service_times": df["service_time"].astype(int).tolist(),
        "time_windows": list(zip(df["ready_time"].astype(int), df["due_time"].astype(int))),
        "depot_time_window": tuple(depot_time_window),
    }

    return data


def solve_cvrptw(instance_name: str, scenario_name: str = "medium", time_limit_sec: int = 10) -> Dict:
    data = create_data_model(instance_name, scenario_name)

    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]),
        data["num_vehicles"],
        data["depot"],
    )

    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        return data["demands"][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        data["vehicle_capacities"],
        True,
        "Capacity",
    )

    def time_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        travel_time = data["time_matrix"][from_node][to_node]
        service_time = data["service_times"][from_node]

        return travel_time + service_time

    time_callback_index = routing.RegisterTransitCallback(time_callback)

    routing.AddDimension(
        time_callback_index,
        120,   # waiting time slack
        480,   # max route duration
        False, # do not force start cumul to zero
        "Time",
    )

    time_dimension = routing.GetDimensionOrDie("Time")

    for node_idx, (ready_time, due_time) in enumerate(data["time_windows"]):
        index = manager.NodeToIndex(node_idx)
        time_dimension.CumulVar(index).SetRange(ready_time, due_time)

    depot_start, depot_end = data["depot_time_window"]
    for vehicle_id in range(data["num_vehicles"]):
        start_index = routing.Start(vehicle_id)
        end_index = routing.End(vehicle_id)
        time_dimension.CumulVar(start_index).SetRange(depot_start, depot_end)
        time_dimension.CumulVar(end_index).SetRange(depot_start, depot_end)

    for i in range(data["num_vehicles"]):
        routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(i)))

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.seconds = time_limit_sec

    start_time = time.time()
    solution = routing.SolveWithParameters(search_parameters)
    runtime_sec = time.time() - start_time

    if solution is None:
        return {
            "status": "NO_SOLUTION",
            "instance_name": instance_name,
            "scenario_name": scenario_name,
            "runtime_sec": round(runtime_sec, 4),
        }

    routes = []
    total_distance = 0
    total_load = 0
    used_vehicles = 0

    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)

        if routing.IsEnd(solution.Value(routing.NextVar(index))):
            continue

        used_vehicles += 1
        route_nodes = []
        route_distance = 0

        while not routing.IsEnd(index):
            node_id = manager.IndexToNode(index)
            time_var = time_dimension.CumulVar(index)
            arrival_time = solution.Value(time_var)

            route_nodes.append(
                {
                    "solver_node_index": node_id,
                    "original_node_id": int(data["df"].iloc[node_id]["node_id"]),
                    "arrival_time": int(arrival_time),
                    "demand": int(data["df"].iloc[node_id]["demand"]),
                }
            )

            previous_index = index
            next_index = solution.Value(routing.NextVar(index))

            from_node = manager.IndexToNode(previous_index)

            if routing.IsEnd(next_index):
                to_node = data["depot"]
            else:
                to_node = manager.IndexToNode(next_index)

            route_distance += data["distance_matrix"][from_node][to_node]
            index = next_index

        end_node = manager.IndexToNode(index)
        end_time = solution.Value(time_dimension.CumulVar(index))
        route_nodes.append(
            {
                "solver_node_index": end_node,
                "original_node_id": int(data["df"].iloc[end_node]["node_id"]),
                "arrival_time": int(end_time),
                "demand": 0,
            }
        )

        route_load = sum(stop["demand"] for stop in route_nodes)
        total_distance += route_distance
        total_load += route_load

        routes.append(
            {
                "vehicle_id": vehicle_id,
                "route_distance": route_distance,
                "route_load": route_load,
                "stops": route_nodes,
            }
        )

    result = {
        "status": "SOLVED",
        "instance_name": instance_name,
        "scenario_name": scenario_name,
        "runtime_sec": round(runtime_sec, 4),
        "num_vehicles_available": data["num_vehicles"],
        "vehicles_used": used_vehicles,
        "total_distance": total_distance,
        "total_load": total_load,
        "routes": routes,
    }

    return result


def print_solution_summary(result: Dict) -> None:
    print("=" * 80)
    print(f"Instance: {result['instance_name']}")
    print(f"Scenario: {result['scenario_name']}")
    print(f"Status: {result['status']}")
    print(f"Runtime (sec): {result['runtime_sec']}")

    if result["status"] != "SOLVED":
        print("=" * 80)
        return

    print(f"Vehicles used: {result['vehicles_used']}")
    print(f"Total distance: {result['total_distance']}")
    print(f"Total load: {result['total_load']}")
    print("-" * 80)

    for route in result["routes"]:
        print(f"Vehicle {route['vehicle_id']}")
        print(f"  Route distance: {route['route_distance']}")
        print(f"  Route load: {route['route_load']}")
        print("  Stops:")

        for stop in route["stops"]:
            print(
                f"    node={stop['original_node_id']}, "
                f"arrival={stop['arrival_time']}, "
                f"demand={stop['demand']}"
            )
        print("-" * 80)

    print("=" * 80)


def save_solution_result(result: Dict) -> None:
    result_dir = (
        PROJECT_ROOT
        / "results"
        / result["instance_name"]
        / f"cvrptw_{result['scenario_name']}"
    )
    result_dir.mkdir(parents=True, exist_ok=True)

    solution_path = result_dir / "solution.json"

    with open(solution_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved solution: {solution_path}")


def save_metrics_csv(result: Dict) -> None:
    result_dir = (
        PROJECT_ROOT
        / "results"
        / result["instance_name"]
        / f"cvrptw_{result['scenario_name']}"
    )
    result_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = result_dir / "metrics.csv"

    metrics_df = pd.DataFrame(
        [
            {
                "instance_name": result["instance_name"],
                "scenario_name": result["scenario_name"],
                "status": result["status"],
                "runtime_sec": result["runtime_sec"],
                "vehicles_used": result.get("vehicles_used"),
                "total_distance": result.get("total_distance"),
                "total_load": result.get("total_load"),
            }
        ]
    )

    metrics_df.to_csv(metrics_path, index=False)
    print(f"Saved metrics: {metrics_path}")


if __name__ == "__main__":
    result = solve_cvrptw(
        instance_name="A-n32-k5",
        scenario_name="medium",
        time_limit_sec=10,
    )
    print_solution_summary(result)
    save_solution_result(result)
    save_metrics_csv(result)