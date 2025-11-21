"""
Game modes manager
Handles different game modes: Explore, Dynamic, Multi-Goal, AI Duel

This file contains the GameState class which manages:
- Different game modes (Explore, Obstacle Course, Multi-Goal, AI Duel, Blind Duel)
- Game state (maze, player, AI, win/lose conditions)
- Turn-based gameplay (for AI Duel modes)
- Fog of war (for Blind Duel mode)
- Algorithm selection and comparison
- Hint system
- Win/lose condition checking
"""

import random  # For random checkpoint placement, obstacle changes
from maze import Maze  # Import maze class
from player import Player, AIAgent  # Import player and AI classes
from pathfinding import Pathfinder  # Import pathfinding algorithms
from config import *  # Import all configuration constants

class GameState:
    """
    Manages the current game state.
    
    This class is the central coordinator for a game session. It:
    - Creates and manages the maze, player, and AI
    - Handles different game modes
    - Tracks game progress (checkpoints, energy, etc.)
    - Checks win/lose conditions
    - Manages turn-based gameplay
    - Handles fog of war
    """
    
    def __init__(self, mode='Explore', selected_ai_algorithm=None):
        """
        Initialize a new game state.
        
        Args:
            mode: Game mode ('Explore', 'Obstacle Course', 'Multi-Goal', 'AI Duel', 'Blind Duel')
            selected_ai_algorithm: Optional algorithm for AI (usually auto-selected)
        """
        # ====================================================================
        # GAME MODE
        # ====================================================================
        self.mode = mode  # Current game mode
        
        # ====================================================================
        # GAME OBJECTS
        # ====================================================================
        self.maze = None        # The maze (will be created in initialize_game())
        self.player = None      # The human player (will be created in initialize_game())
        self.ai_agent = None   # The AI opponent (created for some modes)
        self.ai_pathfinder = None  # Pathfinder for AI (contains algorithms)
        
        # ====================================================================
        # GAME STATUS
        # ====================================================================
        self.game_over = False  # Whether the game has ended
        self.winner = None      # 'Player', 'AI', or None (if game not over or draw)
        self.message = ""       # Message to display when game ends
        
        # ====================================================================
        # TURN-BASED GAMEPLAY
        # ====================================================================
        self.turn = 'player'  # Whose turn it is: 'player' or 'ai'
                            # Only used in turn-based modes (AI Duel, Blind Duel)
        
        # ====================================================================
        # UI FEATURES
        # ====================================================================
        self.algorithm_comparison = False  # Whether algorithm comparison panel is visible
        self.show_hints = False           # Whether hints are shown (H key toggles)
        self.show_exploration = False     # Whether AI exploration visualization is shown (V key toggles)
        
        # ====================================================================
        # ALGORITHM SELECTION
        # ====================================================================
        self.algorithm_results_cache = None  # Cached results from algorithm comparison
                                            # Avoids recalculating every frame
        self.selected_algorithm = AI_ALGORITHM  # Currently selected algorithm (can be cycled with [ ])
        
        # ====================================================================
        # FOG OF WAR (Blind Duel Mode)
        # ====================================================================
        # Fog of war limits visibility - you can only see nearby cells
        self.fog_of_war_enabled = (mode == 'Blind Duel')  # Only enabled in Blind Duel mode
        
        # Visibility radius in cells (how far you can see)
        self.player_visibility_radius = 2  # Player sees 2 cells in each direction
        self.ai_visibility_radius = 1      # AI sees only 1 cell (harder for AI)
        
        # Track which cells have been discovered (seen before)
        self.player_discovered_cells = set()  # Cells the player has seen
        self.ai_discovered_cells = set()      # Cells the AI has seen
        
        # ====================================================================
        # ALGORITHM SELECTION FOR SPECIAL MODES
        # ====================================================================
        # For Blind Duel: always use modified A* (no selection needed)
        # Modified A* handles fog of war with memory and exploration
        if mode == 'Blind Duel':
            self.selected_algorithm = 'MODIFIED_ASTAR_FOG'
        
        # ====================================================================
        # INITIALIZE THE GAME
        # ====================================================================
        # Create maze, player, AI, checkpoints, obstacles, etc.
        self.initialize_game()
    
    def initialize_game(self):
        """
        Initialize a new game based on the current mode.
        
        This function:
        1. Creates a new maze
        2. Creates the player
        3. Sets up mode-specific features (checkpoints, obstacles, AI, etc.)
        4. Spawns obstacles and rewards
        5. Initializes fog of war (if enabled)
        6. Computes AI's initial path
        
        Called when starting a new game or resetting.
        """
        # ====================================================================
        # CLEAR PREVIOUS GAME STATE
        # ====================================================================
        # Clear victory screen cache for new game
        self.victory_screen_cache = None
        
        # ====================================================================
        # CREATE MAZE
        # ====================================================================
        # Generate a new perfect maze with specified dimensions
        self.maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
        
        # Assign basic terrain types (grass, water, mud)
        # include_obstacles=False means no obstacles yet (will be added by mode setup)
        self.maze.assign_terrain(include_obstacles=False)
        
        # ====================================================================
        # CREATE PLAYER
        # ====================================================================
        # Create the human player at the start position
        if self.maze.start_pos:
            self.player = Player(self.maze, self.maze.start_pos)
        
        # ====================================================================
        # MODE-SPECIFIC SETUP
        # ====================================================================
        # Each mode has different features:
        # - Explore: Simple static maze
        # - Obstacle Course: Obstacles with different costs
        # - Multi-Goal: Checkpoints that must be visited
        # - AI Duel: Competitive mode with AI opponent and checkpoints
        # - Blind Duel: Fog of war mode with limited visibility
        if self.mode == 'Explore':
            self.setup_explore_mode()
        elif self.mode == 'Obstacle Course':
            self.setup_obstacle_course_mode()
        elif self.mode == 'Multi-Goal':
            self.setup_multigoal_mode()
        elif self.mode == 'AI Duel':
            self.setup_ai_duel_mode()
        elif self.mode == 'Blind Duel':
            self.setup_blind_duel_mode()
        
        # ====================================================================
        # SPAWN OBSTACLES AND REWARDS
        # ====================================================================
        # Spawn initial lava obstacles in all modes
        # Lava obstacles are impassable (block paths)
        # Lower spawn rate (0.04 = 4%) to avoid blocking too many paths
        # The spawn function ensures at least one path to goal exists
        self.maze.spawn_initial_lava_obstacles(spawn_rate=0.04)
        
        # Spawn reward cells in ALL game modes
        # Rewards give temporary cost reduction bonuses
        from config import REWARD_SPAWN_RATE
        self.maze.spawn_reward_cells(spawn_rate=REWARD_SPAWN_RATE)
        
        # ====================================================================
        # INITIALIZE FOG OF WAR (Blind Duel Mode)
        # ====================================================================
        # In Blind Duel mode, visibility is limited
        # We need to mark the starting area as discovered
        if self.fog_of_war_enabled and self.player:
            # Update discovered cells based on visibility radius
            self.update_discovered_cells()
            
            # Initialize AI memory map with starting position
            # The AI remembers what it has seen
            if self.ai_agent:
                start_terrain = self.maze.terrain.get(self.maze.start_pos, 'GRASS')
                self.ai_agent.memory_map[self.maze.start_pos] = start_terrain
                self.ai_agent.recent_positions.append(self.maze.start_pos)
        
        # ====================================================================
        # COMPUTE AI'S INITIAL PATH
        # ====================================================================
        # The AI needs to calculate its path to the goal
        # Different modes use different algorithms
        if self.ai_agent:
            # For Blind Duel mode, AI can only see discovered cells
            # For other modes, use None (full visibility - AI can see everything)
            discovered_cells_for_ai = self.ai_discovered_cells if self.fog_of_war_enabled else None
            
            if self.mode == 'Multi-Goal':
                # Multi-Goal mode has checkpoints - must use MULTI_OBJECTIVE algorithm
                if self.maze.goal_pos:
                    if self.maze.checkpoints:
                        # Multiple goals: all checkpoints + final goal
                        goals = self.maze.checkpoints + [self.maze.goal_pos]
                        self.ai_agent.compute_path(goals, algorithm='MULTI_OBJECTIVE', discovered_cells=None)
                    else:
                        # No checkpoints - use regular algorithm
                        self.ai_agent.compute_path(self.maze.goal_pos, algorithm=self.selected_algorithm, discovered_cells=None)
                        
            elif self.mode == 'AI Duel':
                # AI Duel mode also has checkpoints - use MULTI_OBJECTIVE
                if self.maze.goal_pos:
                    if self.maze.checkpoints:
                        goals = self.maze.checkpoints + [self.maze.goal_pos]
                        self.ai_agent.compute_path(goals, algorithm='MULTI_OBJECTIVE', discovered_cells=None)
                    else:
                        self.ai_agent.compute_path(self.maze.goal_pos, algorithm=self.selected_algorithm, discovered_cells=None)
                        
            elif self.mode == 'Blind Duel':
                # Blind Duel: no checkpoints, but has fog of war
                # Use modified A* that handles limited visibility
                if self.maze.goal_pos:
                    self.ai_agent.compute_path(self.maze.goal_pos, algorithm='MODIFIED_ASTAR_FOG', discovered_cells=discovered_cells_for_ai)
        
        # ====================================================================
        # RESET GAME STATUS
        # ====================================================================
        self.game_over = False
        self.winner = None
        self.message = ""
    
    def setup_explore_mode(self):
        """Setup simple static maze mode"""
        # Create AI agent for visualization purposes (doesn't move, just computes path for exploration viz)
        # Determine heuristic based on AI difficulty
        from config import AI_DIFFICULTY, HEURISTIC_TYPE
        if AI_DIFFICULTY == 'HARD':
            heuristic = 'EUCLIDEAN'
        elif AI_DIFFICULTY == 'EASY':
            heuristic = 'MANHATTAN'
        else:  # MEDIUM or default
            heuristic = HEURISTIC_TYPE
        
        self.ai_pathfinder = Pathfinder(self.maze, heuristic)
        if self.maze.start_pos:
            self.ai_agent = AIAgent(self.maze, self.maze.start_pos, self.ai_pathfinder)
            # Compute path to goal for exploration visualization
            if self.maze.goal_pos:
                self.ai_agent.compute_path(self.maze.goal_pos, algorithm=self.selected_algorithm)
        else:
            self.ai_agent = None
        # Fog of war removed
    
    def setup_obstacle_course_mode(self):
        """Setup obstacle course mode with varied terrain costs"""
        # Add static obstacles to the terrain at generation time
        # These obstacles stay in place throughout the game (not dynamic)
        self.maze.assign_terrain(include_obstacles=True)
        
        # Create AI agent for visualization purposes (doesn't move, just computes path for exploration viz)
        # Determine heuristic based on AI difficulty
        from config import AI_DIFFICULTY, HEURISTIC_TYPE
        if AI_DIFFICULTY == 'HARD':
            heuristic = 'EUCLIDEAN'
        elif AI_DIFFICULTY == 'EASY':
            heuristic = 'MANHATTAN'
        else:  # MEDIUM or default
            heuristic = HEURISTIC_TYPE
        
        self.ai_pathfinder = Pathfinder(self.maze, heuristic)
        if self.maze.start_pos:
            self.ai_agent = AIAgent(self.maze, self.maze.start_pos, self.ai_pathfinder)
            # Compute path to goal for exploration visualization
            # Use selected algorithm (can be cycled with [ ])
            if self.maze.goal_pos:
                self.ai_agent.compute_path(self.maze.goal_pos, algorithm=self.selected_algorithm)
        else:
            self.ai_agent = None
    
    def setup_multigoal_mode(self):
        """Setup multi-checkpoint mode with ordered checkpoints and obstacles"""
        # Assign terrain with obstacles (spikes, thorns, quicksand, rocks)
        self.maze.assign_terrain(include_obstacles=True)
        
        # Clear any existing checkpoints
        self.maze.checkpoints = []
        
        # Add 3 checkpoints in ORDER along the path
        num_checkpoints = 3
        # Collect all path cells (ensure we have valid paths, avoid obstacles)
        path_cells = []
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.is_passable(x, y):
                    if (x, y) != self.maze.start_pos and (x, y) != self.maze.goal_pos:
                        # Make sure it's not too close to start/goal
                        start_dist = abs(x - self.maze.start_pos[0]) + abs(y - self.maze.start_pos[1])
                        goal_dist = abs(x - self.maze.goal_pos[0]) + abs(y - self.maze.goal_pos[1])
                        # Don't place checkpoints on obstacles
                        terrain = self.maze.terrain.get((x, y), 'GRASS')
                        if start_dist > 3 and goal_dist > 3 and terrain not in ['SPIKES', 'THORNS', 'QUICKSAND', 'ROCKS']:
                            path_cells.append((x, y))
        
        # Select checkpoints in ORDERED sequence (not random)
        # Sort by distance from start to create a natural path order
        if path_cells and len(path_cells) >= num_checkpoints:
            # Sort path cells by distance from start
            path_cells_sorted = sorted(path_cells, 
                                      key=lambda p: abs(p[0] - self.maze.start_pos[0]) + 
                                                   abs(p[1] - self.maze.start_pos[1]))
            # Select evenly spaced checkpoints along the sorted path
            interval = len(path_cells_sorted) // (num_checkpoints + 1)
            checkpoint_positions = []
            for i in range(1, num_checkpoints + 1):
                idx = min(i * interval, len(path_cells_sorted) - 1)
                checkpoint_positions.append(path_cells_sorted[idx])
            
            for x, y in checkpoint_positions:
                self.maze.add_checkpoint(x, y)
        elif path_cells:
            # If not enough cells, just use what we have
            for x, y in path_cells[:num_checkpoints]:
                self.maze.add_checkpoint(x, y)
        
        # Create AI agent for visualization in Multi-Goal mode
        # Determine heuristic based on AI difficulty
        from config import AI_DIFFICULTY, HEURISTIC_TYPE
        if AI_DIFFICULTY == 'HARD':
            heuristic = 'EUCLIDEAN'
        elif AI_DIFFICULTY == 'EASY':
            heuristic = 'MANHATTAN'
        else:  # MEDIUM or default
            heuristic = HEURISTIC_TYPE
        
        self.ai_pathfinder = Pathfinder(self.maze, heuristic)
        if self.maze.start_pos:
            self.ai_agent = AIAgent(self.maze, self.maze.start_pos, self.ai_pathfinder)
            # AI will compute path with checkpoints using MULTI_OBJECTIVE in initialize_game()
        else:
            self.ai_agent = None
    
    def setup_ai_duel_mode(self):
        """Setup AI vs Player race mode with ordered checkpoints and obstacles"""
        # Assign terrain with obstacles (spikes, thorns, quicksand, rocks)
        self.maze.assign_terrain(include_obstacles=True)
        
        # Add ordered checkpoints
        self.maze.checkpoints = []
        num_checkpoints = 3  # 3 checkpoints in order
        
        # Find all valid path cells
        path_cells = []
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.is_passable(x, y):
                    if (x, y) != self.maze.start_pos and (x, y) != self.maze.goal_pos:
                        start_dist = abs(x - self.maze.start_pos[0]) + abs(y - self.maze.start_pos[1])
                        goal_dist = abs(x - self.maze.goal_pos[0]) + abs(y - self.maze.goal_pos[1])
                        # Don't place checkpoints on obstacles
                        terrain = self.maze.terrain.get((x, y), 'GRASS')
                        if start_dist > 5 and goal_dist > 5 and terrain not in ['SPIKES', 'THORNS', 'QUICKSAND', 'ROCKS']:
                            path_cells.append((x, y, start_dist))
        
        # Sort by distance from start to create an ordered path
        if path_cells:
            path_cells.sort(key=lambda cell: cell[2])
            
            # Select evenly spaced checkpoints along the path
            if len(path_cells) >= num_checkpoints:
                step = len(path_cells) // (num_checkpoints + 1)
                for i in range(1, num_checkpoints + 1):
                    idx = min(i * step, len(path_cells) - 1)
                    x, y, _ = path_cells[idx]
                    self.maze.add_checkpoint(x, y)
        
        # Setup AI
        from config import AI_ALGORITHM
        # Determine heuristic based on AI difficulty
        from config import AI_DIFFICULTY, HEURISTIC_TYPE
        if AI_DIFFICULTY == 'HARD':
            heuristic = 'EUCLIDEAN'
        elif AI_DIFFICULTY == 'EASY':
            heuristic = 'MANHATTAN'
        else:  # MEDIUM or default
            heuristic = HEURISTIC_TYPE
        
        self.ai_pathfinder = Pathfinder(self.maze, heuristic)
        if self.maze.start_pos:
            self.ai_agent = AIAgent(self.maze, self.maze.start_pos, self.ai_pathfinder)
            # Initial path will be computed after discovered cells are initialized in initialize_game()
        self.turn = 'player'  # Player goes first
    
    def setup_blind_duel_mode(self):
        """Setup Blind Duel mode with fog of war - no checkpoints"""
        # No checkpoints in Blind Duel
        self.maze.checkpoints = []
        
        # Setup AI
        # Determine heuristic based on AI difficulty
        from config import AI_DIFFICULTY, HEURISTIC_TYPE
        if AI_DIFFICULTY == 'HARD':
            heuristic = 'EUCLIDEAN'
        elif AI_DIFFICULTY == 'EASY':
            heuristic = 'MANHATTAN'
        else:  # MEDIUM or default
            heuristic = HEURISTIC_TYPE
        
        self.ai_pathfinder = Pathfinder(self.maze, heuristic)
        if self.maze.start_pos:
            self.ai_agent = AIAgent(self.maze, self.maze.start_pos, self.ai_pathfinder)
        self.turn = 'player'  # Player goes first
    
    def update(self, dt, current_time):
        """Update game state"""
        if self.game_over:
            return
        
        # Fog of war removed - all cells always visible
        
        # Dynamic obstacles are now handled after player move in handle_player_input
        
        # Obstacles are now only updated on player/AI movement, not continuously
        # Check if path is blocked (for AI in duel modes)
        # NOTE: This check is redundant - pathfinding happens in make_ai_move() for turn-based
        # Keeping this for non-turn-based modes, but ensuring it respects fog of war
        if self.mode == 'AI Duel' and self.ai_agent:
            goal = self.maze.goal_pos
            if self.ai_agent.needs_replanning(goal):
                discovered_cells = None  # Fog of war removed
                self.ai_agent.compute_path(goal, algorithm=self.selected_algorithm, discovered_cells=discovered_cells)
        
        # Update AI agent in Duel modes (turn-based with adaptive pathfinding)
        if self.mode == 'AI Duel' and self.ai_agent:
            goal = self.maze.goal_pos
            # ALWAYS use MULTI_OBJECTIVE if checkpoints exist (ignore selected_algorithm)
            if self.maze.checkpoints:
                unvisited = [cp for cp in self.maze.checkpoints if cp not in self.ai_agent.reached_checkpoints]
                if unvisited:
                    goal = unvisited + [self.maze.goal_pos]
                    algorithm = 'MULTI_OBJECTIVE'
                else:
                    # All checkpoints reached, just go to goal (still use MULTI_OBJECTIVE for consistency)
                    algorithm = 'MULTI_OBJECTIVE'
            else:
                # No checkpoints - use selected algorithm
                algorithm = self.selected_algorithm
            
            # Adaptive pathfinding: recompute if environment changed
            check_goal = goal if not isinstance(goal, list) else goal[0] if goal else None
            if check_goal and self.ai_agent.needs_replanning(check_goal):
                discovered_cells = None  # Fog of war removed
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
        duel_modes = ['AI Duel', 'Blind Duel']
        if self.mode in duel_modes and self.ai_agent and self.turn == 'ai':
            # Determine goal and algorithm based on mode
            goal = self.maze.goal_pos
            # ALWAYS use MULTI_OBJECTIVE if checkpoints exist (ignore selected_algorithm)
            if self.maze.checkpoints:
                unvisited = [cp for cp in self.maze.checkpoints if cp not in self.ai_agent.reached_checkpoints]
                if unvisited:
                    # Pass all unvisited checkpoints + goal for multi-objective
                    goal = unvisited + [self.maze.goal_pos]
                    algorithm = 'MULTI_OBJECTIVE'
                elif self.maze.goal_pos:
                    # All checkpoints reached, just go to goal (still use MULTI_OBJECTIVE for consistency)
                    goal = self.maze.goal_pos
                    algorithm = 'MULTI_OBJECTIVE'
            elif self.mode == 'Blind Duel':
                # Blind Duel: use modified A* for fog of war
                algorithm = 'MODIFIED_ASTAR_FOG'
            elif self.mode == 'Dynamic':
                # Use D* for dynamic obstacles
                algorithm = 'DSTAR'
            else:
                # No checkpoints - use selected algorithm
                algorithm = self.selected_algorithm
            
            # IMPORTANT: Update AI's discovered cells BEFORE pathfinding (if fog of war enabled)
            if self.fog_of_war_enabled:
                self.update_discovered_cells()
                discovered_cells = self.ai_discovered_cells
            else:
                discovered_cells = None
            
            check_goal = goal if not isinstance(goal, list) else goal[0] if goal else None
            should_replan = False
            if check_goal:
                # Replan if needed (always replan in fog of war mode as AI discovers new cells)
                if self.fog_of_war_enabled or self.ai_agent.needs_replanning(check_goal):
                    should_replan = True
            
            if should_replan:
                self.ai_agent.compute_path(goal, algorithm=algorithm, discovered_cells=discovered_cells)
                
                # If path not found, try to explore towards goal
                if not self.ai_agent.path_result or not self.ai_agent.path_result.path_found:
                    # Find nearest accessible cell in the general direction of goal
                    ai_x, ai_y = self.ai_agent.get_position()
                    goal_x, goal_y = check_goal
                    
                    # Get all valid neighbors from current position
                    # Fog of war removed - all neighbors are accessible
                    neighbors = self.maze.get_neighbors(ai_x, ai_y, False)
                    accessible_neighbors = neighbors
                    
                    # Find best neighbor for exploration
                    best_next = None
                    # Use actual visited cells from AI's history, not just current path
                    visited_cells = self.ai_agent.visited_cells if hasattr(self.ai_agent, 'visited_cells') else set()
                    
                    if accessible_neighbors:
                        # Goal discovered - can navigate toward it
                        # Prefer unexplored cells, but penalize recently visited cells
                        ai_path = self.ai_agent.path if hasattr(self.ai_agent, 'path') else []
                        min_dist = float('inf')
                        for nx, ny in accessible_neighbors:
                            dist_to_goal = abs(nx - goal_x) + abs(ny - goal_y)
                            is_visited = (nx, ny) in visited_cells
                            is_recent_visit = (nx, ny) in ai_path[-3:] if len(ai_path) >= 3 else False
                            # Strongly prefer unexplored cells, penalize visited and recently visited
                            score = dist_to_goal + (200 if is_visited else 0) + (100 if is_recent_visit else 0)
                            if score < min_dist:
                                min_dist = score
                                best_next = (nx, ny)
                    else:
                        # Goal not discovered - explore randomly, STRONGLY prefer unexplored cells
                        unexplored = [n for n in accessible_neighbors if n not in visited_cells]
                        if unexplored:
                            # Prefer unexplored cells
                            import random
                            best_next = random.choice(unexplored)
                        elif accessible_neighbors:
                            # All neighbors explored - backtrack intelligently
                            # Avoid immediate back-and-forth by preferring positions further back in history
                            ai_move_history = self.ai_agent.move_history if hasattr(self.ai_agent, 'move_history') else []
                            current_pos = (ai_x, ai_y)
                            
                            # Get the immediate previous position (from last move)
                            previous_pos = None
                            if ai_move_history:
                                last_move = ai_move_history[-1]
                                previous_pos = last_move.get('old_pos')  # Position we came from
                            
                            # Score each neighbor: prefer positions that are further back in history
                            scored_neighbors = []
                            for nx, ny in accessible_neighbors:
                                score = 1000  # Base score
                                
                                # Strongly penalize immediate backtrack (previous position)
                                if (nx, ny) == previous_pos:
                                    score = 0  # Avoid immediate back-and-forth
                                    scored_neighbors.append((score, (nx, ny)))
                                    continue
                                
                                # Check how many moves ago this position was visited
                                found_in_history = False
                                for i, move in enumerate(reversed(ai_move_history[-15:])):  # Look at last 15 moves
                                    if move.get('old_pos') == (nx, ny) or move.get('new_pos') == (nx, ny):
                                        # Further back in history = higher score (preferred for backtracking)
                                        # Position visited 10 moves ago is better than position visited 2 moves ago
                                        score = 100 + (15 - i) * 10  # More moves ago = higher score
                                        found_in_history = True
                                        break
                                
                                # If position is not in recent history, it might be a good backtrack target
                                # but less preferred than positions we know we've been to
                                if not found_in_history:
                                    score = 50  # Lower score than known positions in history
                                
                                scored_neighbors.append((score, (nx, ny)))
                            
                            # Sort by score (highest first) and pick the best
                            scored_neighbors.sort(reverse=True, key=lambda x: x[0])
                            if scored_neighbors and scored_neighbors[0][0] > 0:
                                best_next = scored_neighbors[0][1]
                            else:
                                # All neighbors are immediate previous position - must backtrack anyway
                                # Choose the one furthest back in history
                                import random
                                best_next = random.choice(accessible_neighbors)
                    
                    # If we found a next cell, create a simple path to it
                    if best_next:
                        from pathfinding import PathfindingResult
                        result = PathfindingResult()
                        result.path_found = True
                        result.path = [(ai_x, ai_y), best_next]
                        result.cost = self.maze.get_cost(best_next[0], best_next[1])
                        result.nodes_explored = 1
                        self.ai_agent.path_result = result
                        self.ai_agent.path = [(ai_x, ai_y), best_next]
                        self.ai_agent.current_path_index = 0
            
            # AI can move if it has a valid path
            if self.ai_agent.path_result and self.ai_agent.path_result.path_found:
                # Check if AI is already at goal (reached it in previous turn)
                ai_pos = self.ai_agent.get_position()
                if ai_pos == self.maze.goal_pos:
                    # AI is at goal - check win conditions immediately
                    self.check_win_conditions()
                    # If game is over, return True to stop further processing
                    # If game is not over (shouldn't happen, but safety check), switch turn to prevent infinite loop
                    if self.game_over:
                        return True
                    else:
                        # Safety: if AI is at goal but game_over not set, force it
                        # This prevents infinite loop
                        self.game_over = True
                        self.winner = 'AI'
                        self.message = "AI won! It reached the goal first!"
                        return True
                
                if self.ai_agent.current_path_index < len(self.ai_agent.path) - 1:
                    self.ai_agent.current_path_index += 1
                    next_pos = self.ai_agent.path[self.ai_agent.current_path_index]
                    old_pos = (self.ai_agent.x, self.ai_agent.y)
                    old_cost = self.ai_agent.total_cost
                    
                    self.ai_agent.x, self.ai_agent.y = next_pos
                    
                    # Debug: Check if we just reached the goal
                    if next_pos == self.maze.goal_pos:
                        from config import DEBUG_MODE
                        if DEBUG_MODE:
                            print(f"[AI Move] AI reached goal at {next_pos}! current_path_index={self.ai_agent.current_path_index}, path_length={len(self.ai_agent.path)}")
                    # Track visited cell
                    self.ai_agent.visited_cells.add(next_pos)
                    
                    # Update memory map for fog of war (Blind Duel mode)
                    if self.fog_of_war_enabled:
                        terrain = self.maze.terrain.get((self.ai_agent.x, self.ai_agent.y), 'GRASS')
                        self.ai_agent.memory_map[(self.ai_agent.x, self.ai_agent.y)] = terrain
                        # Update recent positions for revisit penalty
                        self.ai_agent.recent_positions.append((self.ai_agent.x, self.ai_agent.y))
                        if len(self.ai_agent.recent_positions) > self.ai_agent.max_recent_positions:
                            self.ai_agent.recent_positions.pop(0)
                    
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
                    
                    # Check win conditions immediately after AI moves (to detect AI win)
                    self.check_win_conditions()
                    
                    # If AI won, don't switch turns (game is over)
                    if self.game_over:
                        return True
                    
                    # All modes are fully static - no spawning during gameplay
                    # Terrain and obstacles are set at maze generation
                    
                    # Switch back to player's turn
                    self.turn = 'player'
                    return True
                else:
                    # AI is at the end of the path (can't move further)
                    # Check if AI is at goal - if so, check win conditions
                    ai_pos = self.ai_agent.get_position()
                    path_end_pos = self.ai_agent.path[-1] if self.ai_agent.path else None
                    from config import DEBUG_MODE
                    if DEBUG_MODE:
                        print(f"[AI Move] AI at end of path. Position={ai_pos}, Goal={self.maze.goal_pos}, Path end={path_end_pos}, Path length={len(self.ai_agent.path) if self.ai_agent.path else 0}")
                    
                    if ai_pos == self.maze.goal_pos:
                        from config import DEBUG_MODE
                        if DEBUG_MODE:
                            print(f"[AI Move] AI is at goal! Checking win conditions...")
                        self.check_win_conditions()
                        if self.game_over:
                            if DEBUG_MODE:
                                print(f"[AI Move] Game over set, winner={self.winner}")
                            return True
                        else:
                            # Safety: if AI is at goal but game_over not set, force it
                            if DEBUG_MODE:
                                print(f"[AI Move] AI at goal but game_over not set! Forcing game over...")
                            self.game_over = True
                            self.winner = 'AI'
                            self.message = "AI won! It reached the goal first!"
                            return True
                    elif path_end_pos == self.maze.goal_pos and ai_pos != self.maze.goal_pos:
                        # Path ends at goal but AI position isn't there yet - force move to goal
                        from config import DEBUG_MODE
                        if DEBUG_MODE:
                            print(f"[AI Move] Path ends at goal but AI not there! Forcing move to goal...")
                        old_pos = (self.ai_agent.x, self.ai_agent.y)
                        old_cost = self.ai_agent.total_cost
                        self.ai_agent.x, self.ai_agent.y = self.maze.goal_pos
                        self.ai_agent.visited_cells.add(self.maze.goal_pos)
                        
                        # Update cost
                        move_cost = self.maze.get_cost(self.ai_agent.x, self.ai_agent.y)
                        self.ai_agent.total_cost += move_cost
                        
                        # Save move
                        self.ai_agent.move_history.append({
                            'old_pos': old_pos,
                            'new_pos': self.maze.goal_pos,
                            'cost': move_cost,
                            'total_cost_before': old_cost,
                            'checkpoint_reached': False
                        })
                        
                        # Check win conditions
                        self.check_win_conditions()
                        if self.game_over:
                            return True
                        else:
                            self.game_over = True
                            self.winner = 'AI'
                            self.message = "AI won! It reached the goal first!"
                            return True
                    else:
                        # If AI is adjacent to goal but stopped early, force it to move to goal
                        goal_x, goal_y = self.maze.goal_pos
                        ai_x, ai_y = ai_pos
                        manhattan_distance = abs(ai_x - goal_x) + abs(ai_y - goal_y)
                        
                        if manhattan_distance == 1:
                            from config import DEBUG_MODE
                            if DEBUG_MODE:
                                print(f"[AI Move] AI adjacent to goal (distance=1), forcing move to goal...")
                            old_pos = (self.ai_agent.x, self.ai_agent.y)
                            old_cost = self.ai_agent.total_cost
                            self.ai_agent.x, self.ai_agent.y = self.maze.goal_pos
                            self.ai_agent.visited_cells.add(self.maze.goal_pos)
                            
                            # Update memory map for fog of war (Blind Duel mode)
                            if self.fog_of_war_enabled:
                                terrain = self.maze.terrain.get((self.ai_agent.x, self.ai_agent.y), 'GRASS')
                                self.ai_agent.memory_map[(self.ai_agent.x, self.ai_agent.y)] = terrain
                                self.ai_agent.recent_positions.append((self.ai_agent.x, self.ai_agent.y))
                                if len(self.ai_agent.recent_positions) > self.ai_agent.max_recent_positions:
                                    self.ai_agent.recent_positions.pop(0)
                            
                            move_cost = self.maze.get_cost(goal_x, goal_y)
                            self.ai_agent.total_cost += move_cost
                            
                            self.ai_agent.move_history.append({
                                'old_pos': old_pos,
                                'new_pos': self.maze.goal_pos,
                                'cost': move_cost,
                                'total_cost_before': old_cost,
                                'checkpoint_reached': False
                            })
                            
                            self.check_win_conditions()
                            if not self.game_over:
                                self.game_over = True
                                self.winner = 'AI'
                                self.message = "AI won! It reached the goal first!"
                            return True
                        
                        # If not at goal and not adjacent, switch turn to prevent infinite loop
                        self.turn = 'player'
                        return True
        return False
    
    def can_player_afford_any_move(self):
        """Check if player has enough energy to make ANY move (even to visited cells)"""
        player_pos = self.player.get_position()
        
        # Check all four directions
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            new_x, new_y = player_pos[0] + dx, player_pos[1] + dy
            
            # Check if cell is valid and passable
            if self.maze.is_valid(new_x, new_y) and self.maze.is_passable(new_x, new_y):
                move_cost = self.maze.get_cost(new_x, new_y)
                
                # Apply reward bonus if active
                actual_cost = move_cost
                if self.player.reward_active and self.player.reward_moves_left > 0:
                    from config import REWARD_BONUS
                    actual_cost = max(0, move_cost + REWARD_BONUS)
                
                # If player can afford this move, return True
                if actual_cost != float('inf') and self.player.energy >= actual_cost:
                    return True
        
        # Can't afford any move
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
        # Determine heuristic based on AI difficulty
        from config import AI_DIFFICULTY, HEURISTIC_TYPE
        if AI_DIFFICULTY == 'HARD':
            heuristic = 'EUCLIDEAN'
        elif AI_DIFFICULTY == 'EASY':
            heuristic = 'MANHATTAN'
        else:  # MEDIUM or default
            heuristic = HEURISTIC_TYPE
        pathfinder = Pathfinder(self.maze, heuristic)
        
        # In multi-goal/checkpoint modes, check path through ALL unvisited checkpoints to goal
        if self.mode in ['Multi-Goal', 'AI Duel'] and self.maze.checkpoints:
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
        
        # In AI Duel modes, check both player and AI simultaneously to determine winner
        # (whoever reaches goal first with all checkpoints wins)
        if self.mode in ['AI Duel', 'Blind Duel']:
            player_won = False
            ai_won = False
            
            # Check if player reached goal
            if player_pos == self.maze.goal_pos:
                if self.maze.checkpoints:
                    if self.player.has_reached_all_checkpoints():
                        player_won = True
                else:
                    # No checkpoints - just reach goal
                    player_won = True
            
            # Check if AI reached goal
            if self.ai_agent:
                ai_pos = self.ai_agent.get_position()
                if ai_pos == self.maze.goal_pos:
                    if self.maze.checkpoints:
                        # Check if AI visited all checkpoints in order
                        if hasattr(self.ai_agent, 'reached_checkpoints'):
                            if len(self.ai_agent.reached_checkpoints) == len(self.maze.checkpoints):
                                # Verify order
                                ai_visited_in_order = True
                                for i, cp in enumerate(self.maze.checkpoints):
                                    if i >= len(self.ai_agent.reached_checkpoints) or self.ai_agent.reached_checkpoints[i] != cp:
                                        ai_visited_in_order = False
                                        break
                                
                                if ai_visited_in_order:
                                    ai_won = True
                    else:
                        # No checkpoints (Blind Duel mode) - just reach goal
                        ai_won = True
                        from config import DEBUG_MODE
                        if DEBUG_MODE:
                            print(f"[Win Condition] AI reached goal at {ai_pos} in {self.mode} mode!")
            
            # Determine winner (if both reach goal, player wins by default - player has priority)
            if player_won:
                self.game_over = True
                self.winner = 'Player'
                if self.maze.checkpoints:
                    self.message = "Victory! You visited all checkpoints in order and reached the goal first!"
                else:
                    self.message = "Victory! You reached the goal first!"
            elif ai_won:
                self.game_over = True
                self.winner = 'AI'
                if self.maze.checkpoints:
                    self.message = "AI won! It visited all checkpoints in order and reached the goal first!"
                else:
                    self.message = "AI won! It reached the goal first!"
                from config import DEBUG_MODE
                if DEBUG_MODE:
                    print(f"[Win Condition] AI WON! Game over set to True, winner = {self.winner}")
        
        # Check if player reached goal (for non-duel modes)
        elif player_pos == self.maze.goal_pos:
            # Modes with checkpoints require visiting all checkpoints IN ORDER
            if self.mode in ['Multi-Goal']:
                if self.maze.checkpoints and not self.player.has_reached_all_checkpoints():
                    # Player reached goal but not all checkpoints in order - don't win
                    missing = len(self.maze.checkpoints) - len(self.player.reached_checkpoints)
                    self.game_over = False  # Prevent win
                    # Show feedback about missing checkpoints
                    from config import DEBUG_MODE
                    if DEBUG_MODE:
                        if len(self.player.reached_checkpoints) < len(self.maze.checkpoints):
                            next_checkpoint_num = len(self.player.reached_checkpoints) + 1
                            print(f"[Win Condition] Must visit checkpoint {next_checkpoint_num} before goal!")
                        else:
                            print(f"[Win Condition] Checkpoints must be visited in order (1→2→3→Goal)!")
                else:
                    # Either no checkpoints or all visited in order
                    self.game_over = True
                    self.winner = 'Player'
                    if self.maze.checkpoints:
                        self.message = "Victory! You visited all checkpoints in order and reached the goal!"
                    else:
                        self.message = "Victory! You reached the goal!"
            else:
                # Other modes - just reach goal
                self.game_over = True
                self.winner = 'Player'
                self.message = "Victory! You reached the goal!"
        
        # Check if player ran out of energy or can't afford any move (PRIORITY CHECK - before trapped)
        if not self.game_over:
            if self.player.energy <= 0:
                self.game_over = True
                self.winner = None
                self.message = "Out of Energy! You ran out of fuel before reaching the goal!"
            elif not self.can_player_afford_any_move():
                # Player has energy but can't afford any available move
                self.game_over = True
                self.winner = None
                self.message = "Out of Energy! Not enough fuel for any available move!"
        
        # Check if player is trapped (no valid moves available)
        if not self.game_over:
            if self.is_player_trapped():
                self.game_over = True
                self.winner = None
                self.message = "Trapped! No valid moves remaining. All paths are blocked!"
    
    def get_hint(self):
        """Get hint for player's next move"""
        if self.game_over:
            return None
        
        # Determine heuristic based on AI difficulty
        from config import AI_DIFFICULTY, HEURISTIC_TYPE
        if AI_DIFFICULTY == 'HARD':
            heuristic = 'EUCLIDEAN'
        elif AI_DIFFICULTY == 'EASY':
            heuristic = 'MANHATTAN'
        else:  # MEDIUM or default
            heuristic = HEURISTIC_TYPE
        pathfinder = Pathfinder(self.maze, heuristic)
        current_pos = self.player.get_position()
        
        # In multi-goal/checkpoint modes, find path through all unvisited checkpoints to goal
        if self.mode in ['Multi-Goal', 'AI Duel'] and self.maze.checkpoints:
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
        algo = self.algorithm_comparison
        hints = self.show_hints
        self.initialize_game()
        self.mode = mode
        self.algorithm_comparison = algo
        self.show_hints = hints
    
    # Fog of war removed - toggle method deleted
    
    def toggle_algorithm_comparison(self):
        """Toggle algorithm comparison dashboard"""
        self.algorithm_comparison = not self.algorithm_comparison
        # Don't clear cache - keep it so times stay consistent when toggling
        # Cache will be cleared automatically when maze/obstacles change
    
    # Fog of war code removed
    
    def toggle_hints(self):
        """Toggle hint system"""
        self.show_hints = not self.show_hints
    
    def toggle_exploration_viz(self):
        """Toggle exploration visualization"""
        self.show_exploration = not self.show_exploration
    
    def cycle_algorithm(self, forward=True):
        """Cycle to next/previous available algorithm
        
        Args:
            forward: If True, cycle forward, if False cycle backward
        """
        from config import AVAILABLE_ALGORITHMS
        current_index = AVAILABLE_ALGORITHMS.index(self.selected_algorithm) if self.selected_algorithm in AVAILABLE_ALGORITHMS else 0
        if forward:
            next_index = (current_index + 1) % len(AVAILABLE_ALGORITHMS)
        else:
            next_index = (current_index - 1) % len(AVAILABLE_ALGORITHMS)
        self.selected_algorithm = AVAILABLE_ALGORITHMS[next_index]
        
        # Recompute AI path with new algorithm if AI exists
        if self.ai_agent:
            goal = self.maze.goal_pos
            # ALWAYS use MULTI_OBJECTIVE if checkpoints exist (ignore selected_algorithm for gameplay)
            if self.maze.checkpoints and self.mode in ['Multi-Goal', 'AI Duel']:
                unvisited = [cp for cp in self.maze.checkpoints 
                           if cp not in (self.ai_agent.reached_checkpoints if hasattr(self.ai_agent, 'reached_checkpoints') else [])]
                if unvisited:
                    goal = unvisited + [self.maze.goal_pos]
                    algorithm = 'MULTI_OBJECTIVE'
                else:
                    # All checkpoints reached, still use MULTI_OBJECTIVE for consistency
                    algorithm = 'MULTI_OBJECTIVE'
            else:
                # No checkpoints - use selected algorithm
                algorithm = self.selected_algorithm
            
            # Fog of war removed - always use full visibility
            self.ai_agent.compute_path(goal, algorithm=algorithm, discovered_cells=None)
    
    def undo_move(self):
        """Undo last move - affects both player and AI in competitive modes"""
        if self.game_over:
            return False
        
        # Undo player move
        player_undone = False
        if self.player:
            player_undone = self.player.undo()
        
        # In competitive modes, also undo AI move
        if self.mode == 'AI Duel' and self.ai_agent:
            if player_undone:  # Only undo AI if player undo was successful
                ai_undone = self.ai_agent.undo()
                # If AI undo happened, it's still AI's turn (synchronized undo)
                # Actually, let's keep it as player's turn since player initiated undo
                # self.turn = 'player'  # Player goes again after undo
        
        return player_undone

    # Fog of war code removed - all orphaned code deleted
    
    def toggle_algorithm_comparison(self):
        """Toggle algorithm comparison dashboard"""
        self.algorithm_comparison = not self.algorithm_comparison
        # Don't clear cache - keep it so times stay consistent when toggling
        # Cache will be cleared automatically when maze/obstacles change
    
    def toggle_hints(self):
        """Toggle hint system"""
        self.show_hints = not self.show_hints
    
    def toggle_exploration_viz(self):
        """Toggle exploration visualization"""
        self.show_exploration = not self.show_exploration
    
    def cycle_algorithm(self, forward=True):
        """Cycle to next/previous available algorithm
        
        Args:
            forward: If True, cycle forward, if False cycle backward
        """
        from config import AVAILABLE_ALGORITHMS
        current_index = AVAILABLE_ALGORITHMS.index(self.selected_algorithm) if self.selected_algorithm in AVAILABLE_ALGORITHMS else 0
        if forward:
            next_index = (current_index + 1) % len(AVAILABLE_ALGORITHMS)
        else:
            next_index = (current_index - 1) % len(AVAILABLE_ALGORITHMS)
        self.selected_algorithm = AVAILABLE_ALGORITHMS[next_index]
        
        # Recompute AI path with new algorithm if AI exists
        if self.ai_agent:
            goal = self.maze.goal_pos
            algorithm = self.selected_algorithm
            
            # Handle special modes
            if self.mode in ['Multi-Goal', 'AI Duel'] and self.maze.checkpoints:
                unvisited = [cp for cp in self.maze.checkpoints 
                           if cp not in (self.ai_agent.reached_checkpoints if hasattr(self.ai_agent, 'reached_checkpoints') else [])]
                if unvisited:
                    goal = unvisited + [self.maze.goal_pos]
                    algorithm = 'MULTI_OBJECTIVE'
            
            discovered_cells = None  # Fog of war removed
            self.ai_agent.compute_path(goal, algorithm=algorithm, discovered_cells=discovered_cells)
    
    def undo_move(self):
        """Undo last move - affects both player and AI in competitive modes"""
        if self.game_over:
            return False
        
        # Undo player move
        player_undone = False
        if self.player:
            player_undone = self.player.undo()
        
        # In competitive modes, also undo AI move
        if self.mode == 'AI Duel' and self.ai_agent:
            if player_undone:  # Only undo AI if player undo was successful
                ai_undone = self.ai_agent.undo()
                # If AI undo happened, it's still AI's turn (synchronized undo)
                # Actually, let's keep it as player's turn since player initiated undo
                # self.turn = 'player'  # Player goes again after undo
        
        return player_undone

    def update_discovered_cells(self):
        """Update discovered cells for player and AI based on visibility radius"""
        if not self.fog_of_war_enabled:
            return
        
        # Update player discovered cells
        if self.player:
            player_pos = self.player.get_position()
            for y in range(self.maze.height):
                for x in range(self.maze.width):
                    distance = abs(x - player_pos[0]) + abs(y - player_pos[1])
                    if distance <= self.player_visibility_radius:
                        self.player_discovered_cells.add((x, y))
        
        # Update AI discovered cells
        if self.ai_agent:
            ai_pos = self.ai_agent.get_position()
            for y in range(self.maze.height):
                for x in range(self.maze.width):
                    distance = abs(x - ai_pos[0]) + abs(y - ai_pos[1])
                    if distance <= self.ai_visibility_radius:
                        self.ai_discovered_cells.add((x, y))
    
    def get_player_visible_cells(self):
        """Get cells currently visible to player"""
        if not self.fog_of_war_enabled or not self.player:
            return None
        return self.player_discovered_cells
    
    def increase_player_visibility(self, amount=1):
        """Increase player visibility radius (from rewards)"""
        if self.fog_of_war_enabled:
            self.player_visibility_radius += amount
            # Re-discover cells with new radius
            self.update_discovered_cells()

