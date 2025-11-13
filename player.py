"""
Player controller and AI agent
Handles movement, path tracking, and cost calculation
"""

import pygame
from config import *

class Player:
    def __init__(self, maze, start_pos):
        self.maze = maze
        self.x, self.y = start_pos
        self.path = [start_pos]
        self.visited_cells = {start_pos}  # Track all visited cells
        self.total_cost = 0
        self.energy = INITIAL_ENERGY
        self.reached_checkpoints = []
        self.moved_this_frame = False
        self.move_history = []  # For undo: stores (position, cost, energy_before)
        # Reward system
        self.collected_rewards = set()  # Track collected reward cells
        self.reward_active = False  # Is reward bonus currently active?
        self.reward_moves_left = 0  # How many moves left with reward bonus
    
    def get_position(self):
        """Get current position"""
        return (self.x, self.y)
    
    def move(self, dx, dy, allow_revisit=False):
        """Move player in direction"""
        new_x, new_y = self.x + dx, self.y + dy
        
        if self.maze.is_valid(new_x, new_y) and self.maze.is_passable(new_x, new_y):
            # Check if revisiting is allowed
            if PREVENT_PATH_REVISITING and not allow_revisit:
                if (new_x, new_y) in self.visited_cells:
                    return False  # Cannot revisit previous cells
            
            move_cost = self.maze.get_cost(new_x, new_y)
            
            # Apply reward bonus if active
            actual_cost = move_cost
            if self.reward_active and self.reward_moves_left > 0:
                actual_cost = max(0, move_cost + REWARD_BONUS)  # Reduce cost by REWARD_BONUS
            
            if move_cost != float('inf') and self.energy >= actual_cost:
                # Store state for undo
                old_pos = (self.x, self.y)
                old_cost = self.total_cost
                old_energy = self.energy
                old_reward_moves = self.reward_moves_left
                
                self.x, self.y = new_x, new_y
                self.path.append((self.x, self.y))
                self.visited_cells.add((self.x, self.y))
                self.total_cost += actual_cost
                self.energy -= actual_cost
                self.moved_this_frame = True
                
                # Decrease reward duration
                if self.reward_active and self.reward_moves_left > 0:
                    self.reward_moves_left -= 1
                    if self.reward_moves_left == 0:
                        self.reward_active = False
                
                # Check for reward cell
                terrain = self.maze.terrain.get((self.x, self.y), 'GRASS')
                if terrain == 'REWARD' and (self.x, self.y) not in self.collected_rewards:
                    self.collected_rewards.add((self.x, self.y))
                    self.reward_active = True
                    self.reward_moves_left = REWARD_DURATION
                    # DON'T remove reward from maze - let it stay for AI to see
                    # self.maze.terrain[(self.x, self.y)] = 'GRASS'
                
                # Save move for undo
                self.move_history.append({
                    'old_pos': old_pos,
                    'new_pos': (self.x, self.y),
                    'cost': actual_cost,
                    'total_cost_before': old_cost,
                    'energy_before': old_energy,
                    'checkpoint_reached': False,
                    'reward_moves_before': old_reward_moves
                })
                
                # Check if reached checkpoint
                if (self.x, self.y) in self.maze.checkpoints:
                    if (self.x, self.y) not in self.reached_checkpoints:
                        self.reached_checkpoints.append((self.x, self.y))
                        if self.move_history:
                            self.move_history[-1]['checkpoint_reached'] = True
                
                return True
        return False
    
    def undo(self):
        """Undo last move - returns True if successful"""
        if len(self.move_history) == 0 or len(self.path) <= 1:
            return False  # Nothing to undo
        
        # Check if we have enough energy for undo cost
        if self.energy < UNDO_COST:
            return False  # Not enough energy to undo
        
        # Get last move
        last_move = self.move_history.pop()
        
        # Restore previous position
        self.x, self.y = last_move['old_pos']
        
        # Remove from path and visited
        if self.path:
            self.path.pop()
        self.visited_cells.discard(last_move['new_pos'])
        
        # Restore costs and energy
        # Remove the move cost and add undo cost
        self.total_cost = last_move['total_cost_before']
        self.energy = last_move['energy_before'] - UNDO_COST
        
        # Restore reward state
        if 'reward_moves_before' in last_move:
            self.reward_moves_left = last_move['reward_moves_before']
            self.reward_active = self.reward_moves_left > 0
        
        # If checkpoint was reached, remove it
        if last_move.get('checkpoint_reached', False):
            if last_move['new_pos'] in self.reached_checkpoints:
                self.reached_checkpoints.remove(last_move['new_pos'])
        
        return True
    
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
    def __init__(self, maze, start_pos, pathfinder):
        self.maze = maze
        self.pathfinder = pathfinder
        self.x, self.y = start_pos
        self.path = []
        self.current_path_index = 0
        self.total_cost = 0
        self.last_update_time = 0
        self.path_result = None
        self.is_moving = False
        self.move_history = []  # For undo: stores (position, cost, total_cost_before)
        self.reached_checkpoints = []  # Track AI checkpoints for checkpoint mode
        self.visited_cells = {start_pos}  # Track all cells AI has actually visited
        # Reward tracking (same as player)
        self.collected_rewards = set()
        self.reward_active = False
        self.reward_moves_left = 0
        # Memory map for fog of war (Blind Duel mode)
        self.memory_map = {}  # (x, y) -> terrain type (what AI has seen)
        self.recent_positions = []  # Last N positions visited (for revisit penalty)
        self.max_recent_positions = 10  # Keep track of last 10 positions
    
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
        Compute path to goal using specified algorithm
        
        Args:
            goal: Target position (x, y) or list of goals for multi-objective
            algorithm: Algorithm to use ('DIJKSTRA', 'ASTAR', 'BIDIRECTIONAL_ASTAR', 'DSTAR', 'MULTI_OBJECTIVE')
                      If None, uses default from config
            discovered_cells: Set of (x, y) positions that are visible (for fog of war blindness)
                            If None, all cells are visible. AI can only pathfind through discovered cells.
        """
        from config import AI_ALGORITHM
        
        if algorithm is None:
            algorithm = AI_ALGORITHM
        
        current_pos = (self.x, self.y)
        
        # Check if we're in Obstacle Course mode with dynamic obstacles
        # If so, use predictive pathfinding that accounts for future obstacle changes
        from game_modes import GameState
        is_obstacle_course = hasattr(self.maze, 'turn_number') and self.maze.turn_number > 0
        
        if is_obstacle_course and algorithm in ['BFS', 'DIJKSTRA', 'ASTAR', 'BIDIRECTIONAL_ASTAR']:
            # Use predictive pathfinding for dynamic obstacles
            self.path_result = self.pathfinder.predictive_pathfinding(
                current_pos, goal, 
                algorithm=algorithm,
                discovered_cells=discovered_cells
            )
        # Select algorithm (pass discovered_cells for fog of war blindness)
        elif algorithm == 'BFS':
            self.path_result = self.pathfinder.bfs(current_pos, goal, discovered_cells=discovered_cells)
        elif algorithm == 'DIJKSTRA':
            self.path_result = self.pathfinder.dijkstra(current_pos, goal, discovered_cells=discovered_cells)
        elif algorithm == 'ASTAR':
            self.path_result = self.pathfinder.a_star(current_pos, goal, discovered_cells=discovered_cells)
        elif algorithm == 'MODIFIED_ASTAR_FOG':
            # Modified A* for fog of war with memory map and revisit penalty
            visited_set = set(self.recent_positions)
            self.path_result = self.pathfinder.modified_a_star_fog_of_war(
                current_pos, goal, 
                discovered_cells=discovered_cells,
                memory_map=self.memory_map,
                visited_positions=visited_set,
                revisit_penalty=5.0
            )
        elif algorithm == 'BIDIRECTIONAL_ASTAR':
            self.path_result = self.pathfinder.bidirectional_a_star(current_pos, goal, discovered_cells=discovered_cells)
        elif algorithm == 'DSTAR':
            self.path_result = self.pathfinder.d_star(current_pos, goal, discovered_cells=discovered_cells)
        elif algorithm == 'MULTI_OBJECTIVE':
            # For multi-objective, goal should be a list
            if isinstance(goal, list):
                self.path_result = self.pathfinder.multi_objective_search(current_pos, goal, discovered_cells=discovered_cells)
            else:
                # Fallback to A* if single goal
                self.path_result = self.pathfinder.a_star(current_pos, goal, discovered_cells=discovered_cells)
        else:
            # Default to A*
            self.path_result = self.pathfinder.a_star(current_pos, goal, discovered_cells=discovered_cells)
        
        if self.path_result.path_found:
            self.path = self.path_result.path
            self.current_path_index = 0
            return True
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

