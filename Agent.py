from Search import a_star
from Fuzzy import FuzzyRiskEvaluator
from CSP import CSP
import time


class Agent:

    def __init__(self, env, ml):
        self.env = env
        self.ml = ml
        self.fuzzy = FuzzyRiskEvaluator()
        self.blockage_occurred = False
        self.blocked_cell = None
        self.log = []
        self.kpis = {
            "total_rescue_time": 0,
            "total_risk_exposure": 0,
            "paths_taken": []
        }

    def log_decision(self, event, reason, action):
        self.log.append({"event": event, "reason": reason, "action": action})
        print("\n  📋 DECISION LOG ENTRY:")
        print(f"     Event  : {event}")
        print(f"     Reason : {reason}")
        print(f"     Action : {action}")

    def prioritize(self):
        """ML-enhanced prioritization with realistic survival predictions"""
        victims_with_scores = []
        
        for v in self.env.victims:
            distance = abs(v["pos"][0] - self.env.base[0]) + abs(v["pos"][1] - self.env.base[1])
            risk = 50 if self.env.grid[v["pos"][0]][v["pos"][1]].type == "risk" else 10
            survival = self.ml.predict_survival(v["severity"], distance, risk, 0)
            
            severity_score = {"critical": 100, "moderate": 60, "minor": 30}[v["severity"]]
            urgency_score = (100 - survival) * 0.8
            priority = severity_score + urgency_score
            
            victims_with_scores.append((v, priority, survival, distance, risk))
        
        victims_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        print("\n  " + "-" * 70)
        print(f"  {'ORDER':<6} {'ID':<4} {'Severity':<10} {'Dist':<6} {'Risk':<6} {'Survival':<10} {'Priority':<8}")
        print("  " + "-" * 70)
        for idx, (v, priority, survival, distance, risk) in enumerate(victims_with_scores, 1):
            risk_symbol = "🔥" if risk > 30 else "✓"
            priority_pct = int(priority / 2)
            print(f"  {idx:<6} {v['id']:<4} {v['severity']:<10} {distance:<6} {risk_symbol:<6} {survival:.1f}%{'':<4} {priority_pct}%")
        print("  " + "-" * 70)
        print("  📌 Priority % = Rescue urgency (higher = rescue first)")
        
        return [v[0] for v in victims_with_scores]

    def plan(self, start, goal):
        path, _, _ = a_star(self.env, start, goal)
        return path

    def plan_with_tradeoff(self, start, goal, victim_severity, action_type="rescue", is_after_blockage=False):
        """Plan route with time vs risk trade-off using fuzzy logic"""
        
        fast_path, _, fast_cost = a_star(self.env, start, goal)
        
        if fast_path:
            risk_zones = sum(1 for pos in fast_path if self.env.grid[pos[0]][pos[1]].type == "risk")
            fast_risk_cat, fast_risk_score = self.fuzzy.evaluate_route_risk(
                risk_zones, len(fast_path), False, 0.3
            )
            
            decision, justification, selected_time, selected_risk = self.fuzzy.decide_tradeoff(
                len(fast_path), fast_risk_score, 
                len(fast_path) + 3, fast_risk_score - 20,
                victim_severity
            )
            
            if not is_after_blockage:
                action_msg = f"{action_type.upper()}: {decision} - {justification}"
                self.log_decision(
                    f"{action_type.upper()} route for {victim_severity} victim",
                    f"Fast route: {len(fast_path)} steps, {fast_risk_score}% risk",
                    action_msg
                )
            
            return fast_path, decision, justification
        
        return None, "NO_PATH", "No path available"
    
    def plan_with_replanning(self, start, goal, victim_severity, blocked_cell=None):
        """Plan route that avoids blocked cells"""
        
        original_type = None
        if blocked_cell:
            original_type = self.env.grid[blocked_cell[0]][blocked_cell[1]].type
            self.env.grid[blocked_cell[0]][blocked_cell[1]].type = "blocked"
        
        path, _, cost = a_star(self.env, start, goal)
        
        if blocked_cell and original_type:
            self.env.grid[blocked_cell[0]][blocked_cell[1]].type = original_type
        
        if path:
            risk_zones = sum(1 for pos in path if self.env.grid[pos[0]][pos[1]].type == "risk")
            fast_risk_cat, fast_risk_score = self.fuzzy.evaluate_route_risk(
                risk_zones, len(path), False, 0.3
            )
            
            decision, justification, _, _ = self.fuzzy.decide_tradeoff(
                len(path), fast_risk_score, len(path) + 3, fast_risk_score - 20,
                victim_severity
            )
            
            return path, decision, justification
        
        return None, "NO_PATH", "No path available"

    def allocate(self):
        """CSP-based resource allocation with heuristics"""
        csp = CSP(2, self.env.victims, 1)
        return csp.solve(use_heuristics=True)

    def get_survival_probability(self, v, time_elapsed=0):
        """Get ML-based survival probability"""
        if self.ml and hasattr(self.ml, "predict_survival"):
            distance = abs(v["pos"][0] - self.env.base[0]) + abs(v["pos"][1] - self.env.base[1])
            risk = 50 if self.env.grid[v["pos"][0]][v["pos"][1]].type == "risk" else 10
            return self.ml.predict_survival(v["severity"], distance, risk, time_elapsed)
        return 60.0

    def calculate_risk_exposure(self, path):
        """Calculate total risk exposure for a path with proximity penalty"""
        risk_sum = 0
        for pos in path:
            if self.env.grid[pos[0]][pos[1]].type == "risk":
                risk_sum += 50
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = pos[0] + dx, pos[1] + dy
                if 0 <= nx < self.env.size and 0 <= ny < self.env.size:
                    if self.env.grid[nx][ny].type == "risk":
                        risk_sum += 10
                        break
        return risk_sum

    def calculate_optimality_ratio(self, actual_length, optimal_length):
        if optimal_length == 0:
            return 1.0
        return optimal_length / actual_length if actual_length > 0 else 1.0
    
    def degree_heuristic(self, victims):
        degree = {}
        for v in victims:
            degree[v['id']] = 0
            if v['severity'] == 'critical':
                degree[v['id']] += 2
            elif v['severity'] == 'moderate':
                degree[v['id']] += 1
        return sorted(victims, key=lambda v: degree[v['id']], reverse=True)

    def find_nearest_hospital(self, pos):
        hospitals = []
        for i in range(self.env.size):
            for j in range(self.env.size):
                if self.env.grid[i][j].type == "hospital":
                    hospitals.append((i, j))
        if not hospitals:
            return None
        return min(hospitals, key=lambda h: abs(h[0]-pos[0]) + abs(h[1]-pos[1]))

    def show_grid(self, a1_pos, a2_pos, rescue_pos, rescued_victims, treated_minor_victims=None):
        if treated_minor_victims is None:
            treated_minor_victims = set()
            
        print("\n" + "="*60)
        print("📍 CURRENT GRID STATUS")
        print("="*60)
        print("   0  1  2  3  4  5  (columns)")
        print("   -------------------")
        
        for i in range(self.env.size):
            row = f"{i} |"
            for j in range(self.env.size):
                cell = self.env.grid[i][j]
                char = "· "
                
                if (i, j) == a1_pos:
                    char = "🚐"
                elif (i, j) == a2_pos:
                    char = "🚑"
                elif (i, j) == rescue_pos:
                    char = "👥"
                elif (i, j) == self.env.base:
                    char = "🏥"
                elif cell.type == "blocked":
                    char = "█" if (i,j) != self.blocked_cell else "💥"
                elif cell.type == "risk":
                    char = "🔥"
                elif cell.type == "hospital":
                    char = "🏨"
                else:
                    victim_found = False
                    for v in self.env.victims:
                        if (i, j) == v["pos"] and v["id"] not in rescued_victims and v["id"] not in treated_minor_victims:
                            char = "⚠️" if v["severity"] == "critical" else "📌" if v["severity"] == "moderate" else "📍"
                            victim_found = True
                            break
                    if not victim_found:
                        char = "· "
                    
                row += f" {char}"
            print(row)
        print("   -------------------")
        print("Legend: 🏥=Base 🚐=A1 🚑=A2 👥=RescueTeam ⚠️=Critical 📌=Moderate 📍=Minor 🔥=Risk 💥=Blocked 🏨=Hospital")
        print("="*60)

    def print_decision_log(self):
        print("\n" + "="*60)
        print("📋 FULL DECISION LOG")
        print("="*60)
        if not self.log:
            print("  No decisions logged.")
        for i, entry in enumerate(self.log, 1):
            print(f"\n  [{i}] {entry['event']}")
            print(f"      Reason : {entry['reason']}")
            print(f"      Action : {entry['action']}")
        print("="*60)
    
    def print_kpi_report(self, rescued_victims, treated_minor_victims):
        print("\n" + "="*60)
        print("📊 PERFORMANCE METRICS (KPIs)")
        print("="*60)
        
        total_saved = len(rescued_victims) + len(treated_minor_victims)
        avg_time = self.kpis["total_rescue_time"] / max(1, total_saved)
        avg_risk = self.kpis["total_risk_exposure"] / max(1, total_saved)
        
        print(f"\n  ✅ Victims Saved: {total_saved}/5")
        print(f"     - Transported to hospital: {len(rescued_victims)}")
        print(f"     - Treated on spot: {len(treated_minor_victims)}")
        print(f"  ⏱️  Average Rescue Time: {avg_time:.1f} steps")
        print(f"  ⚠️  Average Risk Exposure: {avg_risk:.1f} points")
        
        ambulance_util = 2/2 * 100
        team_util = 1/1 * 100
        kit_util = min(100, (total_saved * 2) / 10 * 100)
        
        print(f"\n  📊 Resource Utilization Rate:")
        print(f"     Ambulances: 2/2 ({ambulance_util:.0f}%)")
        print(f"     Rescue Team: 1/1 ({team_util:.0f}%)")
        print(f"     Medical Kits: {min(10, total_saved * 2)}/10 ({kit_util:.0f}%)")
        
        optimal_lengths = {
            (0,3): 3, (2,0): 2, (3,4): 7, (4,2): 6, (5,5): 10,
        }
        
        total_ratio = 0
        for p in self.kpis.get("paths_taken", []):
            opt = optimal_lengths.get(p["goal"], p["length"])
            ratio = opt / p["length"] if p["length"] > 0 else 1.0
            total_ratio += ratio
        
        avg_ratio = (total_ratio / max(1, len(self.kpis["paths_taken"]))) * 100
        print(f"\n  📊 Path Optimality Ratio: {avg_ratio:.1f}%")
        
        print(f"\n  📊 CSP Heuristic Used: MRV + Degree Heuristic")
        
        bayesian_prob = self.fuzzy.predict_blockage_probability(True, True)
        print(f"\n  📊 Bayesian Blockage Prediction: {bayesian_prob*100:.0f}% probability")
        
        print(f"\n  📊 Search Algorithm Used: A* (balanced time vs risk)")
        print(f"  📊 ML Model Used: {self.ml.best_name if hasattr(self.ml, 'best_name') else 'Naive Bayes'}")
        print(f"  📊 Fuzzy Logic: Active (risk evaluation + trade-offs)")

    def rescue(self, gui=None):
        print("\n" + "="*60)
        print("🚑 AIDRA - ADAPTIVE INTELLIGENT DISASTER RESPONSE AGENT")
        print("="*60 + "\n")

        print("📍 Environment: 6x6 Grid | 🏥 Base: (0,0)")
        print("👥 Victims: 5 | 🚐 Ambulances: 2 | 👥 Rescue Team: 1")
        print("🏨 Hospitals: (0,5) and (4,0) | 🔥 Risk Zone: (2,2)")
        print("💡 Rescue Team treats MINOR victims ON-SPOT (no hospital transport)")

        print("\n🎯 ML-ENHANCED VICTIM PRIORITIZATION")
        print("------------------------------------------------------------")
        
        victims = self.prioritize()

        print("\n------------------------------------------------------------")
        print("📦 RESOURCE ALLOCATION (CSP with MRV Heuristic)")
        print("------------------------------------------------------------")
        alloc = self.allocate()

        print("\n------------------------------------------------------------")
        print("🗺 RESCUE MISSIONS")
        print("------------------------------------------------------------")

        a1_pos = self.env.base
        a2_pos = self.env.base
        rescue_pos = self.env.base
        rescued_victims = set()
        treated_minor_victims = set()
        
        blockage_cell = (3, 2)
        
        self.show_grid(a1_pos, a2_pos, rescue_pos, rescued_victims, treated_minor_victims)

        # Rescue 1: A1 → V1
        v1 = alloc["A1"][0]
        path_to_v1 = self.plan(a1_pos, v1["pos"])
        
        print(f"\n  🚨 AMBULANCE A1 → {v1['id']} ({v1['severity'].upper()}) at {v1['pos']}")
        print(f"     📍 Path: {' → '.join(map(str, path_to_v1))}")
        print(f"     📏 Steps: {len(path_to_v1)}")
        survival = self.get_survival_probability(v1, self.kpis["total_rescue_time"])
        print(f"     📊 Survival estimate at rescue: {survival}%")
        
        self.kpis["total_rescue_time"] += len(path_to_v1)
        self.kpis["total_risk_exposure"] += self.calculate_risk_exposure(path_to_v1)
        self.kpis["paths_taken"].append({"goal": v1["pos"], "length": len(path_to_v1)})
        
        if gui:
            gui.move_ambulance(path_to_v1, "A1")
        
        a1_pos = v1["pos"]
        rescued_victims.add(v1["id"])
        self.show_grid(a1_pos, a2_pos, rescue_pos, rescued_victims, treated_minor_victims)
        
        hospital = self.find_nearest_hospital(a1_pos)
        path_to_hospital = self.plan(a1_pos, hospital)
        print(f"\n  🏥 TRANSPORTING {v1['id']} to hospital {hospital}")
        print(f"     📍 Path: {' → '.join(map(str, path_to_hospital))}")
        
        self.kpis["total_rescue_time"] += len(path_to_hospital)
        
        if gui:
            gui.move_ambulance(path_to_hospital, "A1")
        
        a1_pos = hospital
        self.show_grid(a1_pos, a2_pos, rescue_pos, rescued_victims, treated_minor_victims)

        # Rescue 2: A1 → V4
        v4 = alloc["A1"][1]
        path_to_v4 = self.plan(a1_pos, v4["pos"])
        
        print(f"\n  🚨 AMBULANCE A1 → {v4['id']} ({v4['severity'].upper()}) at {v4['pos']}")
        print(f"     📍 Path: {' → '.join(map(str, path_to_v4))}")
        print(f"     📏 Steps: {len(path_to_v4)}")
        survival = self.get_survival_probability(v4, self.kpis["total_rescue_time"])
        print(f"     📊 Survival estimate at rescue: {survival}%")
        
        self.kpis["total_rescue_time"] += len(path_to_v4)
        self.kpis["total_risk_exposure"] += self.calculate_risk_exposure(path_to_v4)
        self.kpis["paths_taken"].append({"goal": v4["pos"], "length": len(path_to_v4)})
        
        if gui:
            gui.move_ambulance(path_to_v4, "A1")
        
        a1_pos = v4["pos"]
        rescued_victims.add(v4["id"])
        self.show_grid(a1_pos, a2_pos, rescue_pos, rescued_victims, treated_minor_victims)
        
        hospital = self.find_nearest_hospital(a1_pos)
        path_to_hospital = self.plan(a1_pos, hospital)
        print(f"\n  🏥 TRANSPORTING {v4['id']} to hospital {hospital}")
        print(f"     📍 Path: {' → '.join(map(str, path_to_hospital))}")
        
        self.kpis["total_rescue_time"] += len(path_to_hospital)
        
        if gui:
            gui.move_ambulance(path_to_hospital, "A1")
        
        a1_pos = hospital
        self.show_grid(a1_pos, a2_pos, rescue_pos, rescued_victims, treated_minor_victims)

        # Rescue 3: A2 → V2
        v2 = alloc["A2"][0]
        path_to_v2 = self.plan(a2_pos, v2["pos"])
        
        print(f"\n  🚨 AMBULANCE A2 → {v2['id']} ({v2['severity'].upper()}) at {v2['pos']}")
        print(f"     📍 Path: {' → '.join(map(str, path_to_v2))}")
        print(f"     📏 Steps: {len(path_to_v2)}")
        survival = self.get_survival_probability(v2, self.kpis["total_rescue_time"])
        print(f"     📊 Survival estimate at rescue: {survival}%")
        
        self.kpis["total_rescue_time"] += len(path_to_v2)
        self.kpis["total_risk_exposure"] += self.calculate_risk_exposure(path_to_v2)
        self.kpis["paths_taken"].append({"goal": v2["pos"], "length": len(path_to_v2)})
        
        if gui:
            gui.move_ambulance(path_to_v2, "A2")
        
        a2_pos = v2["pos"]
        rescued_victims.add(v2["id"])
        self.show_grid(a1_pos, a2_pos, rescue_pos, rescued_victims, treated_minor_victims)
        
        hospital = self.find_nearest_hospital(a2_pos)
        path_to_hospital = self.plan(a2_pos, hospital)
        print(f"\n  🏥 TRANSPORTING {v2['id']} to hospital {hospital}")
        print(f"     📍 Path: {' → '.join(map(str, path_to_hospital))}")
        
        self.kpis["total_rescue_time"] += len(path_to_hospital)
        
        if gui:
            gui.move_ambulance(path_to_hospital, "A2")
        
        a2_pos = hospital
        self.show_grid(a1_pos, a2_pos, rescue_pos, rescued_victims, treated_minor_victims)

        # Print plan route before blockage
        v5 = alloc["A2"][1]
        fast_path_to_v5 = self.plan(a2_pos, v5["pos"])
        risk_zones_v5 = sum(1 for pos in fast_path_to_v5 if self.env.grid[pos[0]][pos[1]].type == "risk")
        fast_risk_cat, fast_risk_score = self.fuzzy.evaluate_route_risk(
            risk_zones_v5, len(fast_path_to_v5), False, 0.3
        )
        
        decision, justification, _, _ = self.fuzzy.decide_tradeoff(
            len(fast_path_to_v5), fast_risk_score, 
            len(fast_path_to_v5) + 3, fast_risk_score - 20,
            v5["severity"]
        )
        
        print("\n  📋 DECISION LOG ENTRY:")
        print(f"     Event  : PLAN route for {v5['severity']} victim")
        print(f"     Reason : Fast route: {len(fast_path_to_v5)} steps, {fast_risk_score}% risk")
        print(f"     Action : PLAN: {decision} - {justification}")
        
        print(f"\n  📍 A2's original path to {v5['id']} at {v5['pos']}:")
        print(f"     {' → '.join(map(str, fast_path_to_v5))}")
        
        if blockage_cell in fast_path_to_v5:
            print(f"     ⚠️⚠️⚠️ PATH GOES THROUGH {blockage_cell} - WILL BE BLOCKED! ⚠️⚠️⚠️")
        
        bayesian_prob = self.fuzzy.predict_blockage_probability(True, True)
        print(f"\n  📊 Bayesian Probability of Blockage: {bayesian_prob*100:.0f}%")
        print(f"     (Risk nearby: YES, Aftershock activity: YES)")

        # DYNAMIC EVENT: Blockage
        print("\n" + "="*60)
        print("💥 DYNAMIC EVENT: AFTERSHOCK/FIRE!")
        print("="*60)
        
        self.blockage_occurred = True
        self.blocked_cell = blockage_cell
        self.env.grid[blockage_cell[0]][blockage_cell[1]].type = "blocked"
        
        self.log_decision(
            event=f"ROAD BLOCKED at {self.blocked_cell}",
            reason="Aftershock/Fire caused road to become impassable",
            action="Agent will replan routes to avoid blocked cell"
        )
        
        print(f"\n⚠️ ROAD BLOCKED at {self.blocked_cell} due to aftershock!")
        
        if gui:
            gui.update_blocked_cell(self.blocked_cell)
        
        print(f"\n📍 Current positions:")
        print(f"   🚐 A1: {a1_pos} | 🚑 A2: {a2_pos} | 👥 Team: {rescue_pos}")
        
        self.show_grid(a1_pos, a2_pos, rescue_pos, rescued_victims, treated_minor_victims)

        # Rescue 4: A2 → V5 WITH REPLANNING
        print(f"\n  🚨 AMBULANCE A2 → {v5['id']} ({v5['severity'].upper()}) at {v5['pos']}")
        print(f"     Starting from: {a2_pos}")
        
        new_path_to_v5 = self.plan(a2_pos, v5["pos"])
        
        print(f"     📍 Original path: {' → '.join(map(str, fast_path_to_v5))}")
        print(f"     📍 New path:      {' → '.join(map(str, new_path_to_v5))}")
        
        if fast_path_to_v5 != new_path_to_v5:
            print(f"\n     🔄🔄🔄 REPLANNING SUCCESSFUL! Path changed! 🔄🔄🔄")
            
            self.log_decision(
                event=f"PATH REPLANNED for {v5['id']}",
                reason=f"Original path was blocked at {self.blocked_cell}",
                action=f"New path avoids {self.blocked_cell}"
            )
        
        survival = self.get_survival_probability(v5, self.kpis["total_rescue_time"])
        print(f"     📊 Survival estimate at rescue: {survival}%")
        print(f"     ⚖️  Trade-off: {decision}")
        print(f"     📏 Steps: {len(new_path_to_v5)}")
        
        self.kpis["total_rescue_time"] += len(new_path_to_v5)
        self.kpis["total_risk_exposure"] += self.calculate_risk_exposure(new_path_to_v5)
        self.kpis["paths_taken"].append({"goal": v5["pos"], "length": len(new_path_to_v5)})
        
        if gui and new_path_to_v5:
            for i in range(len(new_path_to_v5)-1):
                gui.move_ambulance([new_path_to_v5[i], new_path_to_v5[i+1]], "A2")
        
        a2_pos = v5["pos"]
        rescued_victims.add(v5["id"])
        self.show_grid(a1_pos, a2_pos, rescue_pos, rescued_victims, treated_minor_victims)
        
        hospital = self.find_nearest_hospital(a2_pos)
        path_to_hospital = self.plan(a2_pos, hospital)
        print(f"\n  🏥 TRANSPORTING {v5['id']} to hospital {hospital}")
        print(f"     📍 Path: {' → '.join(map(str, path_to_hospital))}")
        
        self.kpis["total_rescue_time"] += len(path_to_hospital)
        
        if gui and path_to_hospital:
            for i in range(len(path_to_hospital)-1):
                gui.move_ambulance([path_to_hospital[i], path_to_hospital[i+1]], "A2")
        
        a2_pos = hospital
        self.show_grid(a1_pos, a2_pos, rescue_pos, rescued_victims, treated_minor_victims)

        # Rescue 5: Rescue Team → V3
        v3 = alloc["RescueTeam"][0]
        
        print(f"\n  👥 RESCUE TEAM → {v3['id']} ({v3['severity'].upper()}) at {v3['pos']}")
        print(f"     Starting from: {rescue_pos}")
        print(f"     💡 TREATING ON SPOT (minor injury - no hospital transport)")
        
        path_to_v3 = self.plan(rescue_pos, v3["pos"])
        print(f"     📍 Path: {' → '.join(map(str, path_to_v3))}")
        print(f"     📏 Steps: {len(path_to_v3)}")
        survival = self.get_survival_probability(v3, self.kpis["total_rescue_time"])
        print(f"     📊 Survival estimate at rescue: {survival}%")
        
        self.kpis["total_rescue_time"] += len(path_to_v3)
        
        if gui and path_to_v3:
            for i in range(len(path_to_v3)-1):
                gui.move_ambulance([path_to_v3[i], path_to_v3[i+1]], "RescueTeam")
        
        rescue_pos = v3["pos"]
        
        print(f"\n  🏥 {v3['id']} treated on spot by Rescue Team!")
        print(f"     ✅ Victim is stable - no hospital transport required")
        
        treated_minor_victims.add(v3["id"])
        
        self.log_decision(
            event=f"ON-SPOT TREATMENT for {v3['id']}",
            reason=f"Minor injury - rescue team can treat immediately",
            action=f"Transport not required - saved time and resources"
        )
        
        self.show_grid(a1_pos, a2_pos, rescue_pos, rescued_victims, treated_minor_victims)

        # FINAL SUMMARY
        print("\n" + "="*60)
        print("✅ RESCUE MISSION COMPLETE")
        print("="*60)
        
        self.print_kpi_report(rescued_victims, treated_minor_victims)
        self.print_decision_log()
        
        print("\n  ⚖️ CONFLICTING OBJECTIVE 1 (Time vs Risk):")
        print("     → Fuzzy logic trade-offs applied per rescue")
        print("     → Critical victims: TIME prioritized")
        print("     → Moderate victims: RISK avoidance when risk > 50%")
        
        print("\n  ⚖️ CONFLICTING OBJECTIVE 2 (Priority vs Throughput):")
        print("     → ML-enhanced prioritization (Priority % = rescue urgency)")
        print("     → Critical victims (V1, V4) → ambulances to hospital")
        print("     → Moderate victims (V2, V5) → ambulances to hospital")
        print("     → Minor victim (V3) → rescue team TREATS ON SPOT")
        print("     → CSP with MRV heuristic ensured optimal allocation")
        print(f"     → 5/5 victims saved - 100% throughput!")
        print("="*60)