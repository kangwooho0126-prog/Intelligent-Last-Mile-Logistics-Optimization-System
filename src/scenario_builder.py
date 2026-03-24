import pandas as pd
from pathlib import Path


def assign_station_type(node_id: int) -> str:
    station_types = [
        "parcel_station",
        "pickup_locker",
        "partner_store"
    ]
    return station_types[node_id % len(station_types)]


def build_logistics_tables(parsed_data: dict):
    depot_id = parsed_data["depot_id"]
    coordinates = parsed_data["coordinates"]
    demands = parsed_data["demands"]

    depot_x, depot_y = coordinates[depot_id]

    depot_df = pd.DataFrame([
        {
            "node_id": depot_id,
            "node_name": "Regional Distribution Center",
            "node_type": "distribution_center",
            "x": depot_x,
            "y": depot_y
        }
    ])

    node_rows = []
    for node_id, (x, y) in coordinates.items():
        if node_id == depot_id:
            continue

        node_rows.append({
            "node_id": node_id,
            "node_name": f"Service Point {node_id}",
            "node_type": assign_station_type(node_id),
            "x": x,
            "y": y,
            "parcel_demand": demands.get(node_id, 0)
        })

    nodes_df = pd.DataFrame(node_rows).sort_values("node_id").reset_index(drop=True)

    return depot_df, nodes_df


def save_tables(depot_df, nodes_df, depot_path: str, nodes_path: str) -> None:
    Path(depot_path).parent.mkdir(parents=True, exist_ok=True)
    depot_df.to_csv(depot_path, index=False)
    nodes_df.to_csv(nodes_path, index=False)