"""
UI and visualization components
Handles rendering of stats, exploration visualization, and game interface
"""

import pygame
from config import *

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.ui_panel_x = WINDOW_WIDTH - GRID_PADDING
        self.ui_panel_width = GRID_PADDING
        self.ui_panel_height = WINDOW_HEIGHT
        
    def draw_ui_panel(self, game_state):
        """Draw the right-side UI panel with modern styling"""
        # Draw main panel with gradient
        panel_rect = pygame.Rect(self.ui_panel_x, 0, self.ui_panel_width, self.ui_panel_height)
        pygame.draw.rect(self.screen, COLORS['UI_PANEL'], panel_rect)
        pygame.draw.rect(self.screen, COLORS['UI_BORDER'], panel_rect, 2)
        
        # Draw subtle shadow (removed transparency - use solid color)
        shadow_rect = pygame.Rect(self.ui_panel_x - 2, 2, self.ui_panel_width, self.ui_panel_height)
        pygame.draw.rect(self.screen, (200, 200, 200), shadow_rect)
        
        y_offset = 20
        font_title = pygame.font.Font(None, FONT_SIZE_LARGE + 8)
        font_normal = pygame.font.Font(None, FONT_SIZE_MEDIUM + 2)
        font_small = pygame.font.Font(None, FONT_SIZE_SMALL + 2)
        font_bold = pygame.font.Font(None, FONT_SIZE_MEDIUM + 4)
        
        # Title with gradient effect
        title = font_title.render("MazeRunner X", True, COLORS['TEXT'])
        self.screen.blit(title, (self.ui_panel_x + 15, y_offset))
        y_offset += 45
        
        # Game Mode with colored badge
        mode_colors = {
            'Explore': (76, 175, 80),
            'Dynamic': (255, 152, 0),
            'Multi-Goal': (156, 39, 176),
            'AI Duel': (244, 67, 54),
            'AI Duel (Checkpoints)': (244, 67, 54)
        }
        mode_color = mode_colors.get(game_state.mode, COLORS['TEXT'])
        mode_rect = pygame.Rect(self.ui_panel_x + 10, y_offset, 180, 30)
        pygame.draw.rect(self.screen, mode_color, mode_rect, border_radius=5)
        mode_text = font_bold.render(f"{game_state.mode}", True, (255, 255, 255))
        text_rect = mode_text.get_rect(center=mode_rect.center)
        self.screen.blit(mode_text, text_rect)
        y_offset += 40
        
        # Turn indicator (for AI Duel modes)
        duel_modes = ['AI Duel', 'AI Duel (Checkpoints)']
        if game_state.mode in duel_modes and TURN_BASED:
            turn_text = "Your Turn" if game_state.turn == 'player' else "AI's Turn"
            turn_color = COLORS['PLAYER'] if game_state.turn == 'player' else COLORS['AI']
            turn_surf = font_normal.render(turn_text, True, turn_color)
            self.screen.blit(turn_surf, (self.ui_panel_x + 15, y_offset))
            y_offset += 30
        
        # Player Stats
        y_offset = self.draw_player_stats(game_state, y_offset, font_normal, font_small)
        
        # AI Stats (if in duel modes)
        duel_modes = ['AI Duel', 'AI Duel (Checkpoints)']
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
        
        # Extensions toggle
        y_offset += 20
        y_offset = self.draw_extensions_toggles(game_state, y_offset, font_small)
    
    def draw_energy_bar(self, game_state, y_offset, font_small):
        """Draw energy bar with visual feedback"""
        title = font_small.render("Energy:", True, COLORS['TEXT'])
        self.screen.blit(title, (self.ui_panel_x + 15, y_offset))
        y_offset += 20
        
        bar_width = 170
        bar_height = 20
        bar_rect = pygame.Rect(self.ui_panel_x + 15, y_offset, bar_width, bar_height)
        pygame.draw.rect(self.screen, (200, 200, 200), bar_rect, border_radius=3)
        
        # Calculate energy percentage
        energy_pct = max(0, min(1, game_state.player.energy / INITIAL_ENERGY))
        fill_width = int(bar_width * energy_pct)
        
        if fill_width > 0:
            fill_rect = pygame.Rect(self.ui_panel_x + 15, y_offset, fill_width, bar_height)
            bar_color = COLORS['ENERGY_BAR'] if energy_pct > 0.3 else COLORS['ENERGY_BAR_LOW']
            pygame.draw.rect(self.screen, bar_color, fill_rect, border_radius=3)
        
        # Energy text
        energy_text = font_small.render(f"{game_state.player.energy:.0f}/{INITIAL_ENERGY}", True, COLORS['TEXT'])
        text_rect = energy_text.get_rect(center=bar_rect.center)
        self.screen.blit(energy_text, text_rect)
        
        return y_offset + 35
    
    def draw_player_stats(self, game_state, y_offset, font_normal, font_small):
        """Draw player statistics with modern styling"""
        # Section header
        header_rect = pygame.Rect(self.ui_panel_x + 10, y_offset, 180, 25)
        pygame.draw.rect(self.screen, COLORS['PLAYER'], header_rect, border_radius=3)
        title = font_normal.render("Player", True, (255, 255, 255))
        self.screen.blit(title, (self.ui_panel_x + 15, y_offset + 3))
        y_offset += 35
        
        stats = [
            f"Position: ({game_state.player.x}, {game_state.player.y})",
            f"Path Cost: {game_state.player.total_cost:.1f}",
            f"Steps: {len(game_state.player.path)}",
        ]
        
        if game_state.maze.checkpoints:
            checkpoints_text = f"Checkpoints: {len(game_state.player.reached_checkpoints)}/{len(game_state.maze.checkpoints)}"
            stats.append(checkpoints_text)
        
        for stat in stats:
            text = font_small.render(stat, True, COLORS['TEXT'])
            self.screen.blit(text, (self.ui_panel_x + 20, y_offset))
            y_offset += 22
        
        return y_offset
    
    def draw_ai_stats(self, game_state, y_offset, font_normal, font_small):
        """Draw AI statistics with modern styling"""
        # Section header
        header_rect = pygame.Rect(self.ui_panel_x + 10, y_offset, 180, 25)
        pygame.draw.rect(self.screen, COLORS['AI'], header_rect, border_radius=3)
        title = font_normal.render("AI", True, (255, 255, 255))
        self.screen.blit(title, (self.ui_panel_x + 15, y_offset + 3))
        y_offset += 35
        
        if game_state.ai_agent:
            stats = [
                f"Position: ({game_state.ai_agent.x}, {game_state.ai_agent.y})",
                f"Path Cost: {game_state.ai_agent.total_cost:.1f}",
                f"Nodes: {game_state.ai_agent.path_result.nodes_explored if game_state.ai_agent.path_result else 0}",
            ]
            
            # Add checkpoint progress for checkpoint mode
            if game_state.mode == 'AI Duel (Checkpoints)' and game_state.maze.checkpoints:
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
            "G: New Maze",
            "1-5: Change Mode",
            "F: Fog of War",
            "C: Algorithm Compare",
            "ESC: Quit"
        ]
        
        for control in controls:
            text = font_small.render(control, True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(text, (self.ui_panel_x + 20, y_offset))
            y_offset += 18
        
        return y_offset
    
    def draw_algorithm_info(self, game_state, y_offset, font_small):
        """Draw algorithm exploration information"""
        from config import AI_ALGORITHM
        header = font_small.render("AI Algorithm:", True, COLORS['TEXT'])
        self.screen.blit(header, (self.ui_panel_x + 15, y_offset))
        y_offset += 25
        
        if game_state.ai_agent and game_state.ai_agent.path_result:
            result = game_state.ai_agent.path_result
            # Determine which algorithm was actually used
            algo_name = AI_ALGORITHM
            if game_state.mode == 'Multi-Goal' or game_state.mode == 'AI Duel (Checkpoints)':
                if game_state.maze.checkpoints:
                    algo_name = 'MULTI_OBJECTIVE'
            elif game_state.mode == 'Dynamic':
                algo_name = 'DSTAR'
            
            # Format algorithm name nicely
            algo_display = {
                'DIJKSTRA': 'Dijkstra',
                'ASTAR': 'A*',
                'BIDIRECTIONAL_ASTAR': 'Bidirectional A*',
                'DSTAR': 'D* (Dynamic A*)',
                'MULTI_OBJECTIVE': 'Multi-Objective'
            }.get(algo_name, algo_name)
            
            info = [
                f"Algorithm: {algo_display}",
                f"Heuristic: {game_state.ai_pathfinder.heuristic_type if game_state.ai_pathfinder else 'N/A'}",
                f"Path Found: {'Yes' if result.path_found else 'No'}",
                f"Optimal Cost: {result.cost:.1f}",
            ]
            
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
        
        # Fog of War toggle
        fog_status = "ON" if game_state.fog_of_war else "OFF"
        fog_color = (76, 175, 80) if game_state.fog_of_war else COLORS['TEXT_SECONDARY']
        fog_text = font_small.render(f"Fog of War: {fog_status}", True, fog_color)
        self.screen.blit(fog_text, (self.ui_panel_x + 20, y_offset))
        y_offset += 18
        
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
        
        # Draw explored nodes with transparency
        explored_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for x, y in pathfinder_result.explored_nodes:
            if (x, y) != maze.start_pos and (x, y) != maze.goal_pos:
                rect = pygame.Rect(
                    offset_x + x * CELL_SIZE + 3,
                    offset_y + y * CELL_SIZE + 3,
                    CELL_SIZE - 6,
                    CELL_SIZE - 6
                )
                explored_color = (*COLORS['EXPLORED'], 120)
                pygame.draw.rect(explored_surf, explored_color, rect)
        self.screen.blit(explored_surf, (0, 0))
        
        # Draw frontier nodes
        frontier_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for x, y in pathfinder_result.frontier_nodes:
            if (x, y) not in pathfinder_result.explored_nodes:
                rect = pygame.Rect(
                    offset_x + x * CELL_SIZE + 3,
                    offset_y + y * CELL_SIZE + 3,
                    CELL_SIZE - 6,
                    CELL_SIZE - 6
                )
                frontier_color = (*COLORS['FRONTIER'], 150)
                pygame.draw.rect(frontier_surf, frontier_color, rect)
        self.screen.blit(frontier_surf, (0, 0))
        
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
    
    def draw_game_over_message(self, message, winner=None):
        """Draw game over or win message with modern styling"""
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        # Background overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay_color = (0, 0, 0, 200) if winner is None else (0, 0, 0, 180)
        overlay.fill(overlay_color)
        self.screen.blit(overlay, (0, 0))
        
        # Determine colors based on outcome
        if winner == 'Player':
            bg_color = (40, 167, 69)  # Success green
            border_color = (76, 175, 80)
            text_color = (255, 255, 255)
        elif winner == 'AI':
            bg_color = (220, 53, 69)  # Danger red
            border_color = (244, 67, 54)
            text_color = (255, 255, 255)
        else:
            # Trapped or failed
            bg_color = (108, 117, 125)  # Dark gray
            border_color = (134, 142, 150)
            text_color = (255, 255, 255)
        
        # Main message box
        box_width = 600
        box_height = 200
        box_x = (WINDOW_WIDTH - box_width) // 2
        box_y = (WINDOW_HEIGHT - box_height) // 2 - 40
        
        bg_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=15)
        pygame.draw.rect(self.screen, border_color, bg_rect, 4, border_radius=15)
        
        # Draw shadow effect behind the box
        shadow_rect = bg_rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        shadow_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 100))
        self.screen.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
        
        # Draw the main box
        pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=15)
        pygame.draw.rect(self.screen, border_color, bg_rect, 4, border_radius=15)
        
        # Title text
        if winner == 'Player':
            title_text = "VICTORY!"
        elif winner == 'AI':
            title_text = "DEFEAT"
        elif "Trapped" in message:
            title_text = "TRAPPED!"
        else:
            title_text = "GAME OVER"
        
        title = font_large.render(title_text, True, text_color)
        title_rect = title.get_rect(center=(box_x + box_width // 2, box_y + 50))
        self.screen.blit(title, title_rect)
        
        # Message text (wrap if too long)
        words = message.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_text = font_medium.render(test_line, True, text_color)
            if test_text.get_width() <= box_width - 80:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw message lines
        start_y = box_y + 100
        for i, line in enumerate(lines):
            msg_text = font_medium.render(line, True, text_color)
            msg_rect = msg_text.get_rect(center=(box_x + box_width // 2, start_y + i * 35))
            self.screen.blit(msg_text, msg_rect)
        
        # Instructions
        y_offset = box_y + box_height + 30
        instructions = [
            "Press R to reset",
            "Press G for new maze",
            "Press ESC to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = font_small.render(instruction, True, (200, 200, 200))
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset + i * 25))
            self.screen.blit(inst_text, inst_rect)
    
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
        font_normal = pygame.font.Font(None, 20)
        
        title = font_title.render("Algorithm Comparison", True, COLORS['TEXT'])
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, panel_y + 30))
        self.screen.blit(title, title_rect)
        
        y = panel_y + 70
        headers = ["Algorithm", "Nodes", "Cost", "Time (ms)"]
        header_x = panel_x + 20
        for i, header in enumerate(headers):
            text = font_normal.render(header, True, COLORS['TEXT'])
            self.screen.blit(text, (header_x + i * 90, y))
        
        y += 30
        for algo_name, result in algorithms_results.items():
            name_text = font_normal.render(algo_name, True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(name_text, (header_x, y))
            
            nodes_text = font_normal.render(str(result.get('nodes', 0)), True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(nodes_text, (header_x + 90, y))
            
            cost_text = font_normal.render(f"{result.get('cost', 0):.1f}", True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(cost_text, (header_x + 180, y))
            
            time_text = font_normal.render(f"{result.get('time', 0):.2f}", True, COLORS['TEXT_SECONDARY'])
            self.screen.blit(time_text, (header_x + 270, y))
            
            y += 25
        
        # Close instruction
        close_text = font_normal.render("Press C to close", True, COLORS['TEXT_SECONDARY'])
        close_rect = close_text.get_rect(center=(panel_x + panel_width // 2, panel_y + panel_height - 30))
        self.screen.blit(close_text, close_rect)
