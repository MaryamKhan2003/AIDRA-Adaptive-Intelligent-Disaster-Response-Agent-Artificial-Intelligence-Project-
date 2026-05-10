class FuzzyRiskEvaluator:
    def __init__(self):
        # Fuzzy rule base for risk assessment
        self.risk_levels = ["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
        self.tradeoff_log = []
        
    def evaluate_route_risk(self, risk_zone_count, route_length, has_blocked_nearby, aftershock_prob=0.3):
        """Evaluate route risk using fuzzy logic rules"""
        risk_score = 0
        
        # Rule 1: Risk zones increase danger (weight: 0-60)
        if risk_zone_count >= 2:
            risk_score += 60
        elif risk_zone_count == 1:
            risk_score += 30
        
        # Rule 2: Nearby blockages increase risk (weight: 0-40)
        if has_blocked_nearby:
            risk_score += 40
        
        # Rule 3: Long routes increase exposure time (weight: 0-20)
        if route_length > 8:
            risk_score += 20
        elif route_length > 5:
            risk_score += 10
        
        # Rule 4: Aftershock probability (uncertainty handling)
        risk_score += int(aftershock_prob * 30)
        
        # Cap at 100
        risk_score = min(100, risk_score)
        
        # Fuzzy membership
        if risk_score < 25:
            return "LOW", risk_score
        elif risk_score < 50:
            return "MEDIUM", risk_score
        elif risk_score < 75:
            return "HIGH", risk_score
        else:
            return "VERY_HIGH", risk_score
    
    def evaluate_route(self, path, env, victim_severity=None):
        """Evaluate route risk based on the actual path - returns 3 values"""
        if not path:
            return "UNKNOWN", 100, {}
        
        risk_zones = 0
        max_risk = 0
        
        for pos in path:
            if env.grid[pos[0]][pos[1]].type == "risk":
                risk_zones += 1
                max_risk = max(max_risk, 50)
        
        # Calculate risk score based on path
        route_length = len(path)
        has_blocked_nearby = False
        
        # Check for blocked roads nearby
        for pos in path:
            if hasattr(env, 'blocked_roads') and pos in env.blocked_roads:
                has_blocked_nearby = True
                break
        
        # Get category and score
        category, score = self.evaluate_route_risk(risk_zones, route_length, has_blocked_nearby, 0.3)
        
        # Return 3 values to match expected unpacking
        return category, score, {"risk_zones": risk_zones, "length": route_length}
    
    def decide_tradeoff(self, fast_route_time, fast_route_risk, safe_route_time, safe_route_risk, victim_severity):
        """Make trade-off decision between time and risk"""
        
        # Store decision for summary
        decision_info = {
            "fast_time": fast_route_time,
            "fast_risk": fast_route_risk,
            "safe_time": safe_route_time,
            "safe_risk": safe_route_risk,
            "severity": victim_severity
        }
        
        # Conflicting Objective 1: Rescue Time vs Risk Exposure
        if victim_severity == "critical":
            # Critical victim - prioritize time even if high risk
            decision = "TIME"
            justification = f"CRITICAL victim - immediate rescue needed despite {fast_route_risk}% risk"
            self.tradeoff_log.append({**decision_info, "decision": decision, "justification": justification})
            return decision, justification, fast_route_time, fast_route_risk
        
        elif fast_route_risk >= 70:
            # Very high risk - take safer longer route
            decision = "RISK"
            justification = f"High risk ({fast_route_risk}%) - taking safer route (+{safe_route_time - fast_route_time} steps)"
            self.tradeoff_log.append({**decision_info, "decision": decision, "justification": justification})
            return decision, justification, safe_route_time, safe_route_risk
        
        elif fast_route_risk >= 50 and victim_severity == "moderate":
            # Moderate risk with moderate victim - balanced approach
            decision = "BALANCED"
            justification = f"Moderate risk ({fast_route_risk}%) with moderate victim - balancing time and safety"
            self.tradeoff_log.append({**decision_info, "decision": decision, "justification": justification})
            return decision, justification, fast_route_time, fast_route_risk
        
        elif safe_route_time - fast_route_time <= 2:
            # Safe route is almost as fast
            decision = "RISK"
            justification = f"Safer route only +{safe_route_time - fast_route_time} steps - avoiding {fast_route_risk}% risk"
            self.tradeoff_log.append({**decision_info, "decision": decision, "justification": justification})
            return decision, justification, safe_route_time, safe_route_risk
        
        elif fast_route_risk < 30:
            # Low risk - take fast route
            decision = "TIME"
            justification = f"Low risk ({fast_route_risk}%) - fast route ({fast_route_time} steps)"
            self.tradeoff_log.append({**decision_info, "decision": decision, "justification": justification})
            return decision, justification, fast_route_time, fast_route_risk
        
        else:
            # Default balanced
            decision = "BALANCED"
            justification = f"Balancing {fast_route_time} steps vs {fast_route_risk}% risk"
            self.tradeoff_log.append({**decision_info, "decision": decision, "justification": justification})
            return decision, justification, fast_route_time, fast_route_risk
    
    def predict_blockage_probability(self, risk_nearby, aftershock_activity):
        """Bayesian-like reasoning for blockage probability"""
        base_prob = 0.1
        
        if risk_nearby:
            base_prob += 0.3
        
        if aftershock_activity:
            base_prob += 0.4
        
        return min(0.95, base_prob)
    
    def print_decision_summary(self):
        """Print summary of all trade-off decisions"""
        print("\n" + "="*60)
        print("⚖️ TRADE-OFF DECISION SUMMARY (Time vs Risk)")
        print("="*60)
        if not self.tradeoff_log:
            print("  No trade-off decisions recorded.")
        for i, d in enumerate(self.tradeoff_log, 1):
            print(f"\n  [{i}] {d.get('severity', 'Unknown').upper()} victim")
            print(f"      Decision: {d.get('decision', 'Unknown')}")
            print(f"      Fast route: {d.get('fast_time', '?')} steps, {d.get('fast_risk', '?')}% risk")
            print(f"      Safe route: {d.get('safe_time', '?')} steps, {d.get('safe_risk', '?')}% risk")
            print(f"      Reason: {d.get('justification', 'N/A')}")
        print("="*60)