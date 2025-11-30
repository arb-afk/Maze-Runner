# Maze Generation via Recursive Backtracking

This document explains how the maze generation algorithm works, why it creates a "perfect maze," and the step-by-step process.

---

## Table of Contents

1. [What is a Perfect Maze?](#what-is-a-perfect-maze)
2. [Recursive Backtracking Overview](#recursive-backtracking-overview)
3. [The Grid Pattern](#the-grid-pattern)
4. [Step-by-Step Algorithm](#step-by-step-algorithm)
5. [Why It Creates a Perfect Maze](#why-it-creates-a-perfect-maze)
6. [Visual Example](#visual-example)
7. [Implementation Details](#implementation-details)

---

## What is a Perfect Maze?

A **perfect maze** (also called a "simply connected maze") has exactly **one unique path** between any two cells.

### Characteristics:
- **No Loops**: There are no cycles - you can't create a loop by following paths
- **No Isolated Areas**: Every cell is reachable from every other cell
- **Exactly One Path**: Between any two cells, there is exactly one route (no alternative paths)
- **Always Solvable**: Guaranteed to have a solution

### Why Perfect Mazes?
- **Guaranteed Solvability**: Every maze has a solution
- **Interesting Gameplay**: Forces players to make decisions (no shortcuts)
- **Predictable Structure**: Pathfinding algorithms work well with perfect mazes
- **No Dead-End Clusters**: All dead-ends connect to the main path

---

## Recursive Backtracking Overview

**Recursive Backtracking** is a depth-first search algorithm that:
1. Starts at a cell and carves a path
2. Randomly chooses unvisited neighbors
3. Carves paths to those neighbors
4. Backtracks when no unvisited neighbors remain
5. Continues until all cells are visited

### Key Components:
- **Stack**: Tracks the current path being carved (for backtracking)
- **Visited Set**: Tracks which cells have been processed
- **Random Selection**: Chooses random unvisited neighbors (creates variety)

### Why "Recursive"?
The algorithm uses a **stack** to simulate recursion. Instead of actual function recursion, it:
- Pushes cells onto a stack when moving forward
- Pops cells from the stack when backtracking
- This is more efficient and easier to control than true recursion

---

## The Grid Pattern

The algorithm uses a **special grid pattern** where it only works on **odd-numbered coordinates** and moves **2 cells at a time**.

### Why Odd Coordinates?
The algorithm starts at `(1, 1)` and moves in steps of 2:
- **Start**: `(1, 1)` (odd, odd)
- **Neighbors**: `(1, 3)`, `(3, 1)`, `(1, -1)`, `(-1, 1)` (all 2 cells away)
- **Pattern**: Only cells at odd coordinates are used for path carving

### Why Move 2 Cells at a Time?
Moving 2 cells creates an alternating pattern:
```
W P W P W  (W = Wall, P = Path)
P ? P ? P
W P W P W
P ? P ? P
```

When moving from `(1, 1)` to `(3, 1)`:
- **Current cell**: `(1, 1)` - path
- **Wall cell**: `(2, 1)` - gets removed (becomes path)
- **Next cell**: `(3, 1)` - becomes path

This creates the characteristic maze structure with walls and paths.

### Grid Structure:
```
0 1 2 3 4 5 6 7 8 9  (x coordinates)
0 W W W W W W W W W
1 W P W P W P W P W  ← Only odd rows/cols are carved
2 W W W W W W W W W
3 W P W P W P W P W
4 W W W W W W W W W
```

---

## Step-by-Step Algorithm

### Phase 1: Initialization

1. **Create Grid**: All cells start as walls (`0 = wall`)
   ```python
   self.cells = [[0 for _ in range(width)] for _ in range(height)]
   ```

2. **Initialize Walls**: All four walls (N, E, S, W) are closed for every cell
   ```python
   for each cell:
       walls[(x, y, 'N')] = False  # Closed
       walls[(x, y, 'E')] = False  # Closed
       walls[(x, y, 'S')] = False  # Closed
       walls[(x, y, 'W')] = False  # Closed
   ```

3. **Start Position**: Begin at `(1, 1)` (must be odd coordinates)
   ```python
   start_x, start_y = 1, 1
   stack = [(1, 1)]
   visited = {(1, 1)}
   cells[1][1] = 1  # Make it a path
   ```

### Phase 2: Main Loop (Carving Paths)

The algorithm continues until the stack is empty (all cells processed):

#### Step 1: Get Current Cell
```python
current_x, current_y = stack[-1]  # Top of stack
```

#### Step 2: Find Unvisited Neighbors
Look for neighbors 2 cells away that haven't been visited:
```python
neighbors = []
for direction in ['N', 'E', 'S', 'W']:
    dx, dy = directions[direction]  # (0, -2), (2, 0), (0, 2), (-2, 0)
    nx, ny = current_x + dx, current_y + dy
    if (nx, ny) is valid and not visited:
        neighbors.append((nx, ny, direction))
```

#### Step 3A: If Neighbors Found (Carve Path)
1. **Choose Random Neighbor**: Pick one unvisited neighbor randomly
   ```python
   next_x, next_y, direction = random.choice(neighbors)
   ```

2. **Remove Wall**: The cell between current and next becomes a path
   ```python
   wall_x = current_x + dx // 2  # Halfway point
   wall_y = current_y + dy // 2
   cells[wall_y][wall_x] = 1  # Remove wall
   cells[next_y][next_x] = 1  # Make next cell a path
   ```

3. **Open Walls**: Mark the walls between cells as open
   ```python
   if direction == 'N':
       walls[(current_x, current_y, 'N')] = True  # Open
       walls[(next_x, next_y, 'S')] = True        # Open
   # ... similar for E, S, W
   ```

4. **Mark Visited and Continue**: Add next cell to stack and visited set
   ```python
   visited.add((next_x, next_y))
   stack.append((next_x, next_y))  # Continue from here
   ```

#### Step 3B: If No Neighbors (Backtrack)
When no unvisited neighbors exist:
```python
stack.pop()  # Go back to previous cell
# Algorithm continues with previous cell at top of stack
```

### Phase 3: Entry and Exit Points

After all cells are processed, create entry and exit points:

1. **Entry Point**: Left side of maze (where player enters)
   ```python
   entry_x, entry_y = 0, height // 2
   cells[entry_y][entry_x] = 1  # Make it a path
   walls[(entry_x, entry_y, 'W')] = True  # Open west wall
   ```

2. **Exit Point**: Right side of maze (where player exits)
   ```python
   exit_x, exit_y = width - 1, height // 2
   cells[exit_y][exit_x] = 1  # Make it a path
   walls[(exit_x, exit_y, 'E')] = True  # Open east wall
   ```

3. **Start/Goal Positions**: Placed outside the maze
   ```python
   start_pos = (-1, height // 2)  # Left of maze
   goal_pos = (width, height // 2)  # Right of maze
   ```

---

## Why It Creates a Perfect Maze

### Guarantee 1: All Cells Are Visited
- The algorithm continues until the stack is empty
- Every cell is either:
  - Visited (added to stack at some point)
  - Unreachable (but algorithm ensures all are reachable)
- **Result**: Every cell is connected to the starting cell

### Guarantee 2: Exactly One Path Between Cells
- Each cell is visited **exactly once** (tracked by `visited` set)
- When moving to a neighbor, we **remove exactly one wall**
- No cell is revisited during path carving
- **Result**: Only one path is carved between any two cells

### Guarantee 3: No Loops
- The algorithm never revisits cells during carving
- Each cell has exactly one "parent" (the cell we came from)
- If we backtrack, we're following the same path back
- **Result**: No cycles can be created

### Mathematical Proof (Informal):
1. **Base Case**: Starting cell `(1, 1)` is a path (trivially perfect)
2. **Inductive Step**: When we carve to a new cell:
   - We remove exactly one wall (creates exactly one connection)
   - The new cell connects to exactly one existing path
   - No loops are created (we never revisit cells)
3. **Conclusion**: After all cells are processed, the maze is perfect

---

## Visual Example

### Initial State (All Walls):
```
W W W W W
W W W W W
W W W W W
W W W W W
W W W W W
```

### After First Few Steps:
```
W W W W W
W P P W W  ← Carved from (1,1) to (3,1)
W W W W W
W P W W W  ← Carved from (1,1) to (1,3)
W W W W W
```

### After More Carving:
```
W W W W W
W P P P W  ← Path continues
W W W P W  ← Carved down
W P P P W  ← Path continues
W W W W W
```

### Final Perfect Maze:
```
W W W W W
W P P P W
W W W P W
W P P P W
W W W W W
```

**Note**: Every path cell has exactly one way to reach any other path cell.

---

## Implementation Details

### Data Structures

1. **`cells`**: 2D array where `0 = wall`, `1 = path`
   ```python
   cells[y][x] = 0  # Wall
   cells[y][x] = 1  # Path
   ```

2. **`walls`**: Dictionary tracking wall states
   ```python
   walls[(x, y, 'N')] = True   # Open (can pass through)
   walls[(x, y, 'N')] = False  # Closed (blocked)
   ```

3. **`stack`**: List tracking current carving path
   ```python
   stack = [(1, 1), (3, 1), (3, 3), ...]  # Current path
   ```

4. **`visited`**: Set of processed cells
   ```python
   visited = {(1, 1), (3, 1), (3, 3), ...}
   ```

### Direction Mapping

```python
directions = {
    'N': (0, -2),   # Move up 2 cells
    'E': (2, 0),    # Move right 2 cells
    'S': (0, 2),    # Move down 2 cells
    'W': (-2, 0)    # Move left 2 cells
}
```

### Wall Removal Logic

When moving from `(1, 1)` to `(3, 1)` (East):
- **Current**: `(1, 1)`
- **Wall**: `(2, 1)` (halfway point)
- **Next**: `(3, 1)`

```python
# Remove wall cell
cells[1][2] = 1  # Make (2, 1) a path

# Open walls
walls[(1, 1, 'E')] = True  # Open east wall of (1, 1)
walls[(3, 1, 'W')] = True  # Open west wall of (3, 1)
```

### Backtracking Example

```
Stack: [(1,1), (3,1), (3,3), (5,3)]
Current: (5, 3)
Neighbors: None (all visited or invalid)
Action: stack.pop() → Stack: [(1,1), (3,1), (3,3)]
Current: (3, 3)  ← Backtracked here
```

### Time Complexity

- **Time**: O(n) where n = number of cells
  - Each cell is visited exactly once
  - Each visit checks 4 neighbors (constant time)
  - Total: O(n) operations

- **Space**: O(n)
  - Stack can hold up to n cells (worst case: long path)
  - Visited set holds n cells
  - Total: O(n) space

### Randomness

The algorithm uses `random.choice()` to select neighbors:
- **Same Seed**: Same maze every time (deterministic)
- **Different Seed**: Different maze (variety)
- **Random Selection**: Creates interesting, non-predictable mazes

---

## Key Code Sections

### Main Algorithm Loop
```python
while stack:
    current_x, current_y = stack[-1]
    
    # Find unvisited neighbors
    neighbors = []
    for direction, (dx, dy) in directions.items():
        nx, ny = current_x + dx, current_y + dy
        if is_valid(nx, ny) and (nx, ny) not in visited:
            neighbors.append((nx, ny, direction))
    
    if neighbors:
        # Carve path to random neighbor
        next_x, next_y, direction = random.choice(neighbors)
        # Remove wall, open walls, mark visited, add to stack
    else:
        # Backtrack
        stack.pop()
```

### Wall Removal
```python
wall_x = current_x + directions[direction][0] // 2
wall_y = current_y + directions[direction][1] // 2
cells[wall_y][wall_x] = 1  # Remove wall
cells[next_y][next_x] = 1  # Make next cell a path
```

### Entry/Exit Creation
```python
# Entry (left side)
entry_x, entry_y = 0, self.height // 2
self.cells[entry_y][entry_x] = 1
self.walls[(entry_x, entry_y, 'W')] = True

# Exit (right side)
exit_x, exit_y = self.width - 1, self.height // 2
self.cells[exit_y][exit_x] = 1
self.walls[(exit_x, exit_y, 'E')] = True
```

---

## Summary

**Recursive Backtracking** creates perfect mazes by:
1. Starting with all walls
2. Carving paths by removing walls between cells
3. Using a stack to track the current path
4. Backtracking when no unvisited neighbors exist
5. Continuing until all cells are processed

**Why it's perfect**:
- Every cell is visited exactly once
- Exactly one wall is removed between cells
- No loops are created
- All cells are connected

**Result**: A maze with exactly one path between any two cells - a perfect maze!

---

## References

- **Implementation**: `maze.py` → `initialize_maze()`
- **Algorithm**: Recursive Backtracking (Depth-First Search variant)
- **Grid Pattern**: Odd coordinates, 2-cell movements
- **Complexity**: O(n) time and space

