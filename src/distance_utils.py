import math
import pandas as pd


def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.hypot(x1 - x2, y1 - y2)


def build_node_dict(depot_df: pd.DataFrame, nodes_df: pd.DataFrame) -> dict:
    node_dict = {}

    depot_row = depot_df.iloc[0]
    node_dict[int(depot_row["node_id"])] = {
        "x": float(depot_row["x"]),
        "y": float(depot_row["y"]),
        "demand": 0,
        "node_type": depot_row["node_type"],
        "node_name": depot_row["node_name"],
    }

    for _, row in nodes_df.iterrows():
        node_id = int(row["node_id"])
        node_dict[node_id] = {
            "x": float(row["x"]),
            "y": float(row["y"]),
            "demand": int(row["parcel_demand"]),
            "node_type": row["node_type"],
            "node_name": row["node_name"],
        }

    return node_dict


def build_distance_matrix(node_dict: dict) -> dict:
    node_ids = sorted(node_dict.keys())
    distance_matrix = {i: {} for i in node_ids}

    for i in node_ids:
        for j in node_ids:
            xi, yi = node_dict[i]["x"], node_dict[i]["y"]
            xj, yj = node_dict[j]["x"], node_dict[j]["y"]
            distance_matrix[i][j] = euclidean_distance(xi, yi, xj, yj)

    return distance_matrix


def compute_route_distance(route: list, distance_matrix: dict) -> float:
    distance = 0.0
    for i in range(len(route) - 1):
        distance += distance_matrix[route[i]][route[i + 1]]
    return distance