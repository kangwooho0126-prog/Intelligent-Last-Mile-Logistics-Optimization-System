from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def parse_vrp_file(file_path: Path) -> Tuple[Dict, pd.DataFrame, pd.DataFrame]:
    """
    Parse a CVRP .vrp file in Augerat-like format.

    Returns:
        meta_info: dict
        depot_df: DataFrame with one row
        nodes_df: DataFrame with customer nodes only
    """
    lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    lines = [line.strip() for line in lines if line.strip()]

    meta: Dict[str, str] = {}
    node_coords: Dict[int, Tuple[float, float]] = {}
    demands: Dict[int, int] = {}
    depot_ids: List[int] = []

    section = None

    for line in lines:
        upper_line = line.upper()

        if upper_line.startswith("NODE_COORD_SECTION"):
            section = "NODE_COORD_SECTION"
            continue
        elif upper_line.startswith("DEMAND_SECTION"):
            section = "DEMAND_SECTION"
            continue
        elif upper_line.startswith("DEPOT_SECTION"):
            section = "DEPOT_SECTION"
            continue
        elif upper_line.startswith("EOF"):
            section = None
            break

        if section is None:
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip().upper()] = value.strip()
            continue

        if section == "NODE_COORD_SECTION":
            parts = line.split()
            if len(parts) >= 3:
                node_id = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                node_coords[node_id] = (x, y)

        elif section == "DEMAND_SECTION":
            parts = line.split()
            if len(parts) >= 2:
                node_id = int(parts[0])
                demand = int(parts[1])
                demands[node_id] = demand

        elif section == "DEPOT_SECTION":
            if line == "-1":
                section = None
            else:
                depot_ids.append(int(line))

    if not node_coords:
        raise ValueError(f"No node coordinates found in {file_path.name}")
    if not demands:
        raise ValueError(f"No demand section found in {file_path.name}")
    if not depot_ids:
        raise ValueError(f"No depot section found in {file_path.name}")

    depot_id = depot_ids[0]
    if depot_id not in node_coords:
        raise ValueError(f"Depot node {depot_id} not found in coordinate section")

    depot_x, depot_y = node_coords[depot_id]
    depot_demand = demands.get(depot_id, 0)

    depot_df = pd.DataFrame(
        [
            {
                "node_id": depot_id,
                "x": depot_x,
                "y": depot_y,
                "demand": depot_demand,
            }
        ]
    )

    customer_rows = []
    for node_id, (x, y) in sorted(node_coords.items(), key=lambda t: t[0]):
        if node_id == depot_id:
            continue
        demand = demands.get(node_id, 0)
        dist_to_depot = math.dist((x, y), (depot_x, depot_y))
        customer_rows.append(
            {
                "node_id": node_id,
                "x": x,
                "y": y,
                "demand": demand,
                "distance_to_depot": round(dist_to_depot, 4),
            }
        )

    nodes_df = pd.DataFrame(customer_rows)

    dimension = None
    if "DIMENSION" in meta:
        try:
            dimension = int(meta["DIMENSION"])
        except ValueError:
            dimension = meta["DIMENSION"]

    capacity = None
    if "CAPACITY" in meta:
        try:
            capacity = int(meta["CAPACITY"])
        except ValueError:
            capacity = meta["CAPACITY"]

    meta_info = {
        "instance_name": file_path.stem,
        "source_file": file_path.name,
        "problem_type": meta.get("TYPE"),
        "comment": meta.get("COMMENT"),
        "dimension": dimension,
        "vehicle_capacity": capacity,
        "depot_id": depot_id,
        "num_customers": len(nodes_df),
        "total_demand": int(nodes_df["demand"].sum()) if not nodes_df.empty else 0,
    }

    return meta_info, depot_df, nodes_df


def save_processed_instance(
    instance_name: str,
    meta_info: Dict,
    depot_df: pd.DataFrame,
    nodes_df: pd.DataFrame,
) -> None:
    instance_dir = PROCESSED_DIR / instance_name
    instance_dir.mkdir(parents=True, exist_ok=True)

    depot_path = instance_dir / "depot.csv"
    nodes_path = instance_dir / "nodes.csv"
    meta_path = instance_dir / "meta.json"

    depot_df.to_csv(depot_path, index=False)
    nodes_df.to_csv(nodes_path, index=False)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_info, f, ensure_ascii=False, indent=2)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    vrp_files = sorted(RAW_DIR.glob("*.vrp"))

    if not vrp_files:
        print(f"No .vrp files found in: {RAW_DIR}")
        return

    print(f"Found {len(vrp_files)} .vrp file(s).")
    print("-" * 60)

    success_count = 0
    failed_files = []

    for file_path in vrp_files:
        try:
            meta_info, depot_df, nodes_df = parse_vrp_file(file_path)
            save_processed_instance(file_path.stem, meta_info, depot_df, nodes_df)

            print(f"[OK] {file_path.name}")
            print(f"     -> processed/{file_path.stem}/depot.csv")
            print(f"     -> processed/{file_path.stem}/nodes.csv")
            print(f"     -> processed/{file_path.stem}/meta.json")
            print(
                f"     customers={meta_info['num_customers']}, "
                f"capacity={meta_info['vehicle_capacity']}, "
                f"total_demand={meta_info['total_demand']}"
            )
            success_count += 1

        except Exception as e:
            print(f"[FAILED] {file_path.name}: {e}")
            failed_files.append(file_path.name)

    print("-" * 60)
    print(f"Done. Success: {success_count}, Failed: {len(failed_files)}")

    if failed_files:
        print("Failed files:")
        for name in failed_files:
            print(f" - {name}")


if __name__ == "__main__":
    main()