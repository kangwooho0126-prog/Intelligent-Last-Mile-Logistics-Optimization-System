import streamlit as st
import pandas as pd
from PIL import Image

from src.config import (
    BASELINE_METRICS_CSV,
    ORTOOLS_METRICS_CSV,
    DISTANCE_COMPARISON_PNG,
    COST_COMPARISON_PNG,
    UTILIZATION_COMPARISON_PNG,
    LLM_ANALYSIS_TXT,
    COMPARISON_SUMMARY_TXT
)
from src.agent_dispatcher import dispatch_agent
from src.distance_utils import build_node_dict, build_distance_matrix
from src.data_loader import parse_cvrp_file
from src.scenario_builder import build_logistics_tables


st.set_page_config(page_title="Logistics Optimization System", layout="wide")

st.title(" AI-Powered Last-Mile Logistics Optimization System")
st.caption("Optimization + LLM + Agent-based Decision Support")

baseline_df = pd.read_csv(BASELINE_METRICS_CSV)
ortools_df = pd.read_csv(ORTOOLS_METRICS_CSV)

baseline = baseline_df.iloc[0]
ortools = ortools_df.iloc[0]

distance_reduction = (
    (baseline["total_distance"] - ortools["total_distance"])
    / baseline["total_distance"]
    * 100
)

cost_reduction = (
    (baseline["total_cost"] - ortools["total_cost"])
    / baseline["total_cost"]
    * 100
)

st.header("Key Performance Improvement")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Distance Reduction",
        f"{distance_reduction:.2f}%",
        delta=f"-{baseline['total_distance'] - ortools['total_distance']:.1f}"
    )

with col2:
    st.metric(
        "Cost Reduction",
        f"{cost_reduction:.2f}%",
        delta=f"-{baseline['total_cost'] - ortools['total_cost']:.1f}"
    )

with col3:
    st.metric(
        "Vehicles Used",
        f"{int(ortools['vehicles_used'])}",
        delta=f"{int(ortools['vehicles_used'] - baseline['vehicles_used'])}"
    )

st.success(
    f"OR-Tools reduces total distance by {distance_reduction:.2f}% "
    f"and delivery cost by {cost_reduction:.2f}% under the same fleet size."
)

st.header("Routing Performance Comparison")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Baseline Metrics")
    st.dataframe(baseline_df, use_container_width=True)

with col2:
    st.subheader("OR-Tools Metrics")
    st.dataframe(ortools_df, use_container_width=True)

st.header("Comparison Charts")

col1, col2, col3 = st.columns(3)

with col1:
    st.image(Image.open(DISTANCE_COMPARISON_PNG), caption="Distance", use_container_width=True)

with col2:
    st.image(Image.open(COST_COMPARISON_PNG), caption="Cost", use_container_width=True)

with col3:
    st.image(Image.open(UTILIZATION_COMPARISON_PNG), caption="Utilization", use_container_width=True)

st.header("LLM Dispatch Analysis")

with open(LLM_ANALYSIS_TXT, "r", encoding="utf-8") as f:
    llm_text = f.read()

st.markdown("###  Business Insight")
st.info(llm_text)

st.header("Interactive Agent")
st.markdown("Try different scenarios like:")
st.markdown("- replan with capacity 120")
st.markdown("- replan with capacity 150")
st.markdown("- compare baseline and ortools")
st.markdown("- summarize the routing result")

user_query = st.text_input(
    "Enter query",
    value="replan with capacity 120"
)

if st.button("Run Agent"):
    parsed_data = parse_cvrp_file("data/raw/A-n32-k5.vrp")
    depot_df, nodes_df = build_logistics_tables(parsed_data)

    node_dict = build_node_dict(depot_df, nodes_df)
    distance_matrix = build_distance_matrix(node_dict)

    with st.spinner("Running optimization..."):
        response = dispatch_agent(
            user_query=user_query,
            comparison_summary_path=str(COMPARISON_SUMMARY_TXT),
            llm_analysis_path=str(LLM_ANALYSIS_TXT),
            depot_df=depot_df,
            nodes_df=nodes_df,
            node_dict=node_dict,
            distance_matrix=distance_matrix,
            fixed_vehicle_cost=80.0,
            cost_per_distance_unit=3.0,
            depot_id=parsed_data["depot_id"]
        )

    st.success("Agent Response")
    st.markdown("###  Result")
    st.write(response)