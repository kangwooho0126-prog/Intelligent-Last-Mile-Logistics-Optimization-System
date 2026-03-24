import json
from pathlib import Path

import pandas as pd


def evaluate_solution(
    route_summary_df: pd.DataFrame,
    vehicle_capacity: int,
    fixed_vehicle_cost: float,
    cost_per_distance_unit: float
) -> dict:
    vehicles_used = int(route_summary_df["vehicle_id"].nunique())
    total_distance = float(route_summary_df["distance"].sum())
    total_load = float(route_summary_df["load"].sum())

    total_cost = vehicles_used * fixed_vehicle_cost + total_distance * cost_per_distance_unit
    avg_load_utilization = 0.0
    if vehicles_used > 0 and vehicle_capacity > 0:
        avg_load_utilization = total_load / (vehicles_used * vehicle_capacity)

    cost_per_parcel = 0.0
    if total_load > 0:
        cost_per_parcel = total_cost / total_load

    metrics = {
        "vehicles_used": vehicles_used,
        "total_distance": round(total_distance, 4),
        "total_load": round(total_load, 4),
        "total_cost": round(total_cost, 4),
        "avg_load_utilization": round(avg_load_utilization, 4),
        "cost_per_parcel": round(cost_per_parcel, 4)
    }

    return metrics


def save_metrics_json(metrics: dict, save_path: str) -> None:
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4, ensure_ascii=False)


def save_route_summary_csv(route_summary_df: pd.DataFrame, save_path: str) -> None:
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    route_summary_df.to_csv(save_path, index=False)


def save_metrics_csv(metrics: dict, save_path: str) -> None:
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(save_path, index=False)