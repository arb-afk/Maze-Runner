# MazeRunner X — The Intelligent Shortest Path Challenge

A strategic puzzle game where perfect mazes evolve dynamically and multiple pathfinding challenges coexist. Navigate through weighted terrain within wall-based mazes, avoid obstacles, and race against an AI opponent using advanced pathfinding algorithms.

## Features

### 🎮 Game Modes
- **Explore Mode**: Static perfect maze - perfect for learning the mechanics
- **Dynamic Mode**: Walls and obstacles dynamically change - test your adaptability  
- **Multi-Goal Mode**: Visit multiple checkpoints before reaching the goal
- **AI Duel Mode**: Turn-based race against an AI opponent to reach the goal first

### 🧠 AI Features
- **Adaptive Pathfinding**: AI automatically recomputes optimal path when environment changes
- **Heuristic Visualization**: Real-time display of f, g, and h values on frontier nodes
- **Competitive Turn-Based Mode**: Player and AI alternate turns in AI Duel mode
- **Hint System**: Toggle hints to see AI's suggestion for next best move (press H)

### 🎯 Terrain System
The maze consists of:
- **Perfect Maze Structure**: Generated using recursive backtracking algorithm with walls and paths
- **Weighted Terrain Types** (on paths):
  - 🟩 **Grass** (Cost: 1) - Fast, easy terrain (70% of paths)
  - 🟦 **Water** (Cost: 3) - Slower movement (20% of paths)
  - 🟫 **Mud** (Cost: 5) - Very slow movement (10% of paths)
- **Dynamic Obstacles**: Walls can appear/disappear in Dynamic mode
- **Special Cells**:
  - 🟢 **Start** - Beginning point (green)
  - 🟡 **Goal** - Target destination (gold, pulsing animation)
  - 🟠 **Checkpoints** - Required visits in Multi-Goal mode (orange stars)

### 🔍 Pathfinding Algorithms
- **Dijkstra's Algorithm**: Guaranteed optimal path in static mazes
- **A* Algorithm**: Faster heuristic-driven search with Manhattan/Euclidean distance
- **Bidirectional A***: Advanced variant for even faster searches
- **Visualization**: See explored nodes (pink), frontier nodes (blue), and heuristic values

### 🎨 Visual Features
- **Modern UI**: Clean interface with color-coded stats and energy bar
- **Exploration Visualization**: Watch AI's search process in real-time
- **Terrain Cost Display**: See movement costs on each cell
- **Animated Elements**: Pulsing goals, glowing effects, and smooth animations

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd MazeRunner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python main.py
```

## Controls

### Movement
- **Arrow Keys** or **WASD**: Move player

### Game Management
- **R**: Reset current game (keeps mode and settings)
- **G**: Generate new maze
- **ESC**: Quit game

### Mode Selection
- **1**: Switch to Explore Mode
- **2**: Switch to Dynamic Mode
- **3**: Switch to Multi-Goal Mode
- **4**: Switch to AI Duel Mode

### Extensions & Features
- **H**: Toggle hints (shows next best move)
- **F**: Toggle Fog of War (limited visibility mode)
- **C**: Toggle Algorithm Comparison Dashboard

## Game Rules

1. **Maze Structure**: Navigate through a perfect maze with walls and corridors
2. **Terrain Costs**: Each path cell has a movement cost (displayed as numbers)
   - Minimize total cost by choosing optimal routes
3. **Start to Goal**: Navigate from Start (green) to Goal (gold)
4. **Energy System**: Player has limited energy (1000 points) based on movement costs
5. **Dynamic Mode**: Walls can appear/disappear randomly, obstacles spawn/despawn
6. **Multi-Goal Mode**: Must visit all checkpoints (orange stars) before reaching goal
7. **AI Duel Mode**: 
   - Turn-based gameplay: Player moves, then AI moves
   - First to reach the goal wins
   - AI uses A* pathfinding with adaptive replanning

## Game Modes Explained

### Explore Mode
Perfect for beginners. Navigate through a static perfect maze with no dynamic changes. Learn the terrain costs, understand the maze structure, and plan your optimal path without time pressure.

### Dynamic Mode
The maze comes alive! Walls can dynamically convert to paths and vice versa, obstacles spawn and despawn randomly. Your path might get blocked, requiring quick replanning. This mode tests your adaptability and real-time decision-making.

### Multi-Goal Mode
Before reaching the final goal, you must visit all checkpoints on the map. This adds strategic complexity - you need to find the optimal order to visit checkpoints while minimizing total path cost. Checkpoints are marked with orange stars.

### AI Duel Mode
Compete against an AI opponent in turn-based gameplay. Watch as the AI:
- Uses A* pathfinding to find optimal routes
- Visually explores nodes (you'll see pink explored nodes and blue frontier nodes)
- Displays heuristic values (f, g, h) on frontier nodes
- Automatically replans when obstacles block its path

The AI moves after each of your moves. First to reach the goal wins!

## Technical Details

### Maze Generation
- **Algorithm**: Recursive backtracking (perfect maze generation)
- **Structure**: Walls (dark) and paths (terrain-colored) with proper connectivity
- **Size**: 31x23 grid (odd dimensions for proper maze generation)

### Pathfinding Algorithms

#### Dijkstra's Algorithm
- Explores nodes in order of increasing distance from start
- Guaranteed to find optimal path
- Useful for static mazes

#### A* Algorithm
- Uses heuristic function (Manhattan or Euclidean distance) to guide search
- Faster than Dijkstra's by prioritizing promising directions
- Still finds optimal path if heuristic is admissible
- Shows f, g, h values for visualization:
  - **f** = total estimated cost (g + h)
  - **g** = actual cost from start
  - **h** = heuristic estimate to goal

#### Bidirectional A*
- Searches from both start and goal simultaneously
- Faster convergence for large mazes
- Advanced optimization technique

### Visualization
The game provides rich visual feedback:
- **Explored Nodes**: Light pink overlay showing where AI has searched
- **Frontier Nodes**: Light blue overlay showing nodes being considered
- **Heuristic Values**: f, g, h displayed on frontier nodes (AI Duel mode)
- **Path Visualization**: Yellow semi-transparent lines show AI's planned route
- **Terrain Colors**: Instant recognition of terrain types
- **Cost Display**: Numbers on cells show movement cost

### Dynamic Systems

#### Adaptive Pathfinding
- AI continuously checks if its path is blocked
- Automatically recomputes optimal path when obstacles appear
- Works seamlessly in Dynamic and AI Duel modes

#### Dynamic Walls
- In Dynamic mode, some walls can convert to paths (opening new routes)
- Paths can convert to walls (creating obstacles)
- Core maze structure remains intact
- Low probability changes prevent chaos

## Extensions (Implemented)

### ✅ Fog of War (Press F)
- Limited visibility radius (3 cells)
- Only see nearby cells and previously discovered areas
- Adds exploration challenge
- Dark fog covers unexplored regions

### ✅ Algorithm Comparison Dashboard (Press C)
- Compare Dijkstra vs A* performance
- Shows: nodes explored, path cost, execution time
- Real-time benchmarking
- Cached results for performance

### ✅ Energy System
- Player starts with 1000 energy points
- Movement costs reduce energy
- Visual energy bar with color coding (green → red)
- Game over if energy depletes

### ✅ Hint System (Press H)
- Toggle on/off with H key
- AI calculates optimal next move using A*
- Visual indicator: pulsing golden circle with arrow
- Adapts to Multi-Goal mode (guides to next checkpoint)
- Status shown in Extensions panel

## Project Structure

```
MazeRunner/
├── main.py          # Main game loop and entry point
├── config.py        # Game configuration and constants
├── maze.py          # Perfect maze generation and terrain management
├── player.py        # Player and AI agent classes
├── pathfinding.py   # Pathfinding algorithms (Dijkstra, A*, Bidirectional)
├── game_modes.py    # Game mode management and state
├── ui.py            # UI and visualization components
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## Configuration

Key settings in `config.py`:
- `MAZE_WIDTH`, `MAZE_HEIGHT`: Maze dimensions (must be odd numbers)
- `CELL_SIZE`: Size of each cell in pixels
- `FPS`: Game frame rate
- `INITIAL_ENERGY`: Starting energy for player
- `TURN_BASED`: Enable turn-based mode in AI Duel
- `FOG_OF_WAR_RADIUS`: Visibility range in Fog of War mode
- `OBSTACLE_SPAWN_RATE`: Probability of obstacles spawning
- `HEURISTIC_TYPE`: 'MANHATTAN' or 'EUCLIDEAN' for A*

## Requirements

- Python 3.7+
- pygame 2.5.0+

## Tips & Strategies

1. **Terrain Optimization**: Plan routes to minimize expensive terrain (mud, water)
2. **Checkpoint Ordering**: In Multi-Goal mode, visiting checkpoints in optimal order saves energy
3. **Dynamic Mode**: Be flexible - your path might get blocked, always have a backup plan
4. **AI Duel**: Watch the AI's exploration to learn optimal paths
5. **Hint System**: Use hints when stuck, but try to solve without them first
6. **Energy Management**: In long paths, conserve energy by choosing cheaper terrain
7. **Heuristic Learning**: Observe f, g, h values in AI Duel mode to understand pathfinding

## Future Enhancements

Potential additions:
- Energy power-ups (cells that restore energy)
- Multi-Agent Mode (multiple AIs competing)
- Time attack mode (speed challenges)
- Custom maze editor
- Save/Load game states
- Leaderboard system
- Different maze generation algorithms

## License

This project is created for educational purposes as part of the MazeRunner X challenge.

## Credits

Developed for the Intelligent Shortest Path Challenge project.

---

**Enjoy navigating the mazes and competing with AI! Good luck finding the optimal paths!** 🎮✨
