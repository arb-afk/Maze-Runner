"""
Configuration file for MazeRunner X
Contains constants, colors, and game settings
"""

# Window settings
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1000
CELL_SIZE = 30
GRID_PADDING = 250  # Space for UI on the right

# Colors - Modern, vibrant palette with improved aesthetics
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

# Terrain costs
TERRAIN_COSTS = {
    'PATH': 1,
    'GRASS': 1,
    'WATER': 3,
    'MUD': 5,
    'LAVA': float('inf'),  # Impassable
    'WALL': float('inf'),  # Impassable wall
    'START': 0,
    'GOAL': 0,
    'CHECKPOINT': 0,
    # New obstacle types for Dynamic mode
    'SPIKES': 4,      # Sharp spikes - moderate cost
    'THORNS': 3,      # Thorny bushes - light cost
    'QUICKSAND': 6,   # Quicksand - high cost
    'ROCKS': 2,       # Rocky terrain - low cost
    # Reward cells - reduce cost temporarily
    'REWARD': 0,      # Free to traverse, gives bonus
}

# Reward settings
REWARD_BONUS = -2  # Cost reduction when collecting reward (negative = bonus)
REWARD_DURATION = 5  # Number of moves the reward effect lasts
REWARD_SPAWN_RATE = 0.03  # 3% of cells spawn as rewards

# Dynamic obstacles (for Obstacle Course mode)
DYNAMIC_OBSTACLE_CHANGE_PER_TURN = 2  # Number of obstacles to add/remove per turn
DYNAMIC_OBSTACLE_MAX_CHANGES = 3  # Maximum total changes (adds + removes) per turn

# Game settings
FPS = 60
MAZE_WIDTH = 31  # Use odd number for proper maze generation
MAZE_HEIGHT = 23  # Use odd number for proper maze generation

# AI settings
AI_SPEED = 0.5  # Moves every N seconds (for non-turn-based)
HEURISTIC_TYPE = 'MANHATTAN'  # MANHATTAN or EUCLIDEAN
TURN_BASED = True  # Turn-based mode for AI Duel

# AI Difficulty settings
AI_DIFFICULTY = 'MEDIUM'  # Options: 'EASY', 'MEDIUM', 'HARD'
# EASY: Uses MANHATTAN heuristic with 0.7 scaling (more predictable, suboptimal)
# MEDIUM: Uses MANHATTAN heuristic with 1.0 scaling (balanced)
# HARD: Uses EUCLIDEAN heuristic with 1.5 scaling (more optimal, aggressive)
AI_HEURISTIC_SCALE = {
    'EASY': 0.7,
    'MEDIUM': 1.0,
    'HARD': 1.5
}

# Algorithm selection
# Options: 'DIJKSTRA', 'ASTAR', 'BIDIRECTIONAL_ASTAR', 'DSTAR', 'MULTI_OBJECTIVE'
# - DIJKSTRA: Optimal for static mazes (guaranteed shortest path)
# - ASTAR: Faster heuristic-driven search (Manhattan/Euclidean)
# - BIDIRECTIONAL_ASTAR: Searches from both ends for speed
# - DSTAR: Dynamic A* for moving obstacles (adaptive replanning)
# - MULTI_OBJECTIVE: For multiple goals/checkpoints
AI_ALGORITHM = 'ASTAR'  # Default algorithm for AI
# Algorithm auto-selection:
# - Uses DSTAR in Dynamic mode (for moving obstacles)
# - Uses MULTI_OBJECTIVE in Multi-Goal/Checkpoint modes
# - Uses ASTAR or DIJKSTRA otherwise

# Available algorithms for user selection
AVAILABLE_ALGORITHMS = ['BFS', 'DIJKSTRA', 'ASTAR', 'BIDIRECTIONAL_ASTAR']

# Extensions
FOG_OF_WAR_RADIUS = 3  # Fallback visibility radius (actual radius set per mode in game_modes.py)

# Gameplay settings
PREVENT_PATH_REVISITING = False  # Allow revisiting cells (set to False to ensure checkpoint accessibility)
UNDO_COST = 2  # Cost of using undo (deducted from energy)

# Player settings
INITIAL_ENERGY = 1000
ENABLE_DIAGONALS = False

# Font settings
FONT_SIZE_SMALL = 16
FONT_SIZE_MEDIUM = 20
FONT_SIZE_LARGE = 24

# Debug settings
DEBUG_MODE = False  # Set to True to enable debug print statements

