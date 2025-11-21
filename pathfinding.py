"""
Pathfinding algorithms: Dijkstra, A*, and advanced variants
Includes visualization support for explored nodes and frontiers

This file implements several graph-based pathfinding algorithms:
- Dijkstra's Algorithm: Guaranteed optimal path, explores uniformly
- A* Algorithm: Fast heuristic-driven search, still optimal
- Bidirectional A*: Searches from both ends for speed
- Multi-Objective Search: Handles multiple goals (checkpoints)
- Modified A* for Fog of War: Handles limited visibility

All algorithms operate on a weighted graph where:
- Nodes = passable cells in the maze
- Edges = connections between adjacent cells
- Edge weights = terrain movement costs
"""

import heapq  # Priority queue for Dijkstra and A* algorithms
import math  # For Euclidean distance calculation
from collections import OrderedDict, deque  # OrderedDict for LRU cache, deque for BFS queue
from typing import Optional, Set, Tuple, List, Dict, Any  # Type hints for better code clarity
from config import (
    ENABLE_DIAGONALS, DEBUG_MODE, TERRAIN_COSTS, 
    AI_DIFFICULTY, AI_HEURISTIC_SCALE
)

class PathfindingResult:
    """
    Container class for pathfinding algorithm results.
    
    This class stores all the information returned by a pathfinding algorithm:
    - The calculated path
    - Total cost of the path
    - How many nodes were explored
    - Which nodes were explored (for visualization)
    - Which nodes are on the frontier (for visualization)
    - Heuristic values (f, g, h) for each node (for A* visualization)
    """
    def __init__(self):
        # The calculated path: list of (x, y) positions from start to goal
        self.path: List[Tuple[int, int]] = []
        
        # Total cost of the path (sum of all terrain costs along the path)
        self.cost: float = float('inf')  # Start with infinity (no path found yet)
        
        # Number of nodes explored during pathfinding
        # Lower is better (means algorithm was more efficient)
        self.nodes_explored: int = 0
        
        # Set of all nodes that were explored (visited) during pathfinding
        # Used for visualization (shows which cells the algorithm checked)
        self.explored_nodes: Set[Tuple[int, int]] = set()
        
        # Set of nodes currently on the frontier (being considered)
        # Used for visualization (shows which cells the algorithm is about to check)
        self.frontier_nodes: Set[Tuple[int, int]] = set()
        
        # Whether a path was successfully found
        # True = path exists, False = goal unreachable
        self.path_found: bool = False
        
        # Dictionary storing f, g, h values for each node (for A* visualization)
        # Key: (x, y) position
        # Value: Dictionary with 'g' (actual cost), 'h' (heuristic), 'f' (total estimate)
        self.node_data: Dict[Tuple[int, int], Dict[str, Any]] = {}

class Pathfinder:
    """
    Container for all pathfinding algorithms.
    
    This class provides methods for different pathfinding algorithms.
    It also includes:
    - Caching system to avoid recalculating the same paths
    - Helper methods for path reconstruction
    - Heuristic functions (Manhattan, Euclidean)
    """
    
    def __init__(self, maze, heuristic_type='MANHATTAN'):
        """
        Initialize the pathfinder.
        
        Args:
            maze: The maze object (needed to check terrain, costs, neighbors)
            heuristic_type: Type of heuristic for A* ('MANHATTAN' or 'EUCLIDEAN')
        """
        self.maze = maze  # Reference to the maze
        self.heuristic_type = heuristic_type  # Heuristic type for A* algorithm
        
        # ====================================================================
        # PATHFINDING CACHE (Performance Optimization)
        # ====================================================================
        # LRU (Least Recently Used) cache for pathfinding results
        # This avoids recalculating the same paths multiple times
        # 
        # How it works:
        # - When we calculate a path, we store it in the cache
        # - If we need the same path again, we return the cached result
        # - Cache automatically removes old entries when it gets full
        # 
        # Cache key: (start position, goal position, algorithm name, discovered cells hash)
        # Cache value: PathfindingResult (the calculated path and stats)
        self._path_cache: OrderedDict = OrderedDict()
        self._cache_max_size = 100  # Maximum number of cached paths (prevents memory issues)
    
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
    
    # ==================== HEURISTIC METHODS ====================
    # Heuristics are "estimates" of distance to goal
    # They help A* algorithm explore in the right direction (toward goal)
    # A good heuristic never overestimates the actual distance (admissible)
    
    def manhattan_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """
        Calculate Manhattan distance between two points.
        
        Manhattan distance is like city blocks - you can only move horizontally or vertically.
        Formula: |x1 - x2| + |y1 - y2|
        
        Example: Distance from (0, 0) to (3, 4) = |0-3| + |0-4| = 3 + 4 = 7
        
        This is perfect for grid-based movement where you can only move in 4 directions.
        
        Args:
            x1, y1: First point coordinates
            x2, y2: Second point coordinates
        
        Returns:
            Manhattan distance (always positive)
        """
        return abs(x1 - x2) + abs(y1 - y2)
    
    def euclidean_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """
        Calculate Euclidean (straight-line) distance between two points.
        
        Euclidean distance is the actual straight-line distance.
        Formula: √((x1 - x2)² + (y1 - y2)²)
        
        Example: Distance from (0, 0) to (3, 4) = √(3² + 4²) = √(9 + 16) = √25 = 5
        
        This is more accurate but slightly slower to calculate than Manhattan.
        Works well when diagonal movement is allowed.
        
        Args:
            x1, y1: First point coordinates
            x2, y2: Second point coordinates
        
        Returns:
            Euclidean distance (always positive)
        """
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    def heuristic(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """
        Calculate heuristic value using the selected heuristic type.
        
        This is a wrapper that calls the appropriate heuristic function
        (Manhattan or Euclidean) based on the pathfinder's configuration.
        
        Args:
            x1, y1: First point coordinates
            x2, y2: Second point coordinates
        
        Returns:
            Heuristic distance estimate
        """
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
        Dijkstra's algorithm for finding the shortest path in a weighted graph.
        
        How it works:
        1. Start with a priority queue containing the start node (cost 0)
        2. Always explore the node with lowest cost from start
        3. For each neighbor, calculate new cost and update if cheaper
        4. Stop when goal is reached
        
        Guarantees: Finds the optimal (cheapest) path
        Time Complexity: O((V + E) log V) where V = vertices, E = edges
        
        Args:
            start: Starting position (x, y) tuple
            goal: Goal position (x, y) tuple
            discovered_cells: Set of (x, y) positions visible to AI (for fog of war)
                            If None, all cells are accessible.
        
        Returns:
            PathfindingResult with path, cost, nodes explored, etc.
        """
        # ====================================================================
        # CHECK CACHE FIRST
        # ====================================================================
        # If we've calculated this path before, return cached result
        cache_key = self._get_cache_key(start, goal, 'DIJKSTRA', discovered_cells)
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result  # Return cached result (much faster!)
        
        # ====================================================================
        # INITIALIZATION
        # ====================================================================
        result = PathfindingResult()  # Create result object to store pathfinding results
        
        # Safety limit to prevent infinite loops (shouldn't happen, but safety check)
        max_steps = self.maze.width * self.maze.height * 4
        steps = 0
        
        # Priority queue: stores (cost, position) tuples
        # heapq always returns the item with lowest cost first
        # We start with the start position at cost 0
        pq = [(0, start)]
        
        # came_from: Dictionary to reconstruct the path
        # Key: node position, Value: previous node position
        # Example: came_from[goal] = node_before_goal
        came_from = {}
        
        # cost_so_far: Dictionary storing the cheapest cost to reach each node
        # Key: node position, Value: cost to reach that node
        cost_so_far = {start: 0}  # Start position costs 0 to reach
        
        # Track explored nodes for visualization
        result.explored_nodes = set()
        
        # ====================================================================
        # MAIN ALGORITHM LOOP
        # ====================================================================
        while pq and steps < max_steps:
            steps += 1
            
            # Get the node with lowest cost from the priority queue
            # heapq.heappop() returns the smallest item (lowest cost)
            current_cost, current = heapq.heappop(pq)
            
            # Skip if we've already explored this node (might be in queue multiple times)
            if current in result.explored_nodes:
                continue
            
            # Mark this node as explored
            result.explored_nodes.add(current)
            result.nodes_explored += 1
            
            # ================================================================
            # GOAL CHECK
            # ================================================================
            # If we reached the goal, we're done!
            if current == goal:
                # Reconstruct the path by following came_from backwards from goal to start
                path = []
                node = goal
                while node in came_from:
                    path.append(node)  # Add current node to path
                    node = came_from[node]  # Move to previous node
                path.append(start)  # Add start position
                path.reverse()  # Reverse to get path from start to goal
                
                # Store results
                result.path = path
                result.cost = cost_so_far[goal]  # Total cost to reach goal
                result.path_found = True
                
                # Cache the result for future use
                self._add_to_cache(cache_key, result)
                return result
            
            # ================================================================
            # EXPLORE NEIGHBORS
            # ================================================================
            # Get all valid neighbors (filtered by fog of war if applicable)
            neighbors = self._get_neighbors_filtered(current[0], current[1], discovered_cells, start, goal)
            
            # Check each neighbor
            for next_node in neighbors:
                nx, ny = next_node
                
                # Get the cost to move to this neighbor (based on terrain)
                edge_cost = self.maze.get_cost(nx, ny)
                
                # Calculate new cost: cost to current + cost to neighbor
                new_cost = current_cost + edge_cost
                
                # ============================================================
                # RELAXATION (Update if we found a cheaper path)
                # ============================================================
                # If we haven't seen this node before, OR we found a cheaper path to it
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    # Update the cost to reach this node
                    cost_so_far[next_node] = new_cost
                    
                    # Add to priority queue with the new cost
                    # Lower cost nodes will be explored first
                    heapq.heappush(pq, (new_cost, next_node))
                    
                    # Remember how we got to this node (for path reconstruction)
                    came_from[next_node] = current
        
        # ====================================================================
        # NO PATH FOUND
        # ====================================================================
        # If we exit the loop without finding the goal, no path exists
        result.path_found = False
        
        # Cache the negative result too (so we don't recalculate)
        self._add_to_cache(cache_key, result)
        return result
    
    def a_star(self, start, goal, discovered_cells=None):
        """
        A* (A-Star) algorithm with heuristic guidance.
        
        A* is like Dijkstra, but uses a heuristic (estimate) to guide the search toward the goal.
        This makes it much faster than Dijkstra while still finding optimal paths.
        
        How it works:
        1. Uses f(n) = g(n) + h(n) where:
           - g(n) = actual cost from start to node n
           - h(n) = heuristic estimate from node n to goal
        2. Explores nodes with lower f(n) values first
        3. Guaranteed optimal if heuristic is admissible (never overestimates)
        
        Time Complexity: O((V + E) log V) worst case, but often much better than Dijkstra
        
        Args:
            start: Starting position (x, y) tuple
            goal: Goal position (x, y) tuple
            discovered_cells: Set of (x, y) positions visible to AI (for fog of war)
                            If None, all cells are accessible.
        
        Returns:
            PathfindingResult with path, cost, nodes explored, etc.
        """
        # ====================================================================
        # CHECK CACHE FIRST
        # ====================================================================
        cache_key = self._get_cache_key(start, goal, 'ASTAR', discovered_cells)
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result  # Return cached result if available
        
        # ====================================================================
        # INITIALIZATION
        # ====================================================================
        result = PathfindingResult()
        
        # Safety limit to prevent infinite loops
        max_steps = self.maze.width * self.maze.height * 4
        steps = 0
        
        # Extract coordinates for heuristic calculations
        start_x, start_y = start
        goal_x, goal_y = goal
        
        # Priority queue: stores (f_score, position) tuples
        # f_score = g_score + h_score (total estimated cost)
        # Lower f_score = more promising, explored first
        pq = [(0, start)]
        
        # came_from: For path reconstruction (same as Dijkstra)
        came_from = {}
        
        # g_score: Actual cost from start to each node
        # This is the "real" cost, not an estimate
        g_score = {start: 0}  # Start costs 0 to reach
        
        # ====================================================================
        # HEURISTIC FUNCTION SETUP
        # ====================================================================
        # For fog of war: Only use heuristic if goal is discovered
        # If goal is not discovered, use zero heuristic (acts like Dijkstra)
        goal_discovered = discovered_cells is None or goal in discovered_cells
        
        if goal_discovered:
            # Goal is known - use normal heuristic (Manhattan or Euclidean)
            # This guides search toward the goal
            heuristic_fn = lambda nx, ny: self.heuristic(nx, ny, goal_x, goal_y)
        else:
            # Goal not discovered - use zero heuristic (Dijkstra-like behavior)
            # Without knowing where goal is, we can't guide the search
            heuristic_fn = lambda nx, ny: 0
        
        # Calculate initial f_score for start position
        initial_h = heuristic_fn(start_x, start_y)  # Heuristic from start to goal
        f_score = {start: initial_h}  # f = g + h = 0 + h
        
        # Initialize visualization sets
        result.explored_nodes = set()
        result.frontier_nodes = {start}  # Start is on the frontier
        
        # ====================================================================
        # MAIN ALGORITHM LOOP
        # ====================================================================
        while pq:
            # Get node with lowest f_score (most promising)
            current_f, current = heapq.heappop(pq)
            
            # Skip if already explored (might be in queue with different f_score)
            if current in result.explored_nodes:
                continue
            
            # Mark as explored
            result.explored_nodes.add(current)
            if current in result.frontier_nodes:
                result.frontier_nodes.remove(current)  # No longer on frontier
            result.nodes_explored += 1
            
            # ================================================================
            # GOAL CHECK
            # ================================================================
            if current == goal:
                # Found the goal! Reconstruct path
                path = []
                node = goal
                while node in came_from:
                    path.append(node)
                    node = came_from[node]
                path.append(start)
                path.reverse()
                
                # Store results
                result.path = path
                result.cost = g_score[goal]  # Use g_score (actual cost), not f_score
                result.path_found = True
                return result
            
            # ================================================================
            # EXPLORE NEIGHBORS
            # ================================================================
            neighbors = self._get_neighbors_filtered(current[0], current[1], discovered_cells, start, goal)
            
            for next_node in neighbors:
                nx, ny = next_node
                
                # Get terrain cost for this neighbor
                edge_cost = self.maze.get_cost(nx, ny)
                
                # Calculate tentative g_score (actual cost from start to this neighbor)
                tentative_g = g_score[current] + edge_cost
                
                # ============================================================
                # RELAXATION (Update if we found a cheaper path)
                # ============================================================
                if next_node not in g_score or tentative_g < g_score[next_node]:
                    # Found a better path to this node!
                    came_from[next_node] = current
                    g_score[next_node] = tentative_g
                    
                    # Calculate heuristic for this neighbor
                    h = heuristic_fn(nx, ny)
                    
                    # Apply difficulty scaling to heuristic
                    # This adjusts how much the AI trusts the heuristic
                    from config import AI_DIFFICULTY, AI_HEURISTIC_SCALE
                    heuristic_scale = AI_HEURISTIC_SCALE.get(AI_DIFFICULTY, 1.0)
                    
                    # Calculate f_score = g_score + (scaled heuristic)
                    f_score[next_node] = tentative_g + (heuristic_scale * h)
                    
                    # Add to priority queue (will be explored in order of f_score)
                    heapq.heappush(pq, (f_score[next_node], next_node))
                    
                    # Mark as frontier node (for visualization)
                    result.frontier_nodes.add(next_node)
                    
                    # Store node data for visualization (f, g, h values)
                    result.node_data[next_node] = {
                        'g': tentative_g,           # Actual cost from start
                        'h': h,                     # Heuristic estimate to goal
                        'f': f_score[next_node]     # Total estimate (g + h)
                    }
        
        # ====================================================================
        # NO PATH FOUND
        # ====================================================================
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
        Multi-Objective Search for finding optimal path visiting multiple goals (checkpoints).
        
        This algorithm solves a variant of the Traveling Salesman Problem (TSP):
        "What's the best order to visit all checkpoints before reaching the goal?"
        
        Strategy:
        1. Uses Nearest Neighbor heuristic: always visit the closest unvisited goal
        2. For each goal, uses A* to find the path to it
        3. Combines all path segments into one complete path
        4. Falls back to brute force (trying all permutations) if Nearest Neighbor fails
        
        Why Nearest Neighbor?
        - Brute force tries all N! permutations (factorial - very slow for large N)
        - Nearest Neighbor is O(N²) - much faster, still finds good paths
        - For 3 checkpoints, both are fast, but Nearest Neighbor scales better
        
        Args:
            start: Starting position (x, y) tuple
            goals: List of goal positions [(x1, y1), (x2, y2), ...]
                  These are the checkpoints that must be visited
            discovered_cells: Set of (x, y) positions visible to AI (for fog of war)
                            If None, all cells are accessible.
        
        Returns:
            PathfindingResult with path visiting all goals in optimal order
        """
        result = PathfindingResult()
        
        # ====================================================================
        # EDGE CASES
        # ====================================================================
        # No goals provided - can't find a path
        if not goals:
            result.path_found = False
            return result
        
        # Single goal - just use regular A* (no need for multi-objective)
        if len(goals) == 1:
            return self.a_star(start, goals[0], discovered_cells=discovered_cells)
        
        # ====================================================================
        # NEAREST NEIGHBOR HEURISTIC (Greedy Approach)
        # ====================================================================
        # Strategy: Always visit the closest unvisited goal
        # This is much faster than brute force (O(N²) vs O(N!))
        # While not always optimal, it finds very good paths quickly
        
        best_path = None
        best_cost = float('inf')
        
        # Start with all goals unvisited
        unvisited_goals = list(goals)
        current_pos = start  # Start from the starting position
        path_segments = []   # Will store all path segments combined
        total_cost = 0       # Total cost of visiting all goals
        
        # Safety limit to prevent infinite loops
        max_iterations = len(goals) * 2
        iterations = 0
        
        # ====================================================================
        # VISIT ALL GOALS USING NEAREST NEIGHBOR
        # ====================================================================
        while unvisited_goals and iterations < max_iterations:
            iterations += 1
            
            # Find the nearest unvisited goal using heuristic distance
            # This is the "greedy" part - always pick the closest one
            next_goal = min(unvisited_goals, 
                          key=lambda g: self.heuristic(current_pos[0], current_pos[1], g[0], g[1]))
            
            # Find path from current position to this goal using A*
            segment_result = self.a_star(current_pos, next_goal, discovered_cells)
            
            if not segment_result.path_found:
                # Can't reach this goal - remove it and try next closest
                unvisited_goals.remove(next_goal)
                continue
            
            # Add this path segment to our complete path
            # Skip first element to avoid duplicate (current_pos is already in path)
            if path_segments:
                path_segments.extend(segment_result.path[1:])  # Skip first, add rest
            else:
                path_segments.extend(segment_result.path)  # First segment includes start
            
            # Update total cost and exploration stats
            total_cost += segment_result.cost
            result.explored_nodes.update(segment_result.explored_nodes)
            result.nodes_explored += segment_result.nodes_explored
            
            # Move to this goal and mark it as visited
            current_pos = next_goal
            unvisited_goals.remove(next_goal)
        
        # ====================================================================
        # CHECK IF NEAREST NEIGHBOR SUCCEEDED
        # ====================================================================
        # If we successfully visited all goals, we have a valid path
        if not unvisited_goals and path_segments:
            best_path = path_segments
            best_cost = total_cost
        
        # ====================================================================
        # FALLBACK: BRUTE FORCE (if Nearest Neighbor failed)
        # ====================================================================
        # If Nearest Neighbor couldn't visit all goals, try brute force
        # We limit to first 10 permutations to avoid factorial explosion
        if best_path is None:
            import itertools
            import random
            
            # Generate all possible orderings of goals (permutations)
            # Example: 3 goals = 6 permutations (3! = 6)
            # Limit to first 10 to avoid trying too many (for performance)
            goal_permutations = list(itertools.permutations(goals))[:10]
            random.shuffle(goal_permutations)  # Shuffle for variety
            
            # Try each permutation
            for goal_order in goal_permutations:
                # Build path through goals in this order
                current_pos = start
                total_cost = 0
                full_path = [start]
                path_valid = True
                
                # Visit each goal in this order
                for goal in goal_order:
                    # Find path from current position to this goal
                    segment_result = self.a_star(current_pos, goal, discovered_cells=discovered_cells)
                    
                    if not segment_result.path_found:
                        # Can't reach this goal in this order - try next permutation
                        path_valid = False
                        break
                    
                    # Add path segment (skip first node to avoid duplicates)
                    full_path.extend(segment_result.path[1:])
                    total_cost += segment_result.cost
                    current_pos = goal
                    
                    # Track explored nodes for visualization
                    result.explored_nodes.update(segment_result.explored_nodes)
                    result.nodes_explored += segment_result.nodes_explored
                
                # Check if this ordering is better than current best
                if path_valid and total_cost < best_cost:
                    best_cost = total_cost
                    best_path = full_path
        
        # ====================================================================
        # RETURN RESULTS
        # ====================================================================
        if best_path:
            result.path = best_path
            result.cost = best_cost
            result.path_found = True
        
        return result

