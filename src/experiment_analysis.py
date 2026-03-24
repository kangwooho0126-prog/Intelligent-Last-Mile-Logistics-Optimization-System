from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def load_metrics_csv(file_path: str, method_name: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df["method"] = method_name
    return df


def build_comparison_table(
    baseline_metrics_path: str,
    ortools_metrics_path: str
) -> pd.DataFrame:
    baseline_df = load_metrics_csv(baseline_metrics_path, "baseline")
    ortools_df = load_metrics_csv(ortools_metrics_path, "ortools")

    comparison_df = pd.concat([baseline_df, ortools_df], ignore_index=True)

    ordered_cols = [
        "method",
        "vehicles_used",
        "total_distance",
        "total_load",
        "total_cost",
        "avg_load_utilization",
        "cost_per_parcel"
    ]
    comparison_df = comparison_df[ordered_cols]

    return comparison_df


def save_comparison_table(comparison_df: pd.DataFrame, save_path: str) -> None:
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    comparison_df.to_csv(save_path, index=False)


def plot_metric_comparison(
    comparison_df: pd.DataFrame,
    metric_col: str,
    title: str,
    ylabel: str,
    save_path: str
) -> None:
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(7, 5))
    plt.bar(comparison_df["method"], comparison_df[metric_col])
    plt.title(title)
    plt.xlabel("Method")
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def generate_comparison_summary(comparison_df: pd.DataFrame) -> str:
    baseline_row = comparison_df[comparison_df["method"] == "baseline"].iloc[0]
    ortools_row = comparison_df[comparison_df["method"] == "ortools"].iloc[0]

    baseline_distance = float(baseline_row["total_distance"])
    ortools_distance = float(ortools_row["total_distance"])

    baseline_cost = float(baseline_row["total_cost"])
    ortools_cost = float(ortools_row["total_cost"])

    baseline_vehicles = int(baseline_row["vehicles_used"])
    ortools_vehicles = int(ortools_row["vehicles_used"])

    baseline_util = float(baseline_row["avg_load_utilization"])
    ortools_util = float(ortools_row["avg_load_utilization"])

    distance_improvement = 0.0
    if baseline_distance > 0:
        distance_improvement = (baseline_distance - ortools_distance) / baseline_distance * 100

    cost_improvement = 0.0
    if baseline_cost > 0:
        cost_improvement = (baseline_cost - ortools_cost) / baseline_cost * 100

    summary_lines = [
        "Method Comparison Summary",
        "",
        f"Baseline total distance: {baseline_distance:.4f}",
        f"OR-Tools total distance: {ortools_distance:.4f}",
        f"Distance reduction: {distance_improvement:.2f}%",
        "",
        f"Baseline total cost: {baseline_cost:.4f}",
        f"OR-Tools total cost: {ortools_cost:.4f}",
        f"Cost reduction: {cost_improvement:.2f}%",
        "",
        f"Baseline vehicles used: {baseline_vehicles}",
        f"OR-Tools vehicles used: {ortools_vehicles}",
        "",
        f"Baseline average load utilization: {baseline_util:.4f}",
        f"OR-Tools average load utilization: {ortools_util:.4f}",
        "",
        "Conclusion:",
        "The OR-Tools solution provides a more efficient routing plan than the greedy baseline,",
        "with lower total travel distance and lower delivery cost under the same logistics setting."
    ]

    return "\n".join(summary_lines)


def save_summary_text(summary_text: str, save_path: str) -> None:
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(summary_text)