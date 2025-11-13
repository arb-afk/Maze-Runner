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
        
        # Game states
        self.in_menu = True  # Start in main menu
        self.game_state = None
        self.ui = UI(self.screen)
        
        # Calculate maze offset to center it and account for start/goal outside maze
        # Start is at x=-1 (outside left), Goal is at x=width (outside right)
        # Calculate total width: 1 cell (start) + maze width + 1 cell (goal)
        total_maze_width = (1 + MAZE_WIDTH + 1) * CELL_SIZE  # start + maze + goal
        available_width = WINDOW_WIDTH - GRID_PADDING  # Space left of UI panel
        # Center the total maze area (including start/goal) horizontally
        self.maze_offset_x = max(20, (available_width - total_maze_width) // 2)
        # Small top padding for labels
        self.maze_offset_y = 80
        
        # Split-screen offsets for AI Duel modes
        self.calculate_split_screen_offsets()
    
    def handle_events(self):
        """Handle user input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEWHEEL:
                # Mouse wheel scrolling for split-screen view
                duel_modes = ['AI Duel', 'Blind Duel']
                if not self.in_menu and self.game_state and self.game_state.mode in duel_modes:
                    # event.y is positive when scrolling up, negative when scrolling down
                    scroll_amount = event.y * 30
                    self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - scroll_amount))
                    self.calculate_split_screen_offsets()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Mouse wheel button scrolling (fallback for older pygame versions)
                duel_modes = ['AI Duel', 'Blind Duel']
                if not self.in_menu and self.game_state and self.game_state.mode in duel_modes:
                    if event.button == 4:  # Scroll up
                        self.scroll_offset = max(0, self.scroll_offset - 30)
                        self.calculate_split_screen_offsets()
                    elif event.button == 5:  # Scroll down
                        self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
                        self.calculate_split_screen_offsets()
                
                # Mouse click handling
                elif event.button == 1:  # Left click
                    if self.in_menu:
                        clicked_mode = self.ui.get_clicked_mode(event.pos)
                        if clicked_mode:
                            # Map key to mode name
                            mode_map = {
                                '1': 'Explore',
                                '2': 'Obstacle Course',
                                '3': 'Multi-Goal',
                                '4': 'AI Duel',
                                '5': 'Blind Duel'
                            }
                            if clicked_mode in mode_map:
                                # Blind Duel mode now uses modified A* directly (no selection needed)
                                self.start_game(mode_map[clicked_mode])
            
            elif event.type == pygame.KEYDOWN:
                # Menu handling (keep keyboard support)
                if self.in_menu:
                    if event.key == pygame.K_1:
                        self.start_game('Explore')
                    elif event.key == pygame.K_2:
                        self.start_game('Obstacle Course')
                    elif event.key == pygame.K_3:
                        self.start_game('Multi-Goal')
                    elif event.key == pygame.K_4:
                        self.start_game('AI Duel')
                    elif event.key == pygame.K_5:
                        # Blind Duel mode - start directly (uses modified A*)
                        self.start_game('Blind Duel')
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                    continue
                
                # Game controls (only when in game)
                if self.game_state is None:
                    continue
                    
                if event.key == pygame.K_r:
                    self.game_state.reset()
                elif event.key == pygame.K_g:
                    # Generate new maze
                    mode = self.game_state.mode
                    self.game_state = GameState(mode=mode)
                elif event.key == pygame.K_h:
                    # Toggle hints
                    self.game_state.toggle_hints()
                elif event.key == pygame.K_c:
                    # Toggle algorithm comparison
                    self.game_state.toggle_algorithm_comparison()
                elif event.key == pygame.K_u:
                    # Undo last move
                    self.game_state.undo_move()
                elif event.key == pygame.K_LEFTBRACKET:
                    # Cycle through algorithms backward
                    self.game_state.cycle_algorithm(forward=False)
                elif event.key == pygame.K_RIGHTBRACKET:
                    # Cycle through algorithms forward
                    self.game_state.cycle_algorithm(forward=True)
                elif event.key == pygame.K_v:
                    # Toggle exploration visualization
                    self.game_state.toggle_exploration_viz()
                elif event.key == pygame.K_m:
                    # Return to menu
                    self.in_menu = True
                    self.game_state = None
                # Mode selection (in-game quick switch)
                elif event.key == pygame.K_1:
                    self.game_state = GameState(mode='Explore')
                elif event.key == pygame.K_2:
                    self.game_state = GameState(mode='Obstacle Course')
                elif event.key == pygame.K_3:
                    self.game_state = GameState(mode='Multi-Goal')
                elif event.key == pygame.K_4:
                    self.game_state = GameState(mode='AI Duel')
                elif event.key == pygame.K_5:
                    # Blind Duel mode - start directly (uses modified A*)
                    self.start_game('Blind Duel')
                elif event.key == pygame.K_ESCAPE:
                    self.in_menu = True
                    self.game_state = None
                # Movement controls (only if player's turn in turn-based mode and not in menu)
                if not self.in_menu and self.game_state:
                    duel_modes = ['AI Duel', 'Blind Duel']
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
                        
                        # If player moved, handle post-move actions
                        if player_moved:
                            # Update fog of war discovered cells (for Blind Duel mode)
                            if self.game_state.fog_of_war_enabled:
                                self.game_state.update_discovered_cells()
                                # Check if player collected a reward - increase visibility
                                player_pos = self.game_state.player.get_position()
                                terrain = self.game_state.maze.terrain.get(player_pos, 'GRASS')
                                if terrain == 'REWARD' and player_pos in self.game_state.player.collected_rewards:
                                    # Check if this is a newly collected reward (not already processed)
                                    if not hasattr(self.game_state.player, '_visibility_bonus_applied'):
                                        self.game_state.player._visibility_bonus_applied = set()
                                    if player_pos not in self.game_state.player._visibility_bonus_applied:
                                        self.game_state.increase_player_visibility(amount=1)
                                        self.game_state.player._visibility_bonus_applied.add(player_pos)
                            
                            # Update dynamic obstacles for Obstacle Course mode
                            if self.game_state.mode == 'Obstacle Course':
                                self.game_state.maze.update_dynamic_obstacles(
                                    player_path=self.game_state.player.path,
                                    checkpoints=self.game_state.maze.checkpoints,
                                    reached_checkpoints=self.game_state.player.reached_checkpoints
                                )
                                # Clear algorithm comparison cache since graph changed
                                self.game_state.algorithm_results_cache = None
                                
                                # Recompute AI path after obstacles change
                                if self.game_state.ai_agent and self.game_state.maze.goal_pos:
                                    self.game_state.ai_agent.compute_path(
                                        self.game_state.maze.goal_pos, 
                                        algorithm=self.game_state.selected_algorithm
                                    )
                            
                            # If player moved in turn-based duel mode, switch to AI turn
                            if is_duel_mode and TURN_BASED:
                                self.game_state.turn = 'ai'
    
    def calculate_split_screen_offsets(self):
        """Calculate offsets for split-screen view in AI Duel modes (vertical split with scrolling)"""
        # For split screen, we need to fit two mazes top and bottom
        # Each maze includes: 1 cell (start) + MAZE_WIDTH + 1 cell (goal)
        total_cells_width = (1 + MAZE_WIDTH + 1)  # 33 cells wide
        
        # Use full cell size - we'll scroll instead of shrinking
        self.split_cell_size = CELL_SIZE  # Full 30 pixels
        
        # Calculate actual maze dimensions
        actual_maze_width = total_cells_width * self.split_cell_size
        actual_maze_height = MAZE_HEIGHT * self.split_cell_size
        
        # Center horizontally
        self.maze_x = (WINDOW_WIDTH - actual_maze_width) // 2
        
        # Position vertically with spacing
        header_space = 80  # Space for "AI DUEL" title
        label_space = 50   # Space for AI/PLAYER labels
        spacing = 30       # Space between mazes
        
        # Scrolling offset (starts at 0)
        if not hasattr(self, 'scroll_offset'):
            self.scroll_offset = 0
        
        # Total content height (both mazes + spacing)
        self.total_content_height = header_space + actual_maze_height + spacing + actual_maze_height + 50
        
        # Maximum scroll (content height - window height)
        self.max_scroll = max(0, self.total_content_height - WINDOW_HEIGHT)
        
        # Top maze (AI) - affected by scroll
        self.top_maze_y = header_space - self.scroll_offset
        
        # Bottom maze (Player) - affected by scroll
        self.bottom_maze_y = header_space + actual_maze_height + spacing - self.scroll_offset
        
        # Debug output
        from config import DEBUG_MODE
        if DEBUG_MODE:
            print(f"Split-screen debug (vertical with scroll):")
            print(f"  Cell size: {self.split_cell_size}")
            print(f"  Maze dimensions: {actual_maze_width} × {actual_maze_height}")
            print(f"  Total content height: {self.total_content_height}")
            print(f"  Max scroll: {self.max_scroll}")
            print(f"  Current scroll offset: {self.scroll_offset}")
    
    def start_game(self, mode, ai_algorithm=None):
        """Start a new game with the selected mode"""
        self.in_menu = False
        self.game_state = GameState(mode=mode, selected_ai_algorithm=ai_algorithm)
        # Reset cursor to normal arrow
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        # Reset scroll offset for split-screen modes
        self.scroll_offset = 0
        if mode in ['AI Duel', 'Blind Duel']:
            self.calculate_split_screen_offsets()
    
    def update(self, dt, current_time):
        """Update game logic"""
        if self.in_menu or self.game_state is None:
            return
        
        self.game_state.update(dt, current_time)
        
        # Handle AI turn in turn-based mode
        duel_modes = ['AI Duel', 'Blind Duel']
        if self.game_state.mode in duel_modes and TURN_BASED:
            if self.game_state.turn == 'ai' and not self.game_state.game_over:
                self.game_state.make_ai_move()
    
    def draw(self):
        """Draw everything to screen"""
        # Clear screen
        self.screen.fill(COLORS['BACKGROUND'])
        
        # Draw main menu if in menu mode
        if self.in_menu:
            self.ui.draw_main_menu()
            
            # Change cursor to hand when hovering over buttons
            mouse_pos = pygame.mouse.get_pos()
            hovering = False
            for button in self.ui.menu_buttons:
                if button['rect'].collidepoint(mouse_pos):
                    hovering = True
                    break
            
            if hovering:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
            pygame.display.flip()
            return
        
        # Check if we're in AI Duel mode for split-screen view
        is_duel_mode = self.game_state.mode in ['AI Duel', 'Blind Duel']
        
        if is_duel_mode:
            # Draw split-screen view
            self.draw_split_screen_view()
        else:
            # Draw single maze view
            # Fog of war for Blind Duel mode
            fog_of_war = self.game_state.fog_of_war_enabled if self.game_state else False
            player_pos = self.game_state.player.get_position() if (self.game_state and self.game_state.player) else None
            visibility_radius = self.game_state.player_visibility_radius if (self.game_state and self.game_state.fog_of_war_enabled) else None
            self.game_state.maze.draw(self.screen, self.maze_offset_x, self.maze_offset_y, 
                                       fog_of_war=fog_of_war, player_pos=player_pos, visibility_radius=visibility_radius)
            
            # Draw single player view elements
            self.draw_single_player_view()
        
        # Draw common UI elements (for both modes)
        self.draw_common_ui()
    
    def draw_split_screen_view(self):
        """Draw split-screen view for AI Duel modes (vertical layout)"""
        # Draw title/header
        font_title = pygame.font.Font(None, 48)
        title = font_title.render("AI DUEL", True, COLORS['TEXT'])
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title, title_rect)
        
        # Draw labels for each view
        font_label = pygame.font.Font(None, 32)
        
        # Calculate the actual width each maze occupies
        total_cells_width = (1 + MAZE_WIDTH + 1)
        actual_maze_width = total_cells_width * self.split_cell_size
        
        # AI View label (top) - positioned above the maze
        ai_label = font_label.render("AI", True, COLORS['AI'])
        ai_label_y = self.top_maze_y - 10
        
        # Only draw if within visible area
        if 0 < ai_label_y < WINDOW_HEIGHT:
            ai_label_rect = ai_label.get_rect(midleft=(20, ai_label_y))
            
            # Draw background for label
            label_bg = pygame.Rect(ai_label_rect.x - 10, ai_label_rect.y - 5, 
                                   ai_label_rect.width + 20, ai_label_rect.height + 10)
            pygame.draw.rect(self.screen, (255, 255, 255), label_bg, border_radius=5)
            pygame.draw.rect(self.screen, COLORS['AI'], label_bg, 3, border_radius=5)
            self.screen.blit(ai_label, ai_label_rect)
        
        # Player View label (bottom) - positioned above the maze
        player_label = font_label.render("PLAYER", True, COLORS['PLAYER'])
        player_label_y = self.bottom_maze_y - 10
        
        # Only draw if within visible area
        if 0 < player_label_y < WINDOW_HEIGHT:
            player_label_rect = player_label.get_rect(midleft=(20, player_label_y))
            
            # Draw background for label
            label_bg = pygame.Rect(player_label_rect.x - 10, player_label_rect.y - 5,
                                   player_label_rect.width + 20, player_label_rect.height + 10)
            pygame.draw.rect(self.screen, (255, 255, 255), label_bg, border_radius=5)
            pygame.draw.rect(self.screen, COLORS['PLAYER'], label_bg, 3, border_radius=5)
            self.screen.blit(player_label, player_label_rect)
        
        # Draw both mazes with scaled cell size
        # Fog of war removed - always use full visibility
        
        # Top maze (AI view) - with fog of war if enabled
        ai_fog = self.game_state.fog_of_war_enabled if self.game_state else False
        ai_pos = self.game_state.ai_agent.get_position() if self.game_state.ai_agent else None
        ai_visibility_radius = self.game_state.ai_visibility_radius if (self.game_state and self.game_state.fog_of_war_enabled) else None
        self.game_state.maze.draw(self.screen, self.maze_x, self.top_maze_y,
                                   fog_of_war=ai_fog, player_pos=ai_pos, 
                                   cell_size=self.split_cell_size, visibility_radius=ai_visibility_radius)
        
        # Bottom maze (Player view) - with fog of war if enabled
        player_fog = self.game_state.fog_of_war_enabled if self.game_state else False
        player_pos = self.game_state.player.get_position() if self.game_state.player else None
        player_visibility_radius = self.game_state.player_visibility_radius if (self.game_state and self.game_state.fog_of_war_enabled) else None
        self.game_state.maze.draw(self.screen, self.maze_x, self.bottom_maze_y,
                                   fog_of_war=player_fog, player_pos=player_pos,
                                   cell_size=self.split_cell_size, visibility_radius=player_visibility_radius)
        
        # Draw AI path and position on TOP maze
        if self.game_state.ai_agent:
            # Build AI's actual path taken from move history
            ai_path_positions = []
            if self.game_state.ai_agent.move_history:
                ai_path_positions.append(self.game_state.ai_agent.move_history[0]['old_pos'])
                for move in self.game_state.ai_agent.move_history:
                    ai_path_positions.append(move['new_pos'])
            else:
                ai_path_positions.append(self.game_state.ai_agent.get_position())
            
            # Draw AI path line (purple) on TOP maze with glow effect
            if len(ai_path_positions) > 1:
                for i in range(1, len(ai_path_positions)):
                    x1, y1 = ai_path_positions[i-1]
                    x2, y2 = ai_path_positions[i]
                    start_pos = (
                        self.maze_x + x1 * self.split_cell_size + self.split_cell_size // 2,
                        self.top_maze_y + y1 * self.split_cell_size + self.split_cell_size // 2
                    )
                    end_pos = (
                        self.maze_x + x2 * self.split_cell_size + self.split_cell_size // 2,
                        self.top_maze_y + y2 * self.split_cell_size + self.split_cell_size // 2
                    )
                    # Draw thick line for AI path (bright purple)
                    pygame.draw.line(self.screen, COLORS['AI'], start_pos, end_pos, 5)
                    # Add bright accent on top
                    pygame.draw.line(self.screen, (255, 200, 255), start_pos, end_pos, 2)
            
            # Draw AI agent on TOP maze
            self.game_state.ai_agent.draw(self.screen, self.maze_x, self.top_maze_y, 
                                          cell_size=self.split_cell_size)
        
        # Draw player path and position on BOTTOM maze with glow
        if len(self.game_state.player.path) > 1:
            for i in range(1, len(self.game_state.player.path)):
                x1, y1 = self.game_state.player.path[i-1]
                x2, y2 = self.game_state.player.path[i]
                start_pos = (
                    self.maze_x + x1 * self.split_cell_size + self.split_cell_size // 2,
                    self.bottom_maze_y + y1 * self.split_cell_size + self.split_cell_size // 2
                )
                end_pos = (
                    self.maze_x + x2 * self.split_cell_size + self.split_cell_size // 2,
                    self.bottom_maze_y + y2 * self.split_cell_size + self.split_cell_size // 2
                )
                # Draw thick line for player path (bright pink)
                pygame.draw.line(self.screen, COLORS['PLAYER'], start_pos, end_pos, 5)
                # Add bright accent on top
                pygame.draw.line(self.screen, (255, 200, 220), start_pos, end_pos, 2)
        
        # Draw player on BOTTOM maze
        self.game_state.player.draw(self.screen, self.maze_x, self.bottom_maze_y,
                                     cell_size=self.split_cell_size)
        
        # Draw AI exploration visualization if enabled (only on AI's maze - top)
        if self.game_state.show_exploration and self.game_state.ai_agent and self.game_state.ai_agent.path_result:
            self.ui.draw_exploration_visualization(
                self.game_state.maze,
                self.game_state.ai_agent.path_result,
                self.maze_x,
                self.top_maze_y,
                show_heuristics=False
            )
        
        # Draw visited cells overlay for both views
        self.draw_split_visited_cells()
        
        # Draw scrollbar
        self.draw_scrollbar()
        
        # Continue with rest of drawing (UI panel, hints, etc.)
        
    def draw_scrollbar(self):
        """Draw a scrollbar on the right side of the screen"""
        if not hasattr(self, 'max_scroll') or self.max_scroll <= 0:
            return  # No scrolling needed
        
        # Scrollbar dimensions
        scrollbar_width = 20
        scrollbar_x = WINDOW_WIDTH - scrollbar_width - 5
        scrollbar_y = 5
        scrollbar_height = WINDOW_HEIGHT - 10
        
        # Draw scrollbar background (track)
        track_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(self.screen, (200, 200, 200), track_rect, border_radius=10)
        
        # Calculate thumb size and position
        # Thumb size represents visible portion
        thumb_ratio = WINDOW_HEIGHT / self.total_content_height
        thumb_height = max(30, int(scrollbar_height * thumb_ratio))
        
        # Thumb position based on scroll offset
        scroll_ratio = self.scroll_offset / self.max_scroll if self.max_scroll > 0 else 0
        thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * scroll_ratio)
        
        # Draw scrollbar thumb
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
        pygame.draw.rect(self.screen, (100, 100, 100), thumb_rect, border_radius=10)
        
        # Draw scroll hint text
        font = pygame.font.Font(None, 18)
        hint_text = font.render("Scroll", True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(scrollbar_x + scrollbar_width // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(hint_text, hint_rect)
    
    def draw_split_visited_cells(self):
        """Draw visited cells overlay for split-screen view (vertical layout)"""
        visited_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        # Draw AI visited cells on TOP maze
        if self.game_state.ai_agent:
            for x, y in self.game_state.ai_agent.visited_cells:
                if self.game_state.maze.is_valid(x, y) and x >= 0 and x < self.game_state.maze.width:
                    if (x, y) != self.game_state.ai_agent.get_position():
                        cell_rect = pygame.Rect(
                            self.maze_x + x * self.split_cell_size + 2,
                            self.top_maze_y + y * self.split_cell_size + 2,
                            self.split_cell_size - 4,
                            self.split_cell_size - 4
                        )
                        pygame.draw.rect(visited_surf, (*COLORS['AI'], 40), cell_rect)
        
        # Draw player visited cells on BOTTOM maze
        for x, y in self.game_state.player.visited_cells:
            if self.game_state.maze.is_valid(x, y) and x >= 0 and x < self.game_state.maze.width:
                if (x, y) != self.game_state.player.get_position():
                    cell_rect = pygame.Rect(
                        self.maze_x + x * self.split_cell_size + 2,
                        self.bottom_maze_y + y * self.split_cell_size + 2,
                        self.split_cell_size - 4,
                        self.split_cell_size - 4
                    )
                    pygame.draw.rect(visited_surf, (*COLORS['PLAYER'], 40), cell_rect)
        
        self.screen.blit(visited_surf, (0, 0))
    
    def draw_single_player_view(self):
        """Draw single player view elements (for non-duel modes)"""
        # Draw AI exploration visualization if enabled and AI exists
        if self.game_state.show_exploration and self.game_state.ai_agent and self.game_state.ai_agent.path_result:
            self.ui.draw_exploration_visualization(
                self.game_state.maze,
                self.game_state.ai_agent.path_result,
                self.maze_offset_x,
                self.maze_offset_y,
                show_heuristics=False  # Don't show values, just colors
            )
        
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
        
        # Draw player path with glow effect (pink)
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
                # Draw thick line for player path (bright pink)
                pygame.draw.line(self.screen, COLORS['PLAYER'], start_pos, end_pos, 4)
                # Add bright accent on top
                pygame.draw.line(self.screen, (255, 200, 220), start_pos, end_pos, 2)
        
        # Draw player on top (pink) - this is what the player controls
        self.game_state.player.draw(self.screen, self.maze_offset_x, self.maze_offset_y)
        
        # Draw hint if enabled
    def draw_common_ui(self):
        """Draw UI elements common to all modes"""
        if self.game_state.show_hints:
            hint = self.game_state.get_hint()
            if hint:
                self.ui.draw_hint(hint, self.maze_offset_x, self.maze_offset_y)
        
        # Draw UI panel
        self.ui.draw_ui_panel(self.game_state)
        
        # Always calculate algorithm comparison (needed for victory screen even if panel not visible)
        # For Obstacle Course mode, don't cache since obstacles change every turn
        should_cache = self.game_state.mode != 'Obstacle Course'
        
        # For Obstacle Course mode, clear cache at start of each frame to force recalculation
        if not should_cache:
            self.game_state.algorithm_results_cache = None
        
        # Run algorithm comparison (with caching for static modes)
        # Calculate if cache is empty, or if in Obstacle Course mode (recalculate every frame)
        if self.game_state.algorithm_results_cache is None:
            try:
                import time
                from pathfinding import Pathfinder
                
                if self.game_state.maze.start_pos and self.game_state.maze.goal_pos:
                    # Use player's current position instead of start for dynamic comparison
                    if self.game_state.mode == 'Obstacle Course':
                        start = self.game_state.player.get_position()
                    else:
                        start = self.game_state.maze.start_pos
                    goal = self.game_state.maze.goal_pos
                    pf = Pathfinder(self.game_state.maze, 'MANHATTAN')
                    
                    # Always use full visibility (fog of war removed)
                    discovered_cells_for_comparison = None
                    
                    # When checkpoints exist, all algorithms should try to solve the same problem
                    # (visiting all checkpoints before goal). For algorithms that can't handle multiple goals,
                    # they'll find a direct path to goal (which is incorrect but shows why Multi-Objective is needed)
                    use_checkpoints = self.game_state.maze.checkpoints is not None and len(self.game_state.maze.checkpoints) > 0
                    
                    algorithms_results = {}
                    
                    # Helper function to simulate reward collection along path
                    def simulate_path_with_rewards(path):
                        """Simulate collecting rewards along a path to get true cost"""
                        from config import REWARD_BONUS, REWARD_DURATION
                        
                        # Get reward positions
                        reward_positions = set()
                        for y in range(self.game_state.maze.height):
                            for x in range(self.game_state.maze.width):
                                terrain = self.game_state.maze.terrain.get((x, y), 'GRASS')
                                if terrain == 'REWARD':
                                    reward_positions.add((x, y))
                        reward_positions.update(self.game_state.player.collected_rewards)
                        
                        total_cost = 0
                        reward_active = False
                        reward_moves_left = 0
                        collected_rewards = set()
                        
                        # Skip first cell (start) - pathfinding algorithms don't count start cell cost
                        # Path is [start, cell1, cell2, ..., goal] but cost is only cell1 + cell2 + ... + goal
                        for i, pos in enumerate(path):
                            # Skip start cell (index 0) - player/AI don't pay for starting position
                            if i == 0:
                                # Still check for reward at start (bonus applies to next moves)
                                if pos in reward_positions and pos not in collected_rewards:
                                    collected_rewards.add(pos)
                                    reward_active = True
                                    reward_moves_left = REWARD_DURATION
                                continue
                            
                            # Calculate cost with reward bonus (if active from previous move)
                            base_cost = self.game_state.maze.get_cost(*pos)
                            if reward_active and reward_moves_left > 0:
                                actual_cost = max(0, base_cost + REWARD_BONUS)
                            else:
                                actual_cost = base_cost
                            
                            total_cost += actual_cost
                            
                            # Decrease reward duration
                            if reward_active and reward_moves_left > 0:
                                reward_moves_left -= 1
                                if reward_moves_left == 0:
                                    reward_active = False
                            
                            # Check if cell has reward (applies to NEXT moves)
                            if pos in reward_positions and pos not in collected_rewards:
                                collected_rewards.add(pos)
                                reward_active = True
                                reward_moves_left = REWARD_DURATION
                        
                        return total_cost
                    
                    # Helper to round time with appropriate precision
                    def round_time(t):
                        if t < 0.1:
                            return round(t, 2)  # 2 decimal places for sub-millisecond
                        else:
                            return round(t, 1)  # 1 decimal place for normal times
                    
                    # For Blind Duel mode, only calculate modified A* for fog of war
                    # For other modes, calculate all algorithms for comparison
                    if self.game_state.mode == 'Blind Duel':
                        # Only calculate modified A* for fog of war
                        # Use AI's memory map and recent positions for accurate comparison
                        ai_agent = self.game_state.ai_agent
                        memory_map = ai_agent.memory_map if (ai_agent and hasattr(ai_agent, 'memory_map') and ai_agent.memory_map) else {}
                        visited_positions = set(ai_agent.recent_positions) if (ai_agent and hasattr(ai_agent, 'recent_positions') and ai_agent.recent_positions) else set()
                        
                        t0 = time.time()
                        result = pf.modified_a_star_fog_of_war(
                            start, goal,
                            discovered_cells=discovered_cells_for_comparison,
                            memory_map=memory_map,
                            visited_positions=visited_positions,
                            revisit_penalty=5.0
                        )
                        
                        algo_time = round_time((time.time() - t0) * 1000)
                        algo_cost = simulate_path_with_rewards(result.path) if result.path_found else float('inf')
                        algorithms_results['Modified A* (Fog)'] = {
                            'nodes': result.nodes_explored,
                            'cost': algo_cost,
                            'time': algo_time,
                            'steps': len(result.path) if result.path_found and result.path else 0
                        }
                    else:
                        # Calculate all algorithms for other modes
                        # Note: When checkpoints exist, BFS/Dijkstra/A*/Bidir A* can only find path to goal
                        # (they ignore checkpoints). Multi-Objective is needed to visit all checkpoints.
                        # For fair comparison, we still compute them, but they're solving a different (easier) problem.
                        
                        # BFS
                        t0 = time.time()
                        bfs_result = pf.bfs(start, goal, discovered_cells=discovered_cells_for_comparison)
                        bfs_time = round_time((time.time() - t0) * 1000)
                        # If checkpoints exist, BFS path doesn't visit them - mark cost as invalid
                        if use_checkpoints and bfs_result.path_found:
                            # Check if path visits all checkpoints
                            path_set = set(bfs_result.path) if bfs_result.path else set()
                            missing_checkpoints = [cp for cp in self.game_state.maze.checkpoints if cp not in path_set]
                            if missing_checkpoints:
                                # Path doesn't visit all checkpoints - invalid solution
                                bfs_cost = float('inf')
                            else:
                                bfs_cost = simulate_path_with_rewards(bfs_result.path)
                        else:
                            bfs_cost = simulate_path_with_rewards(bfs_result.path) if bfs_result.path_found else float('inf')
                        algorithms_results['BFS'] = {
                            'nodes': bfs_result.nodes_explored,
                            'cost': bfs_cost,
                            'time': bfs_time,
                            'steps': len(bfs_result.path) if bfs_result.path_found and bfs_result.path else 0
                        }
                    
                        # Dijkstra
                        t0 = time.time()
                        dijkstra_result = pf.dijkstra(start, goal, discovered_cells=discovered_cells_for_comparison)
                        dijkstra_time = round_time((time.time() - t0) * 1000)
                        if use_checkpoints and dijkstra_result.path_found:
                            path_set = set(dijkstra_result.path) if dijkstra_result.path else set()
                            missing_checkpoints = [cp for cp in self.game_state.maze.checkpoints if cp not in path_set]
                            if missing_checkpoints:
                                dijkstra_cost = float('inf')
                            else:
                                dijkstra_cost = simulate_path_with_rewards(dijkstra_result.path)
                        else:
                            dijkstra_cost = simulate_path_with_rewards(dijkstra_result.path) if dijkstra_result.path_found else float('inf')
                        algorithms_results['Dijkstra'] = {
                            'nodes': dijkstra_result.nodes_explored,
                            'cost': dijkstra_cost,
                            'time': dijkstra_time,
                            'steps': len(dijkstra_result.path) if dijkstra_result.path_found and dijkstra_result.path else 0
                        }
                    
                        # A* Manhattan
                        t0 = time.time()
                        astar_man = pf.a_star(start, goal, discovered_cells=discovered_cells_for_comparison)
                        astar_time = round_time((time.time() - t0) * 1000)
                        if use_checkpoints and astar_man.path_found:
                            path_set = set(astar_man.path) if astar_man.path else set()
                            missing_checkpoints = [cp for cp in self.game_state.maze.checkpoints if cp not in path_set]
                            if missing_checkpoints:
                                astar_cost = float('inf')
                            else:
                                astar_cost = simulate_path_with_rewards(astar_man.path)
                        else:
                            astar_cost = simulate_path_with_rewards(astar_man.path) if astar_man.path_found else float('inf')
                        algorithms_results['A*'] = {
                            'nodes': astar_man.nodes_explored,
                            'cost': astar_cost,
                            'time': astar_time,
                            'steps': len(astar_man.path) if astar_man.path_found and astar_man.path else 0
                        }
                        
                        # Bidirectional A*
                        t0 = time.time()
                        bidir_result = pf.bidirectional_a_star(start, goal, discovered_cells=discovered_cells_for_comparison)
                        bidir_time = round_time((time.time() - t0) * 1000)
                        if use_checkpoints and bidir_result.path_found:
                            path_set = set(bidir_result.path) if bidir_result.path else set()
                            missing_checkpoints = [cp for cp in self.game_state.maze.checkpoints if cp not in path_set]
                            if missing_checkpoints:
                                bidir_cost = float('inf')
                            else:
                                bidir_cost = simulate_path_with_rewards(bidir_result.path)
                        else:
                            bidir_cost = simulate_path_with_rewards(bidir_result.path) if bidir_result.path_found else float('inf')
                        algorithms_results['Bidirectional A*'] = {
                            'nodes': bidir_result.nodes_explored,
                            'cost': bidir_cost,
                            'time': bidir_time,
                            'steps': len(bidir_result.path) if bidir_result.path_found and bidir_result.path else 0
                        }
                    
                    # Multi-Objective (only if checkpoints exist)
                    if self.game_state.maze.checkpoints:
                        try:
                            t0 = time.time()
                            # Multi-Objective needs all checkpoints + goal as a list
                            multi_goals = list(self.game_state.maze.checkpoints) + [goal]
                            multi_result = pf.multi_objective_search(start, multi_goals, discovered_cells=discovered_cells_for_comparison)
                            multi_time = round_time((time.time() - t0) * 1000)
                            multi_cost = simulate_path_with_rewards(multi_result.path) if multi_result.path_found else float('inf')
                            algorithms_results['Multi-Objective'] = {
                                'nodes': multi_result.nodes_explored,
                                'cost': multi_cost,
                                'time': multi_time,
                                'steps': len(multi_result.path) if multi_result.path_found and multi_result.path else 0
                            }
                        except Exception as e:
                            print(f"[Algorithm Comparison] Error computing Multi-Objective: {e}")
                    
                    # Always store results for current frame display
                    # For static modes, this caches and won't recalculate
                    # For Obstacle Course mode, this is temporary (cache will be None next frame)
                    self.game_state.algorithm_results_cache = algorithms_results
            except Exception as e:
                print(f"[Algorithm Comparison] Error: {e}")
                # Draw error message
                font = pygame.font.Font(None, 24)
                error_text = font.render("Algorithm comparison error - see console", True, (255, 0, 0))
                self.screen.blit(error_text, (WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2))
        
        # Draw algorithm comparison panel if enabled
        if self.game_state.algorithm_comparison and self.game_state.algorithm_results_cache:
                self.ui.draw_algorithm_comparison(self.game_state, self.game_state.algorithm_results_cache)
        
        # Draw game over message with stats comparison
        if self.game_state.game_over:
            self.ui.draw_game_over_message(self.game_state.message, self.game_state.winner, self.game_state)
        
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

