# How AI Accounts for Checkpoints, Obstacles, and Terrain

## 1. TERRAIN & OBSTACLE COSTS

All algorithms use the same cost system for terrain:

```python
def get_cost(x, y):
    terrain = self.terrain.get((x, y), 'GRASS')
    return TERRAIN_COSTS.get(terrain, 1)

# TERRAIN_COSTS:
TERRAIN_COSTS = {
    'GRASS': 1,
    'WATER': 3,
    'MUD': 5,
    'SPIKES': 4,
    'THORNS': 3,
    'QUICKSAND': 6,
    'ROCKS': 2,
}
```

**Each algorithm uses these costs when calculating path distance:**
```python
edge_cost = self.maze.get_cost(nx, ny)  # Get terrain/obstacle cost
new_cost = current_cost + edge_cost     # Add to running total
```

---

## 2. HOW EACH ALGORITHM WORKS

### **DIJKSTRA'S ALGORITHM**
**What it does:** Explores uniformly in all directions, finding the cheapest path by total cost

**How it handles terrain/obstacles:**
- Uses cost as priority in the queue
- Lower cost cells explored first
- Priority: `(total_cost, position)`
- Example: Moving through quicksand (cost 6) is 6x more expensive than grass

**Checkpoints:** 
- Only works with single goals
- For multiple checkpoints, it fails (returns None)

**Code:**
```python
while pq:
    current_cost, current = heapq.heappop(pq)  # ← Ordered by COST
    
    for next_node in neighbors:
        edge_cost = self.maze.get_cost(nx, ny)  # ← Get terrain cost
        new_cost = current_cost + edge_cost     # ← Add to total
        
        if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
            heapq.heappush(pq, (new_cost, next_node))
```

---

### **A* (A-STAR) ALGORITHM**
**What it does:** Smart exploration using terrain cost + heuristic toward goal

**How it handles terrain/obstacles:**
- Uses `g_score` = actual cost from start
- Uses `h_score` = estimated cost to goal (heuristic)
- Priority: `f_score = g_score + h_score`
- Prioritizes cells that are both cheap AND close to goal

**Checkpoints:**
- Only works with single goals
- For multiple checkpoints, returns None

**Code:**
```python
g_score = {start: 0}                              # ← Actual cost
f_score = {start: heuristic(start, goal)}         # ← g + h estimate

while pq:
    current_f, current = heapq.heappop(pq)       # ← Ordered by f_score
    
    for next_node in neighbors:
        edge_cost = self.maze.get_cost(nx, ny)   # ← Get terrain cost
        tentative_g = g_score[current] + edge_cost
        
        if tentative_g < g_score[next_node]:
            g_score[next_node] = tentative_g
            f_score[next_node] = tentative_g + heuristic(next_node, goal)
            heapq.heappush(pq, (f_score[next_node], next_node))
```

---

### **BIDIRECTIONAL A* ALGORITHM**
**What it does:** Two A* searches meeting in the middle - MUCH faster

**How it handles terrain/obstacles:**
- Uses SAME terrain cost system as A*
- Searches from start toward goal
- Searches from goal toward start
- Stops when searches meet

**Checkpoints:**
- Only works with single goals

**Code:**
```python
# Forward search (start → goal)
g_forward[next_node] = g_forward[current] + edge_cost

# Backward search (goal → start)  
g_backward[next_node] = g_backward[current] + edge_cost

# Both use same terrain costs from get_cost()
```

---

### **MULTI-OBJECTIVE ALGORITHM** (For Checkpoints!)
**What it does:** Finds optimal path visiting ALL checkpoints in BEST order

**How it handles terrain/obstacles:**
- Tries ALL permutations of checkpoint orderings
- For EACH permutation, runs A* between each checkpoint
- Each A* segment accounts for terrain costs
- Returns path with lowest TOTAL cost

**Checkpoints:**
- ✅ Works with multiple goals!
- Finds best order to visit them
- Example: If you need to visit [C1, C2, C3], it tries:
  - C1 → C2 → C3
  - C1 → C3 → C2
  - C2 → C1 → C3
  - etc... (6 permutations)
- Returns the ordering with lowest total cost

**Code:**
```python
best_path = None
best_cost = float('inf')

for goal_order in itertools.permutations(goals):
    current_pos = start
    total_cost = 0
    full_path = [start]
    
    for goal in goal_order:
        # Find A* path from current to this goal
        segment = a_star(current_pos, goal)  # ← Uses terrain costs!
        
        if segment.path_found:
            full_path.extend(segment.path[1:])
            total_cost += segment.cost
            current_pos = goal
        else:
            break
    
    if total_cost < best_cost:
        best_cost = total_cost
        best_path = full_path
        best_order = goal_order

return best_path  # Path visiting all checkpoints optimally!
```

---

## 3. SUMMARY TABLE

| Algorithm | Terrain | Obstacles | Single Goal | Multiple Goals |
|-----------|---------|-----------|-------------|----------------|
| **Dijkstra** | ✅ Considers cost | ✅ Considers cost | ✅ Works | ❌ Fails |
| **A*** | ✅ + Heuristic | ✅ + Heuristic | ✅ Works | ❌ Fails |
| **Bidirectional A*** | ✅ + Heuristic | ✅ + Heuristic | ✅ Fast | ❌ Fails |
| **Multi-Objective** | ✅ Considers cost | ✅ Considers cost | ✅ Works | ✅ **Finds Best Order!** |

---

## 4. EXAMPLE: How Multi-Goal Finds Optimal Checkpoint Path

**Scenario:** 3 checkpoints in a maze with obstacle costs

```
Visual Display (in Game Mode 3):
  Checkpoint ⭐1 at (10, 10)     ← Displayed as "1" on screen
  Checkpoint ⭐2 at (25, 20)     ← Displayed as "2" on screen
  Checkpoint ⭐3 at (30, 5)      ← Displayed as "3" on screen

NOTE: Numbers 1, 2, 3 show spawn order, NOT visit order!
```

**How Multi-Objective Evaluates Each Permutation:**

```
Permutation 1: Start → C1 → C2 → C3 → Goal
  Start(0,0) → C1(10,10): path through GRASS(1) terrain
    Distance × Cost = 14 cells × 1 cost/cell = 14
  
  C1(10,10) → C2(25,20): path through MUD(5) + WATER(3)
    8 mud cells × 5 + 6 water cells × 3 = 40 + 18 = 58
  
  C2(25,20) → C3(30,5): path through SPIKES(4) + QUICKSAND(6)
    5 spike cells × 4 + 4 quicksand × 6 = 20 + 24 = 44
  
  C3(30,5) → Goal(35,12): path through GRASS(1)
    Distance × Cost = 10 cells × 1 cost/cell = 10
  
  Total Cost = 14 + 58 + 44 + 10 = 126


Permutation 2: Start → C2 → C1 → C3 → Goal
  Start(0,0) → C2(25,20): direct path
    22 cells × avg cost = 45
  
  C2(25,20) → C1(10,10): path avoiding obstacles
    15 cells × 2 cost/cell (through ROCKS terrain) = 30
  
  C1(10,10) → C3(30,5): path through low-cost terrain
    20 cells × 1 cost/cell (through GRASS) = 20
  
  C3(30,5) → Goal(35,12): shortcut
    8 cells × 1 cost/cell = 8
  
  Total Cost = 45 + 30 + 20 + 8 = 103 ✅ BEST


Permutation 3: Start → C3 → C1 → C2 → Goal
  Start(0,0) → C3(30,5): long path
    28 cells × 1 cost/cell = 28
  
  C3(30,5) → C1(10,10): backtrack through obstacles
    20 cells × 5 cost/cell (through MUD/WATER) = 100
  
  C1(10,10) → C2(25,20): difficult path
    15 cells × 4 cost/cell (through SPIKES) = 60
  
  C2(25,20) → Goal(35,12): final leg
    15 cells × 1 cost/cell = 15
  
  Total Cost = 28 + 100 + 60 + 15 = 203
```

**Result:** 
- Visual checkpoints shown as 1 → 2 → 3 (spawn order)
- AI chooses Permutation 2: Visit order [2 → 1 → 3] (cost 103)
- **This is the OPTIMAL order considering all terrain and obstacle costs!**

---

## 5. WHY DIJKSTRA, A*, AND BIDIRECTIONAL A* FAIL WITH MULTIPLE CHECKPOINTS

### **The Core Issue: Type Mismatch**

All three expect a **single goal as a tuple** `goal = (x, y)`:

```python
# What they expect:
goal = (10, 15)  # ← A single (x, y) coordinate

# What happens with multiple checkpoints:
goal = [(10, 15), (25, 20), (30, 5)]  # ← A LIST of coordinates
```

### **How They Check for Goal (and fail)**

**Dijkstra (Line 79):**
```python
if current == goal:
    # Found goal! Reconstruct path and return
```

**A* (Line 162):**
```python
if current == goal:
    # Found goal! Reconstruct path and return
```

**Bidirectional A*:**
```python
if current == goal:
    # Found goal from one direction! Reconstruct path and return
```

### **What Actually Happens:**

```python
current = (10, 15)           # ← A tuple from the maze
goal = [(10, 15), (25, 20)]  # ← A list of checkpoints

# Comparison:
current == goal
# → (10, 15) == [(10, 15), (25, 20)]
# → FALSE (tuple ≠ list)
```

### **The Result:**

1. ❌ `current == goal` is ALWAYS False
2. ❌ Never reaches termination condition  
3. ❌ Keeps exploring the entire maze
4. ❌ Queue eventually empties
5. ❌ Returns "path_found = False"

### **Why Multi-Objective Works**

Multi-Objective **explicitly unpacks the list**:

```python
# Multi-Objective receives:
goal = [(10, 15), (25, 20), (30, 5)]

# It does this:
for goal_order in itertools.permutations(goal):
    # goal_order = (10, 15), (25, 20), (30, 5)
    
    for single_goal in goal_order:
        # single_goal = (10, 15)  ← A tuple!
        segment = a_star(current_pos, single_goal)  # ← Passes tuple to A*
        # A* works because it gets a SINGLE tuple now!
```

### **The Flow:**

```
Multi-Goal Mode:
  goal = [C1, C2, C3]  (list)
       ↓
  Try permutation: C1 → C2 → C3
       ↓
  Call A*(start, C1)      ← C1 is a tuple (10,15) ✅
  Call A*(C1, C2)         ← C2 is a tuple (25,20) ✅
  Call A*(C2, C3)         ← C3 is a tuple (30,5) ✅
  Call A*(C3, goal_pos)   ← goal_pos is a tuple ✅
       ↓
  Total cost = 175
```

### 📊 **Quick Reference:**

| Algorithm | Input Type | Works? | Reason |
|-----------|-----------|--------|--------|
| Dijkstra | `goal = (x, y)` | ✅ Yes | Tuple comparison works |
| Dijkstra | `goal = [(x1,y1), (x2,y2)]` | ❌ No | List ≠ tuple, comparison fails |
| A* | `goal = (x, y)` | ✅ Yes | Tuple comparison works |
| A* | `goal = [(x1,y1), (x2,y2)]` | ❌ No | List ≠ tuple, comparison fails |
| Bidirectional A* | `goal = (x, y)` | ✅ Yes | Tuple comparison works |
| Bidirectional A* | `goal = [(x1,y1), (x2,y2)]` | ❌ No | List ≠ tuple, comparison fails |
| Multi-Objective | `goals = [(x1,y1), (x2,y2)]` | ✅ Yes | Unpacks list, passes individual tuples to A* |

### **Key Insight:**

Dijkstra, A*, and Bidirectional A* are **single-goal algorithms** - they're designed to find one goal. Multi-Objective is a **wrapper** that repeatedly calls A* with different goal orderings to find the optimal checkpoint sequence! 🎯

---

## 6. VISUAL CHECKPOINT NUMBERS vs OPTIMAL AI VISIT ORDER

### **Understanding the Display**

When you play **Multi-Goal Mode (Game Mode 3)**, you see checkpoints numbered **1, 2, 3**:

```
⭐1  ⭐2  ⭐3
(spawn order - the order they appear in the maze)
```

**BUT the AI might visit them in a completely different order!**

### **Why the Difference?**

The visual numbers show **where checkpoints physically spawn** in the maze.
The AI visit order shows **the CHEAPEST path considering terrain and obstacles**.

**Example Scenario:**

```
Visual Layout (spawn order):
  ⭐1 in grassland (easy terrain)
  ⭐2 in mudland (medium cost)
  ⭐3 surrounded by spikes (hard terrain)

AI Discovery:
  ✓ Checkpoint 1 is 50 cells away (all grass)
  ✓ Checkpoint 2 is 20 cells away (through mud)
  ✓ Checkpoint 3 is 80 cells away (through spikes)

Optimal Order Analysis:
  Path 1→2→3: 50(1) + 20(5) + 80(4) = 50 + 100 + 320 = 470 ❌
  Path 2→1→3: 20(5) + 50(1) + 80(4) = 100 + 50 + 320 = 470 ❌
  Path 2→3→1: 20(5) + 80(4) + 50(1) = 100 + 320 + 50 = 470 ❌
  Path 3→2→1: 80(4) + 20(5) + 50(1) = 320 + 100 + 50 = 470 ✅ TIE

Actually visit: 2→1→3 with cost 500 if it avoids spikes!
```

### **How Multi-Objective Handles This**

```python
def multi_objective_search(start, goals):
    """
    goals = [Checkpoint1, Checkpoint2, Checkpoint3]  # Physical spawn order
    
    # But it tries all orderings:
    for permutation in [1→2→3, 1→3→2, 2→1→3, 2→3→1, 3→1→2, 3→2→1]:
        cost = calculate_total_path_cost(permutation)
        # Each step uses A* which considers:
        # - TERRAIN costs (grass=1, mud=5, water=3, etc.)
        # - OBSTACLE costs (spikes=4, thorns=3, quicksand=6, rocks=2)
        # - Distance
    
    # Returns the permutation with lowest total cost
    return best_permutation  # Might be different from spawn order!
```

### **In Your Game**

When you play Multi-Goal Mode:
1. **Checkpoints display as 1, 2, 3** - This is the spawn/placement order
2. **AI computes optimal visit sequence** - Considering terrain and obstacles
3. **You might visit in order 3→1→2** - If that's cheaper considering costs
4. **Press V to see AI exploration** - Shows how AI evaluates different paths

---

## 7. FOG OF WAR (Discovery Mechanic)

All algorithms support `discovered_cells` parameter:
- If `discovered_cells=None`: AI can see whole maze
- If `discovered_cells={set of cells}`: AI ONLY knows those cells
- AI cannot pathfind toward undiscovered goal
- Creates "true blindness" - AI must discover goal first!

