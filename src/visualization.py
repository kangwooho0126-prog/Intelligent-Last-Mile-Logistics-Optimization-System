from pathlib import Path
import matplotlib.pyplot as plt


def plot_node_map(depot_df, nodes_df, save_path: str) -> None:
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(9, 7))

    station_type_markers = {
        "parcel_station": "o",
        "pickup_locker": "^",
        "partner_store": "D"
    }

    for station_type, marker in station_type_markers.items():
        subset = nodes_df[nodes_df["node_type"] == station_type]
        if not subset.empty:
            plt.scatter(
                subset["x"],
                subset["y"],
                s=70,
                marker=marker,
                label=station_type
            )

    plt.scatter(
        depot_df["x"],
        depot_df["y"],
        s=180,
        marker="s",
        label="distribution_center"
    )

    for _, row in nodes_df.iterrows():
        plt.text(row["x"] + 0.3, row["y"] + 0.3, str(int(row["node_id"])), fontsize=8)

    depot_row = depot_df.iloc[0]
    plt.text(depot_row["x"] + 0.3, depot_row["y"] + 0.3, "Depot", fontsize=10)

    plt.title("Urban Parcel Distribution Node Map")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()