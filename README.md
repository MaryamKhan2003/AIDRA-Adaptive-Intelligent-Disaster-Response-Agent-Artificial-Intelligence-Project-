# AIDRA — Adaptive Intelligent Disaster Response Agent

###  A Hybrid AI System for Smart Disaster Rescue Operations

**Artificial Intelligence Complex Computing Problem (CCP)**

---

##  Overview

AIDRA (Adaptive Intelligent Disaster Response Agent) is a Hybrid Artificial Intelligence system designed to simulate intelligent disaster rescue operations in dynamic and uncertain environments.

The system combines multiple AI techniques to perform:

✅ Victim Prioritization 
✅ Intelligent Route Planning 
✅ Resource Allocation 
✅ Risk Analysis 
✅ Dynamic Replanning 
✅ Survival Prediction

AIDRA operates in a changing disaster environment where roads may become blocked, hazards may spread, and rescue resources are limited.

---

##  Project Objectives

The system solves two major conflicting objectives:

### Objective 1 — Rescue Time vs Risk Exposure
- Fast routes are dangerous
- Safe routes are longer

The agent must decide between:
-  Faster rescue (higher risk)
-  Safer rescue (longer time)

**Decision Strategy:**

| Victim Severity | Decision Priority |
|-----------------|-------------------|
|  Critical | Prioritize Speed (TIME) |
|  Moderate | Balanced Decision |
|  Minor | Prioritize Safety |

### Objective 2 — Victim Priority vs Throughput
- Critical victims require immediate rescue
- Saving critical victims may delay others

The system balances:
- ✅ Saving maximum victims
- ✅ Prioritizing severe injuries
- ✅ Efficient resource usage

---

##  AI Components Integrated

AIDRA integrates multiple AI modules into one intelligent system.

| AI Component | Purpose |
|--------------|---------|
| 🔍 Search Algorithms | Route Planning |
| 📦 CSP Solver | Resource Allocation |
|  Machine Learning | Survival Prediction |
| Fuzzy Logic | Uncertainty Handling |
|  Dynamic Replanning | Real-Time Adaptation |

---

## Search Algorithms Implemented

The system compares multiple search algorithms.

### Algorithms Included:
- BFS (Breadth First Search)
- DFS (Depth First Search)
- Greedy Best First Search
- A* Search (Fast, Balanced, Safe variants)
- Hill Climbing

### Best Performing Algorithm: **A* Search**

A* performed best because it:
- ✅ Finds optimal paths
- ✅ Balances speed and safety
- ✅ Uses heuristic intelligence
- ✅ Handles risk-aware planning

**Formula Used:** `f(n) = g(n) + h(n)`

Where:
- `g(n)` = actual path cost (includes risk penalties)
- `h(n)` = estimated distance to goal (Manhattan distance)

### Actual Performance Results:

| Algorithm | Path Length | Nodes Expanded | Cost |
|-----------|-------------|----------------|------|
| BFS | 5 | 10 | 5 |
| DFS | 15 | 15 | 15 |
| Greedy | 5 | 5 | 5 |
| A*_Fast | 5 | 5 | 4 |
| A*_Balanced | 5 | 5 | 4 |
| A*_Safe | 5 | 5 | 4 |
| Hill Climbing | 5 | 4 | 5 |

---

##  Constraint Satisfaction Problem (CSP)

The CSP module allocates victims to rescue resources while satisfying hard constraints.

### Available Resources:
- 2 Ambulances
- 1 Rescue Team
- 10 Medical Kits

### Constraints:
- Maximum 2 victims per ambulance
- Rescue team handles only 1 victim
- Critical victims preferred for ambulances

### CSP Heuristics Used:
- ✅ MRV (Minimum Remaining Values)
- ✅ Degree Heuristic
- ✅ Forward Checking
- ✅ Backtracking

### Actual Allocation Result:
Ambulance A1: V1, V4 (2 victims)
Ambulance A2: V2, V5 (2 victims)
Rescue Team: V3 (1 victim)
Backtracks: 6

text

---

##  Machine Learning Module

Machine Learning predicts victim survival probability using real medical triage data (600 samples).

### Models Used:

| Model | Purpose | Accuracy |
|-------|---------|----------|
|  Naive Bayes | Probability-based prediction | 73.3% |
|  KNN | Similar victim analysis | 73.3% |

### ML Evaluation Metrics:
- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix

### Confusion Matrix (KNN - Best Model):
Predicted
Survive Die
Actual Survive 318 49
Actual Die 36 197

text

---

##  Fuzzy Logic & Uncertainty Handling

Disaster environments are uncertain. Fuzzy logic helps evaluate:
- Fire hazards
- Aftershock probability
- Blocked roads
- Risk exposure

### Risk Categories:

| Score | Risk Level |
|-------|------------|
| 0–24 | 🟢 Low |
| 25–49 | 🟡 Medium |
| 50–74 | 🟠 High |
| 75+ | 🔴 Very High |

### Bayesian Blockage Prediction:
`P(Blockage) = 0.1 + 0.3×risk_nearby + 0.4×aftershock = 80%`

---

##  Dynamic Environment & Replanning

AIDRA supports real-time environmental changes.

### Dynamic Events:
- ✅ Roads become blocked
- ✅ Hazards spread
- ✅ Risk zones change

### Replanning Example:

**Original Path to V5:**
(0,5) → (0,4) → (0,3) → (1,3) → (2,3) → (3,3) → (3,2) → (4,2)

text

**Blockage at (3,2):**
 ROAD BLOCKED! Agent detects obstacle.

text

**New Path After Replanning:**
(0,5) → (0,4) → (0,3) → (1,3) → (2,3) → (3,3) → (4,3) → (4,2)

text

---

## Environment Setup

### Grid Configuration:

| Item | Position |
|------|----------|
| 🏥 Base | (0,0) |
| 🏨 Hospital 1 | (0,5) |
| 🏨 Hospital 2 | (4,0) |
| 🔥 Risk Zone | (2,2) |
| 🚧 Blocked Road | (1,1) |

### Victim Information:

| Victim | Severity | Position |
|--------|----------|----------|
| V1 | 🔴 Critical | (0,3) |
| V2 | 🟠 Moderate | (3,4) |
| V3 | 🟢 Minor | (5,5) |
| V4 | 🔴 Critical | (2,0) |
| V5 | 🟠 Moderate | (4,2) |

---

## 📊 Performance Metrics (KPIs)

The system evaluates performance using:

| Metric | Value |
|--------|-------|
| Victims Saved | 5/5 (100%) |
|  Average Rescue Time | 10.6 steps |
|  Resource Utilization | 100% |
|  Risk Exposure Score | 2.0 points |
|  Path Optimality Ratio | 65.6% |
|  ML Accuracy (KNN) | 73.3% |
|  CSP Backtracks | 6 |

---

## GUI Features

The GUI provides a visual rescue simulation.

### GUI Includes:
- ✅ Animated Ambulance Movement
- ✅ Real-Time Route Display
- ✅ Victim Visualization
- ✅ Dynamic Blockage Updates
- ✅ Rescue Path Animation
- ✅ Grid Status Display

---

Project Structure
AIDRA/
│
├── main.py
├── environment.py
├── search.py
├── agent.py
├── csp.py
├── ml_model.py
├── fuzzy.py
├── gui.py
├── triange_data.csv
└── README.md
How to Run
Install Dependencies
pip install matplotlib scikit-learn numpy
Run the Project
python main.py
Academic Information
Field	Details
📘 Course	Artificial Intelligence (AIC-201)
👨‍🏫 Instructor	Dr. Arshad Farhad
🎯 Project Type	Complex Computing Problem (CCP)
🏫 Semester	5th Semester
Authors
Developed By
Maryam Khan
Khadeeja Hafeez
#LinkedIn Vedio Links: https://www.linkedin.com/posts/maryam-khan-8139432ba_ai-disasterresponse-machinelearning-ugcPost-7459098645619957760--9cS?utm_source=share&utm_medium=member_desktop&rcm=ACoAAEyraM8BYf96yVhTLM1dSW5YyfAyUGkMMgs
Conclusion
AIDRA successfully demonstrates how Hybrid Artificial Intelligence techniques can work together to solve complex disaster management problems.

The system intelligently handles:

✅ Route Planning ✅ Resource Allocation ✅ Risk Analysis ✅ Survival Prediction ✅ Dynamic Replanning

By combining Search Algorithms, CSP, Machine Learning, Fuzzy Logic, and Real-Time Adaptation, AIDRA provides a strong foundation for future intelligent emergency response systems.

Thank You
Intelligent Systems for Smarter Rescue Operations
