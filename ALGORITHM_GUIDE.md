# Algorithm Implementation Guide for MazeRunner

This guide explains how the pathfinding algorithms work in MazeRunner and how students can implement and extend them.

## Available Algorithms

### 1. **Dijkstra's Algorithm** ✅ Implemented
- **Location:** `pathfinding.py` → `Pathfinder.dijkstra()`
- **Use Case:** Guaranteed optimal path for static mazes
- **Best For:** Explore mode (static mazes)
- **How to Use:** Set `AI_ALGORITHM = 'DIJKSTRA'` in `config.py`

**How it works:**
- Uses a priority queue sorted by actual cost from start
- Explores all nodes equally (no heuristic)
- Guarantees shortest path but explores more nodes than A*

**Student Task:** Already implemented. Students can study and understand the code.

---

### 2. **A* (A-Star)** ✅ Implemented
- **Location:** `pathfinding.py` → `Pathfinder.a_star()`
- **Use Case:** Faster heuristic-driven search
- **Best For:** Most game modes (default algorithm)
- **How to Use:** Set `AI_ALGORITHM = 'ASTAR'` in `config.py`

**How it works:**
- Uses `f(n) = g(n) + h(n)` where:
  - `g(n)` = actual cost from start to node n
  - `h(n)` = heuristic estimate from node n to goal
- Two heuristics available:
  - **Manhattan:** `|x1-x2| + |y1-y2|` (default)
  - **Euclidean:** `√((x1-x2)² + (y1-y2)²)`
- Faster than Dijkstra by using heuristics to guide search

**Student Task:** Already implemented. Students can:
- Modify heuristics
- Compare Manhattan vs Euclidean
- Study the frontier visualization

---

### 3. **Bidirectional A*** ✅ Implemented
- **Location:** `pathfinding.py` → `Pathfinder.bidirectional_a_star()`
- **Use Case:** Faster search for long paths
- **Best For:** Large mazes or when speed is critical
- **How to Use:** Set `AI_ALGORITHM = 'BIDIRECTIONAL_ASTAR'` in `config.py`

**How it works:**
- Searches from both start AND goal simultaneously
- Stops when the two searches meet
- Often explores fewer nodes than standard A*

**Student Task:** Already implemented. Students can:
- Study the bidirectional approach
- Compare performance vs standard A*
- Visualize both forward and backward searches

---

### 4. **D* (Dynamic A*)** ⚠️ Partially Implemented
- **Location:** `pathfinding.py` → `Pathfinder.d_star()`
- **Use Case:** Efficiently replans when obstacles appear/disappear
- **Best For:** Dynamic mode (automatically used)
- **Status:** Currently uses A* but designed for extension

**How it works (when fully implemented):**
- Maintains state between pathfinding calls
- Uses incremental replanning when obstacles change
- More efficient than recalculating entire path with A*

**Student Task (EXTENSION):**
1. **Implement Full D* Lite:**
   - Add key-based priority queue
   - Track previous path costs
   - Implement incremental update mechanism
   - Only recalculate affected path segments

2. **Current Implementation:** Uses A* with adaptive replanning
3. **Full D* would:** Maintain keys, handle dynamic updates more efficiently

**Reference:** Research D* Lite algorithm papers for full implementation.

---

### 5. **Multi-Objective Search** ✅ Implemented
- **Location:** `pathfinding.py` → `Pathfinder.multi_objective_search()`
- **Use Case:** Finding optimal path through multiple checkpoints
- **Best For:** Multi-Goal mode, AI Duel (Checkpoints) mode (automatically used)
- **Status:** Basic brute-force implementation (can be optimized)

**How it works:**
- Takes a list of goals (checkpoints + final goal)
- Tries all permutations of goal orderings
- Finds the ordering with minimum total cost
- Uses A* for each segment between goals

**Student Task (EXTENSION):**
1. **Current:** Brute force (tries all permutations)
2. **Optimization Ideas:**
   - Use nearest-neighbor heuristic first
   - Implement branch-and-bound to prune bad paths early
   - Use TSP (Traveling Salesman Problem) algorithms
   - Cache sub-paths to avoid recalculation

---

## Algorithm Selection

### Automatic Selection by Game Mode:
- **Explore Mode:** Uses `AI_ALGORITHM` from config (default: A*)
- **Dynamic Mode:** Automatically uses D* (for moving obstacles)
- **Multi-Goal Mode:** Automatically uses Multi-Objective Search
- **AI Duel Mode:** Uses `AI_ALGORITHM` from config
- **AI Duel (Checkpoints):** Automatically uses Multi-Objective Search

### Manual Selection:
Change `AI_ALGORITHM` in `config.py`:
```python
AI_ALGORITHM = 'DIJKSTRA'      # For guaranteed optimal (slower)
AI_ALGORITHM = 'ASTAR'         # Default (fast, heuristic-driven)
AI_ALGORITHM = 'BIDIRECTIONAL_ASTAR'  # Faster for long paths
AI_ALGORITHM = 'DSTAR'         # For dynamic obstacles
AI_ALGORITHM = 'MULTI_OBJECTIVE'  # For multiple goals
```

---

## Algorithm Comparison Dashboard

Press **C** to toggle the Algorithm Comparison Dashboard (if enabled).

This compares:
- **Dijkstra:** Nodes explored, cost, time
- **A* (Manhattan):** Nodes explored, cost, time
- **A* (Euclidean):** (Can be added)

Shows which algorithm is faster and explores fewer nodes.

---

## Implementation Checklist for Students

### ✅ Required (Already Implemented):
- [x] Dijkstra's Algorithm
- [x] A* with Manhattan heuristic
- [x] A* with Euclidean heuristic

### ⭐ Optional Extensions (Partially Implemented):
- [ ] **Full D* Lite Implementation**
  - Current: Uses A* with replanning
  - Task: Implement incremental replanning with keys
  - Difficulty: Advanced

- [ ] **Optimized Multi-Objective Search**
  - Current: Brute force (tries all permutations)
  - Task: Add nearest-neighbor heuristic, branch-and-bound
  - Difficulty: Medium

- [ ] **Bidirectional A* Enhancements**
  - Current: Basic bidirectional search
  - Task: Optimize meeting point detection
  - Difficulty: Easy-Medium

- [ ] **Algorithm Comparison Dashboard**
  - Current: Basic comparison
  - Task: Add more algorithms, visual graphs
  - Difficulty: Easy

---

## How to Extend

### Adding a New Algorithm:

1. **Add method to `Pathfinder` class** in `pathfinding.py`:
```python
def my_new_algorithm(self, start, goal):
    result = PathfindingResult()
    # Your algorithm implementation
    # Must return PathfindingResult with:
    # - result.path: list of (x, y) positions
    # - result.cost: total path cost
    # - result.path_found: bool
    # - result.explored_nodes: set of explored positions
    # - result.nodes_explored: count
    return result
```

2. **Add to `AIAgent.compute_path()`** in `player.py`:
```python
elif algorithm == 'MY_NEW_ALGORITHM':
    self.path_result = self.pathfinder.my_new_algorithm(current_pos, goal)
```

3. **Add to config options** in `config.py`:
```python
AI_ALGORITHM = 'MY_NEW_ALGORITHM'
```

4. **Update UI** in `ui.py` if needed:
```python
algo_display = {
    # ... existing ...
    'MY_NEW_ALGORITHM': 'My New Algorithm'
}
```

---

## Testing Algorithms

1. **Run in different game modes:**
   - Explore: Test Dijkstra vs A*
   - Dynamic: Test D* (watch replanning)
   - Multi-Goal: Test Multi-Objective

2. **Compare performance:**
   - Press **C** for algorithm comparison
   - Watch nodes explored count
   - Check path cost (should be same for optimal algorithms)

3. **Visualize:**
   - Watch exploration visualization in AI Duel mode
   - See frontier nodes being explored
   - Check heuristic values (g, h, f) for A*

---

## Assignment Requirements Summary

**Required Algorithms:**
1. ✅ Dijkstra's Algorithm (for static mazes)
2. ✅ A* with Manhattan/Euclidean heuristics (faster search)

**Optional Upgrades:**
1. ✅ Bidirectional A* (for speed) - **IMPLEMENTED**
2. ⚠️ D* Lite (for moving obstacles) - **PARTIALLY IMPLEMENTED** (students can complete)
3. ✅ Multi-Objective Search (for multiple goals) - **IMPLEMENTED**

**All required algorithms are implemented and working!**
**Optional algorithms are implemented but can be enhanced by students for bonus marks.**

