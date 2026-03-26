#  Intelligent Last-Mile Logistics Optimization System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![OR-Tools](https://img.shields.io/badge/Google_OR--Tools-Optimization-orange)
![Status](https://img.shields.io/badge/Status-Active-success)

A CVRP-based last-mile delivery optimization project featuring cost-aware routing, scenario simulation, and LLM-assisted decision analysis. 

##  Project Overview

This project builds a simplified yet complete pipeline for **last-mile logistics optimization**, aiming to bridge the gap between operations research algorithms and data-driven business decisions. 

**Key Features:**
-  **CVRP Modeling:** Capacitated Vehicle Routing Problem formulation.
-  **A/B Algorithm Comparison:** Baseline Heuristic vs. Global Optimization.
-  **Business Metrics:** Evaluates Cost per Parcel, Load Utilization, and Total Distance.
-  **Scenario Simulation:** Re-planning under dynamic capacity/demand changes.
-  **LLM-Assisted Interpretation (Optional):** Translates optimization outputs into natural language insights for business decision support.

##  Business Scenario

In urban last-mile logistics (e.g., fresh food delivery, parcel stations), efficiency is dictated by strict physical constraints. This system simulates a real-world delivery network:
- **Depot:** Central Distribution Center (Node 0)
- **Nodes:** Parcel pickup points / Partner stores
- **Demand:** Daily parcel volume per node
- **Vehicles:** Heterogeneous or homogeneous fleet with strict `MAX_CAPACITY` constraints.

##  Mathematical Formulation

We model the scenario as a standard **CVRP**. The core objective is to minimize the total routing cost while strictly adhering to vehicle capacities:

**Objective Function:**
$$\text{Minimize} \quad \sum_{k=1}^{K} \sum_{i=0}^{N} \sum_{j=0}^{N} c_{ij} x_{ijk}$$

**Capacity Constraint:**
$$\sum_{i=1}^{N} d_i y_{ik} \le Q_k \quad \forall k \in K$$
*(Where $c_{ij}$ is the cost matrix, $d_i$ is node demand, and $Q_k$ is vehicle capacity.)*

##  Methods & Tech Stack

1. **Baseline Heuristic:** A greedy "Nearest-Feasible-Node" strategy used as a performance floor.
2. **Optimization Solver:** **Google OR-Tools** (Routing Index Manager & Model) utilizing Guided Local Search meta-heuristics for global optimal convergence.
3. **Data Visualization:** `matplotlib` and `seaborn` for spatial route plotting.

##  Quick Start

**1. Clone the repository**
```bash
git clone https://github.com/YourUsername/Intelligent-Last-Mile-Logistics-Optimization-System.git
cd Intelligent-Last-Mile-Logistics-Optimization-System
```

**2. Install dependencies**
```bash
pip install ortools matplotlib numpy
# Optional for LLM feature: pip install openai
```

**3. Run the optimization engine**
```bash
python main.py --dataset A-n32-k5.vrp
```

##  Results & Evaluation

On a representative CVRP benchmark instance (e.g., Augerat A-n32-k5), the OR-Tools solver demonstrates significant operational savings compared to the greedy baseline:

| Metric | Baseline (Greedy) | Optimized (OR-Tools) | Improvement |
| :--- | :--- | :--- | :--- |
| **Total Distance** | 1,024.5 km | 784.0 km |  **-23.4%** |
| **Vehicles Used** | 6 Trucks | 5 Trucks |  **-1 Truck** |
| **Avg. Load Utilization** | 71.2% | 89.5% |  **+18.3%** |
| **Cost per Parcel** | $1.45 | $1.12 |  **-$0.33** |

*(Visual routing comparisons and scenario simulation heatmaps are saved automatically in the `/results` directory after running the script).*

---
*Developed for advanced supply chain analytics and algorithm engineering research.*