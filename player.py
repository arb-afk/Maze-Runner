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
            if move_cost != float('inf') and self.energy >= move_cost:
                # Store state for undo
                old_pos = (self.x, self.y)
                old_cost = self.total_cost
                old_energy = self.energy
                
                self.x, self.y = new_x, new_y
                self.path.append((self.x, self.y))
                self.visited_cells.add((self.x, self.y))
                self.total_cost += move_cost
                self.energy -= move_cost
                self.moved_this_frame = True
                
                # Save move for undo
                self.move_history.append({
                    'old_pos': old_pos,
                    'new_pos': (self.x, self.y),
                    'cost': move_cost,
                    'total_cost_before': old_cost,
                    'energy_before': old_energy,
                    'checkpoint_reached': False
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
        """Check if player has visited all checkpoints"""
        return len(self.reached_checkpoints) == len(self.maze.checkpoints)
    
    def reset(self, start_pos):
        """Reset player to start position"""
        self.x, self.y = start_pos
        self.path = [start_pos]
        self.visited_cells = {start_pos}
        self.total_cost = 0
        self.energy = INITIAL_ENERGY
        self.reached_checkpoints = []
        self.move_history = []
    
    def draw(self, screen, offset_x=0, offset_y=0):
        """Draw player on screen with enhanced visuals"""
        center_x = offset_x + self.x * CELL_SIZE + CELL_SIZE // 2
        center_y = offset_y + self.y * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - 2
        
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
    
    def reset(self, start_pos):
        """Reset AI to start position"""
        self.x, self.y = start_pos
        self.path = []
        self.current_path_index = 0
        self.total_cost = 0
        self.path_result = None
        self.move_history = []
        self.reached_checkpoints = []
    
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
        
        # Select algorithm (pass discovered_cells for fog of war blindness)
        if algorithm == 'DIJKSTRA':
            self.path_result = self.pathfinder.dijkstra(current_pos, goal, discovered_cells=discovered_cells)
        elif algorithm == 'ASTAR':
            self.path_result = self.pathfinder.a_star(current_pos, goal, discovered_cells=discovered_cells)
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
                
                self.x, self.y = next_pos
                
                # Update cost
                move_cost = self.maze.get_cost(self.x, self.y)
                self.total_cost += move_cost
                
                # Save move for undo
                self.move_history.append({
                    'old_pos': old_pos,
                    'new_pos': next_pos,
                    'cost': move_cost,
                    'total_cost_before': old_cost
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
        
        # Restore previous position
        self.x, self.y = last_move['old_pos']
        
        # Restore cost (undo doesn't cost AI anything, but we restore state)
        self.total_cost = last_move['total_cost_before']
        
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
    
    def draw(self, screen, offset_x=0, offset_y=0):
        """Draw AI agent on screen with enhanced visuals"""
        center_x = offset_x + self.x * CELL_SIZE + CELL_SIZE // 2
        center_y = offset_y + self.y * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - 2
        
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

