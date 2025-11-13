"""
Pathfinding algorithms: Dijkstra, A*, and advanced variants
Includes visualization support for explored nodes and frontiers
"""

import heapq
import math
from collections import OrderedDict, deque
from typing import Optional, Set, Tuple, List, Dict, Any
from config import (
    ENABLE_DIAGONALS, DEBUG_MODE, TERRAIN_COSTS, 
    AI_DIFFICULTY, AI_HEURISTIC_SCALE
)

class PathfindingResult:
    """Result wrapper for pathfinding algorithms"""
    def __init__(self):
        self.path: List[Tuple[int, int]] = []
        self.cost: float = float('inf')
        self.nodes_explored: int = 0
        self.explored_nodes: Set[Tuple[int, int]] = set()
        self.frontier_nodes: Set[Tuple[int, int]] = set()
        self.path_found: bool = False
        self.node_data: Dict[Tuple[int, int], Dict[str, Any]] = {}  # (x, y) -> {'g': cost, 'h': heuristic, 'f': total}

class Pathfinder:
    def __init__(self, maze, heuristic_type='MANHATTAN'):
        self.maze = maze
        self.heuristic_type = heuristic_type
        # LRU Cache for pathfinding results to reduce CPU usage
        # Key: (start, goal, algorithm, discovered_cells_hash)
        # Value: PathfindingResult
        self._path_cache: OrderedDict = OrderedDict()
        self._cache_max_size = 100  # Limit cache size to prevent memory issues
    
    # ==================== Common Helper Methods ====================
    
    def _reconstruct_path(self, came_from: Dict[Tuple[int, int], Tuple[int, int]], 
                          start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from came_from dictionary"""
        path = []
        node = goal
        while node in came_from:
            path.append(node)
            node = came_from[node]
        path.append(start)
        path.reverse()
        return path
    
    def _is_accessible(self, pos: Tuple[int, int], discovered_cells: Optional[Set[Tuple[int, int]]], 
                      start: Tuple[int, int], goal: Tuple[int, int]) -> bool:
        """Check if a cell is accessible (for fog of war)"""
        if discovered_cells is None:
            return True  # All cells visible
        # Start position (current position) is always accessible
        if pos == start:
            return True
        # Goal position is only accessible if discovered (true blindness)
        if pos == goal:
            return pos in discovered_cells
        # All other cells must be discovered
        return pos in discovered_cells
    
    def _get_neighbors_filtered(self, x: int, y: int, discovered_cells: Optional[Set[Tuple[int, int]]],
                                start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get neighbors filtered by accessibility (fog of war)"""
        neighbors = self.maze.get_neighbors(x, y, ENABLE_DIAGONALS)
        if discovered_cells is not None:
            neighbors = [n for n in neighbors if self._is_accessible(n, discovered_cells, start, goal)]
        return neighbors
    
    # ==================== Heuristic Methods ====================
    
    def manhattan_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """Manhattan distance heuristic"""
        return abs(x1 - x2) + abs(y1 - y2)
    
    def euclidean_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """Euclidean distance heuristic"""
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    def heuristic(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """Calculate heuristic value"""
        if self.heuristic_type == 'MANHATTAN':
            return self.manhattan_distance(x1, y1, x2, y2)
        else:
            return self.euclidean_distance(x1, y1, x2, y2)
    
    def predictive_pathfinding(self, start, goal, algorithm='ASTAR', discovered_cells=None):
        """
        Predictive pathfinding for dynamic obstacles (Obstacle Course mode).
        Simulates the entire path and accounts for obstacle changes at each turn.
        
        Strategy:
        1. Compute path using standard algorithm with CURRENT obstacles
        2. Simulate following that path, predicting obstacles at each turn
        3. Calculate true cost accounting for future obstacle states
        4. Return path with accurate cost prediction
        
        Args:
            start: Starting position
            goal: Goal position
            algorithm: Base algorithm to use ('ASTAR', 'DIJKSTRA', or 'BFS')
            discovered_cells: Fog of war cells
            
        Returns:
            PathfindingResult with path optimized for future obstacle changes
        """
        from config import DEBUG_MODE
        if DEBUG_MODE:
            print(f"[Predictive AI] Computing path with future obstacle prediction...")
        
        # First, compute base path with current obstacles
        if algorithm == 'ASTAR':
            base_result = self.a_star(start, goal, discovered_cells)
        elif algorithm == 'DIJKSTRA':
            base_result = self.dijkstra(start, goal, discovered_cells)
        elif algorithm == 'BFS':
            base_result = self.bfs(start, goal, discovered_cells)
        elif algorithm == 'BIDIRECTIONAL_ASTAR':
            base_result = self.bidirectional_a_star(start, goal, discovered_cells)
        else:
            base_result = self.a_star(start, goal, discovered_cells)
        
        if not base_result.path_found:
            return base_result
        
        # Now simulate following this path with future obstacle changes
        path = base_result.path
        current_turn = self.maze.turn_number
        total_predicted_cost = 0
        
        from config import DEBUG_MODE
        if DEBUG_MODE:
            print(f"[Predictive AI] Simulating {len(path)} moves starting from turn {current_turn}")
        
        # Get future obstacle configurations
        future_terrains = self.maze.get_future_obstacles(turns_ahead=len(path))
        
        # Calculate true cost of path considering future obstacles
        for i, pos in enumerate(path):
            # Determine which turn this move happens on
            turn_index = min(i, len(future_terrains) - 1) if future_terrains else 0
            
            # Get obstacle cost at this future turn
            if future_terrains and turn_index < len(future_terrains):
                future_terrain = future_terrains[turn_index]
                terrain_type = future_terrain.get(pos, 'GRASS')
            else:
                terrain_type = self.maze.terrain.get(pos, 'GRASS')
            
            # Calculate cost for this cell
            from config import TERRAIN_COSTS
            move_cost = TERRAIN_COSTS.get(terrain_type, 1)
            total_predicted_cost += move_cost
        
        # Update result with predicted cost (save original first)
        original_cost = base_result.cost
        base_result.cost = total_predicted_cost
        from config import DEBUG_MODE
        if DEBUG_MODE:
            print(f"[Predictive AI] Original cost: {original_cost:.1f}, Predicted future cost: {total_predicted_cost:.1f}")
        
        return base_result
    
    def _get_cache_key(self, start: Tuple[int, int], goal: Tuple[int, int], 
                      algorithm: str, discovered_cells: Optional[Set[Tuple[int, int]]] = None) -> Tuple:
        """Generate cache key for pathfinding result using efficient hashing"""
        # Hash discovered cells instead of storing full tuple to reduce memory and hashing cost
        dc_hash = hash(frozenset(discovered_cells)) if discovered_cells else None
        return (start, goal, algorithm, dc_hash)
    
    def _get_from_cache(self, key):
        """Get result from LRU cache, moving it to end (most recently used)"""
        if key in self._path_cache:
            self._path_cache.move_to_end(key)
            return self._path_cache[key]
        return None
    
    def _add_to_cache(self, key, value):
        """Add result to LRU cache, removing oldest if needed"""
        self._path_cache[key] = value
        self._path_cache.move_to_end(key)
        # Remove oldest entry if cache exceeds max size
        if len(self._path_cache) > self._cache_max_size:
            self._path_cache.popitem(last=False)
    
    def clear_cache(self):
        """Clear the pathfinding cache (call when maze changes significantly)"""
        self._path_cache.clear()
    
    def bfs(self, start, goal, discovered_cells=None):
        """
        Breadth-First Search algorithm for shortest path (unweighted)
        Returns PathfindingResult with path, cost, and exploration data
        
        Args:
            discovered_cells: Set of (x, y) positions visible to AI (for fog of war).
                            If None, all cells are accessible.
        """
        # Check cache first
        cache_key = self._get_cache_key(start, goal, 'BFS', discovered_cells)
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        result = PathfindingResult()
        queue = deque([start])  # FIFO queue for BFS
        came_from = {}
        cost_so_far = {start: 0}
        result.explored_nodes = set()
        
        while queue:
            current = queue.popleft()
            result.explored_nodes.add(current)
            
            if current == goal:
                # Reconstruct path
                path = []
                total_cost = 0
                while current in came_from:
                    path.append(current)
                    prev = came_from[current]
                    # Calculate actual cost including terrain
                    total_cost += self.maze.get_cost(*current)
                    current = prev
                path.append(start)
                path.reverse()
                
                result.path = path
                result.cost = total_cost
                result.nodes_explored = len(result.explored_nodes)
                result.path_found = True
                
                # Cache result using LRU
                self._add_to_cache(cache_key, result)
                return result
            
            # Get filtered neighbors using common helper
            neighbors = self._get_neighbors_filtered(current[0], current[1], discovered_cells, start, goal)
            
            for neighbor in neighbors:
                if not self.maze.is_passable(*neighbor):
                    continue
                
                if neighbor not in cost_so_far:
                    # BFS explores in order, so first visit is shortest path
                    cost_so_far[neighbor] = cost_so_far[current] + self.maze.get_cost(*neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)
        
        # No path found
        result.nodes_explored = len(result.explored_nodes)
        # Cache negative result too (path not found)
        self._add_to_cache(cache_key, result)
        return result
    
    def dijkstra(self, start, goal, discovered_cells=None):
        """
        Dijkstra's algorithm for shortest path
        Returns PathfindingResult with path, cost, and exploration data
        
        Args:
            discovered_cells: Set of (x, y) positions visible to AI (for fog of war).
                            If None, all cells are accessible.
        """
        # Check cache first
        cache_key = self._get_cache_key(start, goal, 'DIJKSTRA', discovered_cells)
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        result = PathfindingResult()
        
        # Safety limit to prevent infinite loops
        max_steps = self.maze.width * self.maze.height * 4
        steps = 0
        pq = [(0, start)]  # Priority queue: (cost, position)
        came_from = {}
        cost_so_far = {start: 0}
        result.explored_nodes = set()
        
        while pq and steps < max_steps:
            steps += 1
            current_cost, current = heapq.heappop(pq)
            
            if current in result.explored_nodes:
                continue
            
            result.explored_nodes.add(current)
            result.nodes_explored += 1
            
            if current == goal:
                # Reconstruct path
                path = []
                node = goal
                while node in came_from:
                    path.append(node)
                    node = came_from[node]
                path.append(start)
                path.reverse()
                result.path = path
                result.cost = cost_so_far[goal]
                result.path_found = True
                
                # Cache result using LRU
                self._add_to_cache(cache_key, result)
                return result
            
            # Get filtered neighbors using common helper
            neighbors = self._get_neighbors_filtered(current[0], current[1], discovered_cells, start, goal)
            
            for next_node in neighbors:
                nx, ny = next_node
                edge_cost = self.maze.get_cost(nx, ny)
                new_cost = current_cost + edge_cost
                
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    heapq.heappush(pq, (new_cost, next_node))
                    came_from[next_node] = current
        
        result.path_found = False
        # Cache negative result too (path not found)
        self._add_to_cache(cache_key, result)
        return result
    
    def a_star(self, start, goal, discovered_cells=None):
        """
        A* algorithm with heuristic
        Returns PathfindingResult with path, cost, and exploration data
        
        Args:
            discovered_cells: Set of (x, y) positions visible to AI (for fog of war).
                            If None, all cells are accessible.
        """
        # Check cache first
        cache_key = self._get_cache_key(start, goal, 'ASTAR', discovered_cells)
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        result = PathfindingResult()
        
        # Safety limit to prevent infinite loops
        max_steps = self.maze.width * self.maze.height * 4
        steps = 0
        start_x, start_y = start
        goal_x, goal_y = goal
        
        pq = [(0, start)]  # Priority queue: (f_score, position)
        came_from = {}
        g_score = {start: 0}  # Actual cost from start
        # Precompute heuristic function to avoid repeated calculations
        # For fog of war: Only use heuristic if goal is discovered, otherwise use zero (Dijkstra-like)
        goal_discovered = discovered_cells is None or goal in discovered_cells
        if goal_discovered:
            # Precompute heuristic function for discovered goal
            heuristic_fn = lambda nx, ny: self.heuristic(nx, ny, goal_x, goal_y)
        else:
            # Goal not discovered - use zero heuristic (Dijkstra-like)
            heuristic_fn = lambda nx, ny: 0
        
        initial_h = heuristic_fn(start_x, start_y)
        f_score = {start: initial_h}
        result.explored_nodes = set()
        result.frontier_nodes = {start}
        
        while pq:
            current_f, current = heapq.heappop(pq)
            
            if current in result.explored_nodes:
                continue
            
            result.explored_nodes.add(current)
            if current in result.frontier_nodes:
                result.frontier_nodes.remove(current)
            result.nodes_explored += 1
            
            if current == goal:
                # Reconstruct path
                path = []
                node = goal
                while node in came_from:
                    path.append(node)
                    node = came_from[node]
                path.append(start)
                path.reverse()
                result.path = path
                result.cost = g_score[goal]
                result.path_found = True
                return result
            
            # Get filtered neighbors using common helper
            neighbors = self._get_neighbors_filtered(current[0], current[1], discovered_cells, start, goal)
            
            for next_node in neighbors:
                nx, ny = next_node
                edge_cost = self.maze.get_cost(nx, ny)
                tentative_g = g_score[current] + edge_cost
                
                if next_node not in g_score or tentative_g < g_score[next_node]:
                    came_from[next_node] = current
                    g_score[next_node] = tentative_g
                    # Use precomputed heuristic function with difficulty scaling
                    h = heuristic_fn(nx, ny)
                    from config import AI_DIFFICULTY, AI_HEURISTIC_SCALE
                    heuristic_scale = AI_HEURISTIC_SCALE.get(AI_DIFFICULTY, 1.0)
                    f_score[next_node] = tentative_g + (heuristic_scale * h)
                    heapq.heappush(pq, (f_score[next_node], next_node))
                    result.frontier_nodes.add(next_node)
                    # Store node data for visualization
                    result.node_data[next_node] = {
                        'g': tentative_g,
                        'h': h,
                        'f': f_score[next_node]
                    }
        
        result.path_found = False
        return result
    
    def modified_a_star_fog_of_war(self, start, goal, discovered_cells=None, memory_map=None, 
                                    visited_positions=None, revisit_penalty=5.0):
        """
        Modified A* algorithm optimized for fog of war with:
        - Memory map (partial world model)
        - Frontier exploration (when goal is unknown)
        - Revisit penalty (to prevent oscillation)
        - Exploration heuristic
        
        Args:
            start: Starting position (x, y)
            goal: Goal position (x, y) - may be unknown
            discovered_cells: Set of (x, y) positions currently visible
            memory_map: Dict mapping (x, y) -> terrain type (what AI has seen before)
            visited_positions: Set of recently visited positions (for revisit penalty)
            revisit_penalty: Cost penalty for revisiting cells (default 5.0)
        
        Returns:
            PathfindingResult with path optimized for exploration
        """
        result = PathfindingResult()
        start_x, start_y = start
        goal_x, goal_y = goal
        
        # Initialize memory map if not provided
        if memory_map is None:
            memory_map = {}
        
        # Initialize visited positions if not provided
        if visited_positions is None:
            visited_positions = set()
        
        # Check if goal is known (in memory or discovered)
        goal_known = (discovered_cells is not None and goal in discovered_cells) or (memory_map is not None and goal in memory_map)
        
        # If goal is unknown, use frontier exploration
        if not goal_known:
            # Find nearest frontier (edge of known area)
            frontier = self._find_nearest_frontier(start, discovered_cells, memory_map)
            if frontier:
                # Explore toward frontier instead of goal
                goal = frontier
                goal_x, goal_y = frontier
                goal_known = True  # Frontier is always known
        
        pq = [(0, start)]  # Priority queue: (f_score, position)
        came_from = {}
        g_score = {start: 0}
        
        # Heuristic: use normal if goal known, otherwise use exploration heuristic
        if goal_known:
            initial_h = self.heuristic(start_x, start_y, goal_x, goal_y)
        else:
            # Exploration heuristic: prefer unexplored areas
            initial_h = self._exploration_heuristic(start, discovered_cells, memory_map)
        
        f_score = {start: initial_h}
        result.explored_nodes = set()
        result.frontier_nodes = {start}
        
        # Helper to check if a cell is accessible
        def is_accessible(pos):
            if discovered_cells is None:
                return True  # All cells visible
            if pos == start:
                return True
            # Can move to discovered cells or cells in memory
            return pos in discovered_cells or (memory_map is not None and pos in memory_map)
        
        # Helper to get cost with revisit penalty
        def get_cost_with_penalty(pos, base_cost):
            if pos in visited_positions:
                return base_cost + revisit_penalty
            return base_cost
        
        while pq:
            current_f, current = heapq.heappop(pq)
            
            if current in result.explored_nodes:
                continue
            
            result.explored_nodes.add(current)
            if current in result.frontier_nodes:
                result.frontier_nodes.remove(current)
            result.nodes_explored += 1
            
            if current == goal:
                # Reconstruct path
                path = []
                node = goal
                while node in came_from:
                    path.append(node)
                    node = came_from[node]
                path.append(start)
                path.reverse()
                result.path = path
                result.cost = g_score[goal]
                result.path_found = True
                return result
            
            x, y = current
            neighbors = self.maze.get_neighbors(x, y, ENABLE_DIAGONALS)
            
            # Filter neighbors by accessibility
            if discovered_cells is not None:
                neighbors = [n for n in neighbors if is_accessible(n)]
            
            for next_node in neighbors:
                nx, ny = next_node
                
                # Get base cost from memory if known, otherwise use maze cost
                if memory_map is not None and next_node in memory_map:
                    # Use remembered terrain cost
                    terrain = memory_map[next_node]
                    base_cost = self.maze.get_cost_for_terrain(terrain)
                else:
                    # Unknown cell - use maze cost with exploration bonus
                    base_cost = self.maze.get_cost(nx, ny)
                    # Apply multiplicative exploration bonus to encourage exploring unknown areas
                    # This maintains cost consistency while still encouraging exploration
                    EXPLORATION_BONUS = 0.8  # 20% cost reduction for unexplored cells
                    in_memory = memory_map is not None and next_node in memory_map
                    in_discovered = discovered_cells is not None and next_node in discovered_cells
                    if not in_memory and not in_discovered:
                        base_cost = max(1, base_cost * EXPLORATION_BONUS)  # Slight bonus for exploration
                
                # Apply revisit penalty
                edge_cost = get_cost_with_penalty(next_node, base_cost)
                tentative_g = g_score[current] + edge_cost
                
                if next_node not in g_score or tentative_g < g_score[next_node]:
                    came_from[next_node] = current
                    g_score[next_node] = tentative_g
                    
                    # Heuristic: use normal if goal known, otherwise exploration
                    if goal_known:
                        h_score = self.heuristic(nx, ny, goal_x, goal_y)
                    else:
                        h_score = self._exploration_heuristic(next_node, discovered_cells, memory_map)
                    
                    f_score[next_node] = tentative_g + h_score
                    heapq.heappush(pq, (f_score[next_node], next_node))
                    result.frontier_nodes.add(next_node)
                    result.node_data[next_node] = {
                        'g': tentative_g,
                        'h': h_score,
                        'f': f_score[next_node]
                    }
        
        result.path_found = False
        return result
    
    def _find_nearest_frontier(self, start, discovered_cells, memory_map):
        """
        Find the nearest frontier cell (edge of known area) for exploration.
        Returns None if no frontier found.
        """
        if discovered_cells is None:
            return None  # No fog of war, no frontier needed
        
        # Find all discovered cells that have unexplored neighbors
        frontier_candidates = []
        for cell in discovered_cells:
            x, y = cell
            neighbors = self.maze.get_neighbors(x, y, ENABLE_DIAGONALS)
            # Check if any neighbor is unexplored
            has_unexplored = any(
                n not in discovered_cells and 
                (memory_map is None or n not in memory_map) 
                for n in neighbors
            )
            if has_unexplored:
                frontier_candidates.append(cell)
        
        if not frontier_candidates:
            return None
        
        # Return nearest frontier to start
        min_dist = float('inf')
        nearest = None
        for candidate in frontier_candidates:
            dist = self.manhattan_distance(start[0], start[1], candidate[0], candidate[1])
            if dist < min_dist:
                min_dist = dist
                nearest = candidate
        
        return nearest
    
    def _exploration_heuristic(self, pos, discovered_cells, memory_map):
        """
        Heuristic for exploration: prefer cells that are near unexplored areas.
        Lower values = better (closer to unexplored frontier).
        """
        if discovered_cells is None:
            return 0  # No exploration needed
        
        x, y = pos
        neighbors = self.maze.get_neighbors(x, y, ENABLE_DIAGONALS)
        
        # Count unexplored neighbors (encourages moving toward frontier)
        unexplored_count = sum(1 for n in neighbors 
                              if n not in discovered_cells and 
                              (memory_map is None or n not in memory_map))
        
        # Return negative of unexplored count (more unexplored = better)
        # But we want to minimize, so return a value that decreases with unexplored neighbors
        return max(0, 10 - unexplored_count * 2)
    
    def bidirectional_a_star(self, start, goal, discovered_cells=None):
        """
        Bidirectional A* for faster search
        Searches from both start and goal simultaneously
        
        Args:
            discovered_cells: Set of (x, y) positions visible to AI (for fog of war).
                            If None, all cells are accessible.
        """
        # Check cache first
        cache_key = self._get_cache_key(start, goal, 'BIDIRECTIONAL_ASTAR', discovered_cells)
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Helper to check if a cell is accessible
        def is_accessible(pos):
            if discovered_cells is None:
                return True  # All cells visible
            # Start position (current position) is always accessible
            if pos == start:
                return True
            # Goal position is only accessible if discovered (true blindness)
            # AI cannot pathfind toward an undiscovered goal - must discover it first
            if pos == goal:
                # Goal must be discovered to be accessible
                return pos in discovered_cells
            # All other cells must be discovered
            return pos in discovered_cells
        result = PathfindingResult()
        start_x, start_y = start
        goal_x, goal_y = goal
        
        # Forward search
        pq_forward = [(0, start)]
        came_from_forward = {}
        g_forward = {start: 0}
        explored_forward = set()
        
        # Backward search - only start if goal is discovered
        # For true blindness: goal must be discovered to pathfind from it
        pq_backward = []
        came_from_backward = {}
        g_backward = {}
        explored_backward = set()
        if discovered_cells is None or goal in discovered_cells:
            pq_backward = [(0, goal)]
            g_backward = {goal: 0}
        
        meet_point = None
        best_meet_cost = float('inf')
        
        # Safety limit to prevent infinite loops
        max_steps = self.maze.width * self.maze.height * 4
        steps = 0
        
        while pq_forward and pq_backward and steps < max_steps:
            steps += 1
            # Forward step
            if pq_forward:
                current_f, current = heapq.heappop(pq_forward)
                if current in explored_forward:
                    continue
                explored_forward.add(current)
                result.explored_nodes.add(current)
                result.nodes_explored += 1
                
                # Check if we've met the backward search
                if current in explored_backward:
                    # Found a meeting point - check if it's better than current best
                    total_cost = g_forward[current] + g_backward[current]
                    if total_cost < best_meet_cost:
                        meet_point = current
                        best_meet_cost = total_cost
                        # Continue searching for potentially better meet points
                        # but break if we've found a good one and queues are getting large
                        if len(pq_forward) + len(pq_backward) > 100:
                            break
                
                x, y = current
                neighbors = self.maze.get_neighbors(x, y, ENABLE_DIAGONALS)
                # Filter neighbors by discovered cells (fog of war)
                if discovered_cells is not None:
                    neighbors = [n for n in neighbors if is_accessible(n)]
                for next_node in neighbors:
                    nx, ny = next_node
                    edge_cost = self.maze.get_cost(nx, ny)
                    new_g = g_forward[current] + edge_cost
                    if next_node not in g_forward or new_g < g_forward[next_node]:
                        g_forward[next_node] = new_g
                        # Precompute heuristic for forward search
                        goal_discovered = discovered_cells is None or goal in discovered_cells
                        if goal_discovered:
                            h_forward = self.heuristic(nx, ny, goal_x, goal_y)
                        else:
                            h_forward = 0
                        heuristic_scale = AI_HEURISTIC_SCALE.get(AI_DIFFICULTY, 1.0)
                        f = new_g + (heuristic_scale * h_forward)
                        heapq.heappush(pq_forward, (f, next_node))
                        came_from_forward[next_node] = current
            
            # Backward step
            if pq_backward:
                current_f, current = heapq.heappop(pq_backward)
                if current in explored_backward:
                    continue
                explored_backward.add(current)
                result.explored_nodes.add(current)
                result.nodes_explored += 1
                
                # Check if we've met the forward search
                if current in explored_forward:
                    # Found a meeting point - check if it's better than current best
                    total_cost = g_forward[current] + g_backward[current]
                    if total_cost < best_meet_cost:
                        meet_point = current
                        best_meet_cost = total_cost
                        # Continue searching for potentially better meet points
                        # but break if we've found a good one and queues are getting large
                        if len(pq_forward) + len(pq_backward) > 100:
                            break
                
                x, y = current
                neighbors = self.maze.get_neighbors(x, y, ENABLE_DIAGONALS)
                # Filter neighbors by discovered cells (fog of war)
                if discovered_cells is not None:
                    neighbors = [n for n in neighbors if is_accessible(n)]
                for next_node in neighbors:
                    nx, ny = next_node
                    edge_cost = self.maze.get_cost(nx, ny)
                    new_g = g_backward[current] + edge_cost
                    if next_node not in g_backward or new_g < g_backward[next_node]:
                        g_backward[next_node] = new_g
                        # For backward search: heuristic is distance to start (always known)
                        h_backward = self.heuristic(nx, ny, start_x, start_y)
                        heuristic_scale = AI_HEURISTIC_SCALE.get(AI_DIFFICULTY, 1.0)
                        f = new_g + (heuristic_scale * h_backward)
                        heapq.heappush(pq_backward, (f, next_node))
                        came_from_backward[next_node] = current
        
        if meet_point:
            # Reconstruct path from both sides
            path_forward = []
            node = meet_point
            while node in came_from_forward:
                path_forward.append(node)
                node = came_from_forward[node]
            path_forward.append(start)
            path_forward.reverse()
            
            path_backward = []
            node = meet_point
            while node in came_from_backward:
                path_backward.append(node)
                node = came_from_backward[node]
            # Add goal to backward path (backward search started from goal)
            path_backward.append(goal)
            
            # Combine paths: forward path (includes meet_point) + backward path (exclude meet_point to avoid duplicate)
            result.path = path_forward + path_backward[1:]  # Skip first element (meet_point) to avoid duplicate
            result.cost = g_forward[meet_point] + g_backward[meet_point]
            result.path_found = True
            
            # Cache result using LRU
            self._add_to_cache(cache_key, result)
        else:
            result.path_found = False
            # Cache negative result too (path not found)
            self._add_to_cache(cache_key, result)
        
        return result
    
    def d_star(self, start, goal, discovered_cells=None):
        """
        D* (Dynamic A*) algorithm for moving obstacles
        Efficiently replans when obstacles appear/disappear
        This is a simplified version - full D* Lite would maintain a priority queue with keys and handle dynamic updates
        For now, uses A* but is designed to be extended for incremental replanning
        
        Args:
            discovered_cells: Set of (x, y) positions visible to AI (for fog of war).
                            If None, all cells are accessible.
        """
        # Note: Full D* would maintain state between calls for incremental updates
        # This implementation provides basic dynamic pathfinding with A*
        # Students can extend this to full D* Lite with key-based priority queue
        return self.a_star(start, goal, discovered_cells=discovered_cells)
    
    def multi_objective_search(self, start, goals, discovered_cells=None):
        """
        Multi-Objective Search for multiple goals (checkpoints)
        Finds optimal path visiting all goals
        Uses brute force to try all permutations - can be optimized with more advanced techniques
        
        Args:
            discovered_cells: Set of (x, y) positions visible to AI (for fog of war).
                            If None, all cells are accessible.
        """
        result = PathfindingResult()
        
        if not goals:
            result.path_found = False
            return result
        
        if len(goals) == 1:
            # Single goal - just use A*
            return self.a_star(start, goals[0], discovered_cells=discovered_cells)
        
        # Strategy: Use Nearest Neighbor heuristic for scalability (O(N²) instead of O(N!))
        # This is much faster for large numbers of checkpoints while still finding good paths
        best_path = None
        best_cost = float('inf')
        
        # Nearest Neighbor approach: always go to closest unvisited goal
        unvisited_goals = list(goals)
        current_pos = start
        path_segments = []
        total_cost = 0
        
        # Safety limit to prevent infinite loops
        max_iterations = len(goals) * 2
        iterations = 0
        
        while unvisited_goals and iterations < max_iterations:
            iterations += 1
            # Find nearest unvisited goal
            next_goal = min(unvisited_goals, 
                          key=lambda g: self.heuristic(current_pos[0], current_pos[1], g[0], g[1]))
            
            # Find path to this goal
            segment_result = self.a_star(current_pos, next_goal, discovered_cells)
            if not segment_result.path_found:
                # Can't reach this goal - try next closest
                unvisited_goals.remove(next_goal)
                continue
            
            # Add segment to path (skip first element to avoid duplicate)
            if path_segments:
                path_segments.extend(segment_result.path[1:])
            else:
                path_segments.extend(segment_result.path)
            
            total_cost += segment_result.cost
            result.explored_nodes.update(segment_result.explored_nodes)
            result.nodes_explored += segment_result.nodes_explored
            current_pos = next_goal
            unvisited_goals.remove(next_goal)
        
        # If we successfully visited all goals, we have a valid path
        if not unvisited_goals and path_segments:
            best_path = path_segments
            best_cost = total_cost
        
        # Fallback: If nearest neighbor failed, try a few random orderings (limited)
        if best_path is None:
            import itertools
            import random
            # Limit to first 10 permutations to avoid factorial explosion
            goal_permutations = list(itertools.permutations(goals))[:10]
            random.shuffle(goal_permutations)
            
            for goal_order in goal_permutations:
                # Build path through goals in this order
                current_pos = start
                total_cost = 0
                full_path = [start]
                path_valid = True
                
                for goal in goal_order:
                    # Find path from current position to this goal
                    segment_result = self.a_star(current_pos, goal, discovered_cells=discovered_cells)
                    if not segment_result.path_found:
                        path_valid = False
                        break
                    
                    # Add path segment (skip first node to avoid duplicates)
                    full_path.extend(segment_result.path[1:])
                    total_cost += segment_result.cost
                    current_pos = goal
                    # Track explored nodes
                    result.explored_nodes.update(segment_result.explored_nodes)
                    result.nodes_explored += segment_result.nodes_explored
                
                # Check if this ordering is better
                if path_valid and total_cost < best_cost:
                    best_cost = total_cost
                    best_path = full_path
        
        if best_path:
            result.path = best_path
            result.cost = best_cost
            result.path_found = True
        
        return result

