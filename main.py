"""
MazeRunner X - Main Game Loop
The Intelligent Shortest Path Challenge
"""

import pygame
import sys
from config import *
from game_modes import GameState
from ui import UI

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("MazeRunner X - The Intelligent Shortest Path Challenge")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize game state
        self.game_state = GameState(mode='Explore')
        self.ui = UI(self.screen)
        
        # Calculate maze offset to center it and account for start/goal outside maze
        # Start is at x=-1 (outside left), Goal is at x=width (outside right)
        # Calculate total width: 1 cell (start) + maze width + 1 cell (goal)
        total_maze_width = (1 + MAZE_WIDTH + 1) * CELL_SIZE  # start + maze + goal
        available_width = WINDOW_WIDTH - GRID_PADDING  # Space left of UI panel
        # Center the total maze area (including start/goal) horizontally
        self.maze_offset_x = max(20, (available_width - total_maze_width) // 2 + CELL_SIZE)
        # Small top padding for labels
        self.maze_offset_y = 30
    
    def handle_events(self):
        """Handle user input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # Game controls (checked first so they always work)
                if event.key == pygame.K_r:
                    self.game_state.reset()
                elif event.key == pygame.K_g:
                    # Generate new maze
                    mode = self.game_state.mode
                    self.game_state = GameState(mode=mode)
                elif event.key == pygame.K_h:
                    # Toggle hints
                    self.game_state.toggle_hints()
                elif event.key == pygame.K_f:
                    # Toggle fog of war
                    self.game_state.toggle_fog_of_war()
                elif event.key == pygame.K_c:
                    # Toggle algorithm comparison
                    self.game_state.toggle_algorithm_comparison()
                elif event.key == pygame.K_u:
                    # Undo last move
                    self.game_state.undo_move()
                # Mode selection
                elif event.key == pygame.K_1:
                    self.game_state = GameState(mode='Explore')
                elif event.key == pygame.K_2:
                    self.game_state = GameState(mode='Dynamic')
                elif event.key == pygame.K_3:
                    self.game_state = GameState(mode='Multi-Goal')
                elif event.key == pygame.K_4:
                    self.game_state = GameState(mode='AI Duel')
                elif event.key == pygame.K_5:
                    self.game_state = GameState(mode='AI Duel (Checkpoints)')
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                # Movement controls (only if player's turn in turn-based mode)
                duel_modes = ['AI Duel', 'AI Duel (Checkpoints)']
                is_duel_mode = self.game_state.mode in duel_modes
                if (self.game_state.turn == 'player' or not is_duel_mode):
                    player_moved = False
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        player_moved = self.game_state.player.move(0, -1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        player_moved = self.game_state.player.move(0, 1)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        player_moved = self.game_state.player.move(-1, 0)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        player_moved = self.game_state.player.move(1, 0)
                    
                    # If player moved, update obstacles (in Dynamic/Duel modes)
                    if player_moved:
                        if self.game_state.mode == 'Dynamic' or is_duel_mode:
                            # Pass player path so terrain only changes near player
                            player_path = self.game_state.player.path
                            self.game_state.maze.update_dynamic_obstacles(player_path)
                            
                            # Check if AI needs replanning after obstacle change
                            if is_duel_mode and self.game_state.ai_agent:
                                from config import AI_ALGORITHM
                                goal = self.game_state.maze.goal_pos
                                algorithm = AI_ALGORITHM
                                
                                if self.game_state.mode == 'AI Duel (Checkpoints)' and self.game_state.maze.checkpoints:
                                    unvisited = [cp for cp in self.game_state.maze.checkpoints 
                                                if cp not in self.game_state.ai_agent.reached_checkpoints]
                                    if unvisited:
                                        goal = unvisited + [self.game_state.maze.goal_pos]
                                        algorithm = 'MULTI_OBJECTIVE'
                                
                                if self.game_state.ai_agent.needs_replanning(goal if not isinstance(goal, list) else goal[0] if goal else None):
                                    # If fog of war is enabled, AI is blind - only use AI's own discovered cells
                                    discovered_cells = self.game_state.ai_discovered_cells if self.game_state.fog_of_war else None
                                    self.game_state.ai_agent.compute_path(goal, algorithm=algorithm, discovered_cells=discovered_cells)
                        
                        # Ensure path to goal exists (for Multi-Goal and checkpoint modes)
                        if self.game_state.mode in ['Multi-Goal', 'AI Duel (Checkpoints)']:
                            player_pos = self.game_state.player.get_position()
                            self.game_state.maze.ensure_path_to_goal(
                                player_pos,
                                self.game_state.maze.checkpoints,
                                self.game_state.player.reached_checkpoints
                            )
                        
                        # In turn-based duel mode, switch to AI turn after player moves
                        if is_duel_mode and TURN_BASED:
                            self.game_state.turn = 'ai'
    
    def update(self, dt, current_time):
        """Update game logic"""
        self.game_state.update(dt, current_time)
        
        # Handle AI turn in turn-based mode
        duel_modes = ['AI Duel', 'AI Duel (Checkpoints)']
        if self.game_state.mode in duel_modes and TURN_BASED:
            if self.game_state.turn == 'ai' and not self.game_state.game_over:
                self.game_state.make_ai_move()
    
    def draw(self):
        """Draw everything to screen"""
        # Clear screen
        self.screen.fill(COLORS['BACKGROUND'])
        
        # Draw maze with fog of war support
        # Fog of war is now allowed in duel modes (AI will be blind to it)
        fog_of_war = self.game_state.fog_of_war
        player_pos = self.game_state.player.get_position() if fog_of_war else None
        self.game_state.maze.draw(self.screen, self.maze_offset_x, self.maze_offset_y, 
                                   fog_of_war=fog_of_war, player_pos=player_pos)
        
        # Don't show AI exploration visualization in duel modes (player shouldn't see AI's path)
        # AI exploration is only shown in non-competitive modes for learning purposes
        
        # Draw visited cells (subtle overlay) - only for cells inside maze bounds
        visited_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for x, y in self.game_state.player.visited_cells:
            # Only draw visited overlay for cells inside the maze (not start/goal outside)
            if self.game_state.maze.is_valid(x, y) and x >= 0 and x < self.game_state.maze.width:
                if (x, y) != self.game_state.player.get_position():  # Don't overlay current position
                    cell_rect = pygame.Rect(
                        self.maze_offset_x + x * CELL_SIZE + 2,
                        self.maze_offset_y + y * CELL_SIZE + 2,
                        CELL_SIZE - 4,
                        CELL_SIZE - 4
                    )
                    # Light overlay to show visited
                    pygame.draw.rect(visited_surf, (*COLORS['EXPLORED'], 60), cell_rect)
        self.screen.blit(visited_surf, (0, 0))
        
        # Draw player path (pink)
        if len(self.game_state.player.path) > 1:
            for i in range(1, len(self.game_state.player.path)):
                x1, y1 = self.game_state.player.path[i-1]
                x2, y2 = self.game_state.player.path[i]
                start_pos = (
                    self.maze_offset_x + x1 * CELL_SIZE + CELL_SIZE // 2,
                    self.maze_offset_y + y1 * CELL_SIZE + CELL_SIZE // 2
                )
                end_pos = (
                    self.maze_offset_x + x2 * CELL_SIZE + CELL_SIZE // 2,
                    self.maze_offset_y + y2 * CELL_SIZE + CELL_SIZE // 2
                )
                pygame.draw.line(self.screen, COLORS['PLAYER'], start_pos, end_pos, 2)
        
        # Draw AI path (purple) - the path the AI has actually taken, not its exploration/frontier
        duel_modes = ['AI Duel', 'AI Duel (Checkpoints)']
        if self.game_state.mode in duel_modes and self.game_state.ai_agent:
            # Build AI's actual path taken from move history
            ai_path_positions = []
            if self.game_state.ai_agent.move_history:
                # Start with the initial position (first move's old_pos)
                ai_path_positions.append(self.game_state.ai_agent.move_history[0]['old_pos'])
                # Add all positions the AI has moved to
                for move in self.game_state.ai_agent.move_history:
                    ai_path_positions.append(move['new_pos'])
            else:
                # If no move history yet, start with current position
                ai_path_positions.append(self.game_state.ai_agent.get_position())
            
            # Draw AI path line (purple) showing where AI has been
            if len(ai_path_positions) > 1:
                for i in range(1, len(ai_path_positions)):
                    x1, y1 = ai_path_positions[i-1]
                    x2, y2 = ai_path_positions[i]
                    start_pos = (
                        self.maze_offset_x + x1 * CELL_SIZE + CELL_SIZE // 2,
                        self.maze_offset_y + y1 * CELL_SIZE + CELL_SIZE // 2
                    )
                    end_pos = (
                        self.maze_offset_x + x2 * CELL_SIZE + CELL_SIZE // 2,
                        self.maze_offset_y + y2 * CELL_SIZE + CELL_SIZE // 2
                    )
                    # Draw purple line for AI path
                    pygame.draw.line(self.screen, COLORS['AI'], start_pos, end_pos, 2)
        
        # Draw AI agent first (so player appears on top in duel modes when they're at same position)
        if self.game_state.ai_agent:
            self.game_state.ai_agent.draw(self.screen, self.maze_offset_x, self.maze_offset_y)
        
        # Draw player on top (pink) - this is what the player controls
        self.game_state.player.draw(self.screen, self.maze_offset_x, self.maze_offset_y)
        
        # Draw hint if enabled
        if self.game_state.show_hints:
            hint = self.game_state.get_hint()
            if hint:
                self.ui.draw_hint(hint, self.maze_offset_x, self.maze_offset_y)
        
        # Draw UI panel
        self.ui.draw_ui_panel(self.game_state)
        
        # Draw algorithm comparison if enabled
        if self.game_state.algorithm_comparison:
            # Run algorithm comparison (with caching)
            if self.game_state.algorithm_results_cache is None:
                import time
                from pathfinding import Pathfinder
                
                if self.game_state.maze.start_pos and self.game_state.maze.goal_pos:
                    start = self.game_state.maze.start_pos
                    goal = self.game_state.maze.goal_pos
                    pf = Pathfinder(self.game_state.maze, 'MANHATTAN')
                    
                    algorithms_results = {}
                    
                    # Dijkstra
                    t0 = time.time()
                    dijkstra_result = pf.dijkstra(start, goal)
                    dijkstra_time = (time.time() - t0) * 1000
                    algorithms_results['Dijkstra'] = {
                        'nodes': dijkstra_result.nodes_explored,
                        'cost': dijkstra_result.cost if dijkstra_result.path_found else float('inf'),
                        'time': dijkstra_time
                    }
                    
                    # A* Manhattan
                    t0 = time.time()
                    astar_man = pf.a_star(start, goal)
                    astar_time = (time.time() - t0) * 1000
                    algorithms_results['A* (Manhattan)'] = {
                        'nodes': astar_man.nodes_explored,
                        'cost': astar_man.cost if astar_man.path_found else float('inf'),
                        'time': astar_time
                    }
                    
                    self.game_state.algorithm_results_cache = algorithms_results
            
            if self.game_state.algorithm_results_cache:
                self.ui.draw_algorithm_comparison(self.game_state, self.game_state.algorithm_results_cache)
        
        # Draw game over message
        if self.game_state.game_over:
            self.ui.draw_game_over_message(self.game_state.message, self.game_state.winner)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            current_time = pygame.time.get_ticks() / 1000.0
            
            self.handle_events()
            self.update(dt, current_time)
            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()

