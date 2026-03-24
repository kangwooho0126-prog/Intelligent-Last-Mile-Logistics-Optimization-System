from __future__ import annotations

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = PROJECT_ROOT / "results" / "summary" / "cvrptw_medium_summary.csv"
OUTPUT_DIR = PROJECT_ROOT / "results" / "summary" / "plots"


def main() -> None:
    df = pd.read_csv(SUMMARY_PATH)
    df = df[df["status"] == "SOLVED"].copy()
    df = df.sort_values("num_customers")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    x = df["num_customers"].values
    y = df["avg_load_utilization"].values

    plt.figure(figsize=(8, 5))

    plt.plot(x, y, marker="o", label="Actual")

    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    plt.plot(x, p(x), linestyle="--", label="Trend")

    for _, row in df.iterrows():
        plt.annotate(
            row["instance_name"],
            (row["num_customers"], row["avg_load_utilization"]),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=9,
        )

    plt.xlabel("Number of Customers")
    plt.ylabel("Average Load Utilization")
    plt.title("Vehicle Utilization vs Problem Size (CVRPTW)")
    plt.ylim(0.85, 1.0)
    plt.legend()
    plt.grid(True)

    output_path = OUTPUT_DIR / "utilization_vs_customers.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved plot: {output_path}")


if __name__ == "__main__":
    main()