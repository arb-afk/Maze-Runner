# Data Structures Used in MazeRunner

This document provides a comprehensive breakdown of all data structures used throughout the MazeRunner codebase, organized by category and usage context.

## Table of Contents
1. [Built-in Python Data Structures](#built-in-python-data-structures)
2. [Collections Module Data Structures](#collections-module-data-structures)
3. [Custom Classes/Structures](#custom-classesstructures)
4. [Configuration Data Structures](#configuration-data-structures)
5. [Usage by Component](#usage-by-component)

---

## Built-in Python Data Structures

### 1. **Lists (`list`)**

Lists are used extensively for ordered sequences of data:

#### **Path Storage**
- **`Player.path`**: `List[Tuple[int, int]]` - Ordered sequence of all positions visited by player
- **`AIAgent.path`**: `List[Tuple[int, int]]` - Planned path from current position to goal
- **`PathfindingResult.path`**: `List[Tuple[int, int]]` - Calculated path from start to goal
- **`Maze.checkpoints`**: `List[Tuple[int, int]]` - Ordered list of checkpoint positions

#### **Move History**
- **`Player.move_history`**: `List[Dict]` - History of all player moves for undo functionality
  - Each entry: `{'old_pos': (x, y), 'new_pos': (x, y), 'cost': float, 'total_cost_before': float, 'checkpoint_reached': bool}`
- **`AIAgent.move_history`**: `List[Dict]` - History of all AI moves (same structure as player)

#### **Checkpoint Tracking**
- **`Player.reached_checkpoints`**: `List[Tuple[int, int]]` - Checkpoints reached in order
- **`AIAgent.reached_checkpoints`**: `List[Tuple[int, int]]` - Checkpoints reached by AI in order
- **`AIAgent.recent_positions`**: `List[Tuple[int, int]]` - Recent positions for revisit penalty (max 10 entries)

#### **Maze Generation**
- **`stack`** (in `Maze.initialize_maze()`): `List[Tuple[int, int]]` - Stack for recursive backtracking algorithm
- **`path_cells`** (in checkpoint placement): `List[Tuple[int, int]]` - Valid cells for checkpoint placement

#### **UI Elements**
- **`UI.menu_buttons`**: `List[Dict]` - Menu button rectangles for click detection
  - Each entry: `{'rect': pygame.Rect, 'mode': str, 'mode_key': str}`
- **`modes`** (in UI): `List[Dict]` - Game mode definitions for menu
  - Each entry: `{'name': str, 'key': str, 'color': Tuple[int, int, int], 'description': str}`

#### **Algorithm Permutations**
- **`itertools.permutations(checkpoints)`**: Used in Multi-Objective Search to try all checkpoint orderings

### 2. **Dictionaries (`dict`)**

Dictionaries provide O(1) key-value lookups for mappings:

#### **Maze Structure**
- **`Maze.terrain`**: `Dict[Tuple[int, int], str]` - Maps cell position to terrain type
  - Keys: `(x, y)` coordinates
  - Values: `'GRASS'`, `'WATER'`, `'MUD'`, `'SPIKES'`, `'THORNS'`, `'QUICKSAND'`, `'ROCKS'`, `'REWARD'`, `'LAVA'`
- **`Maze.walls`**: `Dict[Tuple[int, int, str], bool]` - Maps wall position and direction to open/closed state
  - Keys: `(x, y, direction)` where direction is `'N'`, `'E'`, `'S'`, `'W'`
  - Values: `True` if wall is open (passable), `False` if closed (impassable)

#### **Pathfinding State**
- **`came_from`**: `Dict[Tuple[int, int], Tuple[int, int]]` - Maps each node to its predecessor (for path reconstruction)
- **`cost_so_far`**: `Dict[Tuple[int, int], float]` - Maps node to cheapest cost to reach it (Dijkstra)
- **`g_score`**: `Dict[Tuple[int, int], float]` - Maps node to actual cost from start (A*)
- **`f_score`**: `Dict[Tuple[int, int], float]` - Maps node to total estimated cost (A*)
- **`g_forward`**, **`g_backward`**: `Dict[Tuple[int, int], float]` - Cost dictionaries for bidirectional search

#### **Pathfinding Results**
- **`PathfindingResult.node_data`**: `Dict[Tuple[int, int], Dict[str, Any]]` - Stores f, g, h values per node
  - Keys: `(x, y)` position
  - Values: `{'g': float, 'h': float, 'f': float}`

#### **Fog of War Memory**
- **`AIAgent.memory_map`**: `Dict[Tuple[int, int], str]` - Stores terrain type for cells AI has seen
  - Keys: `(x, y)` position
  - Values: Terrain type string

#### **Configuration**
- **`TERRAIN_COSTS`**: `Dict[str, float]` - Maps terrain type to movement cost
- **`COLORS`**: `Dict[str, Tuple[int, int, int]]` - Maps color name to RGB tuple
- **`AI_HEURISTIC_SCALE`**: `Dict[str, float]` - Maps difficulty level to heuristic scaling factor

#### **Algorithm Comparison Cache**
- **`GameState.algorithm_results_cache`**: `Dict[str, Dict]` - Cached algorithm comparison results
  - Keys: Algorithm name (`'BFS'`, `'Dijkstra'`, `'A*'`, etc.)
  - Values: `{'nodes': int, 'cost': float, 'time': float, 'steps': int}`

### 3. **Sets (`set`)**

Sets provide O(1) membership testing and eliminate duplicates:

#### **Visited Cells Tracking**
- **`Player.visited_cells`**: `Set[Tuple[int, int]]` - All cells player has visited (for quick lookup)
- **`AIAgent.visited_cells`**: `Set[Tuple[int, int]]` - All cells AI has visited
- **`PathfindingResult.explored_nodes`**: `Set[Tuple[int, int]]` - Nodes explored during pathfinding
- **`PathfindingResult.frontier_nodes`**: `Set[Tuple[int, int]]` - Nodes currently on frontier

#### **Fog of War**
- **`GameState.player_discovered_cells`**: `Set[Tuple[int, int]]` - Cells player has seen
- **`GameState.ai_discovered_cells`**: `Set[Tuple[int, int]]` - Cells AI has seen
- **`discovered_cells`** (parameter): `Optional[Set[Tuple[int, int]]]` - Cells visible to pathfinding algorithm

#### **Obstacles**
- **`Maze.dynamic_obstacles`**: `Set[Tuple[int, int]]` - Positions of lava obstacles (impassable)

#### **Rewards**
- **`Player.collected_rewards`**: `Set[Tuple[int, int]]` - Reward cell positions collected by player
- **`AIAgent.collected_rewards`**: `Set[Tuple[int, int]]` - Reward cell positions collected by AI

#### **Maze Generation**
- **`visited`** (in recursive backtracking): `Set[Tuple[int, int]]` - Cells visited during maze generation

#### **Cache Keys**
- **`frozenset(discovered_cells)`**: Used as hashable key component in pathfinding cache

### 4. **Tuples (`tuple`)**

Tuples are used for immutable coordinate pairs and fixed-size data:

#### **Coordinates**
- **`(x, y)`**: Standard coordinate representation throughout the codebase
- **`start_pos`**: `Tuple[int, int]` - Starting position
- **`goal_pos`**: `Tuple[int, int]` - Goal position
- **`checkpoint`**: `Tuple[int, int]` - Checkpoint position

#### **Cache Keys**
- **`(start, goal, algorithm, dc_hash)`**: Cache key tuple for pathfinding results
  - `start`: `Tuple[int, int]`
  - `goal`: `Tuple[int, int]`
  - `algorithm`: `str`
  - `dc_hash`: `int` (hash of discovered cells set)

#### **Colors**
- **RGB tuples**: `Tuple[int, int, int]` - Color values (0-255 for each component)
  - Example: `(255, 0, 0)` for red

### 5. **2D Lists (Nested Lists)**

#### **Maze Grid**
- **`Maze.cells`**: `List[List[int]]` - 2D grid representing maze structure
  - `0` = wall (impassable)
  - `1` = path (passable)
  - Dimensions: `height × width` (rows × columns)

---

## Collections Module Data Structures

### 1. **`collections.deque` (Double-Ended Queue)**

Used for BFS (Breadth-First Search) algorithm:

- **`queue`** (in `Pathfinder.bfs()`): `deque[Tuple[int, int]]` - FIFO queue for BFS
  - Operations: `deque.popleft()` for O(1) removal from front
  - Used because BFS requires FIFO ordering (first in, first out)

### 2. **`collections.OrderedDict` (Ordered Dictionary)**

Used for LRU (Least Recently Used) cache:

- **`Pathfinder._path_cache`**: `OrderedDict[Tuple, PathfindingResult]` - LRU cache for pathfinding results
  - Keys: `(start, goal, algorithm, discovered_cells_hash)` tuple
  - Values: `PathfindingResult` objects
  - Operations:
    - `move_to_end(key)`: Move accessed item to end (most recently used)
    - `popitem(last=False)`: Remove oldest item (least recently used)
  - Max size: 100 entries (prevents memory issues)

### 3. **`heapq` (Heap Queue / Priority Queue)**

Used for Dijkstra's and A* algorithms:

- **Priority Queue**: `List[Tuple[float, Tuple[int, int]]]` - Min-heap for Dijkstra/A*
  - Structure: `[(cost, position), ...]` or `[(f_score, position), ...]`
  - Operations:
    - `heapq.heappush(pq, (cost, node))`: Add item with O(log n) complexity
    - `heapq.heappop(pq)`: Remove minimum item with O(log n) complexity
  - Used in:
    - `Pathfinder.dijkstra()`: Priority queue ordered by cost from start
    - `Pathfinder.a_star()`: Priority queue ordered by f_score (g + h)
    - `Pathfinder.bidirectional_a_star()`: Two priority queues (forward and backward)
    - `Pathfinder.modified_a_star_fog_of_war()`: Priority queue with exploration heuristic

---

## Custom Classes/Structures

### 1. **`PathfindingResult` Class**

Container for pathfinding algorithm results:

```python
class PathfindingResult:
    path: List[Tuple[int, int]]           # Calculated path sequence
    cost: float                           # Total path cost (inf if no path)
    nodes_explored: int                   # Count of explored nodes
    explored_nodes: Set[Tuple[int, int]]  # Set of explored positions
    frontier_nodes: Set[Tuple[int, int]]  # Set of frontier positions
    path_found: bool                      # Success flag
    node_data: Dict[Tuple[int, int], Dict[str, Any]]  # f, g, h values per node
```

### 2. **`Maze` Class**

Represents the game environment:

```python
class Maze:
    # Dimensions
    width: int
    height: int
    
    # Grid structure
    cells: List[List[int]]                    # 2D grid (0=wall, 1=path)
    walls: Dict[Tuple[int, int, str], bool]   # Wall connections
    terrain: Dict[Tuple[int, int], str]       # Terrain type per cell
    
    # Special positions
    start_pos: Tuple[int, int]
    goal_pos: Tuple[int, int]
    checkpoints: List[Tuple[int, int]]
    
    # Obstacles
    dynamic_obstacles: Set[Tuple[int, int]]
    
    # Obstacle system
    obstacle_seed: int
    obstacle_rng: random.Random
    turn_number: int
```

### 3. **`Player` Class**

Represents the human player:

```python
class Player:
    # Position
    x: int
    y: int
    
    # Path tracking
    path: List[Tuple[int, int]]
    visited_cells: Set[Tuple[int, int]]
    
    # Cost/Energy
    total_cost: float
    energy: float
    
    # Checkpoints
    reached_checkpoints: List[Tuple[int, int]]
    
    # Move history
    move_history: List[Dict]
    
    # Rewards
    collected_rewards: Set[Tuple[int, int]]
    reward_active: bool
    reward_moves_left: int
```

### 4. **`AIAgent` Class**

Represents the AI opponent:

```python
class AIAgent:
    # Position
    x: int
    y: int
    
    # Path planning
    path: List[Tuple[int, int]]
    current_path_index: int
    path_result: PathfindingResult
    
    # Cost tracking
    total_cost: float
    
    # Checkpoints
    reached_checkpoints: List[Tuple[int, int]]
    
    # Visited cells
    visited_cells: Set[Tuple[int, int]]
    
    # Move history
    move_history: List[Dict]
    
    # Rewards
    collected_rewards: Set[Tuple[int, int]]
    reward_active: bool
    reward_moves_left: int
    
    # Fog of war memory
    memory_map: Dict[Tuple[int, int], str]
    recent_positions: List[Tuple[int, int]]
    max_recent_positions: int
```

### 5. **`Pathfinder` Class**

Container for pathfinding algorithms:

```python
class Pathfinder:
    maze: Maze
    heuristic_type: str
    _path_cache: OrderedDict[Tuple, PathfindingResult]
    _cache_max_size: int
```

### 6. **`GameState` Class**

Manages game state:

```python
class GameState:
    # Game mode
    mode: str
    
    # Game objects
    maze: Maze
    player: Player
    ai_agent: AIAgent
    ai_pathfinder: Pathfinder
    
    # Game status
    game_over: bool
    winner: str
    message: str
    
    # Turn-based
    turn: str
    
    # UI features
    algorithm_comparison: bool
    show_hints: bool
    show_exploration: bool
    
    # Algorithm selection
    algorithm_results_cache: Dict[str, Dict]
    selected_algorithm: str
    
    # Fog of war
    fog_of_war_enabled: bool
    player_visibility_radius: int
    ai_visibility_radius: int
    player_discovered_cells: Set[Tuple[int, int]]
    ai_discovered_cells: Set[Tuple[int, int]]
```

### 7. **`UI` Class**

Handles rendering:

```python
class UI:
    screen: pygame.Surface
    ui_panel_x: int
    ui_panel_width: int
    ui_panel_height: int
    menu_buttons: List[Dict]
```

### 8. **`Game` Class**

Main game controller:

```python
class Game:
    screen: pygame.Surface
    clock: pygame.time.Clock
    running: bool
    in_menu: bool
    game_state: GameState
    ui: UI
    maze_offset_x: int
    maze_offset_y: int
    scroll_offset: int
    max_scroll: int
```

---

## Configuration Data Structures

### 1. **`TERRAIN_COSTS` Dictionary**

```python
TERRAIN_COSTS: Dict[str, float] = {
    'PATH': 1,
    'GRASS': 1,
    'WATER': 3,
    'MUD': 5,
    'LAVA': float('inf'),
    'WALL': float('inf'),
    'START': 0,
    'GOAL': 0,
    'CHECKPOINT': 0,
    'SPIKES': 4,
    'THORNS': 3,
    'QUICKSAND': 6,
    'ROCKS': 2,
    'REWARD': 0
}
```

### 2. **`COLORS` Dictionary**

```python
COLORS: Dict[str, Tuple[int, int, int]] = {
    'GRASS': (102, 187, 106),
    'WATER': (66, 165, 245),
    'MUD': (141, 110, 99),
    'LAVA': (239, 83, 80),
    'WALL': (45, 45, 48),
    'START': (139, 195, 74),
    'GOAL': (255, 214, 0),
    'CHECKPOINT': (255, 167, 38),
    'PLAYER': (240, 98, 146),
    'AI': (171, 71, 188),
    # ... many more color definitions
}
```

### 3. **`AI_HEURISTIC_SCALE` Dictionary**

```python
AI_HEURISTIC_SCALE: Dict[str, float] = {
    'EASY': 0.7,
    'MEDIUM': 1.0,
    'HARD': 1.5
}
```

### 4. **`AVAILABLE_ALGORITHMS` List**

```python
AVAILABLE_ALGORITHMS: List[str] = [
    'BFS',
    'DIJKSTRA',
    'ASTAR',
    'BIDIRECTIONAL_ASTAR'
]
```

---

## Usage by Component

### **Pathfinding Algorithms**

1. **BFS**: Uses `deque` for FIFO queue
2. **Dijkstra**: Uses `heapq` (priority queue) + `dict` for cost tracking
3. **A***: Uses `heapq` (priority queue) + `dict` for g_score/f_score tracking
4. **Bidirectional A***: Uses two `heapq` priority queues (forward/backward)
5. **Multi-Objective**: Uses `itertools.permutations()` + multiple A* calls
6. **Modified A* (Fog)**: Uses `heapq` + `dict` for memory map

### **Maze Generation**

- **Recursive Backtracking**: Uses `list` (stack) + `set` (visited cells)
- **Terrain Assignment**: Uses `dict` for terrain mapping
- **Wall Tracking**: Uses `dict` with tuple keys `(x, y, direction)`

### **Game State Management**

- **Checkpoint Ordering**: Uses `list` to maintain order
- **Fog of War**: Uses `set` for discovered cells
- **Algorithm Cache**: Uses `OrderedDict` for LRU caching

### **Player/AI Tracking**

- **Path History**: Uses `list` to maintain order
- **Visited Cells**: Uses `set` for O(1) membership testing
- **Move History**: Uses `list` of dictionaries for undo functionality

---

## Performance Characteristics

### **Time Complexities**

- **List operations**:
  - Append: O(1) amortized
  - Index access: O(1)
  - Membership test: O(n)
  - Insert/Delete: O(n)

- **Dictionary operations**:
  - Get/Set: O(1) average case
  - Membership test: O(1) average case

- **Set operations**:
  - Add/Remove: O(1) average case
  - Membership test: O(1) average case

- **Deque operations**:
  - `popleft()`: O(1)
  - `append()`: O(1)

- **Heapq operations**:
  - `heappush()`: O(log n)
  - `heappop()`: O(log n)

- **OrderedDict operations**:
  - `move_to_end()`: O(1)
  - `popitem()`: O(1)

### **Space Complexities**

- **Maze grid**: O(width × height)
- **Terrain dictionary**: O(number of assigned terrain cells)
- **Pathfinding cache**: O(100) - limited by `_cache_max_size`
- **Visited cells sets**: O(number of visited cells)
- **Path lists**: O(path length)

---

## Summary

MazeRunner uses a combination of:
- **Lists** for ordered sequences (paths, history, checkpoints)
- **Dictionaries** for key-value mappings (terrain, costs, state tracking)
- **Sets** for fast membership testing (visited cells, discovered cells)
- **Tuples** for immutable coordinate pairs
- **2D Lists** for grid representation
- **`deque`** for BFS queue
- **`heapq`** for priority queues in Dijkstra/A*
- **`OrderedDict`** for LRU cache
- **Custom classes** for structured data (PathfindingResult, Maze, Player, AIAgent)

The choice of data structures optimizes for:
- **Fast lookups**: Dictionaries and sets for O(1) access
- **Order preservation**: Lists for paths and checkpoints
- **Priority ordering**: Heap queues for pathfinding algorithms
- **Memory efficiency**: LRU cache with size limits
- **Algorithm requirements**: Appropriate structures for each algorithm (FIFO for BFS, priority queue for Dijkstra/A*)

