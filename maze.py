"""
Maze generation and management system
Generates perfect mazes with walls and paths
"""

import random
import pygame
from config import *

class Maze:
    def __init__(self, width, height):
        # Use odd dimensions for proper maze generation
        self.width = width if width % 2 == 1 else width - 1
        self.height = height if height % 2 == 1 else height - 1
        # Walls: 0 = wall, 1 = path. Store as 2D grid of cell states
        # Also track which walls are open (north, east, south, west)
        self.cells = [[1 for _ in range(self.width)] for _ in range(self.height)]  # 1 = path, 0 = wall
        self.walls = {}  # (x, y, direction) -> True if open, False if wall
        self.start_pos = None
        self.goal_pos = None
        self.checkpoints = []
        self.dynamic_obstacles = set()  # Track obstacles spawned in dynamic mode
        self.terrain = {}  # Map (x, y) -> terrain type for path cells (GRASS, WATER, MUD)
        self.initialize_maze()
    
    def initialize_maze(self):
        """Generate a perfect maze using recursive backtracking"""
        # Start with all walls
        self.cells = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.walls = {}
        self.dynamic_obstacles.clear()  # Clear any existing obstacles
        self.terrain = {}  # Reset terrain
        
        # Initialize all walls as closed
        for y in range(self.height):
            for x in range(self.width):
                for direction in ['N', 'E', 'S', 'W']:
                    self.walls[(x, y, direction)] = False
        
        # Generate maze using recursive backtracking
        stack = []
        visited = set()
        
        # Start at (1, 1) - must be odd coordinates
        start_x, start_y = 1, 1
        stack.append((start_x, start_y))
        visited.add((start_x, start_y))
        self.cells[start_y][start_x] = 1
        
        directions = {
            'N': (0, -2),
            'E': (2, 0),
            'S': (0, 2),
            'W': (-2, 0)
        }
        
        while stack:
            current_x, current_y = stack[-1]
            
            # Find unvisited neighbors
            neighbors = []
            for direction, (dx, dy) in directions.items():
                nx, ny = current_x + dx, current_y + dy
                if (self.is_valid(nx, ny) and (nx, ny) not in visited):
                    neighbors.append((nx, ny, direction))
            
            if neighbors:
                # Choose random neighbor
                next_x, next_y, direction = random.choice(neighbors)
                
                # Remove wall between current and next
                wall_x, wall_y = current_x + directions[direction][0] // 2, current_y + directions[direction][1] // 2
                self.cells[wall_y][wall_x] = 1
                self.cells[next_y][next_x] = 1
                
                # Mark walls as open
                if direction == 'N':
                    self.walls[(current_x, current_y, 'N')] = True
                    self.walls[(next_x, next_y, 'S')] = True
                elif direction == 'E':
                    self.walls[(current_x, current_y, 'E')] = True
                    self.walls[(next_x, next_y, 'W')] = True
                elif direction == 'S':
                    self.walls[(current_x, current_y, 'S')] = True
                    self.walls[(next_x, next_y, 'N')] = True
                elif direction == 'W':
                    self.walls[(current_x, current_y, 'W')] = True
                    self.walls[(next_x, next_y, 'E')] = True
                
                visited.add((next_x, next_y))
                stack.append((next_x, next_y))
            else:
                stack.pop()
        
        # Set start and goal positions - outside the maze on left and right edges
        # Start is outside left edge, goal is outside right edge
        # Use -1 for start (outside) and width for goal (outside)
        self.start_pos = (-1, self.height // 2)  # Left side, middle
        self.goal_pos = (self.width, self.height // 2)  # Right side, middle
        
        # Ensure the entry and exit cells (adjacent to start/goal) are paths
        # Entry cell (where player enters maze from start)
        entry_x, entry_y = 0, self.height // 2
        if self.is_valid(entry_x, entry_y):
            self.cells[entry_y][entry_x] = 1
            # Open the west wall of the entry cell
            self.walls[(entry_x, entry_y, 'W')] = True
        
        # Exit cell (where player exits maze to goal)
        exit_x, exit_y = self.width - 1, self.height // 2
        if self.is_valid(exit_x, exit_y):
            self.cells[exit_y][exit_x] = 1
            # Open the east wall of the exit cell
            self.walls[(exit_x, exit_y, 'E')] = True
        
        # Assign terrain types to path cells
        self.assign_terrain()
        
        # Note: Lava obstacles are spawned after checkpoints are added
        # See spawn_initial_lava_obstacles() which should be called after maze setup
    
    def is_valid(self, x, y):
        """Check if coordinates are within bounds (or start/goal positions outside)"""
        # Allow start and goal positions which are outside the maze bounds
        if (x, y) == self.start_pos or (x, y) == self.goal_pos:
            return True
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_passable(self, x, y):
        """Check if cell is a path (not a wall)"""
        if not self.is_valid(x, y):
            return False
        # Start and goal positions outside the maze are always passable
        if (x, y) == self.start_pos or (x, y) == self.goal_pos:
            return True
        return self.cells[y][x] == 1
    
    def has_wall(self, x, y, direction):
        """Check if there's a wall in the given direction from cell (x, y)"""
        if not self.is_valid(x, y) or not self.is_passable(x, y):
            return True  # Out of bounds or current cell is wall = wall
        
        # Check adjacent cell
        dir_map = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
        dx, dy = dir_map[direction]
        nx, ny = x + dx, y + dy
        
        # If adjacent cell is out of bounds or is a wall, there's a wall
        if not self.is_valid(nx, ny) or not self.is_passable(nx, ny):
            return True
        
        # Both cells are passable, so no wall (unless explicitly set)
        # During generation, walls dict tracks opened passages
        # For rendering, if both are paths, draw no wall
        return False
    
    def get_neighbors(self, x, y, allow_diagonals=False):
        """Get valid neighboring path cells"""
        neighbors = []
        
        # Special handling for start/goal positions outside the maze
        if (x, y) == self.start_pos:
            # Start position: only neighbor is entry cell (0, height//2)
            entry_x, entry_y = 0, self.height // 2
            if self.is_valid(entry_x, entry_y) and self.is_passable(entry_x, entry_y):
                neighbors.append((entry_x, entry_y))
            return neighbors
        
        if (x, y) == self.goal_pos:
            # Goal position: only neighbor is exit cell (width-1, height//2)
            exit_x, exit_y = self.width - 1, self.height // 2
            if self.is_valid(exit_x, exit_y) and self.is_passable(exit_x, exit_y):
                neighbors.append((exit_x, exit_y))
            return neighbors
        
        directions = {
            'N': (0, -1),
            'E': (1, 0),
            'S': (0, 1),
            'W': (-1, 0)
        }
        
        for direction, (dx, dy) in directions.items():
            nx, ny = x + dx, y + dy
            # Special case: from entry cell, can go to start
            if (x, y) == (0, self.height // 2) and direction == 'W' and (nx, ny) == self.start_pos:
                neighbors.append((nx, ny))
            # Special case: from exit cell, can go to goal
            elif (x, y) == (self.width - 1, self.height // 2) and direction == 'E' and (nx, ny) == self.goal_pos:
                neighbors.append((nx, ny))
            # Check if wall is open in this direction
            elif not self.has_wall(x, y, direction) and self.is_passable(nx, ny):
                neighbors.append((nx, ny))
        
        if allow_diagonals:
            # Only allow diagonals if both adjacent cells are passable
            diagonal_dirs = {
                'NE': (1, -1),
                'SE': (1, 1),
                'SW': (-1, 1),
                'NW': (-1, -1)
            }
            for diag_dir, (dx, dy) in diagonal_dirs.items():
                nx, ny = x + dx, y + dy
                if self.is_passable(nx, ny):
                    # Check if we can reach diagonally (adjacent paths must be clear)
                    if diag_dir == 'NE' and not self.has_wall(x, y, 'N') and not self.has_wall(x, y, 'E'):
                        neighbors.append((nx, ny))
                    elif diag_dir == 'SE' and not self.has_wall(x, y, 'S') and not self.has_wall(x, y, 'E'):
                        neighbors.append((nx, ny))
                    elif diag_dir == 'SW' and not self.has_wall(x, y, 'S') and not self.has_wall(x, y, 'W'):
                        neighbors.append((nx, ny))
                    elif diag_dir == 'NW' and not self.has_wall(x, y, 'N') and not self.has_wall(x, y, 'W'):
                        neighbors.append((nx, ny))
        
        return neighbors
    
    def assign_terrain(self):
        """Assign terrain types to path cells"""
        import random
        terrain_types = ['GRASS', 'WATER', 'MUD']
        terrain_weights = [0.7, 0.2, 0.1]  # Grass most common
        
        self.terrain = {}
        for y in range(self.height):
            for x in range(self.width):
                if self.is_passable(x, y):
                    if (x, y) == self.start_pos:
                        self.terrain[(x, y)] = 'START'
                    elif (x, y) == self.goal_pos:
                        self.terrain[(x, y)] = 'GOAL'
                    elif (x, y) in self.checkpoints:
                        self.terrain[(x, y)] = 'CHECKPOINT'
                    else:
                        self.terrain[(x, y)] = random.choices(terrain_types, weights=terrain_weights)[0]
    
    def get_cost(self, x, y):
        """Get movement cost for a cell based on terrain"""
        if not self.is_passable(x, y):
            return float('inf')
        terrain = self.terrain.get((x, y), 'GRASS')
        return TERRAIN_COSTS.get(terrain, 1)
    
    def get_terrain(self, x, y):
        """Get terrain type for a cell"""
        if not self.is_passable(x, y):
            return 'WALL'
        return self.terrain.get((x, y), 'GRASS')
    
    def add_checkpoint(self, x, y):
        """Add a checkpoint to the maze (must be on a path)"""
        if self.is_valid(x, y) and self.is_passable(x, y):
            if (x, y) != self.start_pos and (x, y) != self.goal_pos:
                if (x, y) not in self.checkpoints:
                    self.checkpoints.append((x, y))
                    # Update terrain for checkpoint
                    if (x, y) in self.terrain:
                        self.terrain[(x, y)] = 'CHECKPOINT'
    
    def remove_checkpoint(self, x, y):
        """Remove a checkpoint"""
        if (x, y) in self.checkpoints:
            self.checkpoints.remove((x, y))
    
    def spawn_random_obstacle(self, player_path=None, radius=3, spawn_rate=0.05, checkpoints=None, reached_checkpoints=None):
        """
        Spawn obstacles (lava) on path cells near the player's path.
        NOTE: This converts path cells to walls temporarily.
        Original maze walls are NEVER changed - only obstacles (tracked in dynamic_obstacles) can spawn.
        Lava does NOT despawn - it persists once spawned.
        Ensures obstacles don't block path to goal/checkpoints.
        
        Args:
            player_path: List of (x, y) positions representing the player's path
            radius: Radius around player path cells to spawn obstacles (default 3)
            spawn_rate: Probability of spawning obstacle on each valid cell (default 0.05 = 5%)
            checkpoints: List of checkpoint positions to ensure path exists
            reached_checkpoints: List of reached checkpoints
        """
        if player_path is None or len(player_path) == 0:
            return None
        
        # Get cells near the player's path that can spawn obstacles
        cells_to_check = set()
        
        # Include cells near recent path positions (last few steps)
        recent_path = player_path[-5:] if len(player_path) > 5 else player_path
        
        for px, py in recent_path:
            # Add cells within radius of this path position
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    x, y = px + dx, py + dy
                    distance = abs(dx) + abs(dy)  # Manhattan distance
                    
                    # Only include cells within radius and valid
                    if distance <= radius and self.is_valid(x, y):
                        if self.is_passable(x, y) and (x, y) != self.start_pos and (x, y) != self.goal_pos:
                            if (x, y) not in (checkpoints or []) and (x, y) not in self.dynamic_obstacles:
                                # Don't spawn on adjacent cells to checkpoints/goal/start
                                too_close_to_critical = False
                                for cx, cy in [(self.start_pos[0], self.start_pos[1]), 
                                               (self.goal_pos[0], self.goal_pos[1])] + (checkpoints or []):
                                    if abs(x - cx) + abs(y - cy) <= 1:
                                        too_close_to_critical = True
                                        break
                                if not too_close_to_critical:
                                    cells_to_check.add((x, y))
        
        # Try spawning obstacles, but verify path still exists
        spawned = []
        from pathfinding import Pathfinder
        
        for x, y in cells_to_check:
            if random.random() < spawn_rate:
                # Temporarily add obstacle to test if it blocks path
                self.cells[y][x] = 0
                self.dynamic_obstacles.add((x, y))
                
                # Check if path to goal still exists
                pathfinder = Pathfinder(self, 'MANHATTAN')
                current_pos = player_path[-1] if player_path else self.start_pos
                
                # Build waypoint sequence
                unvisited_cps = []
                if checkpoints:
                    unvisited_cps = [cp for cp in checkpoints if cp not in (reached_checkpoints or [])]
                waypoints = [current_pos] + unvisited_cps + [self.goal_pos]
                
                # Check connectivity
                path_blocked = False
                for i in range(len(waypoints) - 1):
                    result = pathfinder.a_star(waypoints[i], waypoints[i + 1])
                    if not result.path_found:
                        path_blocked = True
                        break
                
                # If path is blocked, remove the obstacle
                if path_blocked:
                    self.cells[y][x] = 1
                    self.dynamic_obstacles.remove((x, y))
                else:
                    # Obstacle can stay - it doesn't block the path
                    spawned.append((x, y))
        
        return spawned if spawned else None
    
    def despawn_random_obstacle(self, player_path=None, radius=3, despawn_rate=0.08):
        """
        Lava obstacles do NOT despawn - they persist once spawned.
        This method is kept for compatibility but does nothing.
        """
        # Lava obstacles persist - no despawning
        return None
    
    def update_dynamic_terrain(self, player_path=None, radius=3):
        """
        Change terrain types (grass, water, mud) on path cells near the player's path.
        This creates dynamic obstacles that change costs but don't block paths.
        Only changes terrain cells near the player's current position and path.
        
        Args:
            player_path: List of (x, y) positions representing the player's path
            radius: Radius around player path cells to update (default 3)
        """
        if player_path is None or len(player_path) == 0:
            return
        
        # Get cells near the player's path to update
        cells_to_update = set()
        
        # Include cells near recent path positions (last few steps)
        recent_path = player_path[-5:] if len(player_path) > 5 else player_path
        
        for px, py in recent_path:
            # Add cells within radius of this path position
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    x, y = px + dx, py + dy
                    distance = abs(dx) + abs(dy)  # Manhattan distance
                    
                    # Only include cells within radius and valid
                    if distance <= radius and self.is_valid(x, y):
                        if self.is_passable(x, y) and (x, y) != self.start_pos and (x, y) != self.goal_pos:
                            if (x, y) not in self.checkpoints and (x, y) not in self.dynamic_obstacles:
                                cells_to_update.add((x, y))
        
        # Randomly change terrain on most (70-90%) of these cells
        cells_list = list(cells_to_update)
        if cells_list:
            # Change 70-90% of nearby cells
            change_probability = random.uniform(0.7, 0.9)
            num_to_change = int(len(cells_list) * change_probability)
            cells_to_change = random.sample(cells_list, min(num_to_change, len(cells_list)))
            
            for x, y in cells_to_change:
                # Randomly assign new terrain type
                new_terrain = random.choice(['GRASS', 'WATER', 'MUD'])
                self.terrain[(x, y)] = new_terrain
    
    def _update_walls_around(self, x, y):
        """Update wall connections when a cell changes from wall to path"""
        # When a cell becomes a path, open walls to adjacent path cells
        directions = {
            'W': (-1, 0),
            'E': (1, 0),
            'N': (0, -1),
            'S': (0, 1)
        }
        
        for direction, (dx, dy) in directions.items():
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny) and self.is_passable(nx, ny):
                # Open wall between current and neighbor
                self.walls[(x, y, direction)] = True
                # Open opposite wall on neighbor
                opposite = {'W': 'E', 'E': 'W', 'N': 'S', 'S': 'N'}[direction]
                self.walls[(nx, ny, opposite)] = True
    
    def has_path_through_all_checkpoints(self):
        """
        Check if there's at least one valid path from start through ALL checkpoints to goal.
        Returns True if such a path exists.
        """
        from pathfinding import Pathfinder
        
        if not self.checkpoints:
            # No checkpoints - just check start to goal
            pathfinder = Pathfinder(self, 'MANHATTAN')
            result = pathfinder.a_star(self.start_pos, self.goal_pos)
            return result.path_found
        
        # Try all permutations of checkpoint order to find a valid path
        import itertools
        pathfinder = Pathfinder(self, 'MANHATTAN')
        
        # Check if there's ANY order of checkpoints that allows a valid path
        for checkpoint_order in itertools.permutations(self.checkpoints):
            waypoints = [self.start_pos] + list(checkpoint_order) + [self.goal_pos]
            path_valid = True
            
            # Check connectivity between consecutive waypoints
            for i in range(len(waypoints) - 1):
                result = pathfinder.a_star(waypoints[i], waypoints[i + 1])
                if not result.path_found:
                    path_valid = False
                    break
            
            if path_valid:
                return True
        
        return False
    
    def spawn_initial_lava_obstacles(self, spawn_rate=0.08):
        """
        Spawn lava obstacles when maze is first generated.
        Ensures at least one path from start through all checkpoints to goal exists.
        Validates path through ALL checkpoints in ANY valid order.
        
        Args:
            spawn_rate: Probability of spawning obstacle on each valid cell (default 0.08 = 8%)
        """
        from pathfinding import Pathfinder
        
        # Get all path cells that can have obstacles
        path_cells = []
        for y in range(self.height):
            for x in range(self.width):
                if self.is_passable(x, y) and (x, y) != self.start_pos and (x, y) != self.goal_pos:
                    if (x, y) not in self.checkpoints:
                        # Don't spawn adjacent to start/goal/checkpoints
                        too_close = False
                        for cx, cy in [(self.start_pos[0], self.start_pos[1]), 
                                       (self.goal_pos[0], self.goal_pos[1])] + self.checkpoints:
                            if abs(x - cx) + abs(y - cy) <= 1:
                                too_close = True
                                break
                        if not too_close:
                            path_cells.append((x, y))
        
        # Randomly shuffle to spawn in random order
        import random
        random.shuffle(path_cells)
        
        # Try spawning obstacles, validating path after each one
        for x, y in path_cells:
            if random.random() < spawn_rate:
                # Temporarily add obstacle
                self.cells[y][x] = 0
                self.dynamic_obstacles.add((x, y))
                
                # Check if path through ALL checkpoints still exists (in any order)
                if not self.has_path_through_all_checkpoints():
                    # Path is blocked - remove the obstacle
                    self.cells[y][x] = 1
                    self.dynamic_obstacles.remove((x, y))
        
        # Final validation: ensure path still exists after all spawning attempts
        # If somehow path is broken, remove obstacles until it works
        # Be more aggressive - remove multiple obstacles per attempt
        max_attempts = 30
        attempt = 0
        while not self.has_path_through_all_checkpoints() and attempt < max_attempts and self.dynamic_obstacles:
            # Remove obstacles closest to checkpoints/goal
            obstacles_list = list(self.dynamic_obstacles)
            critical_points = [self.start_pos, self.goal_pos] + self.checkpoints
            
            # Calculate distance from each obstacle to nearest critical point
            obstacle_distances = []
            for obs_pos in obstacles_list:
                min_dist_to_critical = float('inf')
                for cp in critical_points:
                    dist = abs(obs_pos[0] - cp[0]) + abs(obs_pos[1] - cp[1])
                    min_dist_to_critical = min(min_dist_to_critical, dist)
                obstacle_distances.append((min_dist_to_critical, obs_pos))
            
            # Sort by distance (closest first) and remove multiple closest obstacles
            obstacle_distances.sort(key=lambda x: x[0])
            
            # Remove up to 5 closest obstacles per attempt
            num_to_remove = min(5, len(obstacle_distances))
            for i in range(num_to_remove):
                _, obs_pos = obstacle_distances[i]
                obs_x, obs_y = obs_pos
                self.cells[obs_y][obs_x] = 1
                self.dynamic_obstacles.remove((obs_x, obs_y))
                if (obs_x, obs_y) not in self.terrain:
                    self.terrain[(obs_x, obs_y)] = random.choice(['GRASS', 'WATER', 'MUD'])
                self._update_walls_around(obs_x, obs_y)
            
            attempt += 1
    
    def update_dynamic_obstacles(self, player_path=None, checkpoints=None, reached_checkpoints=None):
        """
        Update dynamic obstacles and terrain types.
        IMPORTANT: Original maze walls NEVER change - they are completely static.
        - Lava obstacles are spawned once during maze generation, not dynamically
        - Terrain types (grass, water, mud) can change dynamically on path cells near player
        This should ONLY be called when player or AI moves, not continuously.
        
        Args:
            player_path: Optional list of (x, y) positions representing the player's path
                         If provided, changes only affect cells near the path
            checkpoints: Optional list of checkpoint positions (unused, kept for compatibility)
            reached_checkpoints: Optional list of reached checkpoints (unused, kept for compatibility)
        """
        # Lava obstacles are spawned during maze generation, not here
        # Only update terrain types dynamically
        self.update_dynamic_terrain(player_path)
    
    def has_path_through_unvisited_checkpoints(self, start_pos, unvisited_checkpoints):
        """
        Check if there's at least one valid path from start through all unvisited checkpoints to goal.
        Returns True if such a path exists (tries all checkpoint order permutations).
        """
        from pathfinding import Pathfinder
        
        if not unvisited_checkpoints:
            # No unvisited checkpoints - just check start to goal
            pathfinder = Pathfinder(self, 'MANHATTAN')
            result = pathfinder.a_star(start_pos, self.goal_pos)
            return result.path_found
        
        # Try all permutations of checkpoint order to find a valid path
        import itertools
        pathfinder = Pathfinder(self, 'MANHATTAN')
        
        # Check if there's ANY order of checkpoints that allows a valid path to goal
        for checkpoint_order in itertools.permutations(unvisited_checkpoints):
            waypoints = [start_pos] + list(checkpoint_order) + [self.goal_pos]
            path_valid = True
            
            # Check connectivity between consecutive waypoints
            for i in range(len(waypoints) - 1):
                result = pathfinder.a_star(waypoints[i], waypoints[i + 1])
                if not result.path_found:
                    path_valid = False
                    break
            
            if path_valid:
                return True
        
        return False
    
    def ensure_path_to_goal(self, start_pos, checkpoints, reached_checkpoints):
        """
        Ensure there's at least one valid path from start through all unvisited checkpoints to goal.
        Removes blocking obstacles if necessary. Tries all checkpoint orders to find a valid path.
        Uses current player/AI position as start_pos, not original maze start.
        More aggressive: keeps removing obstacles until a valid path is found.
        """
        # Get unvisited checkpoints
        unvisited_cps = [cp for cp in checkpoints if cp not in reached_checkpoints]
        goal = self.goal_pos
        
        # If no unvisited checkpoints, just ensure path to goal
        if not unvisited_cps:
            from pathfinding import Pathfinder
            pathfinder = Pathfinder(self, 'MANHATTAN')
            result = pathfinder.a_star(start_pos, goal)
            if result.path_found:
                return  # Path exists, no need to remove obstacles
        
        # Keep trying to find a path by removing obstacles
        max_removal_attempts = 50  # More attempts to ensure path is found
        attempt = 0
        
        while attempt < max_removal_attempts:
            # Check if path exists through all unvisited checkpoints (in any order) to goal
            if self.has_path_through_unvisited_checkpoints(start_pos, unvisited_cps):
                return  # Path exists, we're done
            
            # No path found - need to remove obstacles
            if not self.dynamic_obstacles:
                # No more obstacles to remove, but path still doesn't exist
                # This shouldn't happen if initial validation worked, but handle it
                break
            
            # Find obstacles that are blocking the path
            # Strategy: remove obstacles closest to checkpoints and goal
            obstacles_list = list(self.dynamic_obstacles)
            critical_points = unvisited_cps + [goal]
            
            # Calculate distance from each obstacle to nearest critical point
            obstacle_distances = []
            for obs_pos in obstacles_list:
                min_dist_to_critical = float('inf')
                for cp in critical_points:
                    dist = abs(obs_pos[0] - cp[0]) + abs(obs_pos[1] - cp[1])
                    min_dist_to_critical = min(min_dist_to_critical, dist)
                obstacle_distances.append((min_dist_to_critical, obs_pos))
            
            # Sort by distance (closest first) and remove the closest ones
            obstacle_distances.sort(key=lambda x: x[0])
            
            # Remove closest obstacles (at least 1, up to 5 per attempt)
            num_to_remove = min(5, len(obstacle_distances))
            for i in range(num_to_remove):
                _, obs_pos = obstacle_distances[i]
                x, y = obs_pos
                self.cells[y][x] = 1  # Restore path
                self.dynamic_obstacles.discard((x, y))
                if (x, y) not in self.terrain:
                    import random
                    self.terrain[(x, y)] = random.choice(['GRASS', 'WATER', 'MUD'])
                self._update_walls_around(x, y)
            
            attempt += 1
        
        # Final check: ensure each checkpoint and goal has at least one adjacent path
        for wp in unvisited_cps + [goal]:
            adjacent_passable = False
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = wp[0] + dx, wp[1] + dy
                if self.is_valid(nx, ny) and self.is_passable(nx, ny):
                    adjacent_passable = True
                    break
            
            # If no adjacent path, remove obstacles around it
            if not adjacent_passable:
                for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                    nx, ny = wp[0] + dx, wp[1] + dy
                    if (nx, ny) in self.dynamic_obstacles:
                        self.cells[ny][nx] = 1
                        self.dynamic_obstacles.discard((nx, ny))
                        if (nx, ny) not in self.terrain:
                            import random
                            self.terrain[(nx, ny)] = random.choice(['GRASS', 'WATER', 'MUD'])
                        self._update_walls_around(nx, ny)
    
    def draw(self, screen, offset_x=0, offset_y=0, fog_of_war=None, player_pos=None):
        """Draw the maze with walls and paths"""
        # Calculate extended bounds to include start/goal outside maze
        # Start is at x=-1, Goal is at x=width
        left_extend = CELL_SIZE if self.start_pos and self.start_pos[0] < 0 else 0
        right_extend = CELL_SIZE if self.goal_pos and self.goal_pos[0] >= self.width else 0
        total_width = self.width * CELL_SIZE + left_extend + right_extend
        total_height = self.height * CELL_SIZE
        
        # Draw background for entire area including start/goal
        bg_rect = pygame.Rect(
            offset_x - left_extend,
            offset_y,
            total_width,
            total_height
        )
        pygame.draw.rect(screen, COLORS['BACKGROUND'], bg_rect)
        
        # Draw subtle border around the maze area
        border_thickness = 2
        pygame.draw.rect(screen, (200, 200, 200), bg_rect, border_thickness)
        
        # Draw start and goal positions if they're outside the grid
        # Draw start (left side, outside) - enhanced visual
        if self.start_pos and self.start_pos[0] < 0:
            start_rect = pygame.Rect(
                offset_x + self.start_pos[0] * CELL_SIZE,
                offset_y + self.start_pos[1] * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            # Draw background with gradient effect
            pygame.draw.rect(screen, COLORS['START'], start_rect)
            # Draw border
            pygame.draw.rect(screen, COLORS['START_DARK'], start_rect, 3)
            
            # Draw start icon (arrow or circle)
            center_x, center_y = start_rect.centerx, start_rect.centery
            # Outer circle
            pygame.draw.circle(screen, COLORS['START_DARK'], 
                             (center_x, center_y), CELL_SIZE // 2 - 4, 3)
            # Inner circle
            pygame.draw.circle(screen, (255, 255, 255), 
                             (center_x, center_y), CELL_SIZE // 3)
            # Arrow pointing right (toward maze)
            arrow_points = [
                (center_x + CELL_SIZE // 6, center_y),
                (center_x - CELL_SIZE // 6, center_y - CELL_SIZE // 8),
                (center_x - CELL_SIZE // 6, center_y + CELL_SIZE // 8)
            ]
            pygame.draw.polygon(screen, COLORS['START_DARK'], arrow_points)
            
            # Draw "START" label
            font = pygame.font.Font(None, 16)
            label = font.render("START", True, COLORS['START_DARK'])
            label_rect = label.get_rect(center=(center_x, start_rect.top - 10))
            if label_rect.top > 0:  # Only draw if within screen bounds
                screen.blit(label, label_rect)
        
        # Draw goal (right side, outside) - enhanced visual
        if self.goal_pos and self.goal_pos[0] >= self.width:
            goal_rect = pygame.Rect(
                offset_x + self.goal_pos[0] * CELL_SIZE,
                offset_y + self.goal_pos[1] * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            # Draw background
            pygame.draw.rect(screen, COLORS['GOAL'], goal_rect)
            # Draw border
            pygame.draw.rect(screen, COLORS['GOAL_DARK'], goal_rect, 3)
            
            # Draw goal icon with pulsing glow
            import time
            center_x, center_y = goal_rect.centerx, goal_rect.centery
            pulse = int(time.time() * 3) % 2
            # Outer glow
            glow_radius = CELL_SIZE // 2 - 2 + pulse * 2
            glow_surf = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4), pygame.SRCALPHA)
            glow_color = (*COLORS['GOAL_GLOW'], 150 - pulse * 50)
            pygame.draw.circle(glow_surf, glow_color, 
                             (glow_radius + 2, glow_radius + 2), glow_radius)
            screen.blit(glow_surf, (center_x - glow_radius - 2, center_y - glow_radius - 2))
            
            # Inner circle
            pygame.draw.circle(screen, COLORS['GOAL_GLOW'], 
                             (center_x, center_y), CELL_SIZE // 3)
            pygame.draw.circle(screen, COLORS['GOAL_DARK'], 
                             (center_x, center_y), 
                             CELL_SIZE // 4)
            # Star or checkmark in center
            pygame.draw.circle(screen, (255, 255, 255), 
                             (center_x, center_y), CELL_SIZE // 8)
            
            # Draw "GOAL" label
            font = pygame.font.Font(None, 16)
            label = font.render("GOAL", True, COLORS['GOAL_DARK'])
            label_rect = label.get_rect(center=(center_x, goal_rect.top - 10))
            if label_rect.top > 0:  # Only draw if within screen bounds
                screen.blit(label, label_rect)
        
        # Draw paths (white/light) and walls (dark)
        for y in range(self.height):
            for x in range(self.width):
                # Check fog of war
                visible = True
                if fog_of_war and player_pos:
                    px, py = player_pos
                    distance = abs(x - px) + abs(y - py)
                    visible = distance <= FOG_OF_WAR_RADIUS
                
                cell_rect = pygame.Rect(
                    offset_x + x * CELL_SIZE,
                    offset_y + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                
                if not visible:
                    # Draw fog
                    pygame.draw.rect(screen, COLORS['FOG'], cell_rect)
                    continue
                
                # Draw cell
                if self.cells[y][x] == 0:  # Wall or obstacle
                    # Check if this is a dynamic obstacle (lava) or a regular wall
                    if (x, y) in self.dynamic_obstacles:
                        # Draw lava obstacle (red/orange with glow effect)
                        pygame.draw.rect(screen, COLORS['LAVA'], cell_rect)
                        # Add glow/pulse effect
                        import time
                        pulse = int(time.time() * 4) % 2
                        glow_rect = cell_rect.inflate(pulse * 2, pulse * 2)
                        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                        glow_color = (*COLORS.get('LAVA_GLOW', (255, 100, 0)), 100)
                        pygame.draw.rect(glow_surf, glow_color, 
                                        pygame.Rect(0, 0, glow_rect.width, glow_rect.height))
                        screen.blit(glow_surf, glow_rect.topleft)
                        # Draw lava symbol or pattern
                        center_x, center_y = cell_rect.centerx, cell_rect.centery
                        pygame.draw.circle(screen, COLORS.get('LAVA_GLOW', (255, 150, 0)), 
                                         (center_x, center_y), CELL_SIZE // 3)
                    else:
                        # Draw regular wall with texture/shadow effect for depth
                        pygame.draw.rect(screen, COLORS['WALL'], cell_rect)
                        # Add subtle highlight for 3D effect
                        pygame.draw.line(screen, COLORS.get('WALL_LIGHT', (60, 60, 60)), 
                                       cell_rect.topleft, cell_rect.topright, 1)
                else:  # Path
                    # Get terrain-based color
                    terrain_type = self.terrain.get((x, y), 'GRASS')
                    
                    if terrain_type == 'WATER':
                        path_color = COLORS['WATER']
                    elif terrain_type == 'MUD':
                        path_color = COLORS['MUD']
                    elif terrain_type == 'GRASS':
                        path_color = COLORS.get('GRASS', (76, 175, 80))
                    else:
                        path_color = COLORS.get('PATH', (255, 255, 255))
                    
                    # Special cells get different colors
                    # Note: start/goal are now outside the grid, so skip them here
                    if (x, y) in self.checkpoints:
                        path_color = COLORS['CHECKPOINT']
                        pygame.draw.rect(screen, path_color, cell_rect)
                        # Draw checkpoint star (more visible)
                        import math
                        center_x, center_y = cell_rect.centerx, cell_rect.centery
                        outer_radius = CELL_SIZE // 3
                        inner_radius = outer_radius // 2
                        points = []
                        for i in range(10):  # 5-pointed star needs 10 points
                            angle = (i * math.pi / 5) - (math.pi / 2)
                            if i % 2 == 0:
                                px = center_x + int(outer_radius * math.cos(angle))
                                py = center_y + int(outer_radius * math.sin(angle))
                            else:
                                px = center_x + int(inner_radius * math.cos(angle))
                                py = center_y + int(inner_radius * math.sin(angle))
                            points.append((px, py))
                        if len(points) >= 3:
                            pygame.draw.polygon(screen, COLORS['CHECKPOINT_DARK'], points)
                            # Add outline for visibility
                            pygame.draw.polygon(screen, (255, 255, 255), points, 1)
                    else:
                        # Draw terrain-colored path
                        pygame.draw.rect(screen, path_color, cell_rect)
                        # Draw terrain cost
                        cost = self.get_cost(x, y)
                        if cost != float('inf') and terrain_type in ['GRASS', 'WATER', 'MUD']:
                            font = pygame.font.Font(None, 16)
                            cost_text = font.render(str(int(cost)), True, (255, 255, 255))
                            text_rect = cost_text.get_rect(center=(cell_rect.centerx, cell_rect.centery))
                            # Shadow for text
                            shadow = font.render(str(int(cost)), True, (0, 0, 0))
                            screen.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
                            screen.blit(cost_text, text_rect)
                    
                    # Draw grid lines (subtle)
                    pygame.draw.rect(screen, (230, 230, 230), cell_rect, 1)
        
        # Draw wall borders more prominently - thick black lines like in image
        wall_color = (20, 20, 20)  # Very dark/black for walls
        wall_thickness = 3
        
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x] == 1:  # Only draw borders for paths
                    cell_rect = pygame.Rect(
                        offset_x + x * CELL_SIZE,
                        offset_y + y * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                    
                    # Check fog of war
                    visible = True
                    if fog_of_war and player_pos:
                        px, py = player_pos
                        distance = abs(x - px) + abs(y - py)
                        visible = distance <= FOG_OF_WAR_RADIUS
                    
                    if not visible:
                        continue
                    
                    # Draw walls on edges
                    if self.has_wall(x, y, 'N') or y == 0:  # North wall or outer boundary
                        pygame.draw.line(screen, wall_color,
                                       (cell_rect.left, cell_rect.top),
                                       (cell_rect.right, cell_rect.top), wall_thickness)
                    if self.has_wall(x, y, 'E') or x == self.width - 1:  # East wall or outer boundary
                        pygame.draw.line(screen, wall_color,
                                       (cell_rect.right, cell_rect.top),
                                       (cell_rect.right, cell_rect.bottom), wall_thickness)
                    if self.has_wall(x, y, 'S') or y == self.height - 1:  # South wall or outer boundary
                        pygame.draw.line(screen, wall_color,
                                       (cell_rect.left, cell_rect.bottom),
                                       (cell_rect.right, cell_rect.bottom), wall_thickness)
                    if self.has_wall(x, y, 'W') or x == 0:  # West wall or outer boundary
                        pygame.draw.line(screen, wall_color,
                                       (cell_rect.left, cell_rect.top),
                                       (cell_rect.left, cell_rect.bottom), wall_thickness)
        
        # Draw outer border
        border_rect = pygame.Rect(
            offset_x,
            offset_y,
            self.width * CELL_SIZE,
            self.height * CELL_SIZE
        )
        pygame.draw.rect(screen, wall_color, border_rect, wall_thickness)
