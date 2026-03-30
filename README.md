#  Intelligent-Last-Mile-Logistics-Optimization-System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![OR-Tools](https://img.shields.io/badge/Google_OR--Tools-Optimization-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive_UI-red)
![LLM](https://img.shields.io/badge/LLM-Agent_Copilot-brightgreen)

An end-to-end intelligent logistics optimization system integrating Capacitated Vehicle Routing Problem (CVRP) modeling, Google OR-Tools optimization, LLM-based business analysis, and interactive agent-based scenario replanning.

---

##  Project Overview

This project simulates a real-world **last-mile delivery scenario**, where a fleet of vehicles must deliver parcels from a central depot to multiple customers under strict capacity constraints. 

The system provides a complete pipeline for data-driven logistics decision-making:
- **Optimization-based routing** (OR-Tools)
- **Baseline heuristic comparison**
- **KPI-driven performance evaluation**
- **LLM-powered interpretation** of results
- **Agent-based interactive replanning** via a Streamlit dashboard

---

##  Mathematical Formulation

The core routing engine optimizes the standard CVRP objective—minimizing total transportation cost while satisfying rigid physical constraints:

**Objective Function:**
$$\text{Minimize} \quad \sum_{k=1}^{K} \sum_{i=0}^{N} \sum_{j=0}^{N} c_{ij} x_{ijk}$$

**Capacity Constraint:**
$$\sum_{i=1}^{N} d_i y_{ik} \le Q_k \quad \forall k \in K$$

---

##  Methodology

### 1. Problem Modeling
- Modeled as **CVRP** (Capacitated Vehicle Routing Problem).
- Single depot + multiple customer nodes.
- Fixed vehicle capacity constraint.

### 2. Baseline Algorithm
- Greedy nearest-neighbor heuristic.

### 3. Optimization Solver
- Google OR-Tools routing solver (Guided Local Search).

### 4. Evaluation Metrics
- Total distance, Total cost, Vehicles used, Average load utilization, Cost per parcel.

### 5. LLM Copilot
- Converts optimization results into human-readable business insights.

### 6. Agent Module
- Supports natural language queries for dynamic replanning (e.g., `"replan with capacity 120"`, `"compare baseline and ortools"`).

---

##  Quick Start

### 1. Install Dependencies
Clone the repository and install the required packages:
```bash
git clone https://github.com/kangwooho0126-prog/Intelligent-Last-Mile-Logistics-Optimization-System.git
cd Intelligent-Last-Mile-Logistics-Optimization-System
pip install -r requirements.txt
```

### 2. Launch the Interactive Dashboard (Recommended)
Start the Streamlit web application to access the OR-Tools solver and the LLM Agent:
```bash
streamlit run app/streamlit_app.py
```

### 3. Run the CLI Optimization Engine
Alternatively, run the core backend solver directly:
```bash
python main.py
```

---

##  Results & Business Impact

### Baseline vs OR-Tools Evaluation

| Metric | Baseline (Greedy) | OR-Tools (Optimized) | Improvement |
|--------|-------------------|----------------------|-------------|
| **Total Distance** | 1146.40 km | 787.08 km |  **↓ 31.34%** |
| **Total Cost** | $3839.20 | $2761.25 |  **↓ 28.08%** |
| **Vehicles Used** | 5 Trucks | 5 Trucks |  **=** |
| **Load Utilization** | 82.0% | 82.0% |  **=** |

###  Key Insight
> *"Optimization improves delivery efficiency primarily through better route structuring (reducing overlapping paths and deadhead miles), rather than increasing logistics resources."*

---

##  Agent Replanning Example

The integrated LLM Agent allows dispatchers to dynamically interact with the system using natural language.

**User Query:**
```text
> "replan with capacity 120"
```

**System Action & Output:**
1. **Intent Parsing:** Agent identifies the intent to change `MAX_CAPACITY` constraint to 120.
2. **Re-Optimization:** Triggers the OR-Tools solver seamlessly with the new parameters.
3. **LLM Summary:** Generates a comparative business report detailing how the reduced capacity impacts fleet utilization and operational costs, displaying the new metrics directly on the Streamlit dashboard.
