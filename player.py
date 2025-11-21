"""
Player controller and AI agent
Handles movement, path tracking, and cost calculation

This file contains two main classes:
1. Player - The human player that the user controls
2. AIAgent - The AI opponent that uses pathfinding algorithms

Both classes track:
- Current position
- Path taken
- Energy/cost
- Checkpoints reached
- Rewards collected
"""

import pygame  # For drawing the player/AI on screen
from config import *  # Import all configuration constants

class Player:
    """
    Represents the human player in the game.
    
    The Player class handles:
    - Movement (arrow keys/WASD)
    - Energy management (each move costs energy)
    - Path tracking (where the player has been)
    - Checkpoint collection
    - Reward collection and bonuses
    - Undo functionality
    """
    
    def __init__(self, maze, start_pos):
        """
        Initialize a new player.
        
        Args:
            maze: The maze object (contains terrain, obstacles, etc.)
            start_pos: Starting position (x, y) tuple
        """
        # Store reference to the maze (needed to check terrain, costs, etc.)
        self.maze = maze
        
        # Current position coordinates
        self.x, self.y = start_pos
        
        # List of all positions the player has visited (in order)
        # Starts with the starting position
        self.path = [start_pos]
        
        # Set of all cells the player has visited (for quick lookup)
        # Used to prevent revisiting if PREVENT_PATH_REVISITING is enabled
        self.visited_cells = {start_pos}
        
        # Total cost accumulated so far (sum of all terrain costs)
        self.total_cost = 0
        
        # Current energy remaining (starts at INITIAL_ENERGY from config)
        # Each move costs energy based on terrain
        self.energy = INITIAL_ENERGY
        
        # List of checkpoints the player has reached (in order)
        # Used for Multi-Goal mode to track progress
        self.reached_checkpoints = []
        
        # Flag to track if player moved this frame (used for animation/timing)
        self.moved_this_frame = False
        
        # History of all moves for undo functionality
        # Each entry stores: old position, new position, cost, energy before move, etc.
        self.move_history = []
        
        # ====================================================================
        # REWARD SYSTEM
        # ====================================================================
        # Rewards are gold cells that give temporary cost reduction bonuses
        
        # Set of reward cell positions that have been collected
        # Used to prevent collecting the same reward multiple times
        self.collected_rewards = set()
        
        # Whether the reward bonus is currently active
        # When True, next moves cost less energy
        self.reward_active = False
        
        # Number of moves remaining with the reward bonus active
        # Decreases by 1 each move, bonus expires when it reaches 0
        self.reward_moves_left = 0
    
    def get_position(self):
        """
        Get the player's current position.
        
        Returns:
            Tuple (x, y) representing current position
        """
        return (self.x, self.y)
    
    def move(self, dx, dy, allow_revisit=False):
        """
        Move the player in a direction.
        
        This is the main movement function. It:
        1. Checks if the move is valid (within bounds, not a wall)
        2. Calculates the cost of the move
        3. Applies reward bonuses if active
        4. Checks if player has enough energy
        5. Updates position, path, energy, and other state
        6. Handles reward collection and checkpoint detection
        
        Args:
            dx: Change in x direction (-1 for left, 1 for right, 0 for no change)
            dy: Change in y direction (-1 for up, 1 for down, 0 for no change)
            allow_revisit: If True, allows moving to previously visited cells
        
        Returns:
            True if move was successful, False if move failed (invalid, no energy, etc.)
        """
        # Calculate the new position
        new_x, new_y = self.x + dx, self.y + dy
        
        # ====================================================================
        # VALIDATION CHECKS
        # ====================================================================
        # Check if the new position is valid (within maze bounds) and passable (not a wall)
        if self.maze.is_valid(new_x, new_y) and self.maze.is_passable(new_x, new_y):
            
            # Check if revisiting is allowed
            # If PREVENT_PATH_REVISITING is True, player cannot go back to visited cells
            if PREVENT_PATH_REVISITING and not allow_revisit:
                if (new_x, new_y) in self.visited_cells:
                    return False  # Cannot revisit previous cells
            
            # ====================================================================
            # COST CALCULATION
            # ====================================================================
            # Get the base cost of moving to this cell (based on terrain type)
            # Examples: Grass = 1, Water = 3, Mud = 5, Lava = infinity (impassable)
            move_cost = self.maze.get_cost(new_x, new_y)
            
            # Apply reward bonus if active
            # Rewards reduce the cost of moves (REWARD_BONUS is negative, so it reduces cost)
            actual_cost = move_cost
            if self.reward_active and self.reward_moves_left > 0:
                # Add REWARD_BONUS (which is negative, so it reduces cost)
                # max(0, ...) ensures cost never goes below 0
                actual_cost = max(0, move_cost + REWARD_BONUS)
            
            # ====================================================================
            # ENERGY CHECK AND MOVE EXECUTION
            # ====================================================================
            # Check if the move is possible:
            # 1. The cell is not impassable (cost != infinity)
            # 2. Player has enough energy to pay for the move
            if move_cost != float('inf') and self.energy >= actual_cost:
                # ====================================================================
                # SAVE STATE FOR UNDO
                # ====================================================================
                # Before making the move, save all current state
                # This allows the player to undo the move later (U key)
                old_pos = (self.x, self.y)  # Previous position
                old_cost = self.total_cost   # Previous total cost
                old_energy = self.energy     # Previous energy
                old_reward_moves = self.reward_moves_left  # Previous reward moves remaining
                
                # ====================================================================
                # EXECUTE THE MOVE
                # ====================================================================
                # Update position to the new coordinates
                self.x, self.y = new_x, new_y
                
                # Add new position to path (list of all positions visited)
                self.path.append((self.x, self.y))
                
                # Mark this cell as visited (for preventing revisits)
                self.visited_cells.add((self.x, self.y))
                
                # Update total cost (accumulated cost of all moves)
                self.total_cost += actual_cost
                
                # Deduct energy (each move costs energy)
                self.energy -= actual_cost
                
                # Mark that player moved this frame (for animation/timing)
                self.moved_this_frame = True
                
                # ====================================================================
                # REWARD BONUS DURATION
                # ====================================================================
                # Decrease reward duration (bonus expires after REWARD_DURATION moves)
                if self.reward_active and self.reward_moves_left > 0:
                    self.reward_moves_left -= 1  # One move used up
                    if self.reward_moves_left == 0:
                        self.reward_active = False  # Bonus expired
                
                # ====================================================================
                # REWARD COLLECTION
                # ====================================================================
                # Check if the player is standing on a reward cell
                terrain = self.maze.terrain.get((self.x, self.y), 'GRASS')
                if terrain == 'REWARD' and (self.x, self.y) not in self.collected_rewards:
                    # Player collected a reward!
                    self.collected_rewards.add((self.x, self.y))  # Mark as collected
                    self.reward_active = True  # Activate the bonus
                    self.reward_moves_left = REWARD_DURATION  # Bonus lasts for REWARD_DURATION moves
                    # Note: We don't remove the reward from the maze
                    # This allows the AI to also see and collect rewards
                
                # ====================================================================
                # SAVE MOVE TO HISTORY (FOR UNDO)
                # ====================================================================
                # Save all information about this move so it can be undone
                self.move_history.append({
                    'old_pos': old_pos,                    # Where we came from
                    'new_pos': (self.x, self.y),           # Where we moved to
                    'cost': actual_cost,                    # Cost of this move
                    'total_cost_before': old_cost,         # Total cost before this move
                    'energy_before': old_energy,           # Energy before this move
                    'checkpoint_reached': False,          # Will be updated below if checkpoint reached
                    'reward_moves_before': old_reward_moves  # Reward moves before this move
                })
                
                # ====================================================================
                # CHECKPOINT DETECTION
                # ====================================================================
                # Check if the player reached a checkpoint (for Multi-Goal mode)
                if (self.x, self.y) in self.maze.checkpoints:
                    # Only add if not already reached (prevent duplicates)
                    if (self.x, self.y) not in self.reached_checkpoints:
                        self.reached_checkpoints.append((self.x, self.y))  # Add to reached list
                        # Update the move history to mark checkpoint was reached
                        if self.move_history:
                            self.move_history[-1]['checkpoint_reached'] = True
                
                # Move was successful!
                return True
        
        # Move failed (invalid position, wall, not enough energy, etc.)
        return False
    
    def undo(self):
        """
        Undo the last move - restore player to previous position and state.
        
        This function:
        1. Checks if there's a move to undo
        2. Checks if player has enough energy to pay undo cost
        3. Restores previous position, energy, and state
        4. Removes the move from history
        
        Returns:
            True if undo was successful, False if nothing to undo or not enough energy
        """
        # Check if there's anything to undo
        # Need at least one move in history and path must have more than just start position
        if len(self.move_history) == 0 or len(self.path) <= 1:
            return False  # Nothing to undo
        
        # Check if we have enough energy for undo cost
        # Undoing costs energy (UNDO_COST from config) to prevent abuse
        if self.energy < UNDO_COST:
            return False  # Not enough energy to undo
        
        # ====================================================================
        # RESTORE PREVIOUS STATE
        # ====================================================================
        # Get the last move from history (and remove it from the list)
        last_move = self.move_history.pop()
        
        # Restore previous position
        self.x, self.y = last_move['old_pos']
        
        # Remove the last position from path (undo the move)
        if self.path:
            self.path.pop()  # Remove last element
        
        # Remove the undone position from visited cells
        # This allows the player to visit it again if they want
        self.visited_cells.discard(last_move['new_pos'])
        
        # ====================================================================
        # RESTORE COSTS AND ENERGY
        # ====================================================================
        # Restore total cost to what it was before the move
        self.total_cost = last_move['total_cost_before']
        
        # Restore energy to what it was before the move, minus the undo cost
        # The undo itself costs energy (UNDO_COST) to prevent spamming undo
        self.energy = last_move['energy_before'] - UNDO_COST
        
        # ====================================================================
        # RESTORE REWARD STATE
        # ====================================================================
        # Restore reward bonus state to what it was before the move
        if 'reward_moves_before' in last_move:
            self.reward_moves_left = last_move['reward_moves_before']
            self.reward_active = self.reward_moves_left > 0  # Active if moves left > 0
        
        # ====================================================================
        # RESTORE CHECKPOINT STATE
        # ====================================================================
        # If a checkpoint was reached in the undone move, remove it from reached list
        if last_move.get('checkpoint_reached', False):
            if last_move['new_pos'] in self.reached_checkpoints:
                self.reached_checkpoints.remove(last_move['new_pos'])
        
        return True  # Undo successful
    
    def move_to(self, x, y):
        """Move directly to position (for AI)"""
        if self.maze.is_valid(x, y) and self.maze.is_passable(x, y):
            move_cost = self.maze.get_cost(x, y)
            if move_cost != float('inf'):
                old_x, old_y = self.x, self.y
                self.x, self.y = x, y
                if (self.x, self.y) not in self.path:
                    self.path.append((self.x, self.y))
                    self.total_cost += move_cost
                    self.energy -= move_cost
                
                # Check if reached checkpoint
                if (self.x, self.y) in self.maze.checkpoints:
                    if (self.x, self.y) not in self.reached_checkpoints:
                        self.reached_checkpoints.append((self.x, self.y))
                
                return True
        return False
    
    def has_reached_all_checkpoints(self):
        """Check if player has visited all checkpoints IN ORDER"""
        if len(self.reached_checkpoints) != len(self.maze.checkpoints):
            return False
        
        # Verify checkpoints were reached in the correct order
        for i, checkpoint in enumerate(self.maze.checkpoints):
            if i >= len(self.reached_checkpoints) or self.reached_checkpoints[i] != checkpoint:
                return False
        
        return True
    
    def reset(self, start_pos):
        """Reset player to start position"""
        self.x, self.y = start_pos
        self.path = [start_pos]
        self.visited_cells = {start_pos}
        self.total_cost = 0
        self.energy = INITIAL_ENERGY
        self.reached_checkpoints = []
        self.move_history = []
    
    def draw(self, screen, offset_x=0, offset_y=0, cell_size=None):
        """Draw player on screen with enhanced visuals"""
        cs = cell_size if cell_size is not None else CELL_SIZE
        center_x = offset_x + self.x * cs + cs // 2
        center_y = offset_y + self.y * cs + cs // 2
        radius = cs // 2 - 2
        
        # Draw glow effect
        for i in range(3, 0, -1):
            alpha = 30 // i
            glow_surf = pygame.Surface((radius * 2 + i * 4, radius * 2 + i * 4), pygame.SRCALPHA)
            glow_color = (*COLORS['PLAYER'], alpha)
            pygame.draw.circle(glow_surf, glow_color, 
                             (radius + i * 2, radius + i * 2), radius + i)
            screen.blit(glow_surf, (center_x - radius - i * 2, center_y - radius - i * 2))
        
        # Draw player circle
        pygame.draw.circle(screen, COLORS['PLAYER'], (center_x, center_y), radius)
        pygame.draw.circle(screen, COLORS['PLAYER_OUTLINE'], (center_x, center_y), radius, 2)
        
        # Draw direction indicator (small triangle)
        if len(self.path) > 1:
            prev_x, prev_y = self.path[-2]
            dx = self.x - prev_x
            dy = self.y - prev_y
            if dx != 0 or dy != 0:
                tip_x = center_x + dx * radius // 2
                tip_y = center_y + dy * radius // 2
                # Simple arrow
                pygame.draw.circle(screen, COLORS['PLAYER_OUTLINE'], (tip_x, tip_y), 3)

class AIAgent:
    """
    Represents the AI opponent in the game.
    
    The AIAgent class:
    - Uses pathfinding algorithms to find optimal paths
    - Moves automatically toward the goal
    - Handles checkpoints (in Multi-Goal and AI Duel modes)
    - Manages fog of war memory (in Blind Duel mode)
    - Tracks rewards and costs just like the player
    
    The AI is controlled by pathfinding algorithms (Dijkstra, A*, etc.)
    which calculate the best path, and the AI follows that path step by step.
    """
    
    def __init__(self, maze, start_pos, pathfinder):
        """
        Initialize a new AI agent.
        
        Args:
            maze: The maze object (contains terrain, obstacles, etc.)
            start_pos: Starting position (x, y) tuple
            pathfinder: Pathfinder object with pathfinding algorithms
        """
        # Store references
        self.maze = maze  # Reference to the maze (for checking terrain, costs, etc.)
        self.pathfinder = pathfinder  # Pathfinder with algorithms (Dijkstra, A*, etc.)
        
        # Current position coordinates
        self.x, self.y = start_pos
        
        # The path the AI plans to follow (calculated by pathfinding algorithm)
        # This is a list of positions from current position to goal
        self.path = []
        
        # Current index in the path (which step the AI is on)
        # When AI moves, it moves to path[current_path_index + 1]
        self.current_path_index = 0
        
        # Total cost accumulated by the AI (sum of all terrain costs)
        self.total_cost = 0
        
        # Last time the AI moved (for timing in non-turn-based modes)
        self.last_update_time = 0
        
        # Result from the last pathfinding calculation
        # Contains: path, cost, nodes explored, etc.
        self.path_result = None
        
        # Flag to track if AI is currently moving
        self.is_moving = False
        
        # History of all moves for undo functionality (same as player)
        self.move_history = []
        
        # List of checkpoints the AI has reached (in order)
        # Used for Multi-Goal and AI Duel modes
        self.reached_checkpoints = []
        
        # Set of all cells the AI has actually visited
        # Used for visualization and tracking
        self.visited_cells = {start_pos}
        
        # ====================================================================
        # REWARD TRACKING (same as player)
        # ====================================================================
        self.collected_rewards = set()  # Reward cells collected by AI
        self.reward_active = False      # Is reward bonus active?
        self.reward_moves_left = 0      # Moves remaining with bonus
        
        # ====================================================================
        # FOG OF WAR MEMORY (Blind Duel mode)
        # ====================================================================
        # In fog of war mode, AI can only see nearby cells
        # It remembers what it has seen before in this map
        
        # Memory map: stores terrain type for each cell the AI has seen
        # Key: (x, y) position, Value: terrain type ('GRASS', 'WATER', etc.)
        self.memory_map = {}
        
        # Recent positions visited (for revisit penalty)
        # AI avoids revisiting recently visited cells to prevent oscillation
        self.recent_positions = []
        
        # Maximum number of recent positions to track
        # Used to apply penalty for revisiting cells
        self.max_recent_positions = 10
    
    def reset(self, start_pos):
        """Reset AI to start position"""
        self.x, self.y = start_pos
        self.path = []
        self.current_path_index = 0
        self.total_cost = 0
        self.path_result = None
        self.move_history = []
        self.reached_checkpoints = []
        self.visited_cells = {start_pos}
        self.collected_rewards = set()
        self.reward_active = False
        self.reward_moves_left = 0
        # Memory map for fog of war (Blind Duel mode)
        self.memory_map = {}
        self.recent_positions = []
        self.max_recent_positions = 10
    
    def get_position(self):
        """Get current position"""
        return (self.x, self.y)
    
    def compute_path(self, goal, algorithm=None, discovered_cells=None):
        """
        Compute a path from current position to goal using a pathfinding algorithm.
        
        This is the core function that makes the AI "smart". It uses pathfinding algorithms
        (like Dijkstra, A*, etc.) to find the optimal path from the AI's current position
        to the goal, considering terrain costs, obstacles, and fog of war.
        
        The calculated path is stored in self.path, and the AI will follow it step by step.
        
        Args:
            goal: Target position (x, y) tuple OR list of goals for multi-objective search
                 - Single goal: (x, y) tuple
                 - Multiple goals: [(x1, y1), (x2, y2), ...] for checkpoints
            algorithm: Algorithm to use for pathfinding
                      - 'BFS': Breadth-First Search (unweighted)
                      - 'DIJKSTRA': Dijkstra's algorithm (optimal, slower)
                      - 'ASTAR': A* algorithm (optimal, faster with heuristics)
                      - 'BIDIRECTIONAL_ASTAR': Searches from both ends (very fast)
                      - 'MODIFIED_ASTAR_FOG': Modified A* for fog of war
                      - 'DSTAR': Dynamic A* for moving obstacles
                      - 'MULTI_OBJECTIVE': For multiple goals/checkpoints
                      - If None, uses default from config.py
            discovered_cells: Set of (x, y) positions that are visible (for fog of war)
                            - None = all cells visible (normal mode)
                            - Set of positions = only those cells are visible (fog of war)
                            - AI can only pathfind through discovered cells
        
        Returns:
            True if a path was found, False if no path exists
        """
        from config import AI_ALGORITHM
        
        # Use default algorithm from config if none specified
        if algorithm is None:
            algorithm = AI_ALGORITHM
        
        # Get AI's current position
        current_pos = (self.x, self.y)
        
        # ====================================================================
        # OBSTACLE COURSE MODE: PREDICTIVE PATHFINDING
        # ====================================================================
        # In Obstacle Course mode, obstacles change each turn
        # Use predictive pathfinding that accounts for future obstacle changes
        from game_modes import GameState
        is_obstacle_course = hasattr(self.maze, 'turn_number') and self.maze.turn_number > 0
        
        if is_obstacle_course and algorithm in ['BFS', 'DIJKSTRA', 'ASTAR', 'BIDIRECTIONAL_ASTAR']:
            # Predictive pathfinding simulates the entire path and predicts obstacle changes
            # This gives more accurate cost estimates
            self.path_result = self.pathfinder.predictive_pathfinding(
                current_pos, goal, 
                algorithm=algorithm,
                discovered_cells=discovered_cells
            )
        
        # ====================================================================
        # ALGORITHM SELECTION AND PATHFINDING
        # ====================================================================
        # Call the appropriate pathfinding algorithm based on the selected algorithm
        # Each algorithm returns a PathfindingResult with the path, cost, etc.
        
        elif algorithm == 'BFS':
            # Breadth-First Search: Explores uniformly, finds shortest path by steps (not cost)
            self.path_result = self.pathfinder.bfs(current_pos, goal, discovered_cells=discovered_cells)
            
        elif algorithm == 'DIJKSTRA':
            # Dijkstra's Algorithm: Guaranteed optimal path, explores by cost
            self.path_result = self.pathfinder.dijkstra(current_pos, goal, discovered_cells=discovered_cells)
            
        elif algorithm == 'ASTAR':
            # A* Algorithm: Fast heuristic-driven search, still optimal
            self.path_result = self.pathfinder.a_star(current_pos, goal, discovered_cells=discovered_cells)
            
        elif algorithm == 'MODIFIED_ASTAR_FOG':
            # Modified A* for fog of war: Handles limited visibility with memory
            # Uses memory map (remembers seen terrain) and revisit penalty (avoids oscillation)
            visited_set = set(self.recent_positions)  # Convert list to set for faster lookup
            self.path_result = self.pathfinder.modified_a_star_fog_of_war(
                current_pos, goal, 
                discovered_cells=discovered_cells,  # Only visible cells
                memory_map=self.memory_map,          # Remembered terrain
                visited_positions=visited_set,       # Recent positions (for penalty)
                revisit_penalty=5.0                 # Cost penalty for revisiting cells
            )
            
        elif algorithm == 'BIDIRECTIONAL_ASTAR':
            # Bidirectional A*: Searches from both start and goal simultaneously
            # Very fast for long paths
            self.path_result = self.pathfinder.bidirectional_a_star(current_pos, goal, discovered_cells=discovered_cells)
            
        elif algorithm == 'DSTAR':
            # D* (Dynamic A*): For moving obstacles, efficiently replans
            self.path_result = self.pathfinder.d_star(current_pos, goal, discovered_cells=discovered_cells)
            
        elif algorithm == 'MULTI_OBJECTIVE':
            # Multi-Objective Search: For multiple goals (checkpoints)
            # Finds optimal order to visit all goals
            if isinstance(goal, list):
                # Multiple goals: use multi-objective search
                self.path_result = self.pathfinder.multi_objective_search(current_pos, goal, discovered_cells=discovered_cells)
            else:
                # Single goal: fallback to A* (shouldn't happen, but safety check)
                self.path_result = self.pathfinder.a_star(current_pos, goal, discovered_cells=discovered_cells)
        else:
            # Unknown algorithm: default to A*
            self.path_result = self.pathfinder.a_star(current_pos, goal, discovered_cells=discovered_cells)
        
        # ====================================================================
        # STORE THE PATH
        # ====================================================================
        # If a path was found, store it and reset the path index
        if self.path_result.path_found:
            self.path = self.path_result.path  # Store the calculated path
            self.current_path_index = 0        # Start at beginning of path
            return True  # Path found successfully
        
        # No path found (goal unreachable, blocked by obstacles, etc.)
        return False
    
    def update(self, current_time, goal_pos, ai_speed):
        """Update AI position along computed path"""
        if not self.path_result or not self.path_result.path_found:
            return False
        
        if current_time - self.last_update_time >= ai_speed:
            if self.current_path_index < len(self.path) - 1:
                self.current_path_index += 1
                next_pos = self.path[self.current_path_index]
                old_pos = (self.x, self.y)
                old_cost = self.total_cost
                old_reward_moves = self.reward_moves_left
                
                # Calculate move cost with reward bonus BEFORE moving (same order as player)
                move_cost = self.maze.get_cost(next_pos[0], next_pos[1])
                actual_cost = move_cost
                if self.reward_active and self.reward_moves_left > 0:
                    from config import REWARD_BONUS
                    actual_cost = max(0, move_cost + REWARD_BONUS)  # Apply reward bonus
                
                # Now move to new position
                self.x, self.y = next_pos
                self.total_cost += actual_cost
                
                # Decrease reward duration AFTER paying cost (same as player)
                if self.reward_active and self.reward_moves_left > 0:
                    self.reward_moves_left -= 1
                    if self.reward_moves_left == 0:
                        self.reward_active = False
                        from config import DEBUG_MODE
                        if DEBUG_MODE:
                            print(f"[AI] Reward bonus expired.")
                
                # THEN check if this cell has a reward (collected AFTER move, bonus applies to NEXT moves)
                terrain = self.maze.terrain.get((self.x, self.y), 'GRASS')
                if terrain == 'REWARD' and (self.x, self.y) not in self.collected_rewards:
                    from config import REWARD_DURATION
                    self.collected_rewards.add((self.x, self.y))
                    self.reward_active = True
                    self.reward_moves_left = REWARD_DURATION
                    from config import DEBUG_MODE
                    if DEBUG_MODE:
                        print(f"[AI] Collected reward at {(self.x, self.y)}! Bonus applies to next {REWARD_DURATION} moves.")
                
                # Update memory map for fog of war (Blind Duel mode)
                self.memory_map[(self.x, self.y)] = terrain
                
                # Update recent positions for revisit penalty
                self.recent_positions.append((self.x, self.y))
                if len(self.recent_positions) > self.max_recent_positions:
                    self.recent_positions.pop(0)  # Remove oldest
                
                # Save move for undo
                self.move_history.append({
                    'old_pos': old_pos,
                    'new_pos': next_pos,
                    'cost': actual_cost,
                    'total_cost_before': old_cost,
                    'reward_moves_before': old_reward_moves
                })
                
                self.last_update_time = current_time
                return True
        
        return False
    
    def undo(self):
        """Undo last AI move - returns True if successful"""
        if len(self.move_history) == 0:
            return False  # Nothing to undo
        
        # Get last move
        last_move = self.move_history.pop()
        
        # Remove from visited cells
        if hasattr(self, 'visited_cells'):
            self.visited_cells.discard(last_move['new_pos'])
        
        # Restore previous position
        self.x, self.y = last_move['old_pos']
        
        # Restore cost (undo doesn't cost AI anything, but we restore state)
        self.total_cost = last_move['total_cost_before']
        
        # Restore reward state
        if 'reward_moves_before' in last_move:
            self.reward_moves_left = last_move['reward_moves_before']
            self.reward_active = self.reward_moves_left > 0
        
        # If we undid a move where we collected a reward, remove it
        if last_move['new_pos'] in self.collected_rewards:
            terrain = self.maze.terrain.get(last_move['new_pos'], 'GRASS')
            if terrain == 'REWARD':
                self.collected_rewards.discard(last_move['new_pos'])
        
        # If checkpoint was reached, remove it
        if last_move.get('checkpoint_reached', False):
            if last_move['new_pos'] in self.reached_checkpoints:
                self.reached_checkpoints.remove(last_move['new_pos'])
        
        # Adjust path index
        if self.current_path_index > 0:
            self.current_path_index -= 1
        
        return True
    
    def needs_replanning(self, goal_pos):
        """Check if path needs to be recomputed (e.g., obstacle blocked path)"""
        if not self.path_result or not self.path_result.path_found:
            return True
        
        # Check if current path is still valid (adaptive pathfinding)
        for i in range(self.current_path_index, len(self.path)):
            x, y = self.path[i]
            if not self.maze.is_passable(x, y):
                return True  # Path blocked by obstacle
        
        # Check if we've moved significantly (environment may have changed)
        # Always recompute if we're close to goal (final check)
        if self.current_path_index >= len(self.path) - 5:
            return True
        
        return False
    
    def reset(self, start_pos):
        """Reset AI to start position"""
        self.x, self.y = start_pos
        self.path = []
        self.current_path_index = 0
        self.total_cost = 0
        self.path_result = None
    
    def draw(self, screen, offset_x=0, offset_y=0, cell_size=None):
        """Draw AI agent on screen with enhanced visuals"""
        cs = cell_size if cell_size is not None else CELL_SIZE
        center_x = offset_x + self.x * cs + cs // 2
        center_y = offset_y + self.y * cs + cs // 2
        radius = cs // 2 - 2
        
        # Draw glow effect
        for i in range(3, 0, -1):
            alpha = 30 // i
            glow_surf = pygame.Surface((radius * 2 + i * 4, radius * 2 + i * 4), pygame.SRCALPHA)
            glow_color = (*COLORS['AI'], alpha)
            pygame.draw.circle(glow_surf, glow_color, 
                             (radius + i * 2, radius + i * 2), radius + i)
            screen.blit(glow_surf, (center_x - radius - i * 2, center_y - radius - i * 2))
        
        # Draw AI circle
        pygame.draw.circle(screen, COLORS['AI'], (center_x, center_y), radius)
        pygame.draw.circle(screen, COLORS['AI_OUTLINE'], (center_x, center_y), radius, 2)
        
        # Don't draw AI path in competitive/duel modes - player shouldn't see AI's planned route
        # AI path visualization is only for non-competitive learning modes

