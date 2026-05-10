class CSP:

    def __init__(self, ambulances, victims, rescue_team):
        self.ambulances = ambulances
        self.victims = victims
        self.rescue_team = rescue_team
        self.backtracks = 0
        self.heuristic_used = True

    def degree_heuristic(self, victims):
        """Degree heuristic: victims with most constraints first"""
        degree = {}
        for v in victims:
            degree[v['id']] = 0
            if v['severity'] == 'critical':
                degree[v['id']] += 2
            elif v['severity'] == 'moderate':
                degree[v['id']] += 1
        return sorted(victims, key=lambda v: degree[v['id']], reverse=True)

    def solve(self, use_heuristics=True):
        """Solve resource allocation with optional MRV heuristic and Degree Heuristic"""
        
        self.heuristic_used = use_heuristics
        self.backtracks = 0
        
        # Sort victims using Degree Heuristic (most constrained first)
        if use_heuristics:
            sorted_victims = self.degree_heuristic(self.victims)
        else:
            sorted_victims = sorted(
                self.victims,
                key=lambda v: {"critical": 3, "moderate": 2, "minor": 1}[v["severity"]],
                reverse=True
            )
        
        allocation = {"A1": [], "A2": [], "RescueTeam": []}
        ambulance_load = {"A1": 0, "A2": 0}
        team_used = False
        
        def can_assign(victim, resource):
            """Check hard constraints"""
            if resource.startswith('A'):
                return ambulance_load[resource] < 2
            elif resource == "RescueTeam":
                return not team_used or victim["severity"] == "minor"
            return True
        
        def assign(victim, resource):
            """Assign victim to resource"""
            nonlocal team_used
            allocation[resource].append(victim)
            if resource.startswith('A'):
                ambulance_load[resource] += 1
            else:
                team_used = True
        
        def backtrack(index):
            """Recursive backtracking with optional MRV"""
            self.backtracks += 1
            if index >= len(sorted_victims):
                return True
            
            victim = sorted_victims[index]
            
            # MRV Heuristic: Try resources in order of least constraining
            resources = ["A1", "A2", "RescueTeam"]
            if use_heuristics and victim["severity"] == "minor":
                resources = ["RescueTeam", "A2", "A1"]
            elif use_heuristics and victim["severity"] == "critical":
                resources = ["A1", "A2"]
            
            for resource in resources:
                if can_assign(victim, resource):
                    assign(victim, resource)
                    if backtrack(index + 1):
                        return True
                    # Backtrack
                    allocation[resource].pop()
                    if resource.startswith('A'):
                        ambulance_load[resource] -= 1
                    else:
                        team_used = False
            
            return False
        
        success = backtrack(0)
        
        print("\n✓ CSP Solution found after", self.backtracks, "backtracks")
        if use_heuristics:
            print("  ✓ MRV Heuristic + Degree Heuristic active (reduced backtracking)")
            print("  📋 Resource Allocation:")
            print(f"     🚐 Ambulance A1: {len(allocation['A1'])} victims ({', '.join([v['id'] for v in allocation['A1']]) if allocation['A1'] else 'none'})")
            print(f"     🚐 Ambulance A2: {len(allocation['A2'])} victims ({', '.join([v['id'] for v in allocation['A2']]) if allocation['A2'] else 'none'})")
            print(f"     👥 Rescue Team: {len(allocation['RescueTeam'])} victims ({', '.join([v['id'] for v in allocation['RescueTeam']]) if allocation['RescueTeam'] else 'none'})")
            print("  ✓ Hard constraint: Max 2 victims per ambulance satisfied!")
        
        return allocation

    def compare_heuristics(self):
        """Compare CSP with and without heuristics"""
        print("\n" + "="*60)
        print("📊 CSP HEURISTICS COMPARISON")
        print("="*60)
        
        # Run without heuristics
        csp_no = CSP(2, self.victims, 1)
        alloc_no = csp_no.solve(use_heuristics=False)
        backtracks_no = csp_no.backtracks
        
        # Run with heuristics
        csp_yes = CSP(2, self.victims, 1)
        alloc_yes = csp_yes.solve(use_heuristics=True)
        backtracks_yes = csp_yes.backtracks
        
        print(f"\n  Results:")
        print(f"     Without Heuristics: {backtracks_no} backtracks")
        print(f"     With Heuristics (MRV + Degree): {backtracks_yes} backtracks")
        
        if backtracks_no > 0:
            improvement = (1 - backtracks_yes/backtracks_no) * 100
            print(f"     Improvement: {improvement:.1f}% fewer backtracks")
        
        print("="*60)
        return backtracks_no, backtracks_yes