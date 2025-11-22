"""
Configuration file for MazeRunner
Contains constants, colors, and game settings

This file stores all the configuration values used throughout the game.
Think of it as a central place where we define how the game looks and behaves.
By changing values here, you can easily customize the game without digging through code.
"""

# ============================================================================
# WINDOW SETTINGS
# ============================================================================
# These settings control the size of the game window and how big each cell appears

WINDOW_WIDTH = 1600  # Total width of the game window in pixels (horizontal)
WINDOW_HEIGHT = 1000  # Total height of the game window in pixels (vertical)
CELL_SIZE = 30  # Size of each maze cell in pixels (30x30 square)
GRID_PADDING = 250  # Space reserved on the right side for the UI panel (stats, controls, etc.)

# ============================================================================
# COLOR DEFINITIONS
# ============================================================================
# Colors are defined as RGB tuples: (Red, Green, Blue) where each value is 0-255
# Example: (255, 0, 0) = pure red, (0, 255, 0) = pure green, (0, 0, 255) = pure blue
# These colors are used throughout the game to draw different elements

COLORS = {
    'GRASS': (102, 187, 106),         # Brighter Material Green
    'GRASS_DARK': (76, 175, 80),      # Medium green for depth
    'WATER': (66, 165, 245),          # Brighter Material Blue
    'WATER_DARK': (33, 150, 243),     # Medium blue
    'MUD': (141, 110, 99),            # Lighter Material Brown
    'MUD_DARK': (121, 85, 72),        # Medium brown
    'LAVA': (239, 83, 80),            # Brighter Material Red
    'LAVA_DARK': (229, 57, 53),       # Medium red
    'LAVA_GLOW': (255, 183, 77),      # Brighter orange glow
    'WALL': (45, 45, 48),             # Modern dark gray for walls
    'WALL_LIGHT': (78, 78, 82),       # Modern lighter gray for wall highlights
    'PATH': (255, 255, 255),          # Pure white paths
    'START': (139, 195, 74),          # Light Green
    'START_DARK': (104, 159, 56),     # Darker green
    'GOAL': (255, 214, 0),            # Brighter Amber/Gold
    'GOAL_DARK': (255, 193, 7),       # Medium amber
    'GOAL_GLOW': (255, 245, 157),     # Soft yellow glow
    'CHECKPOINT': (255, 167, 38),     # Brighter Orange
    'CHECKPOINT_DARK': (251, 140, 0), # Medium orange
    'PLAYER': (240, 98, 146),         # Brighter Pink
    'PLAYER_OUTLINE': (216, 27, 96),  # Rich dark pink
    'AI': (171, 71, 188),             # Brighter Purple
    'AI_OUTLINE': (142, 36, 170),     # Rich dark purple
    'PATH_LINE': (255, 235, 59),      # Bright yellow for path lines
    'PATH_DARK': (251, 192, 45),      # Darker yellow
    'EXPLORED': (244, 143, 177),      # Light pink with alpha
    'FRONTIER': (144, 202, 249),      # Light blue with alpha
    'BACKGROUND': (248, 249, 250),    # Softer off-white
    'UI_BG': (243, 244, 246),         # Softer light gray
    'UI_PANEL': (255, 255, 255),      # Pure white panel
    'UI_BORDER': (218, 220, 224),     # Softer border
    'TEXT': (32, 33, 36),             # Slightly warmer dark gray text
    'TEXT_SECONDARY': (95, 99, 104),  # Modern secondary text
    'FOG': (33, 33, 33),              # Dark fog of war
    'ENERGY_BAR': (102, 187, 106),    # Bright green energy
    'ENERGY_BAR_LOW': (239, 83, 80),  # Bright red energy
    # New obstacle colors
    'SPIKES': (120, 120, 120),        # Gray spikes
    'SPIKES_DARK': (80, 80, 80),      # Dark gray
    'THORNS': (85, 139, 47),          # Dark olive green
    'THORNS_DARK': (60, 100, 30),     # Darker olive
    'QUICKSAND': (210, 180, 140),     # Tan/beige
    'QUICKSAND_DARK': (180, 150, 110), # Darker tan
    'ROCKS': (160, 160, 160),         # Light gray
    'ROCKS_DARK': (120, 120, 120),    # Medium gray
    # Reward cells
    'REWARD': (255, 215, 0),          # Gold/yellow
    'REWARD_GLOW': (255, 235, 59),    # Bright yellow glow
    'REWARD_DARK': (255, 193, 7),     # Darker gold
}

# ============================================================================
# TERRAIN MOVEMENT COSTS
# ============================================================================
# This dictionary defines how much energy it costs to move through each terrain type.
# Lower numbers = cheaper/easier to move through
# Higher numbers = more expensive/harder to move through
# float('inf') = impossible to move through (infinite cost)
#
# These costs are used by pathfinding algorithms to find the optimal (cheapest) path.
# For example: If grass costs 1 and water costs 3, algorithms will prefer grass paths.

TERRAIN_COSTS = {
    'PATH': 1,        # Basic path - cheapest terrain (cost: 1 energy per cell)
    'GRASS': 1,       # Grassland - same as path, easy to walk (cost: 1 energy per cell)
    'WATER': 3,       # Water - slower to cross (cost: 3 energy per cell, 3x more expensive than grass)
    'MUD': 5,         # Mud - very slow to walk through (cost: 5 energy per cell, 5x more expensive than grass)
    'LAVA': float('inf'),  # Lava - completely impassable (infinite cost = cannot move through)
    'WALL': float('inf'),  # Wall - completely impassable (infinite cost = cannot move through)
    'START': 0,       # Start position - no cost to be here (you start here for free)
    'GOAL': 0,        # Goal position - no cost to be here (reaching goal is free)
    'CHECKPOINT': 0,  # Checkpoint - no cost to visit (checkpoints are free to step on)
    
    # Obstacle types for Obstacle Course mode (these have movement costs but are passable)
    'SPIKES': 4,      # Sharp spikes - moderate cost (cost: 4 energy, dangerous but passable)
    'THORNS': 3,      # Thorny bushes - light cost (cost: 3 energy, slightly painful)
    'QUICKSAND': 6,   # Quicksand - high cost (cost: 6 energy, very slow to cross)
    'ROCKS': 2,       # Rocky terrain - low cost (cost: 2 energy, slightly difficult)
    
    # Reward cells - special cells that give bonuses
    'REWARD': 0,      # Reward cell - free to traverse, and gives cost reduction bonus for next moves
}

# ============================================================================
# REWARD SYSTEM SETTINGS
# ============================================================================
# Rewards are special gold cells that give temporary bonuses when collected

REWARD_BONUS = -2  # Cost reduction when collecting reward (negative = bonus)
                  # Example: If you collect a reward, your next moves cost 2 less energy
                  # So moving through water (cost 3) would only cost 1 energy with active reward
                  
REWARD_DURATION = 5  # Number of moves the reward effect lasts
                    # After collecting a reward, the bonus applies to your next 5 moves
                    # Then it expires and you need to collect another reward
                    
REWARD_SPAWN_RATE = 0.03  # Probability that a cell spawns as a reward (3% chance)
                          # 0.03 means 3 out of 100 cells will be rewards
                          # Higher number = more rewards, lower number = fewer rewards

# ============================================================================
# DYNAMIC OBSTACLE SETTINGS (Obstacle Course Mode)
# ============================================================================
# In Obstacle Course mode, obstacles can appear and disappear each turn
# These settings control how many obstacles change per turn

DYNAMIC_OBSTACLE_CHANGE_PER_TURN = 2  # Number of obstacles to add/remove per turn
                                      # Each turn, 2 obstacles are removed and 2 new ones spawn
                                      # This makes the maze dynamic and challenging
                                      
DYNAMIC_OBSTACLE_MAX_CHANGES = 3  # Maximum total changes (adds + removes) per turn
                                  # Limits how many obstacles can change to prevent chaos
                                  # Total changes = adds + removes, capped at this number

# ============================================================================
# GAME SETTINGS
# ============================================================================

FPS = 60  # Frames Per Second - how many times the game updates per second
         # 60 FPS = smooth gameplay, lower = choppy, higher = smoother (but uses more CPU)
         # Most monitors display at 60Hz, so 60 FPS is optimal

MAZE_WIDTH = 31  # Width of the maze in cells (must be ODD number for proper maze generation)
                 # The maze generation algorithm works best with odd dimensions
                 # 31 cells wide means the maze is 31 cells across horizontally
                 
MAZE_HEIGHT = 23  # Height of the maze in cells (must be ODD number for proper maze generation)
                  # 23 cells tall means the maze is 23 cells high vertically
                  # Total maze size = 31 × 23 = 713 cells

# ============================================================================
# AI SETTINGS
# ============================================================================
# These settings control how the AI opponent behaves

AI_SPEED = 0.5  # How often the AI moves (for non-turn-based modes)
               # 0.5 means the AI moves every 0.5 seconds (2 moves per second)
               # Lower number = faster AI, higher number = slower AI
               # Note: In turn-based modes, this is ignored (AI moves after player)

HEURISTIC_TYPE = 'MANHATTAN'  # Type of heuristic function for A* algorithm
                              # 'MANHATTAN': Uses |x1-x2| + |y1-y2| (like city blocks, only horizontal/vertical)
                              # 'EUCLIDEAN': Uses straight-line distance √((x1-x2)² + (y1-y2)²)
                              # Manhattan is faster to calculate and works well for grid-based movement
                              
TURN_BASED = True  # Whether AI Duel mode uses turn-based gameplay
                  # True = Player moves, then AI moves (alternating turns)
                  # False = Both move continuously (real-time)
                  # Turn-based is recommended for fair competition

# ============================================================================
# AI DIFFICULTY SETTINGS
# ============================================================================
# Controls how smart/aggressive the AI is
# The AI uses heuristics (estimates) to find paths - these settings adjust how much it trusts those estimates

AI_DIFFICULTY = 'MEDIUM'  # Current difficulty level
                         # Options: 'EASY', 'MEDIUM', 'HARD'
                         # EASY: AI is less optimal, more predictable (easier to beat)
                         # MEDIUM: Balanced AI (fair challenge)
                         # HARD: AI is more optimal, finds better paths (harder to beat)

# Heuristic scaling factors - how much the AI trusts its distance estimates
# Lower values = AI explores more (slower but more thorough)
# Higher values = AI trusts estimates more (faster but might miss optimal paths)
AI_HEURISTIC_SCALE = {
    'EASY': 0.7,    # EASY: 70% scaling - AI explores more, less aggressive
                   # Uses MANHATTAN heuristic with 0.7 scaling (more predictable, suboptimal)
    'MEDIUM': 1.0,  # MEDIUM: 100% scaling - balanced exploration
                   # Uses MANHATTAN heuristic with 1.0 scaling (balanced)
    'HARD': 1.5     # HARD: 150% scaling - AI trusts estimates more, more aggressive
                   # Uses EUCLIDEAN heuristic with 1.5 scaling (more optimal, aggressive)
}

# ============================================================================
# PATHFINDING ALGORITHM SELECTION
# ============================================================================
# The game uses different pathfinding algorithms to find optimal paths
# Each algorithm has different strengths and weaknesses

# Available algorithm options:
# - 'DIJKSTRA': Guaranteed optimal path, but slower (explores uniformly in all directions)
# - 'ASTAR': Faster heuristic-driven search, still optimal (uses distance estimates to guide search)
# - 'BIDIRECTIONAL_ASTAR': Very fast, searches from both start and goal simultaneously
# - 'DSTAR': Dynamic A* for moving obstacles (adapts when obstacles change)
# - 'MULTI_OBJECTIVE': For multiple goals/checkpoints (finds optimal order to visit them)

AI_ALGORITHM = 'ASTAR'  # Default algorithm for AI (can be changed with [ ] keys in-game)
                       # A* is a good balance of speed and optimality

# Algorithm auto-selection (the game automatically picks the right algorithm):
# - Uses MULTI_OBJECTIVE in Multi-Goal/Checkpoint modes (needs to visit multiple goals)
# - Uses MODIFIED_ASTAR_FOG in Blind Duel mode (needs to handle fog of war)
# - Uses ASTAR or DIJKSTRA otherwise (based on AI_ALGORITHM setting)

# Available algorithms for user selection (can cycle through these with [ ] keys)
AVAILABLE_ALGORITHMS = ['BFS', 'DIJKSTRA', 'ASTAR', 'BIDIRECTIONAL_ASTAR']
# BFS = Breadth-First Search (unweighted, finds shortest path by steps, not cost)
# DIJKSTRA = Optimal weighted pathfinding
# ASTAR = Fast heuristic-driven pathfinding
# BIDIRECTIONAL_ASTAR = Fastest pathfinding for long paths

# ============================================================================
# FOG OF WAR SETTINGS
# ============================================================================
# Fog of War limits visibility - you can only see nearby cells

FOG_OF_WAR_RADIUS = 3  # Default visibility radius in cells (fallback value)
                      # Actual radius is set per mode in game_modes.py
                      # In Blind Duel mode: Player sees 2 cells, AI sees 1 cell
                      # This value is used as a fallback if not specified elsewhere

# ============================================================================
# GAMEPLAY SETTINGS
# ============================================================================

PREVENT_PATH_REVISITING = False  # Whether player can revisit cells they've already been to
                                # False = Can go back to previous cells (allows backtracking)
                                # True = Cannot revisit cells (forces forward progress)
                                # Set to False to ensure players can always reach checkpoints

UNDO_COST = 2  # Energy cost of using the undo feature (U key)
              # Undoing a move costs 2 energy to prevent abuse
              # This makes players think before moving instead of just undoing mistakes

# ============================================================================
# PLAYER SETTINGS
# ============================================================================

INITIAL_ENERGY = 1000  # Starting energy for the player
                      # Each move costs energy based on terrain
                      # Game ends if energy reaches 0 before reaching goal
                      # Higher value = easier game, lower value = harder game

ENABLE_DIAGONALS = False  # Whether players can move diagonally
                         # False = Only 4-directional movement (up, down, left, right)
                         # True = 8-directional movement (includes diagonals)
                         # Currently disabled for simpler gameplay

# ============================================================================
# FONT SETTINGS
# ============================================================================
# Font sizes for different UI elements (in pixels)

FONT_SIZE_SMALL = 16   # Small text (stats, controls list, etc.)
FONT_SIZE_MEDIUM = 20  # Medium text (section headers, important info)
FONT_SIZE_LARGE = 24   # Large text (titles, main headings)

# ============================================================================
# DEBUG SETTINGS
# ============================================================================

DEBUG_MODE = False  # Enable/disable debug output
                   # True = Prints debug information to console (useful for development)
                   # False = No debug output (cleaner for normal gameplay)
                   # Debug info includes: pathfinding details, obstacle changes, AI decisions, etc.

