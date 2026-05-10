import tkinter as tk
import time

CELL = 60

class GridGUI:
    def __init__(self, env):
        self.env = env
        self.root = tk.Tk()
        self.root.title("AIDRA - Adaptive Intelligent Disaster Response Agent")
        self.canvas = tk.Canvas(self.root, width=env.size * CELL, height=env.size * CELL, bg="#ecf0f1")
        self.canvas.pack()
        self.draw_grid()
        self.vehicles = {}
        
    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(self.env.size):
            for j in range(self.env.size):
                x1, y1 = j * CELL, i * CELL
                x2, y2 = x1 + CELL, y1 + CELL
                cell = self.env.grid[i][j]
                
                # Cell colors
                if cell.type == "blocked" or (i, j) in self.env.blocked_roads:
                    color = "#2c3e50"  # Dark gray for blocked
                elif cell.type == "risk":
                    risk = getattr(cell, 'risk_level', 50)
                    if risk > 70:
                        color = "#e74c3c"  # Red for high risk
                    else:
                        color = "#e67e22"  # Orange for risk
                elif cell.type == "hospital":
                    color = "#27ae60"  # Green for hospital
                elif cell.type == "base":
                    color = "#2980b9"  # Blue for base
                else:
                    # Check for victim
                    victim_here = False
                    for v in self.env.victims:
                        if (i, j) == v["pos"]:
                            victim_here = True
                            break
                    if victim_here:
                        color = "#f1c40f"  # Yellow for victim
                    else:
                        color = "#ecf0f1"  # Light gray for empty
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#bdc3c7")
                
                # Add labels
                if cell.type == "base":
                    self.canvas.create_text(x1+30, y1+30, text="🏥", font=("Arial", 20))
                elif cell.type == "hospital":
                    self.canvas.create_text(x1+30, y1+30, text="🏨", font=("Arial", 20))
                elif cell.type == "risk":
                    risk = getattr(cell, 'risk_level', 50)
                    self.canvas.create_text(x1+30, y1+30, text=f"{risk}", font=("Arial", 10))
                else:
                    for v in self.env.victims:
                        if (i, j) == v["pos"]:
                            if v["severity"] == "critical":
                                self.canvas.create_text(x1+30, y1+30, text="⚠️", font=("Arial", 16))
                            elif v["severity"] == "moderate":
                                self.canvas.create_text(x1+30, y1+30, text="📌", font=("Arial", 16))
                            else:
                                self.canvas.create_text(x1+30, y1+30, text="📍", font=("Arial", 16))
                            break
        self.root.update()
    
    def move_ambulance_with_replanning(self, original_path, new_path, blocked_cell, vehicle_id="A1"):
        """Move ambulance showing encounter with blockage and replanning"""
        if not original_path:
            return
        
        # Create vehicle if not exists
        if vehicle_id not in self.vehicles:
            if vehicle_id == "A1":
                color = "#f39c12"  # Orange for A1
            elif vehicle_id == "A2":
                color = "#e74c3c"  # Red for A2
            else:
                color = "#9b59b6"  # Purple for Rescue Team
            self.vehicles[vehicle_id] = self.canvas.create_oval(10, 10, 40, 40, fill=color, outline="#2c3e50", width=2)
        
        current_pos = original_path[0]
        self.canvas.coords(self.vehicles[vehicle_id],
                          current_pos[1]*CELL+10, current_pos[0]*CELL+10,
                          current_pos[1]*CELL+40, current_pos[0]*CELL+40)
        self.root.update()
        time.sleep(0.3)
        
        # Move along original path until blockage
        for i, next_pos in enumerate(original_path[1:], 1):
            # Update position
            self.canvas.coords(self.vehicles[vehicle_id], 
                              next_pos[1]*CELL+10, next_pos[0]*CELL+10,
                              next_pos[1]*CELL+40, next_pos[0]*CELL+40)
            self.root.update()
            time.sleep(0.25)
            current_pos = next_pos
            
            # Check if reached blocked cell
            if blocked_cell and next_pos == blocked_cell:
                print(f"\n     💥 {vehicle_id} REACHED BLOCKED CELL at {blocked_cell}!")
                
                # Show blocked cell with X mark
                x1, y1 = blocked_cell[1] * CELL, blocked_cell[0] * CELL
                x2, y2 = x1 + CELL, y1 + CELL
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#c0392b", outline="#bdc3c7")
                self.canvas.create_text(x1+30, y1+30, text="💥", font=("Arial", 20))
                self.root.update()
                time.sleep(0.5)
                
                # Show backtracking
                print(f"     ↩️ {vehicle_id} BACKTRACKING from {current_pos}...")
                
                # Move back to previous position
                prev_pos = original_path[i-1] if i > 0 else original_path[0]
                self.canvas.coords(self.vehicles[vehicle_id],
                                  prev_pos[1]*CELL+10, prev_pos[0]*CELL+10,
                                  prev_pos[1]*CELL+40, prev_pos[0]*CELL+40)
                self.root.update()
                time.sleep(0.3)
                current_pos = prev_pos
                
                # Now follow new path
                if new_path and len(new_path) > 0:
                    print(f"     🔄 {vehicle_id} TAKING NEW PATH from {current_pos}...")
                    for idx, new_pos in enumerate(new_path[1:], 1):
                        self.canvas.coords(self.vehicles[vehicle_id],
                                          new_pos[1]*CELL+10, new_pos[0]*CELL+10,
                                          new_pos[1]*CELL+40, new_pos[0]*CELL+40)
                        self.root.update()
                        time.sleep(0.25)
                        current_pos = new_pos
                    print(f"     ✅ {vehicle_id} successfully reached destination via new path!")
                return
        
        # If no blockage encountered, just follow original path
        for next_pos in original_path[1:]:
            self.canvas.coords(self.vehicles[vehicle_id],
                              next_pos[1]*CELL+10, next_pos[0]*CELL+10,
                              next_pos[1]*CELL+40, next_pos[0]*CELL+40)
            self.root.update()
            time.sleep(0.25)
    
    def move_ambulance(self, path, vehicle_id="A1"):
        """Simple movement without replanning (for normal paths)"""
        if not path:
            return
        if vehicle_id not in self.vehicles:
            if vehicle_id == "A1":
                color = "#f39c12"
            elif vehicle_id == "A2":
                color = "#e74c3c"
            else:
                color = "#9b59b6"
            self.vehicles[vehicle_id] = self.canvas.create_oval(10, 10, 40, 40, fill=color, outline="#2c3e50", width=2)
        
        # Show starting position
        start = path[0]
        self.canvas.coords(self.vehicles[vehicle_id],
                          start[1]*CELL+10, start[0]*CELL+10,
                          start[1]*CELL+40, start[0]*CELL+40)
        self.root.update()
        time.sleep(0.3)
        
        for pos in path[1:]:
            self.canvas.coords(self.vehicles[vehicle_id],
                              pos[1]*CELL+10, pos[0]*CELL+10,
                              pos[1]*CELL+40, pos[0]*CELL+40)
            self.root.update()
            time.sleep(0.25)
    
    def highlight_blocked_cell(self, cell):
        """Highlight a cell as blocked with X mark"""
        x1, y1 = cell[1] * CELL, cell[0] * CELL
        x2, y2 = x1 + CELL, y1 + CELL
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#c0392b", outline="#bdc3c7")
        self.canvas.create_text(x1+30, y1+30, text="💥", font=("Arial", 20))
        self.root.update()
    
    def update_blocked_cell(self, cell):
        """Update a cell to show as blocked"""
        x1, y1 = cell[1] * CELL, cell[0] * CELL
        x2, y2 = x1 + CELL, y1 + CELL
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#2c3e50", outline="#bdc3c7")
        self.canvas.create_text(x1+30, y1+30, text="█", font=("Arial", 20))
        self.root.update()
    
    def run(self):
        self.root.mainloop()