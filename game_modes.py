"""
Game modes manager
Handles different game modes: Explore, Dynamic, Multi-Goal, AI Duel
"""

import random
from maze import Maze
from player import Player, AIAgent
from pathfinding import Pathfinder
from config import *

class GameState:
    def __init__(self, mode='Explore'):
        self.mode = mode
        self.maze = None
        self.player = None
        self.ai_agent = None
        self.ai_pathfinder = None
        self.game_over = False
        self.winner = None
        self.message = ""
        self.turn = 'player'  # 'player' or 'ai' for turn-based mode
        self.fog_of_war = False
        self.algorithm_comparison = False
        self.show_hints = False  # Toggle for hint system
        self.discovered_cells = set()  # For fog of war (player's discovered cells)
        self.ai_discovered_cells = set()  # For fog of war (AI's discovered cells - separate from player)
        self.algorithm_results_cache = None  # Cache for algorithm comparison
        self.initialize_game()
    
    def initialize_game(self):
        """Initialize game based on current mode"""
        # Create maze
        self.maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
        
        # Create player
        if self.maze.start_pos:
            self.player = Player(self.maze, self.maze.start_pos)
        
        # Setup based on mode
        if self.mode == 'Explore':
            self.setup_explore_mode()
        elif self.mode == 'Dynamic':
            self.setup_dynamic_mode()
        elif self.mode == 'Multi-Goal':
            self.setup_multigoal_mode()
        elif self.mode == 'AI Duel':
            self.setup_ai_duel_mode()
        elif self.mode == 'AI Duel (Checkpoints)':
            self.setup_ai_duel_checkpoints_mode()
        
        # Spawn initial lava obstacles after maze and checkpoints are set up
        # This ensures path validation includes all checkpoints
        self.maze.spawn_initial_lava_obstacles()
        
        # Initialize discovered cells if fog of war is enabled
        # Add player's starting position and visibility radius
        if self.fog_of_war and self.player:
            px, py = self.player.get_position()
            from config import FOG_OF_WAR_RADIUS
            # Discover cells that are inside the maze bounds within visibility radius
            # Handle case where player starts outside maze (at start_pos = (-1, height//2))
            # Convert player position to entry cell if outside bounds
            player_cell_x = max(0, min(px, self.maze.width - 1))  # Clamp to maze bounds
            player_cell_y = max(0, min(py, self.maze.height - 1))  # Clamp to maze bounds
            
            for y in range(max(0, player_cell_y - FOG_OF_WAR_RADIUS), min(self.maze.height, player_cell_y + FOG_OF_WAR_RADIUS + 1)):
                for x in range(max(0, player_cell_x - FOG_OF_WAR_RADIUS), min(self.maze.width, player_cell_x + FOG_OF_WAR_RADIUS + 1)):
                    # Calculate distance from actual player position (may be outside maze)
                    distance = abs(x - px) + abs(y - py)
                    if distance <= FOG_OF_WAR_RADIUS:
                        self.discovered_cells.add((x, y))
        
        # Compute AI's initial path (without fog restrictions initially - fog can be toggled on later)
        if self.ai_agent:
            if self.mode == 'AI Duel':
                from config import AI_ALGORITHM
                algo = 'DSTAR' if self.mode == 'Dynamic' else AI_ALGORITHM
                # Only restrict if fog is enabled
                discovered_cells = self.ai_discovered_cells if self.fog_of_war else None
                if self.maze.goal_pos:
                    self.ai_agent.compute_path(self.maze.goal_pos, algorithm=algo, discovered_cells=discovered_cells)
            elif self.mode == 'AI Duel (Checkpoints)':
                from config import AI_ALGORITHM
                # Only restrict if fog is enabled
                discovered_cells = self.ai_discovered_cells if self.fog_of_war else None
                if self.maze.goal_pos:
                    if self.maze.checkpoints:
                        goals = self.maze.checkpoints + [self.maze.goal_pos]
                        self.ai_agent.compute_path(goals, algorithm='MULTI_OBJECTIVE', discovered_cells=discovered_cells)
                    else:
                        self.ai_agent.compute_path(self.maze.goal_pos, algorithm=AI_ALGORITHM, discovered_cells=discovered_cells)
        
        # Initialize AI's discovered cells if fog of war is enabled and AI exists
        if self.fog_of_war and self.ai_agent:
            ai_x, ai_y = self.ai_agent.get_position()
            from config import FOG_OF_WAR_RADIUS
            # Discover cells around AI's starting position
            ai_cell_x = max(0, min(ai_x, self.maze.width - 1))
            ai_cell_y = max(0, min(ai_y, self.maze.height - 1))
            
            for y in range(max(0, ai_cell_y - FOG_OF_WAR_RADIUS), min(self.maze.height, ai_cell_y + FOG_OF_WAR_RADIUS + 1)):
                for x in range(max(0, ai_cell_x - FOG_OF_WAR_RADIUS), min(self.maze.width, ai_cell_x + FOG_OF_WAR_RADIUS + 1)):
                    distance = abs(x - ai_x) + abs(y - ai_y)
                    if distance <= FOG_OF_WAR_RADIUS:
                        self.ai_discovered_cells.add((x, y))
            
            # Recompute path with fog restrictions now that discovered cells are initialized
            if self.mode == 'AI Duel':
                from config import AI_ALGORITHM
                algo = 'DSTAR' if self.mode == 'Dynamic' else AI_ALGORITHM
                if self.maze.goal_pos:
                    self.ai_agent.compute_path(self.maze.goal_pos, algorithm=algo, discovered_cells=self.ai_discovered_cells)
            elif self.mode == 'AI Duel (Checkpoints)':
                from config import AI_ALGORITHM
                if self.maze.goal_pos:
                    if self.maze.checkpoints:
                        goals = self.maze.checkpoints + [self.maze.goal_pos]
                        self.ai_agent.compute_path(goals, algorithm='MULTI_OBJECTIVE', discovered_cells=self.ai_discovered_cells)
                    else:
                        self.ai_agent.compute_path(self.maze.goal_pos, algorithm=AI_ALGORITHM, discovered_cells=self.ai_discovered_cells)
        
        self.game_over = False
        self.winner = None
        self.message = ""
    
    def setup_explore_mode(self):
        """Setup simple static maze mode"""
        # Static maze, no AI
        self.ai_agent = None
        self.ai_pathfinder = None
        self.fog_of_war = False
        self.discovered_cells = set()
    
    def setup_dynamic_mode(self):
        """Setup dynamic obstacles mode"""
        # Initial obstacles are spawned after mode setup in initialize_game()
        self.ai_agent = None
        self.ai_pathfinder = None
    
    def setup_multigoal_mode(self):
        """Setup multi-checkpoint mode"""
        # Clear any existing checkpoints
        self.maze.checkpoints = []
        
        # Add 2-3 checkpoints on path cells
        num_checkpoints = 3
        # Collect all path cells (ensure we have valid paths)
        path_cells = []
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.is_passable(x, y):
                    if (x, y) != self.maze.start_pos and (x, y) != self.maze.goal_pos:
                        # Make sure it's not too close to start/goal
                        start_dist = abs(x - self.maze.start_pos[0]) + abs(y - self.maze.start_pos[1])
                        goal_dist = abs(x - self.maze.goal_pos[0]) + abs(y - self.maze.goal_pos[1])
                        if start_dist > 3 and goal_dist > 3:  # At least 3 cells away
                            path_cells.append((x, y))
        
        # Randomly select checkpoint positions
        if path_cells and len(path_cells) >= num_checkpoints:
            checkpoint_positions = random.sample(path_cells, num_checkpoints)
            for x, y in checkpoint_positions:
                self.maze.add_checkpoint(x, y)
        elif path_cells:
            # If not enough cells, just use what we have
            for x, y in path_cells[:num_checkpoints]:
                self.maze.add_checkpoint(x, y)
        
        self.ai_agent = None
        self.ai_pathfinder = None
    
    def setup_ai_duel_mode(self):
        """Setup AI vs Player race mode (turn-based, no checkpoints)"""
        from config import AI_ALGORITHM
        self.ai_pathfinder = Pathfinder(self.maze, HEURISTIC_TYPE)
        if self.maze.start_pos:
            self.ai_agent = AIAgent(self.maze, self.maze.start_pos, self.ai_pathfinder)
            # Initial path will be computed after discovered cells are initialized in initialize_game()
        self.turn = 'player'  # Player goes first
    
    def setup_ai_duel_checkpoints_mode(self):
        """Setup AI vs Player race mode with checkpoints (turn-based)"""
        # Add checkpoints first
        self.maze.checkpoints = []
        num_checkpoints = 2  # Fewer checkpoints for competitive mode
        path_cells = []
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.is_passable(x, y):
                    if (x, y) != self.maze.start_pos and (x, y) != self.maze.goal_pos:
                        start_dist = abs(x - self.maze.start_pos[0]) + abs(y - self.maze.start_pos[1])
                        goal_dist = abs(x - self.maze.goal_pos[0]) + abs(y - self.maze.goal_pos[1])
                        if start_dist > 3 and goal_dist > 3:
                            path_cells.append((x, y))
        
        if path_cells and len(path_cells) >= num_checkpoints:
            checkpoint_positions = random.sample(path_cells, num_checkpoints)
            for x, y in checkpoint_positions:
                self.maze.add_checkpoint(x, y)
        
        # Setup AI
        from config import AI_ALGORITHM
        self.ai_pathfinder = Pathfinder(self.maze, HEURISTIC_TYPE)
        if self.maze.start_pos:
            self.ai_agent = AIAgent(self.maze, self.maze.start_pos, self.ai_pathfinder)
            # Initial path will be computed after discovered cells are initialized in initialize_game()
        self.turn = 'player'  # Player goes first
    
    def update(self, dt, current_time):
        """Update game state"""
        if self.game_over:
            return
        
        # Update discovered cells for fog of war (player's visibility)
        if self.fog_of_war:
            px, py = self.player.get_position()
            for y in range(max(0, py - FOG_OF_WAR_RADIUS), min(self.maze.height, py + FOG_OF_WAR_RADIUS + 1)):
                for x in range(max(0, px - FOG_OF_WAR_RADIUS), min(self.maze.width, px + FOG_OF_WAR_RADIUS + 1)):
                    distance = abs(x - px) + abs(y - py)
                    if distance <= FOG_OF_WAR_RADIUS:
                        self.discovered_cells.add((x, y))
            
            # Update AI's discovered cells for fog of war (AI's own visibility)
            if self.ai_agent:
                ai_x, ai_y = self.ai_agent.get_position()
                # Discover cells around AI's current position
                # Handle case where AI is outside maze bounds
                ai_cell_x = max(0, min(ai_x, self.maze.width - 1))
                ai_cell_y = max(0, min(ai_y, self.maze.height - 1))
                
                for y in range(max(0, ai_cell_y - FOG_OF_WAR_RADIUS), min(self.maze.height, ai_cell_y + FOG_OF_WAR_RADIUS + 1)):
                    for x in range(max(0, ai_cell_x - FOG_OF_WAR_RADIUS), min(self.maze.width, ai_cell_x + FOG_OF_WAR_RADIUS + 1)):
                        # Calculate distance from actual AI position (may be outside maze)
                        distance = abs(x - ai_x) + abs(y - ai_y)
                        if distance <= FOG_OF_WAR_RADIUS:
                            self.ai_discovered_cells.add((x, y))
        
        # Obstacles are now only updated on player/AI movement, not continuously
        # Check if path is blocked (for AI in duel modes)
        # NOTE: This check is redundant - pathfinding happens in make_ai_move() for turn-based
        # Keeping this for non-turn-based modes, but ensuring it respects fog of war
        if self.mode in ['AI Duel', 'AI Duel (Checkpoints)'] and self.ai_agent:
            goal = self.maze.goal_pos
            if self.ai_agent.needs_replanning(goal):
                from config import AI_ALGORITHM
                discovered_cells = self.ai_discovered_cells if self.fog_of_war else None
                self.ai_agent.compute_path(goal, algorithm=AI_ALGORITHM, discovered_cells=discovered_cells)
        
        # Update AI agent in Duel modes (turn-based with adaptive pathfinding)
        if (self.mode == 'AI Duel' or self.mode == 'AI Duel (Checkpoints)') and self.ai_agent:
            from config import AI_ALGORITHM
            goal = self.maze.goal_pos
            algorithm = AI_ALGORITHM
            
            # Determine algorithm based on mode
            if self.mode == 'AI Duel (Checkpoints)' and self.maze.checkpoints:
                unvisited = [cp for cp in self.maze.checkpoints if cp not in self.ai_agent.reached_checkpoints]
                if unvisited:
                    goal = unvisited + [self.maze.goal_pos]
                    algorithm = 'MULTI_OBJECTIVE'
            elif self.mode == 'Dynamic':
                algorithm = 'DSTAR'
            
            # Adaptive pathfinding: recompute if environment changed
            check_goal = goal if not isinstance(goal, list) else goal[0] if goal else None
            if check_goal and self.ai_agent.needs_replanning(check_goal):
                # If fog of war is enabled, AI is blind - only use AI's own discovered cells
                discovered_cells = self.ai_discovered_cells if self.fog_of_war else None
                self.ai_agent.compute_path(goal, algorithm=algorithm, discovered_cells=discovered_cells)
            # Only update if it's AI's turn (turn-based mode)
            if TURN_BASED:
                # AI moves handled separately when turn changes
                pass
            else:
                self.ai_agent.update(current_time, goal, AI_SPEED)
        
        # Check win conditions
        self.check_win_conditions()
    
    def make_ai_move(self):
        """Make AI move in turn-based mode"""
        if (self.mode == 'AI Duel' or self.mode == 'AI Duel (Checkpoints)') and self.ai_agent and self.turn == 'ai':
            from config import AI_ALGORITHM
            
            # Determine goal and algorithm based on mode
            goal = self.maze.goal_pos
            algorithm = AI_ALGORITHM
            
            if self.mode == 'AI Duel (Checkpoints)' and self.maze.checkpoints:
                # Use multi-objective search for checkpoint mode
                unvisited = [cp for cp in self.maze.checkpoints if cp not in self.ai_agent.reached_checkpoints]
                if unvisited:
                    # Pass all unvisited checkpoints + goal for multi-objective
                    goal = unvisited + [self.maze.goal_pos]
                    algorithm = 'MULTI_OBJECTIVE'
                elif self.maze.goal_pos:
                    # All checkpoints reached, just go to goal
                    goal = self.maze.goal_pos
            elif self.mode == 'Dynamic':
                # Use D* for dynamic obstacles
                algorithm = 'DSTAR'
            
            # IMPORTANT: Update AI's discovered cells BEFORE pathfinding (if fog of war enabled)
            # This ensures AI sees its current position before computing path
            if self.fog_of_war:
                ai_x, ai_y = self.ai_agent.get_position()
                from config import FOG_OF_WAR_RADIUS
                ai_cell_x = max(0, min(ai_x, self.maze.width - 1))
                ai_cell_y = max(0, min(ai_y, self.maze.height - 1))
                
                for y in range(max(0, ai_cell_y - FOG_OF_WAR_RADIUS), min(self.maze.height, ai_cell_y + FOG_OF_WAR_RADIUS + 1)):
                    for x in range(max(0, ai_cell_x - FOG_OF_WAR_RADIUS), min(self.maze.width, ai_cell_x + FOG_OF_WAR_RADIUS + 1)):
                        distance = abs(x - ai_x) + abs(y - ai_y)
                        if distance <= FOG_OF_WAR_RADIUS:
                            self.ai_discovered_cells.add((x, y))
            
            # Check if replanning needed (handle list goals)
            check_goal = goal if not isinstance(goal, list) else goal[0] if goal else None
            if check_goal and self.ai_agent.needs_replanning(check_goal):
                # If fog of war is enabled, AI is blind - only use AI's own discovered cells
                discovered_cells = self.ai_discovered_cells if self.fog_of_war else None
                self.ai_agent.compute_path(goal, algorithm=algorithm, discovered_cells=discovered_cells)
            
            if self.ai_agent.path_result and self.ai_agent.path_result.path_found:
                if self.ai_agent.current_path_index < len(self.ai_agent.path) - 1:
                    self.ai_agent.current_path_index += 1
                    next_pos = self.ai_agent.path[self.ai_agent.current_path_index]
                    old_pos = (self.ai_agent.x, self.ai_agent.y)
                    old_cost = self.ai_agent.total_cost
                    
                    self.ai_agent.x, self.ai_agent.y = next_pos
                    
                    # Discover new cells immediately after AI moves (before next path computation)
                    if self.fog_of_war:
                        ai_x, ai_y = self.ai_agent.get_position()
                        from config import FOG_OF_WAR_RADIUS
                        ai_cell_x = max(0, min(ai_x, self.maze.width - 1))
                        ai_cell_y = max(0, min(ai_y, self.maze.height - 1))
                        
                        for y in range(max(0, ai_cell_y - FOG_OF_WAR_RADIUS), min(self.maze.height, ai_cell_y + FOG_OF_WAR_RADIUS + 1)):
                            for x in range(max(0, ai_cell_x - FOG_OF_WAR_RADIUS), min(self.maze.width, ai_cell_x + FOG_OF_WAR_RADIUS + 1)):
                                distance = abs(x - ai_x) + abs(y - ai_y)
                                if distance <= FOG_OF_WAR_RADIUS:
                                    self.ai_discovered_cells.add((x, y))
                    
                    # Check if reached checkpoint
                    checkpoint_reached = False
                    if (self.ai_agent.x, self.ai_agent.y) in self.maze.checkpoints:
                        if (self.ai_agent.x, self.ai_agent.y) not in self.ai_agent.reached_checkpoints:
                            self.ai_agent.reached_checkpoints.append((self.ai_agent.x, self.ai_agent.y))
                            checkpoint_reached = True
                    
                    # Update cost and save for undo
                    move_cost = self.maze.get_cost(self.ai_agent.x, self.ai_agent.y)
                    self.ai_agent.total_cost += move_cost
                    
                    # Save move for undo
                    self.ai_agent.move_history.append({
                        'old_pos': old_pos,
                        'new_pos': next_pos,
                        'cost': move_cost,
                        'total_cost_before': old_cost,
                        'checkpoint_reached': checkpoint_reached
                    })
                    
                    # Update obstacles after AI move (in Dynamic/Duel modes)
                    if self.mode == 'Dynamic' or self.mode in ['AI Duel', 'AI Duel (Checkpoints)']:
                        # Pass AI path so terrain changes near AI position
                        # For AI, we can use a simulated path based on current position
                        ai_path = [(self.ai_agent.x, self.ai_agent.y)] if self.ai_agent else []
                        self.maze.update_dynamic_obstacles(ai_path)
                        
                        # Ensure path to goal still exists (remove blocking obstacles if needed)
                        if self.mode in ['Multi-Goal', 'AI Duel (Checkpoints)']:
                            ai_pos = self.ai_agent.get_position()
                            self.maze.ensure_path_to_goal(
                                ai_pos,
                                self.maze.checkpoints,
                                self.ai_agent.reached_checkpoints if hasattr(self.ai_agent, 'reached_checkpoints') else []
                            )
                        
                        # Also ensure player's path is still valid (for Multi-Goal mode)
                        if self.mode == 'Multi-Goal':
                            player_pos = self.player.get_position()
                            self.maze.ensure_path_to_goal(
                                player_pos,
                                self.maze.checkpoints,
                                self.player.reached_checkpoints
                            )
                        
                        # Check if path needs replanning after obstacle change
                        if self.ai_agent.needs_replanning(goal):
                            self.ai_agent.compute_path(goal)
                    
                    # Switch back to player's turn
                    self.turn = 'player'
                    return True
        return False
    
    def is_player_trapped(self):
        """Check if player is trapped (no valid unvisited moves and no path to goal)"""
        player_pos = self.player.get_position()
        
        # Check if there are any valid unvisited adjacent cells
        has_unvisited_move = False
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            new_x, new_y = player_pos[0] + dx, player_pos[1] + dy
            if self.maze.is_valid(new_x, new_y) and self.maze.is_passable(new_x, new_y):
                if (new_x, new_y) not in self.player.visited_cells:
                    move_cost = self.maze.get_cost(new_x, new_y)
                    if move_cost != float('inf') and self.player.energy >= move_cost:
                        has_unvisited_move = True
                        break
        
        # If there are unvisited moves, player is not trapped
        if has_unvisited_move:
            return False
        
        # No unvisited moves - check if there's still a path to goal
        # (considering visited cells as blocked)
        pathfinder = Pathfinder(self.maze, HEURISTIC_TYPE)
        
        # In multi-goal/checkpoint modes, check path through ALL unvisited checkpoints to goal
        if (self.mode == 'Multi-Goal' or self.mode == 'AI Duel (Checkpoints)') and self.maze.checkpoints:
            unvisited = [cp for cp in self.maze.checkpoints if cp not in self.player.reached_checkpoints]
            if unvisited:
                # Check if there's a path through all unvisited checkpoints (in any order) to goal
                # Use the maze's method that tries all permutations
                if not self.maze.has_path_through_unvisited_checkpoints(player_pos, unvisited):
                    return True  # No path exists - trapped
                
                # Path exists - check if it uses unvisited cells
                # Try to find a valid path sequence
                import itertools
                found_unvisited_path = False
                for checkpoint_order in itertools.permutations(unvisited):
                    waypoints = [player_pos] + list(checkpoint_order) + [self.maze.goal_pos]
                    all_segments_valid = True
                    uses_unvisited = False
                    
                    for i in range(len(waypoints) - 1):
                        result = pathfinder.a_star(waypoints[i], waypoints[i + 1])
                        if not result.path_found:
                            all_segments_valid = False
                            break
                        # Check if this segment uses unvisited cells
                        for pos in result.path[1:]:  # Skip first (already visited)
                            if pos not in self.player.visited_cells:
                                uses_unvisited = True
                                break
                    
                    if all_segments_valid and uses_unvisited:
                        found_unvisited_path = True
                        break
                
                if not found_unvisited_path:
                    return True  # Path exists but only through visited cells - trapped
                return False  # Found a valid path with unvisited cells
        
        # Regular mode - just check path to goal
        goal = self.maze.goal_pos
        result = pathfinder.a_star(player_pos, goal)
        if result.path_found:
            # Check if the path goes through any unvisited cells
            for pos in result.path[1:]:  # Skip current position
                if pos not in self.player.visited_cells:
                    return False  # There's a path with unvisited cells
            # Path exists but only through visited cells - player is trapped
            return True
        
        # No path to goal at all
        return True
    
    def check_win_conditions(self):
        """Check if game is won or lost"""
        player_pos = self.player.get_position()
        
        # Check if player reached goal
        if player_pos == self.maze.goal_pos:
            if self.mode == 'Multi-Goal':
                if self.player.has_reached_all_checkpoints():
                    self.game_over = True
                    self.winner = 'Player'
                    self.message = "Victory! You reached all checkpoints and the goal!"
                else:
                    # Player reached goal but not all checkpoints - don't win
                    missing = len(self.maze.checkpoints) - len(self.player.reached_checkpoints)
                    self.game_over = False  # Prevent win
                    # Don't show message, just prevent winning
            elif self.mode == 'AI Duel (Checkpoints)':
                # Need to check checkpoints in this mode too
                if self.player.has_reached_all_checkpoints():
                    self.game_over = True
                    self.winner = 'Player'
                    self.message = "Victory! You reached all checkpoints and the goal!"
                else:
                    # Player reached goal but not all checkpoints - don't win
                    self.game_over = False  # Prevent win
                    # Don't show message, just prevent winning
            else:
                self.game_over = True
                self.winner = 'Player'
                self.message = "Victory! You reached the goal!"
        
        # Check AI win in duel modes
        if (self.mode == 'AI Duel' or self.mode == 'AI Duel (Checkpoints)') and self.ai_agent:
            ai_pos = self.ai_agent.get_position()
            if self.mode == 'AI Duel':
                if ai_pos == self.maze.goal_pos:
                    self.game_over = True
                    self.winner = 'AI'
                    self.message = "AI won! Better luck next time!"
            elif self.mode == 'AI Duel (Checkpoints)':
                # AI needs to visit all checkpoints and reach goal
                if ai_pos == self.maze.goal_pos:
                    if len(self.ai_agent.reached_checkpoints) == len(self.maze.checkpoints):
                        self.game_over = True
                        self.winner = 'AI'
                        self.message = "AI won! Better luck next time!"
        
        # Check if player is trapped (no valid path to goal or no unvisited moves)
        if not self.game_over:
            if self.is_player_trapped():
                self.game_over = True
                self.winner = None
                self.message = "You're Trapped! No valid path remaining. Use Undo (U) or Reset (R)!"
        
        # Check if player ran out of energy
        if self.player.energy <= 0:
            self.game_over = True
            self.winner = None
            self.message = "Game Over! You ran out of energy!"
    
    def get_hint(self):
        """Get hint for player's next move"""
        if self.game_over:
            return None
        
        pathfinder = Pathfinder(self.maze, HEURISTIC_TYPE)
        current_pos = self.player.get_position()
        
        # In multi-goal/checkpoint modes, find path through all unvisited checkpoints to goal
        if (self.mode == 'Multi-Goal' or self.mode == 'AI Duel (Checkpoints)') and self.maze.checkpoints:
            unvisited = [cp for cp in self.maze.checkpoints if cp not in self.player.reached_checkpoints]
            if unvisited:
                # Try to find a path through all unvisited checkpoints to goal
                # For hint, we'll find the path to the first unvisited checkpoint
                # that's part of a valid sequence to goal
                goal = self.maze.goal_pos
                
                # Try all permutations to find a valid path sequence
                import itertools
                found_path = None
                
                for checkpoint_order in itertools.permutations(unvisited):
                    waypoints = [current_pos] + list(checkpoint_order) + [goal]
                    path_valid = True
                    
                    # Check if this order works
                    for i in range(len(waypoints) - 1):
                        result = pathfinder.a_star(waypoints[i], waypoints[i + 1])
                        if not result.path_found:
                            path_valid = False
                            break
                    
                    if path_valid:
                        # Use the first checkpoint in this valid sequence
                        found_path = pathfinder.a_star(current_pos, checkpoint_order[0])
                        if found_path.path_found and len(found_path.path) > 1:
                            return found_path.path[1]  # Next position
                        break
                
                # Fallback: just try path to first unvisited checkpoint
                if not found_path:
                    result = pathfinder.a_star(current_pos, unvisited[0])
                    if result.path_found and len(result.path) > 1:
                        return result.path[1]
            else:
                # All checkpoints reached - hint towards goal
                goal = self.maze.goal_pos
                result = pathfinder.a_star(current_pos, goal)
                if result.path_found and len(result.path) > 1:
                    return result.path[1]  # Next position after current
        else:
            # Regular mode - just path to goal
            goal = self.maze.goal_pos
            result = pathfinder.a_star(current_pos, goal)
            if result.path_found and len(result.path) > 1:
                return result.path[1]  # Next position after current
        
        return None
    
    def reset(self):
        """Reset game state"""
        mode = self.mode
        fog = self.fog_of_war
        algo = self.algorithm_comparison
        hints = self.show_hints
        self.initialize_game()
        self.mode = mode
        self.fog_of_war = fog
        self.algorithm_comparison = algo
        self.show_hints = hints
        # Reset discovered cells
        self.discovered_cells = set()
        self.ai_discovered_cells = set()
    
    def toggle_fog_of_war(self):
        """Toggle fog of war mode"""
        self.fog_of_war = not self.fog_of_war
        
        if self.fog_of_war:
            # Fog turned ON - initialize discovered cells for both player and AI
            if self.player:
                px, py = self.player.get_position()
                from config import FOG_OF_WAR_RADIUS
                player_cell_x = max(0, min(px, self.maze.width - 1))
                player_cell_y = max(0, min(py, self.maze.height - 1))
                for y in range(max(0, player_cell_y - FOG_OF_WAR_RADIUS), min(self.maze.height, player_cell_y + FOG_OF_WAR_RADIUS + 1)):
                    for x in range(max(0, player_cell_x - FOG_OF_WAR_RADIUS), min(self.maze.width, player_cell_x + FOG_OF_WAR_RADIUS + 1)):
                        distance = abs(x - px) + abs(y - py)
                        if distance <= FOG_OF_WAR_RADIUS:
                            self.discovered_cells.add((x, y))
            
            if self.ai_agent:
                ai_x, ai_y = self.ai_agent.get_position()
                from config import FOG_OF_WAR_RADIUS
                ai_cell_x = max(0, min(ai_x, self.maze.width - 1))
                ai_cell_y = max(0, min(ai_y, self.maze.height - 1))
                for y in range(max(0, ai_cell_y - FOG_OF_WAR_RADIUS), min(self.maze.height, ai_cell_y + FOG_OF_WAR_RADIUS + 1)):
                    for x in range(max(0, ai_cell_x - FOG_OF_WAR_RADIUS), min(self.maze.width, ai_cell_x + FOG_OF_WAR_RADIUS + 1)):
                        distance = abs(x - ai_x) + abs(y - ai_y)
                        if distance <= FOG_OF_WAR_RADIUS:
                            self.ai_discovered_cells.add((x, y))
                
                # Recompute AI path with fog restrictions
                if self.mode == 'AI Duel' or self.mode == 'AI Duel (Checkpoints)':
                    from config import AI_ALGORITHM
                    goal = self.maze.goal_pos
                    algorithm = AI_ALGORITHM
                    
                    if self.mode == 'AI Duel (Checkpoints)' and self.maze.checkpoints:
                        unvisited = [cp for cp in self.maze.checkpoints if cp not in self.ai_agent.reached_checkpoints]
                        if unvisited:
                            goal = unvisited + [self.maze.goal_pos]
                            algorithm = 'MULTI_OBJECTIVE'
                    
                    self.ai_agent.compute_path(goal, algorithm=algorithm, discovered_cells=self.ai_discovered_cells)
        else:
            # Fog turned OFF - clear discovered cells and recompute AI path with full visibility
            self.discovered_cells = set()
            self.ai_discovered_cells = set()
            
            # Recompute AI path with full visibility (no fog restrictions)
            if self.ai_agent and (self.mode == 'AI Duel' or self.mode == 'AI Duel (Checkpoints)'):
                from config import AI_ALGORITHM
                goal = self.maze.goal_pos
                algorithm = AI_ALGORITHM
                
                if self.mode == 'AI Duel (Checkpoints)' and self.maze.checkpoints:
                    unvisited = [cp for cp in self.maze.checkpoints if cp not in self.ai_agent.reached_checkpoints]
                    if unvisited:
                        goal = unvisited + [self.maze.goal_pos]
                        algorithm = 'MULTI_OBJECTIVE'
                
                self.ai_agent.compute_path(goal, algorithm=algorithm, discovered_cells=None)
    
    def toggle_algorithm_comparison(self):
        """Toggle algorithm comparison dashboard"""
        self.algorithm_comparison = not self.algorithm_comparison
        # Clear cache when toggling off, so it recalculates when toggled on again
        if not self.algorithm_comparison:
            self.algorithm_results_cache = None
    
    def toggle_hints(self):
        """Toggle hint system"""
        self.show_hints = not self.show_hints
    
    def undo_move(self):
        """Undo last move - affects both player and AI in competitive modes"""
        if self.game_over:
            return False
        
        # Undo player move
        player_undone = False
        if self.player:
            player_undone = self.player.undo()
        
        # In competitive modes, also undo AI move
        if (self.mode == 'AI Duel' or self.mode == 'AI Duel (Checkpoints)') and self.ai_agent:
            if player_undone:  # Only undo AI if player undo was successful
                ai_undone = self.ai_agent.undo()
                # If AI undo happened, it's still AI's turn (synchronized undo)
                # Actually, let's keep it as player's turn since player initiated undo
                # self.turn = 'player'  # Player goes again after undo
        
        return player_undone

