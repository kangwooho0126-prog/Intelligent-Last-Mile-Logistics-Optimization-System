from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.ortools_solver_tw import (
    PROJECT_ROOT,
    solve_cvrptw,
    save_solution_result,
    save_metrics_csv,
)


PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SUMMARY_DIR = PROJECT_ROOT / "results" / "summary"


def get_instance_names() -> List[str]:
    if not PROCESSED_DIR.exists():
        raise FileNotFoundError(f"Processed directory not found: {PROCESSED_DIR}")

    instance_names = sorted([p.name for p in PROCESSED_DIR.iterdir() if p.is_dir()])
    return instance_names


def load_instance_meta(instance_name: str) -> Dict:
    meta_path = PROCESSED_DIR / instance_name / "meta.json"
    if not meta_path.exists():
        return {}

    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_summary_row(result: Dict) -> Dict:
    instance_name = result.get("instance_name")
    meta = load_instance_meta(instance_name)

    vehicle_capacity = meta.get("vehicle_capacity")
    num_customers = meta.get("num_customers")
    total_distance = result.get("total_distance")
    total_load = result.get("total_load")
    vehicles_used = result.get("vehicles_used")

    avg_distance_per_vehicle = None
    if vehicles_used not in (None, 0) and total_distance is not None:
        avg_distance_per_vehicle = round(total_distance / vehicles_used, 4)

    avg_load_utilization = None
    if (
        vehicles_used not in (None, 0)
        and vehicle_capacity not in (None, 0)
        and total_load is not None
    ):
        avg_load_utilization = round(
            total_load / (vehicles_used * vehicle_capacity),
            4,
        )

    distance_per_customer = None
    if num_customers not in (None, 0) and total_distance is not None:
        distance_per_customer = round(total_distance / num_customers, 4)

    row = {
        "instance_name": instance_name,
        "scenario_name": result.get("scenario_name"),
        "status": result.get("status"),
        "runtime_sec": result.get("runtime_sec"),
        "vehicle_capacity": vehicle_capacity,
        "num_customers": num_customers,
        "num_vehicles_available": result.get("num_vehicles_available"),
        "vehicles_used": vehicles_used,
        "total_distance": total_distance,
        "total_load": total_load,
        "num_routes": len(result.get("routes", [])) if result.get("routes") else 0,
        "avg_distance_per_vehicle": avg_distance_per_vehicle,
        "avg_load_utilization": avg_load_utilization,
        "distance_per_customer": distance_per_customer,
    }
    return row


def run_batch(scenario_name: str = "medium", time_limit_sec: int = 10) -> pd.DataFrame:
    instance_names = get_instance_names()

    if not instance_names:
        print("No processed instances found.")
        return pd.DataFrame()

    print(f"Found {len(instance_names)} instance(s).")
    print("-" * 80)

    summary_rows = []

    for instance_name in instance_names:
        print(f"[RUNNING] {instance_name}")

        try:
            result = solve_cvrptw(
                instance_name=instance_name,
                scenario_name=scenario_name,
                time_limit_sec=time_limit_sec,
            )

            save_solution_result(result)
            save_metrics_csv(result)

            summary_row = build_summary_row(result)
            summary_rows.append(summary_row)

            print(
                f"         status={summary_row['status']}, "
                f"vehicles={summary_row['vehicles_used']}, "
                f"distance={summary_row['total_distance']}, "
                f"utilization={summary_row['avg_load_utilization']}, "
                f"runtime={summary_row['runtime_sec']}"
            )

        except Exception as e:
            print(f"[FAILED] {instance_name}: {e}")

            summary_rows.append(
                {
                    "instance_name": instance_name,
                    "scenario_name": scenario_name,
                    "status": "ERROR",
                    "runtime_sec": None,
                    "vehicle_capacity": None,
                    "num_customers": None,
                    "num_vehicles_available": None,
                    "vehicles_used": None,
                    "total_distance": None,
                    "total_load": None,
                    "num_routes": None,
                    "avg_distance_per_vehicle": None,
                    "avg_load_utilization": None,
                    "distance_per_customer": None,
                    "error_message": str(e),
                }
            )

        print("-" * 80)

    summary_df = pd.DataFrame(summary_rows)

    preferred_order = [
        "instance_name",
        "scenario_name",
        "status",
        "runtime_sec",
        "vehicle_capacity",
        "num_customers",
        "num_vehicles_available",
        "vehicles_used",
        "num_routes",
        "total_distance",
        "total_load",
        "avg_distance_per_vehicle",
        "avg_load_utilization",
        "distance_per_customer",
    ]

    existing_cols = [col for col in preferred_order if col in summary_df.columns]
    other_cols = [col for col in summary_df.columns if col not in existing_cols]
    summary_df = summary_df[existing_cols + other_cols]

    return summary_df


def save_summary(summary_df: pd.DataFrame, scenario_name: str = "medium") -> Path:
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    summary_path = SUMMARY_DIR / f"cvrptw_{scenario_name}_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    print(f"Saved summary: {summary_path}")
    return summary_path


def main() -> None:
    scenario_name = "medium"
    time_limit_sec = 10

    summary_df = run_batch(
        scenario_name=scenario_name,
        time_limit_sec=time_limit_sec,
    )

    if summary_df.empty:
        print("No summary generated.")
        return

    save_summary(summary_df, scenario_name=scenario_name)

    print("=" * 100)
    print("Batch run completed.")
    print(summary_df.to_string(index=False))
    print("=" * 100)


if __name__ == "__main__":
    main()