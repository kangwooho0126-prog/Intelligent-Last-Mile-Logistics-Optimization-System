from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

RAW_VRP_FILE = RAW_DATA_DIR / "A-n32-k5.vrp"

DEPOT_CSV = PROCESSED_DATA_DIR / "depot.csv"
NODES_CSV = PROCESSED_DATA_DIR / "nodes.csv"
META_JSON = PROCESSED_DATA_DIR / "meta.json"

RESULTS_DIR = PROJECT_ROOT / "results"
BASE_RESULTS_DIR = RESULTS_DIR / "base"
SCENARIO_RESULTS_DIR = RESULTS_DIR / "scenarios"
PLOTS_DIR = RESULTS_DIR / "plots"

NODE_MAP_PNG = PLOTS_DIR / "node_map.png"
BASELINE_ROUTE_PNG = PLOTS_DIR / "baseline_routes.png"

BASELINE_ROUTE_PLAN_JSON = BASE_RESULTS_DIR / "baseline_route_plan.json"
BASELINE_ROUTE_SUMMARY_CSV = BASE_RESULTS_DIR / "baseline_route_summary.csv"
BASELINE_METRICS_JSON = BASE_RESULTS_DIR / "baseline_metrics.json"
BASELINE_METRICS_CSV = BASE_RESULTS_DIR / "baseline_metrics.csv"

COMPARISON_METRICS_CSV = BASE_RESULTS_DIR / "comparison_metrics.csv"
COMPARISON_SUMMARY_TXT = BASE_RESULTS_DIR / "comparison_summary.txt"

DISTANCE_COMPARISON_PNG = PLOTS_DIR / "distance_comparison.png"
COST_COMPARISON_PNG = PLOTS_DIR / "cost_comparison.png"
UTILIZATION_COMPARISON_PNG = PLOTS_DIR / "utilization_comparison.png"

FIXED_VEHICLE_COST = 80.0
COST_PER_DISTANCE_UNIT = 3.0

COMPARISON_METRICS_CSV = BASE_RESULTS_DIR / "comparison_metrics.csv"
COMPARISON_SUMMARY_TXT = BASE_RESULTS_DIR / "comparison_summary.txt"
LLM_ANALYSIS_TXT = BASE_RESULTS_DIR / "llm_dispatch_analysis.txt"

DISTANCE_COMPARISON_PNG = PLOTS_DIR / "distance_comparison.png"
COST_COMPARISON_PNG = PLOTS_DIR / "cost_comparison.png"
UTILIZATION_COMPARISON_PNG = PLOTS_DIR / "utilization_comparison.png"

FIXED_VEHICLE_COST = 80.0
COST_PER_DISTANCE_UNIT = 3.0

LLM_MODE = "template"
LLM_API_KEY = ""
LLM_BASE_URL = ""
LLM_MODEL_NAME = ""


def ensure_directories() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    BASE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    SCENARIO_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)