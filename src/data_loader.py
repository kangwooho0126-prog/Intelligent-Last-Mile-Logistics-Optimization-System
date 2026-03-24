import json
from pathlib import Path
from typing import Dict, Tuple


def parse_cvrp_file(file_path: str) -> dict:
    name = None
    capacity = None
    dimension = None

    coordinates: Dict[int, Tuple[float, float]] = {}
    demands: Dict[int, int] = {}
    depot_id = None

    section = None

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    for line in lines:
        if line.startswith("NAME"):
            name = line.split(":")[-1].strip()
        elif line.startswith("CAPACITY"):
            capacity = int(line.split(":")[-1].strip())
        elif line.startswith("DIMENSION"):
            dimension = int(line.split(":")[-1].strip())
        elif line.startswith("NODE_COORD_SECTION"):
            section = "coords"
            continue
        elif line.startswith("DEMAND_SECTION"):
            section = "demands"
            continue
        elif line.startswith("DEPOT_SECTION"):
            section = "depot"
            continue
        elif line.startswith("EOF"):
            break
        else:
            if section == "coords":
                parts = line.split()
                coordinates[int(parts[0])] = (float(parts[1]), float(parts[2]))
            elif section == "demands":
                parts = line.split()
                demands[int(parts[0])] = int(parts[1])
            elif section == "depot":
                if line != "-1":
                    depot_id = int(line)

    return {
        "name": name,
        "capacity": capacity,
        "dimension": dimension,
        "depot_id": depot_id,
        "coordinates": coordinates,
        "demands": demands,
    }


def save_meta_json(meta: dict, save_path: str) -> None:
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)