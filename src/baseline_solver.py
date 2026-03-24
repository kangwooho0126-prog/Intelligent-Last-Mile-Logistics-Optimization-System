import json
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from src.distance_utils import compute_route_distance


def solve_baseline_greedy(
    depot_df: pd.DataFrame,
    nodes_df: pd.DataFrame,
    distance_matrix: dict,
    vehicle_capacity: int,
) -> list:
    depot_id = int(depot_df.iloc[0]["node_id"])

    remaining_nodes = set(nodes_df["node_id"].astype(int).tolist())
    demand_map = {
        int(row["node_id"]): int(row["parcel_demand"])
        for _, row in nodes_df.iterrows()
    }

    routes = []

    while remaining_nodes:
        current_route = [depot_id]
        current_node = depot_id
        remaining_capacity = vehicle_capacity
        current_load = 0

        while True:
            feasible_nodes = [
                node_id
                for node_id in remaining_nodes
                if demand_map[node_id] <= remaining_capacity
            ]

            if not feasible_nodes:
                break

            next_node = min(
                feasible_nodes,
                key=lambda node_id: distance_matrix[current_node][node_id]
            )

            current_route.append(next_node)
            remaining_nodes.remove(next_node)

            node_demand = demand_map[next_node]
            remaining_capacity -= node_demand
            current_load += node_demand
            current_node = next_node

        current_route.append(depot_id)

        routes.append({
            "vehicle_id": len(routes) + 1,
            "route": current_route,
            "load": current_load
        })

    return routes


def summarize_baseline_routes(routes: list, distance_matrix: dict) -> pd.DataFrame:
    rows = []

    for route_info in routes:
        route = route_info["route"]
        route_distance = compute_route_distance(route, distance_matrix)

        rows.append({
            "vehicle_id": route_info["vehicle_id"],
            "route": " -> ".join(map(str, route)),
            "num_stops": len(route) - 2,
            "load": route_info["load"],
            "distance": round(route_distance, 4)
        })

    return pd.DataFrame(rows)


def save_route_plan_json(routes: list, save_path: str) -> None:
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(routes, f, indent=4, ensure_ascii=False)


def plot_baseline_routes(
    depot_df: pd.DataFrame,
    nodes_df: pd.DataFrame,
    routes: list,
    node_dict: dict,
    save_path: str
) -> None:
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(9, 7))

    plt.scatter(
        nodes_df["x"],
        nodes_df["y"],
        s=60,
        label="service_points"
    )

    plt.scatter(
        depot_df["x"],
        depot_df["y"],
        s=180,
        marker="s",
        label="distribution_center"
    )

    for _, row in nodes_df.iterrows():
        plt.text(
            row["x"] + 0.3,
            row["y"] + 0.3,
            str(int(row["node_id"])),
            fontsize=8
        )

    depot_row = depot_df.iloc[0]
    plt.text(
        depot_row["x"] + 0.3,
        depot_row["y"] + 0.3,
        "Depot",
        fontsize=10
    )

    for route_info in routes:
        route = route_info["route"]
        x_coords = [node_dict[node_id]["x"] for node_id in route]
        y_coords = [node_dict[node_id]["y"] for node_id in route]
        plt.plot(x_coords, y_coords, linewidth=1.5, alpha=0.9)

    plt.title("Baseline Greedy Routing")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()