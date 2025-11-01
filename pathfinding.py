"""
Pathfinding algorithms: Dijkstra, A*, and advanced variants
Includes visualization support for explored nodes and frontiers
"""

import heapq
import math
from config import *

class PathfindingResult:
    def __init__(self):
        self.path = []
        self.cost = float('inf')
        self.nodes_explored = 0
        self.explored_nodes = set()
        self.frontier_nodes = set()
        self.path_found = False
        self.node_data = {}  # (x, y) -> {'g': cost, 'h': heuristic, 'f': total}

class Pathfinder:
    def __init__(self, maze, heuristic_type='MANHATTAN'):
        self.maze = maze
        self.heuristic_type = heuristic_type
    
    def manhattan_distance(self, x1, y1, x2, y2):
        """Manhattan distance heuristic"""
        return abs(x1 - x2) + abs(y1 - y2)
    
    def euclidean_distance(self, x1, y1, x2, y2):
        """Euclidean distance heuristic"""
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    def heuristic(self, x1, y1, x2, y2):
        """Calculate heuristic value"""
        if self.heuristic_type == 'MANHATTAN':
            return self.manhattan_distance(x1, y1, x2, y2)
        else:
            return self.euclidean_distance(x1, y1, x2, y2)
    
    def dijkstra(self, start, goal, discovered_cells=None):
        """
        Dijkstra's algorithm for shortest path
        Returns PathfindingResult with path, cost, and exploration data
        
        Args:
            discovered_cells: Set of (x, y) positions visible to AI (for fog of war).
                            If None, all cells are accessible.
        """
        result = PathfindingResult()
        pq = [(0, start)]  # Priority queue: (cost, position)
        came_from = {}
        cost_so_far = {start: 0}
        result.explored_nodes = set()
        
        # Helper to check if a cell is accessible (visible or discovered)
        def is_accessible(pos):
            if discovered_cells is None:
                return True  # All cells visible
            # Always allow start and goal positions (they're outside the maze)
            if pos == start or pos == goal:
                return True
            return pos in discovered_cells
        
        while pq:
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
                return result
            
            x, y = current
            neighbors = self.maze.get_neighbors(x, y, ENABLE_DIAGONALS)
            
            # Filter neighbors by discovered cells (fog of war)
            if discovered_cells is not None:
                neighbors = [n for n in neighbors if is_accessible(n)]
            
            for next_node in neighbors:
                nx, ny = next_node
                edge_cost = self.maze.get_cost(nx, ny)
                new_cost = current_cost + edge_cost
                
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    heapq.heappush(pq, (new_cost, next_node))
                    came_from[next_node] = current
        
        result.path_found = False
        return result
    
    def a_star(self, start, goal, discovered_cells=None):
        """
        A* algorithm with heuristic
        Returns PathfindingResult with path, cost, and exploration data
        
        Args:
            discovered_cells: Set of (x, y) positions visible to AI (for fog of war).
                            If None, all cells are accessible.
        """
        result = PathfindingResult()
        start_x, start_y = start
        goal_x, goal_y = goal
        
        pq = [(0, start)]  # Priority queue: (f_score, position)
        came_from = {}
        g_score = {start: 0}  # Actual cost from start
        f_score = {start: self.heuristic(start_x, start_y, goal_x, goal_y)}
        result.explored_nodes = set()
        result.frontier_nodes = {start}
        
        # Helper to check if a cell is accessible (visible or discovered)
        def is_accessible(pos):
            if discovered_cells is None:
                return True  # All cells visible
            # Always allow start and goal positions (they're outside the maze)
            if pos == start or pos == goal:
                return True
            return pos in discovered_cells
        
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
            
            # Filter neighbors by discovered cells (fog of war)
            if discovered_cells is not None:
                neighbors = [n for n in neighbors if is_accessible(n)]
            
            for next_node in neighbors:
                nx, ny = next_node
                edge_cost = self.maze.get_cost(nx, ny)
                tentative_g = g_score[current] + edge_cost
                
                if next_node not in g_score or tentative_g < g_score[next_node]:
                    came_from[next_node] = current
                    g_score[next_node] = tentative_g
                    h_score = self.heuristic(nx, ny, goal_x, goal_y)
                    f_score[next_node] = tentative_g + h_score
                    heapq.heappush(pq, (f_score[next_node], next_node))
                    result.frontier_nodes.add(next_node)
                    # Store node data for visualization
                    result.node_data[next_node] = {
                        'g': tentative_g,
                        'h': h_score,
                        'f': f_score[next_node]
                    }
        
        result.path_found = False
        return result
    
    def bidirectional_a_star(self, start, goal, discovered_cells=None):
        """
        Bidirectional A* for faster search
        Searches from both start and goal simultaneously
        
        Args:
            discovered_cells: Set of (x, y) positions visible to AI (for fog of war).
                            If None, all cells are accessible.
        """
        # Helper to check if a cell is accessible
        def is_accessible(pos):
            if discovered_cells is None:
                return True
            if pos == start or pos == goal:
                return True
            return pos in discovered_cells
        result = PathfindingResult()
        start_x, start_y = start
        goal_x, goal_y = goal
        
        # Forward search
        pq_forward = [(0, start)]
        came_from_forward = {}
        g_forward = {start: 0}
        explored_forward = set()
        
        # Backward search
        pq_backward = [(0, goal)]
        came_from_backward = {}
        g_backward = {goal: 0}
        explored_backward = set()
        
        meet_point = None
        
        while pq_forward and pq_backward:
            # Forward step
            if pq_forward:
                current_f, current = heapq.heappop(pq_forward)
                if current in explored_forward:
                    continue
                explored_forward.add(current)
                result.explored_nodes.add(current)
                result.nodes_explored += 1
                
                if current in explored_backward:
                    meet_point = current
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
                        h = self.heuristic(nx, ny, goal_x, goal_y)
                        f = new_g + h
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
                
                if current in explored_forward:
                    meet_point = current
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
                        h = self.heuristic(nx, ny, start_x, start_y)
                        f = new_g + h
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
            
            result.path = path_forward + path_backward
            result.cost = g_forward[meet_point] + g_backward[meet_point]
            result.path_found = True
        else:
            result.path_found = False
        
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
        
        # Strategy: Try different orderings of goals to find minimum cost path
        import itertools
        
        best_path = None
        best_cost = float('inf')
        best_order = None
        
        # Try all permutations of goal orderings
        for goal_order in itertools.permutations(goals):
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
                best_order = goal_order
        
        if best_path:
            result.path = best_path
            result.cost = best_cost
            result.path_found = True
        
        return result

