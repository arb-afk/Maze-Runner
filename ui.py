"""
UI and visualization components
Handles rendering of stats, exploration visualization, and game interface

This file contains the UI class which is responsible for:
- Drawing the main menu
- Rendering the game UI panel (stats, energy, controls)
- Visualizing algorithm exploration (explored nodes, frontier, path)
- Showing hints and algorithm comparison
- Rendering victory/defeat screens
- Displaying split-screen for AI Duel modes

All visual elements are drawn using pygame drawing functions.
"""

import pygame  # For drawing graphics, text, and UI elements
from config import *  # Import all configuration constants (colors, sizes, etc.)

class UI:
    """
    User Interface renderer.
    
    This class handles all visual elements that appear on screen:
    - Menus, buttons, text
    - Game statistics and information
    - Algorithm visualizations
    - Victory/defeat screens
    """
    
    def __init__(self, screen):
        """
        Initialize the UI renderer.
        
        Args:
            screen: The pygame Surface to draw on (the game window)
        """
        self.screen = screen  # Reference to the game window (where we draw everything)
        
        # ====================================================================
        # UI PANEL POSITIONING
        # ====================================================================
        # The UI panel is on the right side of the screen
        # It shows stats, energy, controls, etc.
        
        # X position of the UI panel (starts at this x coordinate)
        self.ui_panel_x = WINDOW_WIDTH - GRID_PADDING
        
        # Width of the UI panel (same as GRID_PADDING from config)
        self.ui_panel_width = GRID_PADDING
        
        # Height of the UI panel (full window height)
        self.ui_panel_height = WINDOW_HEIGHT
        
        # ====================================================================
        # MENU BUTTON TRACKING
        # ====================================================================
        # Store button rectangles for click detection
        # Each button has: {'rect': pygame.Rect, 'mode': mode_name, 'mode_key': key}
        # Updated each frame when drawing the menu
        self.menu_buttons = []
    
    def draw_main_menu(self):
        """
        Draw the main menu screen with game mode selection buttons.
        
        The main menu displays:
        - Game title and subtitle
        - Five mode selection buttons (Explore, Obstacle Course, Multi-Goal, AI Duel, Blind Duel)
        - Each button shows mode name, description, and number key
        - Hover effects when mouse is over buttons
        - Gradient background for visual appeal
        """
        # ====================================================================
        # INITIALIZATION
        # ====================================================================
        # Clear button list for this frame (will be repopulated)
        self.menu_buttons = []
        
        # Get current mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # ====================================================================
        # BACKGROUND GRADIENT
        # ====================================================================
        # Create a gradient background effect (darker at top, lighter at bottom)
        # Draw horizontal lines with gradually changing colors
        for y in range(0, WINDOW_HEIGHT, 4):
            progress = y / WINDOW_HEIGHT  # Progress from 0 (top) to 1 (bottom)
            color_value = int(240 - progress * 40)  # Darker at top, lighter at bottom
            # Draw a horizontal line with the calculated color
            pygame.draw.line(self.screen, (color_value, color_value, color_value + 10), 
                           (0, y), (WINDOW_WIDTH, y), 4)
        
        # Title section
        font_title = pygame.font.Font(None, 80)
        font_subtitle = pygame.font.Font(None, 32)
        font_mode = pygame.font.Font(None, 36)
        font_description = pygame.font.Font(None, 22)
        font_footer = pygame.font.Font(None, 20)
        
        # Main title with shadow
        title_text = "MazeRunner X"
        title_shadow = font_title.render(title_text, True, (100, 100, 100))
        title = font_title.render(title_text, True, (33, 33, 33))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 120))
        self.screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = font_subtitle.render("The Intelligent Shortest Path Challenge", True, (100, 100, 100))
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 180))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Mode selection title
        select_text = font_subtitle.render("Select Your Game Mode", True, (50, 50, 50))
        select_rect = select_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
        self.screen.blit(select_text, select_rect)
        
        # Game modes with colored boxes
        modes = [
            {
                'name': 'Explore Mode',
                'key': '1',
                'color': (76, 175, 80),
                'description': 'Navigate through a static maze and find the optimal path'
            },
            {
                'name': 'Obstacle Course',
                'key': '2',
                'color': (255, 152, 0),
                'description': 'Navigate through varied obstacles with different movement costs'
            },
            {
                'name': 'Multi-Goal Mode',
                'key': '3',
                'color': (156, 39, 176),
                'description': 'Visit all checkpoints before reaching the goal'
            },
            {
                'name': 'AI Duel',
                'key': '4',
                'color': (244, 67, 54),
                'description': 'Race against AI with checkpoints and obstacles!'
            },
            {
                'name': 'Blind Duel',
                'key': '5',
                'color': (33, 150, 243),
                'description': 'Fog of War: Limited visibility! Choose your AI opponent'
            }
        ]
        
        start_y = 320
        box_width = 800
        box_height = 90
        spacing = 20
        
        for i, mode in enumerate(modes):
            y = start_y + i * (box_height + spacing)
            x = (WINDOW_WIDTH - box_width) // 2
            
            box_rect = pygame.Rect(x, y, box_width, box_height)
            
            # Check if mouse is hovering over this button
            is_hovered = box_rect.collidepoint(mouse_pos)
            
            # Store button info for click detection
            self.menu_buttons.append({
                'rect': box_rect,
                'mode': mode['name'],
                'mode_key': mode['key']
            })
            
            # Draw mode box with shadow
            shadow_offset = 2 if is_hovered else 3
            shadow_rect = pygame.Rect(x + shadow_offset, y + shadow_offset, box_width, box_height)
            pygame.draw.rect(self.screen, (180, 180, 180), shadow_rect, border_radius=12)
            
            # Change background color on hover
            bg_color = (245, 245, 245) if is_hovered else (255, 255, 255)
            pygame.draw.rect(self.screen, bg_color, box_rect, border_radius=12)
            
            # Thicker border on hover
            border_width = 5 if is_hovered else 4
            pygame.draw.rect(self.screen, mode['color'], box_rect, border_width, border_radius=12)
            
            # Key indicator circle
            key_circle_x = x + 40
            key_circle_y = y + box_height // 2
            pygame.draw.circle(self.screen, mode['color'], (key_circle_x, key_circle_y), 25)
            key_text = font_mode.render(mode['key'], True, (255, 255, 255))
            key_rect = key_text.get_rect(center=(key_circle_x, key_circle_y))
            self.screen.blit(key_text, key_rect)
            
            # Mode name
            name_text = font_mode.render(mode['name'], True, (33, 33, 33))
            self.screen.blit(name_text, (x + 80, y + 15))
            
            # Description
            desc_text = font_description.render(mode['description'], True, (100, 100, 100))
            self.screen.blit(desc_text, (x + 80, y + 50))
        
        # Footer instructions
        footer_y = WINDOW_HEIGHT - 60
        footer_text = "Click on a mode to start  |  Press 1-4 or ESC to quit"
        footer = font_footer.render(footer_text, True, (120, 120, 120))
        footer_rect = footer.get_rect(center=(WINDOW_WIDTH // 2, footer_y))
        self.screen.blit(footer, footer_rect)
    
    def get_clicked_mode(self, mouse_pos):
        """Check if a menu button was clicked and return the mode"""
        for button in self.menu_buttons:
            if button['rect'].collidepoint(mouse_pos):
                return button['mode_key']
        return None
    
    def draw_ui_panel(self, game_state):
        """Draw the right-side UI panel with modern styling"""
        # Draw subtle gradient for panel
        panel_rect = pygame.Rect(self.ui_panel_x, 0, self.ui_panel_width, self.ui_panel_height)
        
        # Create subtle vertical gradient
        for i in range(self.ui_panel_height):
            progress = i / self.ui_panel_height
            # Interpolate between white and very light gray
            color_value = int(255 - progress * 5)
            line_rect = pygame.Rect(self.ui_panel_x, i, self.ui_panel_width, 1)
            pygame.draw.rect(self.screen, (color_value, color_value, color_value), line_rect)
        
        # Draw left border with shadow effect
        pygame.draw.line(self.screen, (200, 200, 200), 
                        (self.ui_panel_x - 1, 0), 
                        (self.ui_panel_x - 1, self.ui_panel_height), 3)
        pygame.draw.line(self.screen, COLORS['UI_BORDER'], 
                        (self.ui_panel_x, 0), 
                        (self.ui_panel_x, self.ui_panel_height), 2)
        
        y_offset = 20
        font_title = pygame.font.Font(None, FONT_SIZE_LARGE + 8)
        font_normal = pygame.font.Font(None, FONT_SIZE_MEDIUM + 2)
        font_small = pygame.font.Font(None, FONT_SIZE_SMALL + 2)
        font_bold = pygame.font.Font(None, FONT_SIZE_MEDIUM + 4)
        
        # Title with gradient effect
        title = font_title.render("MazeRunner X", True, COLORS['TEXT'])
        self.screen.blit(title, (self.ui_panel_x + 15, y_offset))
        y_offset += 45
        
        # Game Mode with colored badge and shadow
        mode_colors = {
            'Explore': (102, 187, 106),
            'Obstacle Course': (255, 167, 38),
            'Multi-Goal': (171, 71, 188),
            'AI Duel': (239, 83, 80)
        }
        mode_color = mode_colors.get(game_state.mode, COLORS['TEXT'])
        
        # Draw shadow
        shadow_rect = pygame.Rect(self.ui_panel_x + 12, y_offset + 2, 180, 32)
        pygame.draw.rect(self.screen, (200, 200, 200), shadow_rect, border_radius=6)
        
        # Draw badge
        mode_rect = pygame.Rect(self.ui_panel_x + 10, y_offset, 180, 32)
        pygame.draw.rect(self.screen, mode_color, mode_rect, border_radius=6)
        mode_text = font_bold.render(f"{game_state.mode}", True, (255, 255, 255))
        text_rect = mode_text.get_rect(center=mode_rect.center)
        self.screen.blit(mode_text, text_rect)
        y_offset += 45
        
        # Turn indicator (for AI Duel modes)
        duel_modes = ['AI Duel', 'Blind Duel']
        if game_state.mode in duel_modes and TURN_BASED:
            turn_text = "Your Turn" if game_state.turn == 'player' else "AI's Turn"
            turn_color = COLORS['PLAYER'] if game_state.turn == 'player' else COLORS['AI']
            turn_surf = font_normal.render(turn_text, True, turn_color)
            self.screen.blit(turn_surf, (self.ui_panel_x + 15, y_offset))
            y_offset += 30
        
        # Player Stats
        y_offset = self.draw_player_stats(game_state, y_offset, font_normal, font_small)
        
        # AI Stats (if in duel modes)
        duel_modes = ['AI Duel', 'Blind Duel']
        if game_state.mode in duel_modes:
            y_offset = self.draw_ai_stats(game_state, y_offset, font_normal, font_small)
        
        # Energy Bar
        y_offset += 10
        y_offset = self.draw_energy_bar(game_state, y_offset, font_small)
        
        # Controls
        y_offset += 20
        y_offset = self.draw_controls(y_offset, font_small)
        
        # Algorithm info
        if game_state.ai_agent and game_state.ai_agent.path_result:
            y_offset += 20
            y_offset = self.draw_algorithm_info(game_state, y_offset, font_small)
        
        # Extensions toggle (skip in AI Duel mode)
        if game_state.mode != 'AI Duel':
            y_offset += 20
            y_offset = self.draw_extensions_toggles(game_state, y_offset, font_small)
    
    def draw_energy_bar(self, game_state, y_offset, font_small):
        """Draw energy bar with visual feedback and smooth gradient"""
        title = font_small.render("Energy:", True, COLORS['TEXT'])
        self.screen.blit(title, (self.ui_panel_x + 15, y_offset))
        y_offset += 22
        
        bar_width = 170
        bar_height = 24
        
        # Background with shadow
        shadow_rect = pygame.Rect(self.ui_panel_x + 16, y_offset + 1, bar_width, bar_height)
        pygame.draw.rect(self.screen, (210, 210, 210), shadow_rect, border_radius=4)
        
        bar_rect = pygame.Rect(self.ui_panel_x + 15, y_offset, bar_width, bar_height)
        pygame.draw.rect(self.screen, (230, 230, 230), bar_rect, border_radius=4)
        
        # Calculate energy percentage
        energy_pct = max(0, min(1, game_state.player.energy / INITIAL_ENERGY))
        fill_width = int(bar_width * energy_pct)
        
        if fill_width > 0:
            fill_rect = pygame.Rect(self.ui_panel_x + 15, y_offset, fill_width, bar_height)
            bar_color = COLORS['ENERGY_BAR'] if energy_pct > 0.3 else COLORS['ENERGY_BAR_LOW']
            pygame.draw.rect(self.screen, bar_color, fill_rect, border_radius=4)
            
            # Add highlight for 3D effect
            highlight_rect = pygame.Rect(self.ui_panel_x + 15, y_offset, fill_width, bar_height // 3)
            highlight_color = tuple(min(255, c + 20) for c in bar_color)
            pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=4)
        
        # Border
        pygame.draw.rect(self.screen, COLORS['UI_BORDER'], bar_rect, 2, border_radius=4)
        
        # Energy text with shadow
        energy_text = font_small.render(f"{game_state.player.energy:.0f}/{INITIAL_ENERGY}", True, COLORS['TEXT'])
        text_rect = energy_text.get_rect(center=bar_rect.center)
        shadow_text = font_small.render(f"{game_state.player.energy:.0f}/{INITIAL_ENERGY}", True, (255, 255, 255))
        self.screen.blit(shadow_text, (text_rect.x + 1, text_rect.y + 1))
        self.screen.blit(energy_text, text_rect)
        
        return y_offset + 38
    
    def draw_player_stats(self, game_state, y_offset, font_normal, font_small):
        """Draw player statistics with modern styling"""
        # Section header with shadow
        shadow_rect = pygame.Rect(self.ui_panel_x + 11, y_offset + 1, 180, 26)
        pygame.draw.rect(self.screen, (200, 200, 200), shadow_rect, border_radius=4)
        
        header_rect = pygame.Rect(self.ui_panel_x + 10, y_offset, 180, 26)
        pygame.draw.rect(self.screen, COLORS['PLAYER'], header_rect, border_radius=4)
        title = font_normal.render("Player", True, (255, 255, 255))
        self.screen.blit(title, (self.ui_panel_x + 15, y_offset + 4))
        y_offset += 36
        
        stats = [
            f"Position: ({game_state.player.x}, {game_state.player.y})",
            f"Path Cost: {game_state.player.total_cost:.1f}",
            f"Steps: {len(game_state.player.path)}",
        ]
        
        if game_state.maze.checkpoints:
            checkpoints_text = f"Checkpoints: {len(game_state.player.reached_checkpoints)}/{len(game_state.maze.checkpoints)}"
            stats.append(checkpoints_text)
        
        # Show reward status if active
        if game_state.player.reward_active:
            stats.append(f"Reward Active: {game_state.player.reward_moves_left} moves")
        
        for stat in stats:
            # Highlight reward status in gold
            if "Reward Active" in stat:
                text = font_small.render(stat, True, COLORS['REWARD'])
            else:
                text = font_small.render(stat, True, COLORS['TEXT'])
            self.screen.blit(text, (self.ui_panel_x + 20, y_offset))
            y_offset += 22
        
        return y_offset
    
    def draw_ai_stats(self, game_state, y_offset, font_normal, font_small):
        """Draw AI statistics with modern styling"""
        # Section header with shadow
        shadow_rect = pygame.Rect(self.ui_panel_x + 11, y_offset + 1, 180, 26)
        pygame.draw.rect(self.screen, (200, 200, 200), shadow_rect, border_radius=4)
        
        header_rect = pygame.Rect(self.ui_panel_x + 10, y_offset, 180, 26)
        pygame.draw.rect(self.screen, COLORS['AI'], header_rect, border_radius=4)
        title = font_normal.render("AI", True, (255, 255, 255))
        self.screen.blit(title, (self.ui_panel_x + 15, y_offset + 4))
        y_offset += 36
        
        if game_state.ai_agent:
            # Calculate steps from path or move history
            ai_steps = len(game_state.ai_agent.path) if game_state.ai_agent.path else 0
            if hasattr(game_state.ai_agent, 'move_history') and game_state.ai_agent.move_history:
                ai_steps = len(game_state.ai_agent.move_history)
            
            stats = [
                f"Position: ({game_state.ai_agent.x}, {game_state.ai_agent.y})",
                f"Path Cost: {game_state.ai_agent.total_cost:.1f}",
                f"Steps: {ai_steps}",
                f"Nodes: {game_state.ai_agent.path_result.nodes_explored if game_state.ai_agent.path_result else 0}",
            ]
            
            # Add checkpoint progress for checkpoint mode
            if game_state.mode == 'AI Duel' and game_state.maze.checkpoints:
                checkpoint_text = f"Checkpoints: {len(game_state.ai_agent.reached_checkpoints)}/{len(game_state.maze.checkpoints)}"
                stats.append(checkpoint_text)
            
            for stat in stats:
                text = font_small.render(stat, True, COLORS['TEXT'])
                self.screen.blit(text, (self.ui_panel_x + 20, y_offset))
                y_offset += 22
        
        return y_offset
    
    def draw_controls(self, y_offset, font_small):
        """Draw control instructions with better formatting"""
        header = font_small.render("Controls:", True, COLORS['TEXT'])
        self.screen.blit(header, (self.ui_panel_x + 15, y_offset))
        y_offset += 25
        
        controls = [
            "Arrow Keys: Move",
            "WASD: Move",
            "R: Reset",
            "U: Undo (costs 2)",
            "H: Toggle Hints",
            "[ ]: Cycle Algorithm",
            "V: Toggle Visualization",
            "G: New Maze",
            "1-5: Change Mode",
            "C: Algorithm Compare",
            "M: Main Menu",
            "ESC: Menu"
        ]
        
        for control in controls:
            text = font_small.render(control, True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(text, (self.ui_panel_x + 20, y_offset))
            y_offset += 18
        
        return y_offset
    
    def draw_algorithm_info(self, game_state, y_offset, font_small):
        """Draw algorithm exploration information"""
        header = font_small.render("AI Algorithm:", True, COLORS['TEXT'])
        self.screen.blit(header, (self.ui_panel_x + 15, y_offset))
        y_offset += 25
        
        # Show currently selected algorithm
        selected_algo = game_state.selected_algorithm
        
        # Determine which algorithm is actually being used (may override selection in special modes)
        active_algo = selected_algo
        if game_state.mode in ['Multi-Goal', 'AI Duel']:
            if game_state.maze.checkpoints:
                active_algo = 'MULTI_OBJECTIVE'
        # Note: Obstacle Course mode respects selected algorithm (no override)
        
        # Format algorithm name nicely
        algo_display = {
            'BFS': 'BFS',
            'DIJKSTRA': 'Dijkstra',
            'ASTAR': 'A*',
            'BIDIRECTIONAL_ASTAR': 'Bidirectional A*',
            'DSTAR': 'D* (Dynamic A*)',
            'MULTI_OBJECTIVE': 'Multi-Objective'
        }.get(active_algo, active_algo)
        
        # Show selected vs active if different
        if active_algo != selected_algo:
            selected_display = {
                'DIJKSTRA': 'Dijkstra',
                'ASTAR': 'A*',
                'BIDIRECTIONAL_ASTAR': 'Bidirectional A*'
            }.get(selected_algo, selected_algo)
            
            info = [
                f"Selected: {selected_display}",
                f"Active: {algo_display}",
                f"(Mode overrides selection)"
            ]
        else:
            info = [f"Active: {algo_display}"]
        
        if game_state.ai_agent and game_state.ai_agent.path_result:
            result = game_state.ai_agent.path_result
            
            # When checkpoints exist, use Multi-Objective result from algorithm comparison for consistency
            # This ensures side panel matches algorithm comparison panel
            if game_state.maze.checkpoints and game_state.algorithm_results_cache and 'Multi-Objective' in game_state.algorithm_results_cache:
                # Use Multi-Objective nodes from comparison (but keep AI agent's path_result for other info)
                multi_obj_result = game_state.algorithm_results_cache['Multi-Objective']
                # Create a temporary result object with Multi-Objective nodes for display
                class TempResult:
                    def __init__(self, original_result, nodes_explored):
                        self.path_found = original_result.path_found
                        self.path = original_result.path
                        self.cost = original_result.cost
                        self.nodes_explored = nodes_explored
                result = TempResult(result, multi_obj_result['nodes'])
            
            # In Explore mode, AI doesn't move, so show algorithm's calculated cost
            # In other modes, show actual AI gameplay cost (includes rewards)
            if game_state.mode == 'Explore' or game_state.ai_agent.total_cost == 0:
                # AI hasn't moved yet - show pathfinding algorithm's cost
                # Need to simulate rewards to match actual gameplay
                if result.path_found and result.path:
                    from config import REWARD_BONUS, REWARD_DURATION
                    simulated_cost = 0
                    reward_active = False
                    reward_moves_left = 0
                    collected_rewards = set()
                    
                    # Get reward positions
                    reward_positions = set()
                    for y in range(game_state.maze.height):
                        for x in range(game_state.maze.width):
                            terrain = game_state.maze.terrain.get((x, y), 'GRASS')
                            if terrain == 'REWARD':
                                reward_positions.add((x, y))
                    
                    # Skip first cell (start) - pathfinding algorithms don't count start cell cost
                    # Path is [start, cell1, cell2, ..., goal] but cost is only cell1 + cell2 + ... + goal
                    for i, pos in enumerate(result.path):
                        # Skip start cell (index 0) - player/AI don't pay for starting position
                        if i == 0:
                            # Still check for reward at start (bonus applies to next moves)
                            if pos in reward_positions and pos not in collected_rewards:
                                collected_rewards.add(pos)
                                reward_active = True
                                reward_moves_left = REWARD_DURATION
                            continue
                        
                        # Calculate cost with reward bonus (if active from previous move)
                        base_cost = game_state.maze.get_cost(*pos)
                        if reward_active and reward_moves_left > 0:
                            actual_cost = max(0, base_cost + REWARD_BONUS)
                        else:
                            actual_cost = base_cost
                        
                        simulated_cost += actual_cost
                        
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
                    
                    ai_cost_display = simulated_cost
                else:
                    ai_cost_display = result.cost if result.path_found else 0.0
            else:
                # AI has moved - show actual gameplay cost
                ai_cost_display = game_state.ai_agent.total_cost
            
            info.extend([
                f"Heuristic: {game_state.ai_pathfinder.heuristic_type if game_state.ai_pathfinder else 'N/A'}",
                f"Path Found: {'Yes' if result.path_found else 'No'}",
                f"AI Path Cost: {ai_cost_display:.1f}",
                f"Nodes Explored: {result.nodes_explored}"
            ])
        
        for item in info:
            text = font_small.render(item, True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(text, (self.ui_panel_x + 20, y_offset))
            y_offset += 18
        
        return y_offset
    
    def draw_extensions_toggles(self, game_state, y_offset, font_small):
        """Draw extension toggles"""
        header = font_small.render("Extensions:", True, COLORS['TEXT'])
        self.screen.blit(header, (self.ui_panel_x + 15, y_offset))
        y_offset += 25
        
        # Current Algorithm Display (clickable indicator)
        algo_display = {
            'BFS': 'BFS',
            'DIJKSTRA': 'Dijkstra',
            'ASTAR': 'A*',
            'BIDIRECTIONAL_ASTAR': 'Bidir A*'
        }.get(game_state.selected_algorithm, game_state.selected_algorithm)
        
        algo_text = font_small.render(f"Algorithm: {algo_display}", True, COLORS['TEXT'])
        self.screen.blit(algo_text, (self.ui_panel_x + 20, y_offset))
        y_offset += 18
        
        # Exploration visualization toggle
        viz_status = "ON" if game_state.show_exploration else "OFF"
        viz_color = (76, 175, 80) if game_state.show_exploration else COLORS['TEXT_SECONDARY']
        viz_text = font_small.render(f"Visualization: {viz_status}", True, viz_color)
        self.screen.blit(viz_text, (self.ui_panel_x + 20, y_offset))
        y_offset += 18
        
        # Show visualization legend when enabled
        if game_state.show_exploration:
            legend_font = pygame.font.Font(None, 14)
            legend_y = y_offset
            
            # Orange circles = Explored
            pygame.draw.circle(self.screen, (255, 200, 50), (self.ui_panel_x + 25, legend_y + 5), 4)
            legend_text = legend_font.render("= Explored", True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(legend_text, (self.ui_panel_x + 35, legend_y))
            legend_y += 15
            
            # Yellow squares = Frontier
            square_rect = pygame.Rect(self.ui_panel_x + 22, legend_y + 2, 6, 6)
            pygame.draw.rect(self.screen, (255, 255, 0), square_rect)
            legend_text = legend_font.render("= Frontier", True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(legend_text, (self.ui_panel_x + 35, legend_y))
            legend_y += 15
            
            # White/cyan line = Optimal path
            pygame.draw.line(self.screen, (255, 255, 255), (self.ui_panel_x + 22, legend_y + 5), (self.ui_panel_x + 30, legend_y + 5), 3)
            pygame.draw.line(self.screen, (0, 255, 255), (self.ui_panel_x + 22, legend_y + 5), (self.ui_panel_x + 30, legend_y + 5), 1)
            legend_text = legend_font.render("= AI Path", True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(legend_text, (self.ui_panel_x + 35, legend_y))
            y_offset = legend_y + 18
        else:
            y_offset += 2
        
        # Hints toggle
        hints_status = "ON" if game_state.show_hints else "OFF"
        hints_color = (76, 175, 80) if game_state.show_hints else COLORS['TEXT_SECONDARY']
        hints_text = font_small.render(f"Hints: {hints_status}", True, hints_color)
        self.screen.blit(hints_text, (self.ui_panel_x + 20, y_offset))
        y_offset += 18
        
        # Algorithm Comparison toggle
        algo_status = "ON" if game_state.algorithm_comparison else "OFF"
        algo_color = (76, 175, 80) if game_state.algorithm_comparison else COLORS['TEXT_SECONDARY']
        algo_text = font_small.render(f"Algorithm Compare: {algo_status}", True, algo_color)
        self.screen.blit(algo_text, (self.ui_panel_x + 20, y_offset))
        y_offset += 18
        
        return y_offset
    
    def draw_exploration_visualization(self, maze, pathfinder_result, offset_x=0, offset_y=0, show_heuristics=True):
        """Draw AI exploration visualization (explored nodes, frontier, heuristics)"""
        if not pathfinder_result:
            return
        
        # Draw explored nodes - SEMI-TRANSPARENT ORANGE DOTS (so you can see terrain underneath)
        explored_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for x, y in pathfinder_result.explored_nodes:
            if (x, y) != maze.start_pos and (x, y) != maze.goal_pos:
                center_x = offset_x + x * CELL_SIZE + CELL_SIZE // 2
                center_y = offset_y + y * CELL_SIZE + CELL_SIZE // 2
                
                # Draw as SMALL ORANGE CIRCLES (dots) - very distinct from terrain
                pygame.draw.circle(explored_surf, (255, 150, 0, 150), (center_x, center_y), 6)  # Orange glow
                pygame.draw.circle(explored_surf, (255, 200, 50, 200), (center_x, center_y), 4)  # Bright orange
        self.screen.blit(explored_surf, (0, 0))
        
        # Draw frontier nodes - BRIGHT YELLOW SQUARES (very visible, different shape)
        frontier_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for x, y in pathfinder_result.frontier_nodes:
            if (x, y) not in pathfinder_result.explored_nodes:
                center_x = offset_x + x * CELL_SIZE + CELL_SIZE // 2
                center_y = offset_y + y * CELL_SIZE + CELL_SIZE // 2
                
                # Draw as BRIGHT YELLOW ROTATING SQUARES - very distinct
                square_size = 8
                square_rect = pygame.Rect(
                    center_x - square_size // 2,
                    center_y - square_size // 2,
                    square_size,
                    square_size
                )
                # Bright yellow with thick border
                pygame.draw.rect(frontier_surf, (255, 255, 0, 230), square_rect)  # Bright yellow fill
                pygame.draw.rect(frontier_surf, (255, 255, 100, 255), square_rect, 2)  # Yellow border
        self.screen.blit(frontier_surf, (0, 0))
        
        # Draw the OPTIMAL PATH as THICK WHITE LINE (most visible)
        if pathfinder_result.path_found and pathfinder_result.path and len(pathfinder_result.path) > 1:
            path_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            for i in range(1, len(pathfinder_result.path)):
                x1, y1 = pathfinder_result.path[i-1]
                x2, y2 = pathfinder_result.path[i]
                start_pos = (
                    offset_x + x1 * CELL_SIZE + CELL_SIZE // 2,
                    offset_y + y1 * CELL_SIZE + CELL_SIZE // 2
                )
                end_pos = (
                    offset_x + x2 * CELL_SIZE + CELL_SIZE // 2,
                    offset_y + y2 * CELL_SIZE + CELL_SIZE // 2
                )
                # Draw glow effect (thick transparent line)
                pygame.draw.line(path_surf, (255, 255, 255, 100), start_pos, end_pos, 8)
                # Draw main line (thick white line)
                pygame.draw.line(path_surf, (255, 255, 255, 255), start_pos, end_pos, 4)
                # Draw accent line (bright cyan center)
                pygame.draw.line(path_surf, (0, 255, 255, 255), start_pos, end_pos, 2)
            self.screen.blit(path_surf, (0, 0))
        
        # Draw heuristic values if enabled
        if show_heuristics and pathfinder_result.node_data:
            font_tiny = pygame.font.Font(None, 12)
            for (x, y), data in pathfinder_result.node_data.items():
                if (x, y) != maze.start_pos and (x, y) != maze.goal_pos:
                    if (x, y) in pathfinder_result.frontier_nodes:
                        # Show f, g, h values for frontier nodes
                        cell_rect = pygame.Rect(
                            offset_x + x * CELL_SIZE,
                            offset_y + y * CELL_SIZE,
                            CELL_SIZE,
                            CELL_SIZE
                        )
                        # Draw f, g, h text
                        g_val = data.get('g', 0)
                        h_val = data.get('h', 0)
                        f_val = data.get('f', 0)
                        text = font_tiny.render(f"f:{f_val:.0f}", True, (255, 255, 255))
                        screen_rect = text.get_rect(center=(cell_rect.centerx, cell_rect.centery - 4))
                        # Shadow
                        shadow = font_tiny.render(f"f:{f_val:.0f}", True, (0, 0, 0))
                        self.screen.blit(shadow, (screen_rect.x + 1, screen_rect.y + 1))
                        self.screen.blit(text, screen_rect)
                        
                        # g and h on separate lines
                        g_text = font_tiny.render(f"g:{g_val:.0f}", True, (200, 255, 200))
                        h_text = font_tiny.render(f"h:{h_val:.0f}", True, (200, 200, 255))
                        self.screen.blit(g_text, (cell_rect.left + 2, cell_rect.top + 2))
                        self.screen.blit(h_text, (cell_rect.right - 20, cell_rect.top + 2))
    
    def draw_hint(self, hint_pos, offset_x=0, offset_y=0):
        """Draw hint arrow pointing to next best move"""
        if hint_pos:
            import time
            x, y = hint_pos
            center_x = offset_x + x * CELL_SIZE + CELL_SIZE // 2
            center_y = offset_y + y * CELL_SIZE + CELL_SIZE // 2
            
            # Animated pulsing circle with arrow
            pulse = int(time.time() * 4) % 2
            radius = 12 + pulse * 2
            
            # Draw arrow pointing to hint
            hint_surf = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
            pygame.draw.circle(hint_surf, (*COLORS['GOAL'], 180), (CELL_SIZE, CELL_SIZE), radius)
            pygame.draw.circle(hint_surf, (*COLORS['GOAL_GLOW'], 200), (CELL_SIZE, CELL_SIZE), radius // 2)
            
            # Draw arrow
            arrow_points = [
                (CELL_SIZE, CELL_SIZE - radius - 5),
                (CELL_SIZE - 5, CELL_SIZE - radius),
                (CELL_SIZE + 5, CELL_SIZE - radius)
            ]
            pygame.draw.polygon(hint_surf, (*COLORS['GOAL'], 255), arrow_points)
            
            self.screen.blit(hint_surf, (center_x - CELL_SIZE, center_y - CELL_SIZE))
    
    def draw_game_over_message(self, message, winner=None, game_state=None):
        """Draw game over or win message with stats comparison - simple and aesthetic"""
        
        # Clean, readable fonts
        font_title = pygame.font.Font(None, 64)
        font_subtitle = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 20)
        font_tiny = pygame.font.Font(None, 18)
        
        # Simple semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Clean color schemes based on outcome
        if winner == 'Player':
            primary_color = (76, 175, 80)  # Material green
            accent_color = (129, 199, 132)  # Light green
            title_text = "VICTORY"
            emoji = "✓"
        elif winner == 'AI':
            primary_color = (244, 67, 54)  # Material red
            accent_color = (239, 154, 154)  # Light red
            title_text = "DEFEAT"
            emoji = "✗"
        else:
            primary_color = (158, 158, 158)  # Material gray
            accent_color = (189, 189, 189)  # Light gray
            title_text = "GAME OVER"
            emoji = "⚠"
        
        # Main box - clean and centered
        box_width = 700
        # Calculate height based on whether we have game_state and if it's a duel mode
        base_height = 260
        if game_state:
            if game_state.mode in ['AI Duel', 'Blind Duel']:
                box_height = 600  # Extra space for actual AI stats row
            else:
                box_height = 550  # Standard comparison table
        else:
            box_height = base_height
        box_x = (WINDOW_WIDTH - box_width) // 2
        box_y = (WINDOW_HEIGHT - box_height) // 2 - 30
        
        # Simple shadow (one layer)
        shadow_rect = pygame.Rect(box_x + 6, box_y + 6, box_width, box_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow_rect, border_radius=12)
        
        # Main box with clean white background
        bg_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, border_radius=12)
        
        # Colored top bar
        header_height = 80
        header_rect = pygame.Rect(box_x, box_y, box_width, header_height)
        pygame.draw.rect(self.screen, primary_color, header_rect, border_top_left_radius=12, border_top_right_radius=12)
        
        # Subtle accent line below header
        pygame.draw.line(self.screen, accent_color, 
                        (box_x, box_y + header_height), 
                        (box_x + box_width, box_y + header_height), 3)
        
        # Title text (white on colored background)
        title = font_title.render(title_text, True, (255, 255, 255))
        title_rect = title.get_rect(center=(box_x + box_width // 2, box_y + header_height // 2))
        self.screen.blit(title, title_rect)
        
        # Emoji icon (left of title)
        emoji_text = font_title.render(emoji, True, (255, 255, 255))
        emoji_rect = emoji_text.get_rect(center=(box_x + 60, box_y + header_height // 2))
        self.screen.blit(emoji_text, emoji_rect)
        
        # Message text - clean and simple (wrap if too long)
        words = message.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_text = font_subtitle.render(test_line, True, (80, 80, 80))
            if test_text.get_width() <= box_width - 100:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw message lines (dark gray text on white background)
        start_y = box_y + header_height + 35
        for i, line in enumerate(lines):
            msg_text = font_subtitle.render(line, True, (80, 80, 80))
            msg_rect = msg_text.get_rect(center=(box_x + box_width // 2, start_y + i * 30))
            self.screen.blit(msg_text, msg_rect)
        
        # Draw stats comparison if game_state is available
        if game_state:
            stats_y = start_y + len(lines) * 30 + 25
            
            # Simple divider line
            pygame.draw.line(self.screen, (220, 220, 220), 
                           (box_x + 60, stats_y - 5), 
                           (box_x + box_width - 60, stats_y - 5), 2)
            
            # Stats header - clean and simple
            header = font_small.render("Performance vs AI", True, (100, 100, 100))
            header_rect = header.get_rect(center=(box_x + box_width // 2, stats_y + 10))
            self.screen.blit(header, header_rect)
            
            stats_y += 28
            
            # Run all AI algorithms and compare (accounting for rewards)
            from config import AVAILABLE_ALGORITHMS, REWARD_BONUS, REWARD_DURATION
            from pathfinding import Pathfinder
            import time
            
            # Get reward positions that exist in the maze
            reward_positions = set()
            for y in range(game_state.maze.height):
                for x in range(game_state.maze.width):
                    terrain = game_state.maze.terrain.get((x, y), 'GRASS')
                    if terrain == 'REWARD':
                        reward_positions.add((x, y))
            
            # Add already collected rewards
            reward_positions.update(game_state.player.collected_rewards)
            
            # Use the same algorithm_results_cache as the algorithm comparison panel for consistency
            # Map display names to internal algorithm names
            algo_name_map = {
                'BFS': 'BFS',
                'Dijkstra': 'DIJKSTRA',
                'A*': 'ASTAR',
                'Bidirectional A*': 'BIDIRECTIONAL_ASTAR',
                'Multi-Objective': 'MULTI_OBJECTIVE',
                'Modified A* (Fog)': 'MODIFIED_ASTAR_FOG'  # For Blind Duel mode
            }
            
            # Ensure algorithm_results_cache exists (it should be calculated in main.py's draw method)
            # If it doesn't exist, we'll use an empty dict (algorithms won't be shown)
            if not hasattr(game_state, 'algorithm_results_cache'):
                game_state.algorithm_results_cache = None
            
            # Get cached results from algorithm comparison (same source for consistency)
            if game_state.algorithm_results_cache:
                # Convert from display names to internal names for victory screen
                algo_results = {}
                for display_name, internal_name in algo_name_map.items():
                    if display_name in game_state.algorithm_results_cache:
                        cache_result = game_state.algorithm_results_cache[display_name]
                        algo_results[internal_name] = {
                            'cost': cache_result.get('cost', 0),
                            'steps': cache_result.get('steps', 0),
                            'nodes': cache_result.get('nodes', 0),
                            'time': cache_result.get('time', 0),
                            'rewards_collected': 0  # Not stored in comparison cache
                        }
            else:
                # Cache not available - show empty results (shouldn't happen if main.py is working correctly)
                algo_results = {}
            
            # Player stats
            player = game_state.player
            player_cost = player.total_cost
            player_steps = len(player.path)
            player_energy = player.energy
            
            # Get ACTUAL AI stats from gameplay (not recalculated)
            if game_state.ai_agent:
                actual_ai_cost = game_state.ai_agent.total_cost
                actual_ai_steps = len(game_state.ai_agent.path)
                actual_ai_algo = game_state.selected_algorithm
                from config import DEBUG_MODE
                if DEBUG_MODE:
                    print(f"\n[Game Over Stats - Using ACTUAL gameplay costs]")
                    print(f"Player: cost={player_cost:.1f}, steps={player_steps}")
                    print(f"AI ({actual_ai_algo}): cost={actual_ai_cost:.1f}, steps={actual_ai_steps}")
            else:
                actual_ai_cost = None
                actual_ai_steps = None
                actual_ai_algo = None
            
            # Debug: Show what we're comparing
            from config import DEBUG_MODE
            if DEBUG_MODE:
                print(f"Available rewards in maze: {len(reward_positions)}")
                for algo, results in algo_results.items():
                    print(f"{algo} (recalculated): cost={results['cost']:.1f}, steps={results['steps']}, rewards={results.get('rewards_collected', 0)}")
            
            # Comprehensive comparison table
            row_height = 22
            start_x = box_x + 40
            col_widths = [100, 70, 60, 70, 70, 80]  # Algorithm, Cost, Steps, Nodes, Time, Energy
            # Calculate cumulative spacing for each column
            col_spacing = [0]
            for i in range(1, len(col_widths)):
                col_spacing.append(col_spacing[i-1] + col_widths[i-1])
            
            # Table headers
            headers = ["Algorithm", "Cost", "Steps", "Nodes", "Time(ms)", "Energy"]
            header_y = stats_y
            for i, h in enumerate(headers):
                h_text = font_small.render(h, True, (100, 100, 100))
                self.screen.blit(h_text, (start_x + col_spacing[i], header_y))
            
            stats_y += row_height + 5
            
            # Draw header underline
            pygame.draw.line(self.screen, (200, 200, 200), 
                           (start_x, stats_y - 3), 
                           (start_x + sum(col_widths), stats_y - 3), 2)
            stats_y += 5
            
            # Player row (highlighted with subtle background)
            player_row_y = stats_y
            # Subtle background tint instead of white box
            player_bg = pygame.Surface((sum(col_widths) + 10, row_height), pygame.SRCALPHA)
            player_bg.fill((primary_color[0]//8, primary_color[1]//8, primary_color[2]//8, 100))
            self.screen.blit(player_bg, (start_x - 5, player_row_y - 2))
            
            player_label = font_small.render("YOU", True, primary_color)
            self.screen.blit(player_label, (start_x + col_spacing[0], player_row_y))
            
            player_data = [
                f"{player_cost:.1f}",
                f"{player_steps}",
                "-",
                "-",
                f"{player_energy:.0f}"
            ]
            for i, val in enumerate(player_data):
                val_text = font_small.render(val, True, (40, 40, 40))  # Darker for better contrast
                self.screen.blit(val_text, (start_x + col_spacing[i+1], player_row_y))
            
            stats_y += row_height + 3
            
            # Show actual AI gameplay stats for duel modes (before algorithm comparison)
            if game_state.mode in ['AI Duel', 'Blind Duel'] and actual_ai_cost is not None:
                # Calculate AI steps from move history if available
                ai_steps_display = actual_ai_steps
                if hasattr(game_state.ai_agent, 'move_history') and game_state.ai_agent.move_history:
                    ai_steps_display = len(game_state.ai_agent.move_history)
                
                # Determine row color based on performance vs player
                if actual_ai_cost < player_cost:
                    row_color = (100, 255, 100, 40)  # Green tint - AI beat player
                    name_color = (40, 120, 40)  # Dark green
                elif abs(actual_ai_cost - player_cost) < 0.1:
                    row_color = (255, 255, 100, 40)  # Yellow tint - Tie
                    name_color = (120, 120, 40)  # Dark yellow
                else:
                    row_color = (255, 100, 100, 40)  # Red tint - Player beat AI
                    name_color = (120, 40, 40)  # Dark red
                
                # Subtle row background
                row_bg = pygame.Surface((sum(col_widths) + 10, row_height), pygame.SRCALPHA)
                row_bg.fill(row_color)
                self.screen.blit(row_bg, (start_x - 5, stats_y - 2))
                
                # AI label (actual gameplay)
                ai_label = "AI (Actual)" if game_state.mode == 'Blind Duel' else "AI (Actual)"
                name_text = font_tiny.render(ai_label, True, name_color)
                self.screen.blit(name_text, (start_x + col_spacing[0], stats_y))
                
                # AI actual stats
                ai_data = [
                    f"{actual_ai_cost:.1f}",
                    f"{ai_steps_display}",
                    "-",  # Nodes not tracked for actual gameplay
                    "-",  # Time not tracked for actual gameplay
                    "-"   # AI doesn't have energy
                ]
                for i, val in enumerate(ai_data):
                    val_text = font_tiny.render(val, True, (50, 50, 50))
                    self.screen.blit(val_text, (start_x + col_spacing[i+1], stats_y))
                
                stats_y += row_height + 5
                
                # Divider line between actual AI and algorithm comparison (only if showing algorithms)
                if game_state.mode != 'Blind Duel':
                    pygame.draw.line(self.screen, (200, 200, 200), 
                                   (start_x, stats_y - 3), 
                                   (start_x + sum(col_widths), stats_y - 3), 1)
                    stats_y += 5
            
            # All AI algorithms (from algorithm comparison)
            algo_display_map = {
                'BFS': 'BFS',
                'DIJKSTRA': 'Dijkstra',
                'ASTAR': 'A*',
                'BIDIRECTIONAL_ASTAR': 'Bidir A*',
                'MULTI_OBJECTIVE': 'Multi-Obj',
                'MODIFIED_ASTAR_FOG': 'Modified A* (Fog)'  # For Blind Duel mode
            }
            
            # For Blind Duel mode, don't show algorithm comparison (only show AI Actual)
            # since the AI already used Modified A* (Fog) during gameplay
            if game_state.mode == 'Blind Duel':
                # Skip algorithm comparison - AI (Actual) is already shown above
                sorted_algos = []
            else:
                # Sort algorithms by cost for better comparison
                sorted_algos = sorted(algo_results.items(), key=lambda x: x[1]['cost'])
            
            for algo, results in sorted_algos:
                # Determine row color based on performance vs player (subtle tint)
                if results['cost'] < player_cost:
                    row_color = (100, 255, 100, 40)  # Green tint - AI beat player
                    name_color = (40, 120, 40)  # Dark green for name
                elif abs(results['cost'] - player_cost) < 0.1:  # Essentially equal
                    row_color = (255, 255, 100, 40)  # Yellow tint - Tie
                    name_color = (120, 120, 40)  # Dark yellow for name
                else:
                    row_color = (255, 100, 100, 40)  # Red tint - Player beat AI
                    name_color = (120, 40, 40)  # Dark red for name
                
                # Subtle row background (no white box)
                row_bg = pygame.Surface((sum(col_widths) + 10, row_height), pygame.SRCALPHA)
                row_bg.fill(row_color)
                self.screen.blit(row_bg, (start_x - 5, stats_y - 2))
                
                # Algorithm name with better contrast
                algo_name = algo_display_map.get(algo, algo)
                name_text = font_tiny.render(algo_name, True, name_color)
                self.screen.blit(name_text, (start_x + col_spacing[0], stats_y))
                
                # Stats with dark text for clarity
                # Format time with appropriate precision (same as algorithm comparison)
                time_val = results['time']
                # Use same round_time logic as main.py
                if time_val < 0.1:
                    time_str = f"{round(time_val, 2)}"  # 2 decimal places for sub-millisecond
                else:
                    time_str = f"{round(time_val, 1)}"  # 1 decimal place for normal times
                
                algo_data = [
                    f"{results['cost']:.1f}",
                    f"{results['steps']}",
                    f"{results['nodes']}",
                    time_str,
                    "-"  # AI doesn't have energy
                ]
                for i, val in enumerate(algo_data):
                    val_text = font_tiny.render(val, True, (50, 50, 50))  # Darker for better readability
                    self.screen.blit(val_text, (start_x + col_spacing[i+1], stats_y))
                
                stats_y += row_height
            
            # Energy info - clean
            stats_y += 8
            energy_text = font_small.render(f"Energy: {player_energy:.0f}/{INITIAL_ENERGY}", True, (120, 120, 120))
            energy_rect = energy_text.get_rect(center=(box_x + box_width // 2, stats_y))
            self.screen.blit(energy_text, energy_rect)
        
        # Simple instructions at bottom
        y_offset = box_y + box_height + 15
        instructions_text = font_tiny.render("R: Reset  |  G: New Maze  |  ESC: Quit", True, (200, 200, 200))
        instructions_rect = instructions_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
        self.screen.blit(instructions_text, instructions_rect)
    
    def draw_algorithm_comparison(self, game_state, algorithms_results):
        """Draw algorithm comparison dashboard"""
        if not game_state.algorithm_comparison:
            return
        
        # Draw comparison panel (overlay)
        panel_width = 400
        panel_height = 300
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay_color = (0, 0, 0, 150)
        overlay.fill(overlay_color)
        self.screen.blit(overlay, (0, 0))
        
        pygame.draw.rect(self.screen, COLORS['UI_PANEL'], panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['UI_BORDER'], panel_rect, 3, border_radius=10)
        
        font_title = pygame.font.Font(None, 28)
        font_normal = pygame.font.Font(None, 18)
        
        title = font_title.render("Algorithm Comparison", True, COLORS['TEXT'])
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, panel_y + 30))
        self.screen.blit(title, title_rect)
        
        y = panel_y + 70
        headers = ["Algorithm", "Nodes", "Cost", "Time (ms)"]
        header_x = panel_x + 20
        column_widths = [120, 60, 60, 80]  # Adjusted column widths
        for i, header in enumerate(headers):
            text = font_normal.render(header, True, COLORS['TEXT'])
            x_pos = header_x + sum(column_widths[:i])
            self.screen.blit(text, (x_pos, y))
        
        y += 30
        for algo_name, result in algorithms_results.items():
            # Shorten algorithm names for display
            display_name = {
                'Dijkstra': 'Dijkstra',
                'A*': 'A*',
                'Bidirectional A*': 'Bidir A*',
                'BFS': 'BFS',
                'Multi-Objective': 'Multi-Obj'
            }.get(algo_name, algo_name)
            
            name_text = font_normal.render(display_name, True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(name_text, (header_x, y))
            
            nodes_text = font_normal.render(str(result.get('nodes', 0)), True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(nodes_text, (header_x + column_widths[0], y))
            
            cost_text = font_normal.render(f"{result.get('cost', 0):.1f}", True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(cost_text, (header_x + column_widths[0] + column_widths[1], y))
            
            # Format time with same precision as algorithm comparison
            time_val = result.get('time', 0)
            if time_val < 0.1:
                time_str = f"{round(time_val, 2)}"  # 2 decimal places for sub-millisecond
            else:
                time_str = f"{round(time_val, 1)}"  # 1 decimal place for normal times
            time_text = font_normal.render(time_str, True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(time_text, (header_x + column_widths[0] + column_widths[1] + column_widths[2], y))
            
            y += 30
        
        # Close instruction
        close_text = font_normal.render("Press C to close", True, COLORS['TEXT_SECONDARY'])
        close_rect = close_text.get_rect(center=(panel_x + panel_width // 2, panel_y + panel_height - 30))
        self.screen.blit(close_text, close_rect)
