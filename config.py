"""
Configuration file for MazeRunner X
Contains constants, colors, and game settings
"""

# Window settings
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1000
CELL_SIZE = 30
GRID_PADDING = 250  # Space for UI on the right

# Colors - Modern, vibrant palette
COLORS = {
    'GRASS': (76, 175, 80),           # Material Green
    'GRASS_DARK': (56, 142, 60),      # Darker green for depth
    'WATER': (33, 150, 243),          # Material Blue
    'WATER_DARK': (25, 118, 210),     # Darker blue
    'MUD': (121, 85, 72),             # Material Brown
    'MUD_DARK': (93, 64, 55),         # Darker brown
    'LAVA': (244, 67, 54),            # Material Red
    'LAVA_DARK': (198, 40, 40),       # Darker red
    'LAVA_GLOW': (255, 152, 0),       # Orange glow
    'WALL': (35, 35, 35),             # Very dark gray for walls (distinct from lava)
    'WALL_LIGHT': (60, 60, 60),       # Lighter gray for wall highlights
    'PATH': (255, 255, 255),          # White paths
    'START': (139, 195, 74),          # Light Green
    'START_DARK': (104, 159, 56),     # Darker green
    'GOAL': (255, 193, 7),            # Amber
    'GOAL_DARK': (255, 160, 0),       # Darker amber
    'GOAL_GLOW': (255, 235, 59),      # Yellow glow
    'CHECKPOINT': (255, 152, 0),      # Orange
    'CHECKPOINT_DARK': (245, 124, 0), # Darker orange
    'PLAYER': (236, 64, 122),         # Pink
    'PLAYER_OUTLINE': (194, 24, 91),  # Dark pink
    'AI': (156, 39, 176),             # Purple
    'AI_OUTLINE': (123, 31, 162),     # Dark purple
    'PATH': (255, 235, 59),           # Bright yellow
    'PATH_DARK': (251, 192, 45),      # Darker yellow
    'EXPLORED': (244, 143, 177),      # Light pink with alpha
    'FRONTIER': (144, 202, 249),      # Light blue with alpha
    'BACKGROUND': (250, 250, 250),    # Off-white
    'UI_BG': (245, 245, 245),         # Light gray
    'UI_PANEL': (255, 255, 255),      # White panel
    'UI_BORDER': (224, 224, 224),     # Light border
    'TEXT': (33, 33, 33),             # Dark gray text
    'TEXT_SECONDARY': (117, 117, 117), # Secondary text
    'FOG': (33, 33, 33),              # Dark fog of war
    'ENERGY_BAR': (76, 175, 80),      # Green energy
    'ENERGY_BAR_LOW': (244, 67, 54),  # Red energy
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
}

# Game settings
FPS = 60
MAZE_WIDTH = 31  # Use odd number for proper maze generation
MAZE_HEIGHT = 23  # Use odd number for proper maze generation
OBSTACLE_SPAWN_RATE = 0.15  # Probability of obstacle appearing (increased for visibility)
OBSTACLE_DESPAWN_RATE = 0.20  # Probability of obstacle disappearing (increased for visibility)

# AI settings
AI_SPEED = 0.5  # Moves every N seconds (for non-turn-based)
HEURISTIC_TYPE = 'MANHATTAN'  # MANHATTAN or EUCLIDEAN
TURN_BASED = True  # Turn-based mode for AI Duel

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

# Extensions
FOG_OF_WAR_ENABLED = False
FOG_OF_WAR_RADIUS = 3  # Visibility radius
ALGORITHM_COMPARISON = False  # Show algorithm comparison dashboard

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

