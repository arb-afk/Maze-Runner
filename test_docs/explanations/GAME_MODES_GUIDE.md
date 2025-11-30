# Game Modes Guide

This document explains how each game mode works, including their objectives, mechanics, and important implementation details.

---

## Table of Contents

1. [Explore Mode](#1-explore-mode)
2. [Obstacle Course Mode](#2-obstacle-course-mode)
3. [Multi-Goal Mode](#3-multi-goal-mode)
4. [AI Duel Mode](#4-ai-duel-mode)
5. [Blind Duel Mode](#5-blind-duel-mode)

---

## 1. Explore Mode

### Overview
**Explore Mode** is the simplest game mode, designed for beginners to learn the game mechanics and pathfinding algorithms.

### Objectives
- Navigate from the start position to the goal position
- Learn terrain costs and optimal path planning
- Observe AI algorithm visualization (AI doesn't compete)

### Key Features
- **Static Maze**: The maze layout never changes during gameplay
- **No Time Pressure**: Take your time to plan and learn
- **AI Visualization**: Watch how different algorithms explore the maze
- **All Terrain Types**: Includes grass, water, mud, and obstacles (but obstacles are static)

### Algorithm Used
- Uses the **selected algorithm** (default: A*) for AI visualization
- AI path is computed once at the start and displayed for educational purposes
- Algorithm can be cycled with `[` and `]` keys to compare different approaches

### Implementation Details
- Maze is generated once using recursive backtracking
- Terrain is assigned statically (no changes during gameplay)
- Lava obstacles spawn at 4% rate (impassable)
- Rewards spawn at 3% rate (provide temporary cost reduction bonuses)
- AI agent computes path once for visualization only

---

## 2. Obstacle Course Mode

### Overview
**Obstacle Course Mode** introduces dynamic obstacles that change each turn, requiring strategic planning and predictive pathfinding.

### Objectives
- Navigate through obstacles while minimizing total movement cost
- Plan ahead for obstacle changes
- Optimize path considering future terrain states

### Key Features
- **Dynamic Obstacles**: Obstacles (spikes, thorns, quicksand, rocks) change each turn
- **Deterministic Changes**: Obstacle changes are predictable (same seed = same changes)
- **Predictive Pathfinding**: AI uses predictive algorithm to account for future obstacles
- **Weighted Terrain**: Different obstacles have different costs:
  - **Spikes**: 4 energy
  - **Thorns**: 3 energy
  - **Quicksand**: 6 energy
  - **Rocks**: 2 energy

### Algorithm Used
- Uses **predictive pathfinding** wrapper around base algorithm (A*, Dijkstra, BFS, or Bidirectional A*)
- Base algorithm finds initial path with current obstacles
- Predictive system simulates the path and accounts for future obstacle changes
- **Best Algorithm**: A* (optimal and fast) or Dijkstra (guaranteed optimal, slower)

### Important: Deterministic Obstacle System

#### How It Works
Obstacle Course mode uses a **seeded random number generator** to ensure deterministic obstacle changes:

1. **Seed Initialization**: When the maze is created, it gets an `obstacle_seed` (either provided or randomly generated)
   ```python
   self.obstacle_seed = seed if seed is not None else random.randint(0, 999999)
   self.obstacle_rng = random.Random(self.obstacle_seed)
   ```

2. **Turn Tracking**: Each turn increments `turn_number` (starts at 0)
   ```python
   self.turn_number += 1
   ```

3. **Deterministic Updates**: On each turn:
   - Obstacles are shuffled using the seeded RNG: `self.obstacle_rng.shuffle(current_obstacles)`
   - New obstacles are chosen using: `self.obstacle_rng.choice(obstacle_types)`
   - The same seed + turn number = same obstacle configuration

4. **Future Prediction**: The AI can predict future obstacles by:
   - Creating a temporary RNG with the same seed
   - Advancing it to the current turn state
   - Simulating future turns to get obstacle configurations

#### Why Algorithm Visualization Doesn't Change Each Turn

**This is a key point**: The algorithm visualization in Obstacle Course mode shows the path computed at the **start of the game**, not recalculated each turn.

**Reason**: 
- The AI path is computed once during `setup_obstacle_course_mode()`
- It uses the **current obstacle state** (turn 0) to find a path
- The visualization shows this initial path, which doesn't update as obstacles change
- However, the **predictive pathfinding** system (used internally) does account for future obstacles when calculating costs

**Visualization Behavior**:
- The explored nodes and frontier shown are from the initial path computation
- The path line represents the initial optimal path through turn 0 obstacles
- Obstacles change each turn, but the visualization doesn't recalculate
- This is intentional - it shows the initial planning, while the actual gameplay uses predictive pathfinding

### Implementation Details
- Obstacles change deterministically each turn (predictable pattern)
- `DYNAMIC_OBSTACLE_CHANGE_PER_TURN` obstacles are removed and new ones spawned
- Player's current position is protected from obstacle spawning
- Path validation ensures at least one route to goal always exists
- Predictive pathfinding simulates the entire path and calculates true cost

### Code Reference
- **Obstacle Updates**: `maze.py` → `update_dynamic_obstacles()`
- **Future Prediction**: `maze.py` → `get_future_obstacles()`
- **Predictive Pathfinding**: `pathfinding.py` → `predictive_pathfinding()`

---

## 3. Multi-Goal Mode

### Overview
**Multi-Goal Mode** requires visiting multiple checkpoints in order before reaching the final goal.

### Objectives
- Visit all 3 checkpoints in the correct order
- Then reach the goal position
- Optimize the path to minimize total cost

### Key Features
- **Ordered Checkpoints**: Must visit checkpoints in sequence (cannot skip)
- **Multi-Objective Pathfinding**: AI uses specialized algorithm to find optimal checkpoint order
- **Obstacles Present**: Includes spikes, thorns, quicksand, and rocks
- **Static Obstacles**: Obstacles don't change during gameplay (unlike Obstacle Course mode)

### Algorithm Used
- **Always uses MULTI_OBJECTIVE algorithm** (ignores selected algorithm)
- Multi-Objective Search finds the optimal order to visit checkpoints
- Considers all possible checkpoint permutations to find the cheapest path
- Computes path: Start → Checkpoint 1 → Checkpoint 2 → Checkpoint 3 → Goal

### Implementation Details
- 3 checkpoints are placed along the path from start to goal
- Checkpoints are evenly spaced and sorted by distance from start
- Checkpoints are not placed on obstacles or too close to start/goal
- AI path is computed once at start using MULTI_OBJECTIVE algorithm
- Visualization shows the optimal checkpoint-visiting path

### Code Reference
- **Checkpoint Placement**: `game_modes.py` → `setup_multigoal_mode()`
- **Multi-Objective Algorithm**: `pathfinding.py` → `multi_objective_search()`

---

## 4. AI Duel Mode

### Overview
**AI Duel Mode** is a competitive turn-based race between the player and an AI opponent.

### Objectives
- Reach the goal before the AI
- Visit all 3 checkpoints in order (both player and AI must visit them)
- Win by reaching the goal first after visiting all checkpoints

### Key Features
- **Turn-Based**: Player and AI take turns moving
- **Competitive**: First to reach goal after visiting all checkpoints wins
- **Checkpoints Required**: Both must visit all 3 checkpoints in order
- **Adaptive AI**: AI recalculates path when environment changes
- **Obstacles Present**: Includes spikes, thorns, quicksand, and rocks (static)

### Algorithm Used
- **Always uses MULTI_OBJECTIVE algorithm** when checkpoints exist (ignores selected algorithm)
- AI recalculates path when:
  - It reaches a checkpoint
  - The environment changes (obstacles, etc.)
  - It needs to replan
- Uses selected algorithm only if no checkpoints exist (shouldn't happen in this mode)

### Turn System
- **Player goes first** (`self.turn = 'player'`)
- After player moves, turn switches to AI
- After AI moves, turn switches back to player
- Turn alternates until someone wins

### Win Conditions
- Player wins: Player reaches goal after visiting all checkpoints
- AI wins: AI reaches goal after visiting all checkpoints
- Game Over: Player runs out of energy

### Implementation Details
- Checkpoints are placed evenly along the path (same as Multi-Goal mode)
- Both player and AI track which checkpoints they've visited
- AI uses adaptive pathfinding - recalculates when needed
- Path validation ensures checkpoints don't block routes
- Energy system applies to player (AI has unlimited energy)

### Code Reference
- **Turn Management**: `game_modes.py` → `make_ai_move()`, `handle_player_input()`
- **Win Conditions**: `game_modes.py` → `check_win_conditions()`
- **AI Pathfinding**: `game_modes.py` → `make_ai_move()` (uses MULTI_OBJECTIVE)

---

## 5. Blind Duel Mode

### Overview
**Blind Duel Mode** is a competitive turn-based race with limited visibility (fog of war).

### Objectives
- Reach the goal before the AI
- Navigate with limited visibility (fog of war)
- Collect rewards to increase visibility radius
- Win by reaching the goal first

### Key Features
- **Fog of War**: Limited visibility around player and AI
- **No Checkpoints**: Direct race to goal (unlike AI Duel mode)
- **Memory System**: AI remembers previously seen terrain
- **Reward Bonus**: Collecting rewards increases visibility radius
- **Turn-Based**: Player and AI take turns moving

### Algorithm Used
- **Always uses MODIFIED_ASTAR_FOG algorithm** (ignores selected algorithm)
- Modified A* for fog of war handles limited visibility
- AI uses memory map to remember discovered terrain
- AI plans paths based on known information + heuristic estimates

### Fog of War Mechanics
- **Default Visibility**: 2-cell radius around player/AI
- **Reward Bonus**: Collecting rewards increases visibility radius
- **Discovered Cells**: Once seen, cells are remembered (for visualization)
- **AI Memory**: AI maintains a memory map of discovered terrain
- **Unknown Terrain**: Treated as passable with estimated costs

### Visibility System
- **Player Visibility**: 
  - Starts at radius 2
  - Increases when rewards are collected
  - Resets to 2 when new game starts
- **AI Visibility**:
  - Same as player (radius 2, increases with rewards)
  - Uses memory map to remember terrain
- **Discovered Cells**:
  - Tracked separately for player and AI
  - Used for visualization (showing what each has seen)

### Implementation Details
- No checkpoints (direct race to goal)
- Fog of war resets between games (visibility radius, discovered cells)
- AI uses modified A* that handles unknown terrain
- Memory map allows AI to plan through previously seen areas
- Turn-based system (player goes first)

### Code Reference
- **Fog of War Setup**: `game_modes.py` → `setup_blind_duel_mode()`
- **Visibility Updates**: `game_modes.py` → `update_discovered_cells()`
- **Modified A* for Fog**: `pathfinding.py` → `modified_a_star_fog()`
- **AI Memory**: `player.py` → `AIAgent` class (memory_map attribute)

---

## Common Features Across All Modes

### Terrain System
All modes use the same terrain cost system:
- **Grass**: 1 energy (cheapest)
- **Water**: 3 energy
- **Mud**: 5 energy
- **Spikes**: 4 energy (Obstacle Course, Multi-Goal, AI Duel)
- **Thorns**: 3 energy (Obstacle Course, Multi-Goal, AI Duel)
- **Quicksand**: 6 energy (Obstacle Course, Multi-Goal, AI Duel)
- **Rocks**: 2 energy (Obstacle Course, Multi-Goal, AI Duel)
- **Lava**: ∞ energy (impassable, all modes)
- **Rewards**: 0 energy + temporary cost reduction bonus

### Reward System
- **Spawn Rate**: 3% of cells (all modes)
- **Bonus**: -2 cost reduction for next 5 moves
- **Visibility Bonus**: In Blind Duel mode, increases visibility radius
- **Stackable**: Can collect multiple rewards

### Energy System
- **Starting Energy**: 1000 points
- **Consumption**: Each move costs energy based on terrain
- **Game Over**: If energy depletes before reaching goal
- **Visual Indicator**: Energy bar shows remaining energy (green → red)

### Algorithm Selection
- **Default**: A* (set in `config.py` as `AI_ALGORITHM`)
- **Cycling**: Press `[` and `]` keys to cycle through algorithms
- **Available**: BFS, Dijkstra, A*, Bidirectional A*
- **Mode Overrides**: Some modes force specific algorithms (Multi-Goal, Blind Duel)

---

## Summary Table

| Mode | Obstacles | Checkpoints | Fog of War | Turn-Based | Algorithm | Key Feature |
|------|-----------|-------------|------------|------------|-----------|-------------|
| **Explore** | Static | None | No | No | Selected | Learning mode |
| **Obstacle Course** | Dynamic (deterministic) | None | No | No | Predictive (base: Selected) | Obstacles change each turn |
| **Multi-Goal** | Static | 3 (ordered) | No | No | MULTI_OBJECTIVE | Must visit all checkpoints |
| **AI Duel** | Static | 3 (ordered) | No | Yes | MULTI_OBJECTIVE | Competitive race |
| **Blind Duel** | Static | None | Yes | Yes | MODIFIED_ASTAR_FOG | Limited visibility |

---

## Technical Notes

### Obstacle Course Determinism
- Same seed + same turn number = same obstacle configuration
- Allows AI to predict future obstacles accurately
- Visualization shows initial path (turn 0), not updated path
- Predictive pathfinding accounts for future obstacles in cost calculation

### Algorithm Overrides
- **Multi-Goal Mode**: Always uses MULTI_OBJECTIVE (ignores selected algorithm)
- **AI Duel Mode**: Always uses MULTI_OBJECTIVE when checkpoints exist
- **Blind Duel Mode**: Always uses MODIFIED_ASTAR_FOG (ignores selected algorithm)
- **Obstacle Course Mode**: Uses selected algorithm with predictive wrapper

### Path Caching
- Pathfinding results are cached for performance (LRU cache, 100 entries)
- Obstacle Course mode disables caching (obstacles change each turn)
- Cache is cleared when obstacles change significantly

---

## References

- **Maze Generation**: `maze.py` → `initialize_maze()`
- **Game Mode Setup**: `game_modes.py` → `setup_*_mode()` methods
- **Pathfinding Algorithms**: `pathfinding.py`
- **Configuration**: `config.py`

