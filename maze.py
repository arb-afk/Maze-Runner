"""
Maze generation and management system
Generates perfect mazes with walls and paths
"""

import random
import pygame
from config import *

class Maze:
    def __init__(self, width, height, seed=None):
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
        self.dynamic_obstacles = set()  # Track lava obstacles (used in Multi-Goal and AI Duel modes)
        self.terrain = {}  # Map (x, y) -> terrain type for path cells (GRASS, WATER, MUD, SPIKES, etc.)
        
        # Deterministic dynamic obstacles system
        self.obstacle_seed = seed if seed is not None else random.randint(0, 999999)
        self.obstacle_rng = random.Random(self.obstacle_seed)  # Separate RNG for obstacles
        self.turn_number = 0  # Track turn for deterministic changes
        
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
        
        # Note: Terrain assignment is done in game mode setup
        # This allows different modes to have different terrain types
        # Default assign_terrain() will be called if not overridden
        
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
    
    @staticmethod
    def random_terrain(include_obstacles: bool = False) -> tuple[list[str], list[float]]:
        """
        Helper function to get terrain types and weights for random selection.
        Reduces redundancy across terrain assignment logic.
        
        Args:
            include_obstacles: If True, include obstacle types (spikes, thorns, quicksand, rocks)
            
        Returns:
            Tuple of (terrain_types list, terrain_weights list)
        """
        if include_obstacles:
            # Obstacle Course mode: include obstacles in the terrain mix
            terrain_types = ['GRASS', 'WATER', 'MUD', 'SPIKES', 'THORNS', 'QUICKSAND', 'ROCKS']
            terrain_weights = [0.55, 0.15, 0.1, 0.05, 0.05, 0.05, 0.05]  # 55% grass, 20% obstacles
        else:
            # Normal mode: just basic terrain
            terrain_types = ['GRASS', 'WATER', 'MUD']
            terrain_weights = [0.7, 0.2, 0.1]  # Grass most common
        
        return terrain_types, terrain_weights
    
    def assign_terrain(self, include_obstacles: bool = False):
        """Assign terrain types to path cells
        
        Args:
            include_obstacles: If True, also place static obstacles (spikes, thorns, quicksand, rocks)
                             Used for Obstacle Course mode
        """
        import random
        
        terrain_types, terrain_weights = self.random_terrain(include_obstacles)
        
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
    
    def get_cost_for_terrain(self, terrain):
        """Get cost for a terrain type"""
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
    
    def spawn_static_obstacles(self, player_path=None, radius=4):
        """
        Spawn static obstacles (spikes, thorns, quicksand, rocks) near player path.
        These obstacles stay once placed, making it easier to understand the maze.
        
        Args:
            player_path: List of (x, y) positions representing the player's path
            radius: Radius around player path cells to spawn obstacles (default 4)
        """
        if player_path is None or len(player_path) == 0:
            return
        
        # Get cells near the player's path where obstacles can spawn
        cells_to_check = set()
        
        # Include cells near recent path positions (last 3 steps)
        recent_path = player_path[-3:] if len(player_path) > 3 else player_path
        
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
                                # Don't place on player's current or recent positions
                                if (x, y) not in recent_path:
                                    # Don't place obstacles if already have an obstacle type
                                    current_terrain = self.terrain.get((x, y), 'GRASS')
                                    if current_terrain in ['GRASS', 'PATH']:
                                        cells_to_check.add((x, y))
        
        # Spawn obstacles on some of these cells (lower rate - 10-20%)
        cells_list = list(cells_to_check)
        if cells_list:
            spawn_probability = 0.15  # 15% chance
            num_to_spawn = int(len(cells_list) * spawn_probability)
            cells_to_spawn = random.sample(cells_list, min(num_to_spawn, len(cells_list)))
            
            # Define obstacle types with weighted probabilities
            obstacle_types = ['SPIKES', 'THORNS', 'QUICKSAND', 'ROCKS']
            obstacle_weights = [0.25, 0.3, 0.2, 0.25]  # Thorns most common, quicksand least
            
            for x, y in cells_to_spawn:
                # Randomly assign obstacle type
                obstacle_type = random.choices(obstacle_types, weights=obstacle_weights)[0]
                self.terrain[(x, y)] = obstacle_type
    
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
    
    def spawn_reward_cells(self, spawn_rate=0.03):
        """
        Spawn reward cells that give temporary cost reduction when collected.
        
        Args:
            spawn_rate: Probability of spawning reward on each valid cell (default 0.03 = 3%)
        """
        import random
        
        # Get all passable cells that can have rewards
        for y in range(self.height):
            for x in range(self.width):
                # Don't spawn on start, goal, checkpoints, or obstacles
                if (x, y) == self.start_pos or (x, y) == self.goal_pos:
                    continue
                if (x, y) in self.checkpoints:
                    continue
                if not self.is_passable(x, y):
                    continue
                
                # Don't spawn adjacent to start/goal/checkpoints
                too_close = False
                for cx, cy in [(self.start_pos[0], self.start_pos[1]), 
                               (self.goal_pos[0], self.goal_pos[1])] + self.checkpoints:
                    if abs(x - cx) + abs(y - cy) <= 1:
                        too_close = True
                        break
                
                if not too_close and random.random() < spawn_rate:
                    # Spawn reward cell
                    self.terrain[(x, y)] = 'REWARD'
    
    def update_dynamic_obstacles(self, player_path=None, checkpoints=None, reached_checkpoints=None):
        """
        Update dynamic obstacles for Obstacle Course mode (turn-based, deterministic).
        Uses seeded RNG so AI can predict future obstacle changes.
        
        The same obstacle changes will occur on turn N regardless of who's simulating.
        This allows AI to look ahead and plan for future obstacle configurations.
        
        Args:
            player_path: Current path taken by player to avoid blocking
            checkpoints: List of checkpoint positions
            reached_checkpoints: List of reached checkpoints
        """
        from config import DYNAMIC_OBSTACLE_CHANGE_PER_TURN, DYNAMIC_OBSTACLE_MAX_CHANGES
        from pathfinding import Pathfinder
        
        self.turn_number += 1
        from config import DEBUG_MODE
        if DEBUG_MODE:
            print(f"[Dynamic Obstacles] Turn {self.turn_number}: Deterministic obstacle update (seed: {self.obstacle_seed})")
        
        obstacle_types = ['SPIKES', 'THORNS', 'QUICKSAND', 'ROCKS']
        total_changes = 0
        
        # Find current obstacles
        current_obstacles = []
        for y in range(self.height):
            for x in range(self.width):
                terrain = self.terrain.get((x, y), 'GRASS')
                if terrain in obstacle_types:
                    current_obstacles.append((x, y))
        
        # Remove exactly DYNAMIC_OBSTACLE_CHANGE_PER_TURN obstacles (deterministic)
        if current_obstacles:
            # Use deterministic RNG - same shuffle every time for this turn
            self.obstacle_rng.shuffle(current_obstacles)
            removed_count = 0
            for x, y in current_obstacles:
                if total_changes >= DYNAMIC_OBSTACLE_MAX_CHANGES:
                    break
                # Don't remove if player is currently on it
                if player_path and (x, y) == player_path[-1]:
                    continue
                # Replace with grass
                self.terrain[(x, y)] = 'GRASS'
                removed_count += 1
                total_changes += 1
                if removed_count >= DYNAMIC_OBSTACLE_CHANGE_PER_TURN:
                    break
            
            if removed_count > 0:
                from config import DEBUG_MODE
                if DEBUG_MODE:
                    print(f"[Dynamic Obstacles] Removed {removed_count} obstacles at positions")
        
        # Spawn exactly DYNAMIC_OBSTACLE_CHANGE_PER_TURN new obstacles (deterministic)
        valid_cells = []
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_passable(x, y):
                    continue
                if (x, y) == self.start_pos or (x, y) == self.goal_pos:
                    continue
                if checkpoints and (x, y) in checkpoints:
                    continue
                # Don't spawn on player's current position or recent path
                if player_path:
                    if (x, y) == player_path[-1]:
                        continue
                    if len(player_path) > 3 and (x, y) in player_path[-3:]:
                        continue
                
                terrain = self.terrain.get((x, y), 'GRASS')
                if terrain in ['GRASS', 'WATER', 'MUD']:  # Can spawn on basic terrain
                    valid_cells.append((x, y))
        
        if valid_cells:
            # Use deterministic RNG - same shuffle every time for this turn
            self.obstacle_rng.shuffle(valid_cells)
            spawned_count = 0
            
            for x, y in valid_cells:
                if total_changes >= DYNAMIC_OBSTACLE_MAX_CHANGES:
                    break
                if spawned_count >= DYNAMIC_OBSTACLE_CHANGE_PER_TURN:
                    break
                
                # Temporarily add obstacle (deterministic type selection)
                old_terrain = self.terrain.get((x, y), 'GRASS')
                new_obstacle = self.obstacle_rng.choice(obstacle_types)
                self.terrain[(x, y)] = new_obstacle
                
                # Check if path still exists from player to goal
                if not self._verify_path_exists(player_path, checkpoints, reached_checkpoints):
                    # Restore old terrain if path is blocked
                    self.terrain[(x, y)] = old_terrain
                else:
                    spawned_count += 1
                    total_changes += 1
            
            if spawned_count > 0:
                from config import DEBUG_MODE
                if DEBUG_MODE:
                    print(f"[Dynamic Obstacles] Spawned {spawned_count} new obstacles")
        
        from config import DEBUG_MODE
        if DEBUG_MODE:
            print(f"[Dynamic Obstacles] Turn {self.turn_number}: {total_changes} total changes")
    
    def get_future_obstacles(self, turns_ahead, current_path=None, checkpoints=None, reached_checkpoints=None):
        """
        Simulate future obstacle changes without modifying current state.
        Used by AI to predict obstacle configurations for multi-step lookahead.
        
        Args:
            turns_ahead: Number of turns to simulate into the future
            current_path: Current player/AI path
            checkpoints: Checkpoint positions
            reached_checkpoints: Reached checkpoints
            
        Returns:
            List of terrain dictionaries, one for each future turn
        """
        from config import DYNAMIC_OBSTACLE_CHANGE_PER_TURN, DYNAMIC_OBSTACLE_MAX_CHANGES
        
        # Create a temporary RNG with the same seed, advanced to future turn
        temp_rng = random.Random(self.obstacle_seed)
        
        # Advance RNG to current turn state
        for _ in range(self.turn_number):
            temp_rng.random()  # Consume random numbers to sync state
        
        # Simulate future turns
        future_configurations = []
        simulated_terrain = dict(self.terrain)  # Copy current terrain
        
        obstacle_types = ['SPIKES', 'THORNS', 'QUICKSAND', 'ROCKS']
        
        for turn in range(turns_ahead):
            # Simulate obstacle removal
            current_obstacles = [(x, y) for (x, y), t in simulated_terrain.items() 
                                if t in obstacle_types]
            
            if current_obstacles:
                temp_rng.shuffle(current_obstacles)
                for i in range(min(DYNAMIC_OBSTACLE_CHANGE_PER_TURN, len(current_obstacles))):
                    x, y = current_obstacles[i]
                    simulated_terrain[(x, y)] = 'GRASS'
            
            # Simulate obstacle spawning
            valid_cells = []
            for y in range(self.height):
                for x in range(self.width):
                    if not self.is_passable(x, y):
                        continue
                    terrain = simulated_terrain.get((x, y), 'GRASS')
                    if terrain in ['GRASS', 'WATER', 'MUD']:
                        valid_cells.append((x, y))
            
            if valid_cells:
                temp_rng.shuffle(valid_cells)
                for i in range(min(DYNAMIC_OBSTACLE_CHANGE_PER_TURN, len(valid_cells))):
                    x, y = valid_cells[i]
                    new_obstacle = temp_rng.choice(obstacle_types)
                    simulated_terrain[(x, y)] = new_obstacle
            
            # Store this configuration
            future_configurations.append(dict(simulated_terrain))
        
        return future_configurations
    
    def _verify_path_exists(self, player_path, checkpoints, reached_checkpoints):
        """Verify that a path still exists from player to goal through unvisited checkpoints"""
        from pathfinding import Pathfinder
        
        # Get player's current position
        if not player_path:
            start = self.start_pos
        else:
            start = player_path[-1]
        
        # Determine remaining checkpoints
        if checkpoints:
            unvisited = [cp for cp in checkpoints if cp not in (reached_checkpoints or [])]
            if unvisited:
                # Check if path exists through all unvisited checkpoints
                pf = Pathfinder(self, 'MANHATTAN')
                # Try a simple path to first unvisited checkpoint
                result = pf.a_star(start, unvisited[0])
                return result.path_found
        
        # No checkpoints or all visited - just check path to goal
        pf = Pathfinder(self, 'MANHATTAN')
        result = pf.a_star(start, self.goal_pos)
        return result.path_found
    
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
        from pathfinding import Pathfinder
        from config import AI_DIFFICULTY, HEURISTIC_TYPE
        # Use difficulty-based heuristic
        if AI_DIFFICULTY == 'HARD':
            heuristic = 'EUCLIDEAN'
        elif AI_DIFFICULTY == 'EASY':
            heuristic = 'MANHATTAN'
        else:
            heuristic = HEURISTIC_TYPE
        pathfinder = Pathfinder(self, heuristic)
        
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
            from config import AI_DIFFICULTY, HEURISTIC_TYPE
            # Use difficulty-based heuristic
            if AI_DIFFICULTY == 'HARD':
                heuristic = 'EUCLIDEAN'
            elif AI_DIFFICULTY == 'EASY':
                heuristic = 'MANHATTAN'
            else:
                heuristic = HEURISTIC_TYPE
            pathfinder = Pathfinder(self, heuristic)
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
    
    def draw(self, screen, offset_x=0, offset_y=0, fog_of_war=None, player_pos=None, cell_size=None, visibility_radius=None):
        """Draw the maze with walls and paths
        
        Args:
            cell_size: Override CELL_SIZE for scaled rendering (e.g. split-screen)
        """
        # Use custom cell size if provided, otherwise use global CELL_SIZE
        cs = cell_size if cell_size is not None else CELL_SIZE
        
        # Calculate extended bounds to include start/goal outside maze
        # Start is at x=-1, Goal is at x=width
        left_extend = cs if self.start_pos and self.start_pos[0] < 0 else 0
        right_extend = cs if self.goal_pos and self.goal_pos[0] >= self.width else 0
        total_width = self.width * cs + left_extend + right_extend
        total_height = self.height * cs
        
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
                offset_x + self.start_pos[0] * cs,
                offset_y + self.start_pos[1] * cs,
                cs,
                cs
            )
            # Draw background with gradient effect
            pygame.draw.rect(screen, COLORS['START'], start_rect)
            # Draw border
            pygame.draw.rect(screen, COLORS['START_DARK'], start_rect, 3)
            
            # Draw start icon (arrow or circle)
            center_x, center_y = start_rect.centerx, start_rect.centery
            # Outer circle
            pygame.draw.circle(screen, COLORS['START_DARK'], 
                             (center_x, center_y), cs // 2 - 4, 3)
            # Inner circle
            pygame.draw.circle(screen, (255, 255, 255), 
                             (center_x, center_y), cs // 3)
            # Arrow pointing right (toward maze)
            arrow_points = [
                (center_x + cs // 6, center_y),
                (center_x - cs // 6, center_y - cs // 8),
                (center_x - cs // 6, center_y + cs // 8)
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
                offset_x + self.goal_pos[0] * cs,
                offset_y + self.goal_pos[1] * cs,
                cs,
                cs
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
            glow_radius = cs // 2 - 2 + pulse * 2
            glow_surf = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4), pygame.SRCALPHA)
            glow_color = (*COLORS['GOAL_GLOW'], 150 - pulse * 50)
            pygame.draw.circle(glow_surf, glow_color, 
                             (glow_radius + 2, glow_radius + 2), glow_radius)
            screen.blit(glow_surf, (center_x - glow_radius - 2, center_y - glow_radius - 2))
            
            # Inner circle
            pygame.draw.circle(screen, COLORS['GOAL_GLOW'], 
                             (center_x, center_y), cs // 3)
            pygame.draw.circle(screen, COLORS['GOAL_DARK'], 
                             (center_x, center_y), 
                             cs // 4)
            # Star or checkmark in center
            pygame.draw.circle(screen, (255, 255, 255), 
                             (center_x, center_y), cs // 8)
            
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
                    # Use provided visibility radius, or fall back to config default
                    radius = visibility_radius if visibility_radius is not None else FOG_OF_WAR_RADIUS
                    visible = distance <= radius
                
                cell_rect = pygame.Rect(
                    offset_x + x * cs,
                    offset_y + y * cs,
                    cs,
                    cs
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
                                         (center_x, center_y), cs // 3)
                    else:
                        # Draw regular wall with texture/shadow effect for depth
                        pygame.draw.rect(screen, COLORS['WALL'], cell_rect)
                        # Add subtle highlight for 3D effect
                        pygame.draw.line(screen, COLORS.get('WALL_LIGHT', (60, 60, 60)), 
                                       cell_rect.topleft, cell_rect.topright, 1)
                else:  # Path
                    # Get terrain-based color
                    terrain_type = self.terrain.get((x, y), 'GRASS')
                    
                    # Special cells get different colors
                    # Note: start/goal are now outside the grid, so skip them here
                    if (x, y) in self.checkpoints:
                        path_color = COLORS['CHECKPOINT']
                        pygame.draw.rect(screen, path_color, cell_rect)
                        # Draw checkpoint star (more visible)
                        import math
                        center_x, center_y = cell_rect.centerx, cell_rect.centery
                        outer_radius = cs // 3
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
                        
                        # Checkpoint numbers removed - ordering is handled by AI pathfinding
                    # Draw obstacle types (SPIKES, THORNS, QUICKSAND, ROCKS)
                    elif terrain_type == 'SPIKES':
                        # Draw gray spikes obstacle with X pattern
                        pygame.draw.rect(screen, COLORS['SPIKES'], cell_rect)
                        # Draw X pattern (diagonal lines)
                        pygame.draw.line(screen, COLORS['SPIKES_DARK'], cell_rect.topleft, cell_rect.bottomright, 2)
                        pygame.draw.line(screen, COLORS['SPIKES_DARK'], cell_rect.topright, cell_rect.bottomleft, 2)
                        pygame.draw.rect(screen, COLORS['SPIKES_DARK'], cell_rect, 1)  # Thin border
                        # Draw cost number
                        cost = self.get_cost(x, y)
                        font = pygame.font.Font(None, 16)
                        cost_text = font.render(str(int(cost)), True, (255, 255, 255))
                        text_rect = cost_text.get_rect(center=(cell_rect.centerx, cell_rect.centery))
                        shadow = font.render(str(int(cost)), True, (0, 0, 0))
                        screen.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
                        screen.blit(cost_text, text_rect)
                    elif terrain_type == 'THORNS':
                        # Draw green thorny bushes with dot pattern
                        pygame.draw.rect(screen, COLORS['THORNS'], cell_rect)
                        # Draw dots in a pattern
                        cx, cy = cell_rect.centerx, cell_rect.centery
                        radius = 2
                        for dx in [-4, 0, 4]:
                            for dy in [-4, 0, 4]:
                                pygame.draw.circle(screen, COLORS['THORNS_DARK'], (cx + dx, cy + dy), radius)
                        pygame.draw.rect(screen, COLORS['THORNS_DARK'], cell_rect, 1)  # Thin border
                        # Draw cost number
                        cost = self.get_cost(x, y)
                        font = pygame.font.Font(None, 16)
                        cost_text = font.render(str(int(cost)), True, (255, 255, 255))
                        text_rect = cost_text.get_rect(center=(cell_rect.centerx, cell_rect.centery))
                        shadow = font.render(str(int(cost)), True, (0, 0, 0))
                        screen.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
                        screen.blit(cost_text, text_rect)
                    elif terrain_type == 'QUICKSAND':
                        # Draw tan/beige quicksand with diagonal stripe pattern
                        pygame.draw.rect(screen, COLORS['QUICKSAND'], cell_rect)
                        # Draw diagonal stripes
                        for i in range(cell_rect.left, cell_rect.right + cs, 4):
                            pygame.draw.line(screen, COLORS['QUICKSAND_DARK'], 
                                           (i, cell_rect.top), 
                                           (i + cs, cell_rect.bottom), 1)
                        pygame.draw.rect(screen, COLORS['QUICKSAND_DARK'], cell_rect, 1)  # Thin border
                        # Draw cost number
                        cost = self.get_cost(x, y)
                        font = pygame.font.Font(None, 16)
                        cost_text = font.render(str(int(cost)), True, (255, 255, 255))
                        text_rect = cost_text.get_rect(center=(cell_rect.centerx, cell_rect.centery))
                        shadow = font.render(str(int(cost)), True, (0, 0, 0))
                        screen.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
                        screen.blit(cost_text, text_rect)
                    elif terrain_type == 'ROCKS':
                        # Draw gray rocky terrain with circle pattern
                        pygame.draw.rect(screen, COLORS['ROCKS'], cell_rect)
                        # Draw circles for rocks
                        cx, cy = cell_rect.centerx, cell_rect.centery
                        pygame.draw.circle(screen, COLORS['ROCKS_DARK'], (cx - 5, cy - 5), 3)
                        pygame.draw.circle(screen, COLORS['ROCKS_DARK'], (cx + 5, cy), 3)
                        pygame.draw.circle(screen, COLORS['ROCKS_DARK'], (cx - 2, cy + 6), 3)
                        pygame.draw.rect(screen, COLORS['ROCKS_DARK'], cell_rect, 1)  # Thin border
                        # Draw cost number
                        cost = self.get_cost(x, y)
                        font = pygame.font.Font(None, 16)
                        cost_text = font.render(str(int(cost)), True, (255, 255, 255))
                        text_rect = cost_text.get_rect(center=(cell_rect.centerx, cell_rect.centery))
                        shadow = font.render(str(int(cost)), True, (0, 0, 0))
                        screen.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
                        screen.blit(cost_text, text_rect)
                    elif terrain_type == 'REWARD':
                        # Draw reward cell with glowing star effect
                        pygame.draw.rect(screen, COLORS['REWARD'], cell_rect)
                        # Draw animated glow effect (pulsing)
                        ticks = pygame.time.get_ticks()
                        pulse = abs((ticks % 2000) / 1000.0 - 1.0)  # Pulsing effect 0->1->0
                        glow_color = tuple(int(COLORS['REWARD'][i] * (0.7 + 0.3 * pulse)) for i in range(3))
                        
                        # Draw star shape
                        cx, cy = cell_rect.centerx, cell_rect.centery
                        star_radius = int(cs * 0.3)
                        # Draw plus sign for star
                        pygame.draw.line(screen, COLORS['REWARD_GLOW'], 
                                       (cx - star_radius, cy), (cx + star_radius, cy), 3)
                        pygame.draw.line(screen, COLORS['REWARD_GLOW'], 
                                       (cx, cy - star_radius), (cx, cy + star_radius), 3)
                        # Draw X for star
                        offset = int(star_radius * 0.7)
                        pygame.draw.line(screen, COLORS['REWARD_GLOW'], 
                                       (cx - offset, cy - offset), (cx + offset, cy + offset), 2)
                        pygame.draw.line(screen, COLORS['REWARD_GLOW'], 
                                       (cx - offset, cy + offset), (cx + offset, cy - offset), 2)
                        
                        pygame.draw.rect(screen, COLORS['REWARD_DARK'], cell_rect, 1)  # Border
                        
                        # Draw "R" or coin symbol
                        font = pygame.font.Font(None, 18)
                        symbol_text = font.render("R", True, (255, 255, 255))
                        text_rect = symbol_text.get_rect(center=(cx, cy))
                        shadow = font.render("R", True, (0, 0, 0))
                        screen.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
                        screen.blit(symbol_text, text_rect)
                    else:
                        # Draw regular terrain (WATER, MUD, GRASS, PATH)
                        if terrain_type == 'WATER':
                            path_color = COLORS['WATER']
                        elif terrain_type == 'MUD':
                            path_color = COLORS['MUD']
                        elif terrain_type == 'GRASS':
                            path_color = COLORS.get('GRASS', (76, 175, 80))
                        else:
                            path_color = COLORS.get('PATH', (255, 255, 255))
                        
                        # Draw terrain-colored path
                        pygame.draw.rect(screen, path_color, cell_rect)
                        # Draw terrain cost for all terrain types
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
                        offset_x + x * cs,
                        offset_y + y * cs,
                        cs,
                        cs
                    )
                    
                    # Check fog of war
                    visible = True
                    if fog_of_war and player_pos:
                        px, py = player_pos
                        distance = abs(x - px) + abs(y - py)
                        # Use provided visibility radius, or fall back to config default
                        radius = visibility_radius if visibility_radius is not None else FOG_OF_WAR_RADIUS
                        visible = distance <= radius
                    
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
            self.width * cs,
            self.height * cs
        )
        pygame.draw.rect(screen, wall_color, border_rect, wall_thickness)
