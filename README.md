🚑 AIDRA — Adaptive Intelligent Disaster Response Agent
🧠 A Hybrid AI System for Smart Disaster Rescue Operations
Artificial Intelligence Complex Computing Problem (CCP)
Overview
AIDRA (Adaptive Intelligent Disaster Response Agent) is a Hybrid Artificial Intelligence system designed to simulate intelligent disaster rescue operations in dynamic and uncertain environments.

The system combines multiple AI techniques to perform:

✅ Victim Prioritization ✅ Intelligent Route Planning ✅ Resource Allocation ✅ Risk Analysis ✅ Dynamic Replanning ✅ Survival Prediction

AIDRA operates in a changing disaster environment where roads may become blocked, hazards may spread, and rescue resources are limited.

Project Objectives
The system solves two major conflicting objectives:

Objective 1 — Rescue Time vs Risk Exposure
Fast routes are dangerous

Safe routes are longer

The agent must decide between:

⏱ Faster rescue
🔥 Safer rescue
Decision Strategy
Victim Severity	Decision Priority
🔴 Critical	Prioritize Speed
🟠 Moderate	Balanced Decision
🟢 Minor	Prioritize Safety
Objective 2 — Victim Priority vs Throughput
Critical victims require immediate rescue
Saving critical victims may delay others
The system balances:

✅ Saving maximum victims ✅ Prioritizing severe injuries ✅ Efficient resource usage

AI Components Integrated
AIDRA integrates multiple AI modules into one intelligent system.

AI Component	Purpose
🔍 Search Algorithms	Route Planning
📦 CSP Solver	Resource Allocation
🤖 Machine Learning	Survival Prediction
🌫 Fuzzy Logic	Uncertainty Handling
🔄 Dynamic Replanning	Real-Time Adaptation
Search Algorithms Implemented
The system compares multiple search algorithms.

Algorithms Included
BFS (Breadth First Search)
DFS (Depth First Search)
Greedy Best First Search
A* Search
A*_Fast
A*_Balanced
A*_Safe
Hill Climbing
Best Performing Algorithm
A* Search
A* performed best because it:

✅ Finds optimal paths ✅ Balances speed and safety ✅ Uses heuristic intelligence ✅ Handles risk-aware planning

Formula Used
f(n)=g(n)+h(n)

Where:

g(n) = actual path cost
h(n) = estimated distance to goal
Constraint Satisfaction Problem (CSP)
The CSP module allocates victims to rescue resources while satisfying hard constraints.

Available Resources
2 Ambulances
1 Rescue Team
10 Medical Kits
Constraints
Maximum 2 victims per ambulance
Rescue team handles only 1 victim
Critical victims preferred for ambulances
CSP Heuristics Used
✅ MRV (Minimum Remaining Values) ✅ Degree Heuristic ✅ Forward Checking ✅ Backtracking

Machine Learning Module
Machine Learning predicts victim survival probability.

Models Used
Model	Purpose
🧮 Naive Bayes	Probability-based prediction
👥 KNN	Similar victim analysis
📊 ML Evaluation Metrics
Accuracy
Precision
Recall
F1 Score
Confusion Matrix
Fuzzy Logic & Uncertainty Handling
Disaster environments are uncertain.

Fuzzy logic helps evaluate:

Fire hazards Aftershock probability Blocked roads Risk exposure

Risk Categories
Score	Risk Level
0–24	🟢 Low
25–49	🟡 Medium
50–74	🟠 High
75+	🔴 Very High
Dynamic Environment & Replanning
AIDRA supports real-time environmental changes.

Dynamic Events
✅ Roads become blocked ✅ Hazards spread ✅ Risk zones change

When a blockage appears:

Agent detects obstacle
Route becomes invalid
A* replans automatically
Rescue continues safely
Environment Setup
Grid Configuration
Item	Position
🏥 Base	(0,0)
🏨 Hospital 1	(0,5)
🏨 Hospital 2	(4,0)
🔥 Risk Zone	(2,2)
🚧 Blocked Road	(1,1)
Victim Information
Victim	Severity	Position
V1	🔴 Critical	(0,3)
V2	🟠 Moderate	(3,4)
V3	🟢 Minor	(5,5)
V4	🔴 Critical	(2,0)
V5	🟠 Moderate	(4,2)
Performance Metrics (KPIs)
The system evaluates performance using:

✅ Victims Saved ✅ Average Rescue Time ✅ Resource Utilization ✅ Risk Exposure Score ✅ Path Optimality Ratio ✅ ML Accuracy ✅ CSP Backtracks

GUI Features
The GUI provides a visual rescue simulation.

GUI Includes
✅ Animated Ambulance Movement ✅ Real-Time Route Display ✅ Victim Visualization ✅ Dynamic Blockage Updates ✅ Rescue Path Animation ✅ KPI Dashboard Graphs

Sample Console Output
🏆 ARTIFICIAL INTELLIGENCE CCP - AIDRA SYSTEM

🔍 SEARCH ALGORITHM COMPARISON

BFS       Path Length: 4
DFS       Path Length: 4
Greedy    Path Length: 4
A*        Path Length: 4

✅ Best algorithm: A*

 PERFORMANCE REPORT

Victims Saved: 5/5
Average Rescue Time: 4.50
Resource Utilization: 100%
Technologies Used
Technology	Purpose
🐍 Python	Core Development
🖼 Tkinter	GUI Interface
📊 Matplotlib	KPI Graphs
🔢 NumPy	Numerical Processing
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
├── triage_data.csv
├── gui.py
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
Intelligent Systems for Smarter Rescue Operations 🚑
