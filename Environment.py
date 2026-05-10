import random

class Cell:
    def __init__(self, x, y, t="empty"):
        self.x = x
        self.y = y
        self.type = t
        self.risk_level = 0  # 0-100 for dynamic risk


class Environment:
    def __init__(self, size):
        self.size = size
        self.grid = [[Cell(i, j) for j in range(size)] for i in range(size)]
        self.victims = []
        self.base = (0, 0)
        self.time_step = 0
        self.blocked_roads = set()
        self.risk_zones = set()
        
    def set_cell(self, x, y, t):
        self.grid[x][y].type = t
        if t == "risk":
            self.risk_zones.add((x, y))
            self.grid[x][y].risk_level = 50
            
    def get_neighbors(self, x, y):
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        res = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if self.grid[nx][ny].type != "blocked" and (nx, ny) not in self.blocked_roads:
                    res.append((nx, ny))
        return res
    
    def dynamic_event(self):
        """Random dynamic events like aftershocks"""
        self.time_step += 1
        events = []
        
        # 20% chance of new blockage at each time step
        if random.random() < 0.2 and len(self.risk_zones) > 0:
            risk_list = list(self.risk_zones)
            new_block = random.choice(risk_list)
            if new_block not in self.blocked_roads:
                self.blocked_roads.add(new_block)
                self.grid[new_block[0]][new_block[1]].type = "blocked"
                events.append(f"ROAD BLOCKED at {new_block} due to aftershock!")
        
        # Update risk levels dynamically
        for (x, y) in self.risk_zones:
            if (x, y) not in self.blocked_roads:
                self.grid[x][y].risk_level = min(100, self.grid[x][y].risk_level + random.randint(-10, 20))
                if self.grid[x][y].risk_level > 70 and random.random() < 0.3:
                    self.blocked_roads.add((x, y))
                    self.grid[x][y].type = "blocked"
                    events.append(f"🔥 FIRE SPREAD - Risk zone {x},{y} now BLOCKED!")
        
        return events
    
    def get_risk_score(self, pos):
        """Get current risk level at a position"""
        x, y = pos
        if self.grid[x][y].type == "risk":
            return self.grid[x][y].risk_level
        return 0
    
    def reset_dynamic(self):
        """Reset dynamic changes (for multiple runs)"""
        self.blocked_roads.clear()
        self.time_step = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j].type == "blocked" and (i, j) not in self.risk_zones:
                    self.grid[i][j].type = "empty"
                elif (i, j) in self.risk_zones:
                    self.grid[i][j].type = "risk"
                    self.grid[i][j].risk_level = 50