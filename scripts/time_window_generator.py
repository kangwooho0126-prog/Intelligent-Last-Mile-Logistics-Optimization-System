from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def assign_time_window_by_distance(distance_to_depot: float, q1: float, q2: float):
    """
    Assign time windows based on customer distance to depot.

    Near customers   -> earlier window
    Mid customers    -> middle window
    Far customers    -> later window
    """
    if distance_to_depot <= q1:
        return 30, 180
    elif distance_to_depot <= q2:
        return 120, 300
    else:
        return 240, 420


def generate_medium_time_windows(nodes_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate medium time-window scenario for customer nodes.
    """
    df = nodes_df.copy()

    if "distance_to_depot" not in df.columns:
        raise ValueError("nodes.csv must contain 'distance_to_depot' column.")

    q1 = df["distance_to_depot"].quantile(0.33)
    q2 = df["distance_to_depot"].quantile(0.66)

    ready_times = []
    due_times = []

    for dist in df["distance_to_depot"]:
        ready, due = assign_time_window_by_distance(dist, q1, q2)
        ready_times.append(ready)
        due_times.append(due)

    df["service_time"] = 10
    df["ready_time"] = ready_times
    df["due_time"] = due_times

    return df


def process_instance(instance_dir: Path) -> None:
    nodes_path = instance_dir / "nodes.csv"
    meta_path = instance_dir / "meta.json"
    output_path = instance_dir / "nodes_tw_medium.csv"

    if not nodes_path.exists():
        print(f"[SKIP] {instance_dir.name}: nodes.csv not found")
        return

    nodes_df = pd.read_csv(nodes_path)
    tw_df = generate_medium_time_windows(nodes_df)
    tw_df.to_csv(output_path, index=False)

    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    else:
        meta = {}

    meta["time_window_scenarios"] = meta.get("time_window_scenarios", [])
    if "medium" not in meta["time_window_scenarios"]:
        meta["time_window_scenarios"].append("medium")

    meta["depot_time_window"] = [0, 480]
    meta["default_service_time"] = 10

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"[OK] {instance_dir.name}")
    print(f"     -> data/processed/{instance_dir.name}/nodes_tw_medium.csv")


def main() -> None:
    if not PROCESSED_DIR.exists():
        print(f"Processed directory not found: {PROCESSED_DIR}")
        return

    instance_dirs = [p for p in PROCESSED_DIR.iterdir() if p.is_dir()]

    if not instance_dirs:
        print("No processed instance directories found.")
        return

    print(f"Found {len(instance_dirs)} processed instance(s).")
    print("-" * 60)

    for instance_dir in sorted(instance_dirs):
        try:
            process_instance(instance_dir)
        except Exception as e:
            print(f"[FAILED] {instance_dir.name}: {e}")

    print("-" * 60)
    print("Done.")


if __name__ == "__main__":
    main()