import heapq
from collections import deque


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def risk_heuristic(a, b, env):
    """Heuristic that considers risk zones"""
    base_dist = abs(a[0] - b[0]) + abs(a[1] - b[1])
    risk_penalty = env.get_risk_score(a) / 20 if hasattr(env, 'get_risk_score') else 0
    return base_dist + risk_penalty


def bfs(env, start, goal):
    q = deque([(start, [start])])
    visited = {start}
    nodes = 0
    while q:
        node, path = q.popleft()
        nodes += 1
        if node == goal:
            return path, nodes
        for n in env.get_neighbors(*node):
            if n not in visited:
                visited.add(n)
                q.append((n, path + [n]))
    return None, nodes


def dfs(env, start, goal):
    stack = [(start, [start])]
    visited = {start}
    nodes = 0
    while stack:
        node, path = stack.pop()
        nodes += 1
        if node == goal:
            return path, nodes
        for n in env.get_neighbors(*node):
            if n not in visited:
                visited.add(n)
                stack.append((n, path + [n]))
    return None, nodes


def greedy(env, start, goal):
    pq = [(heuristic(start, goal), start, [start])]
    visited = set()
    nodes = 0
    while pq:
        _, node, path = heapq.heappop(pq)
        nodes += 1
        if node == goal:
            return path, nodes
        if node in visited:
            continue
        visited.add(node)
        for n in env.get_neighbors(*node):
            if n not in visited:
                heapq.heappush(pq, (heuristic(n, goal), n, path + [n]))
    return None, nodes


def a_star(env, start, goal, risk_weight=1.0):
    """A* with configurable risk weight - higher risk_weight = more risk-avoiding"""
    pq = [(0, start, [start], 0)]
    visited = {}
    nodes = 0
    
    while pq:
        f, node, path, g = heapq.heappop(pq)
        nodes += 1
        if node == goal:
            return path, nodes, g
        if node in visited and visited[node] <= g:
            continue
        visited[node] = g
        
        for n in env.get_neighbors(*node):
            # Base movement cost
            move_cost = 1
            
            # Risk cost based on cell type
            if env.grid[n[0]][n[1]].type == "risk":
                risk = env.get_risk_score(n) if hasattr(env, 'get_risk_score') else 50
                move_cost += risk_weight * (risk / 20)
            
            ng = g + move_cost
            nf = ng + heuristic(n, goal)
            heapq.heappush(pq, (nf, n, path + [n], ng))
    
    return None, nodes, float("inf")


def a_star_safe(env, start, goal):
    """Risk-avoiding A* (high risk_weight)"""
    return a_star(env, start, goal, risk_weight=3.0)


def hill_climbing(env, start, goal):
    current = start
    path = [start]
    nodes = 0
    while current != goal:
        neighbors = env.get_neighbors(*current)
        nodes += 1
        if not neighbors:
            return None, nodes
        next_node = min(neighbors, key=lambda x: heuristic(x, goal))
        if heuristic(next_node, goal) >= heuristic(current, goal):
            break
        current = next_node
        path.append(current)
    return (path if current == goal else None), nodes


def simulated_annealing(env, start, goal, max_iter=1000, temp=100, cooling=0.995):
    """Local search with Simulated Annealing"""
    import random
    import math
    
    current = start
    path = [start]
    
    def path_cost(p):
        cost = 0
        for i in range(len(p) - 1):
            if env.grid[p[i+1][0]][p[i+1][1]].type == "risk":
                cost += 5
            else:
                cost += 1
        return cost
    
    def get_neighbor(p):
        if len(p) < 2:
            return p
        idx = random.randint(0, len(p) - 1)
        neighbors = env.get_neighbors(*p[idx])
        if neighbors and random.random() > 0.5:
            new_path = p[:idx] + [random.choice(neighbors)] + p[idx+1:]
            return new_path
        return p
    
    current_cost = path_cost(path)
    best_path = path[:]
    best_cost = current_cost
    
    for i in range(max_iter):
        new_path = get_neighbor(path)
        new_cost = path_cost(new_path)
        delta = new_cost - current_cost
        
        if delta < 0 or random.random() < math.exp(-delta / temp):
            path = new_path
            current_cost = new_cost
            if current_cost < best_cost:
                best_path = path[:]
                best_cost = current_cost
        
        temp *= cooling
        if temp < 0.1:
            break
    
    return best_path, max_iter, best_cost


def compare_search_algorithms(env, start, goal):
    results = {}
    
    for name, func in [
        ("BFS", bfs),
        ("DFS", dfs),
        ("Greedy", greedy),
        ("A*_Fast", lambda e, s, g: a_star(e, s, g, risk_weight=0.5)),
        ("A*_Balanced", lambda e, s, g: a_star(e, s, g, risk_weight=1.0)),
        ("A*_Safe", a_star_safe),
        ("HillClimb", hill_climbing)
    ]:
        res = func(env, start, goal)
        if len(res) == 3:
            path, nodes, cost = res
        else:
            path, nodes = res
            cost = len(path) if path else 999
        results[name] = {"path": path, "nodes": nodes, "cost": cost}
    
    return results