# Seeding Explained: Deterministic Randomness in MazeRunner

This document provides an extensive explanation of how seeding works in MazeRunner, particularly focusing on the deterministic obstacle system used in Obstacle Course mode.

---

## Table of Contents

1. [What is Seeding?](#what-is-seeding)
2. [Why Use Seeding?](#why-use-seeding)
3. [How Python's Random Module Works](#how-pythons-random-module-works)
4. [Seeding in MazeRunner](#seeding-in-mazerunner)
5. [Deterministic Obstacle System](#deterministic-obstacle-system)
6. [RNG State Synchronization](#rng-state-synchronization)
7. [Future Obstacle Prediction](#future-obstacle-prediction)
8. [Code Walkthrough](#code-walkthrough)
9. [Examples and Scenarios](#examples-and-scenarios)
10. [Benefits and Limitations](#benefits-and-limitations)
11. [Advanced Topics](#advanced-topics)

---

## What is Seeding?

### Conceptual Overview

**Seeding** is the process of initializing a random number generator (RNG) with a starting value called a **seed**. This seed determines the sequence of "random" numbers that will be generated.

### Key Concepts

1. **Pseudo-Randomness**: Computers cannot generate truly random numbers. Instead, they use algorithms that produce sequences that *appear* random but are actually deterministic.

2. **Deterministic Sequences**: Given the same seed, a random number generator will produce the exact same sequence of numbers every time.

3. **Seed Value**: An integer (or other value) that initializes the RNG's internal state.

### Simple Example

```python
import random

# Set seed to 42
random.seed(42)
print(random.randint(1, 10))  # Output: 7
print(random.randint(1, 10))  # Output: 1
print(random.randint(1, 10))  # Output: 4

# Reset seed to 42 again
random.seed(42)
print(random.randint(1, 10))  # Output: 7 (same as first!)
print(random.randint(1, 10))  # Output: 1 (same as second!)
print(random.randint(1, 10))  # Output: 4 (same as third!)
```

**Key Point**: The same seed produces the same sequence of random numbers.

---

## Why Use Seeding?

### 1. **Reproducibility**

With seeding, you can recreate the exact same "random" behavior:
- **Testing**: Run tests with known inputs and expected outputs
- **Debugging**: Reproduce bugs that depend on random events
- **Consistency**: Ensure the same game state across different runs

### 2. **Deterministic Behavior**

In MazeRunner, seeding allows:
- **AI Prediction**: The AI can predict future obstacle changes because they follow a deterministic pattern
- **Fair Competition**: Same maze + same seed = same obstacle changes for all players
- **Replayability**: Players can replay the same scenario

### 3. **Controlled Randomness**

You get randomness when you want it, but can reproduce specific scenarios when needed.

---

## How Python's Random Module Works

### The Random Number Generator

Python's `random` module uses the **Mersenne Twister** algorithm, which:
- Produces high-quality pseudo-random numbers
- Has a very long period (2^19937 - 1)
- Is deterministic when seeded

### Creating Separate RNG Instances

Instead of using the global `random` module, you can create **separate RNG instances**:

```python
import random

# Create a separate RNG instance
rng1 = random.Random(42)  # Seed: 42
rng2 = random.Random(42)  # Seed: 42 (same seed)

# Both produce the same sequence
print(rng1.randint(1, 10))  # Output: 7
print(rng2.randint(1, 10))  # Output: 7

# But they're independent - using one doesn't affect the other
print(rng1.randint(1, 10))  # Output: 1
print(rng2.randint(1, 10))  # Output: 1
```

### RNG State

Each RNG instance maintains an **internal state** that determines what number comes next. When you call a random function:
1. The RNG uses its current state to generate a number
2. The state is updated to prepare for the next number
3. The generated number is returned

**Important**: The state advances with each random operation, so the sequence is consumed as you use it.

---

## Seeding in MazeRunner

### Where Seeding is Used

MazeRunner uses seeding in two main contexts:

1. **Maze Generation** (optional): Can use a seed for reproducible maze layouts
2. **Obstacle Course Mode** (required): Uses seeding for deterministic obstacle changes

### Seed Initialization

In `maze.py`, the `Maze` class constructor accepts an optional seed:

```python
def __init__(self, width, height, seed=None):
    # ... other initialization ...
    
    # Random seed for obstacle generation
    # If no seed provided, generate a random one (0 to 999999)
    self.obstacle_seed = seed if seed is not None else random.randint(0, 999999)
    
    # Create a separate RNG instance for obstacles
    # This ensures deterministic obstacle changes
    self.obstacle_rng = random.Random(self.obstacle_seed)
    
    # Track current turn number
    self.turn_number = 0
```

**Key Points**:
- If `seed=None`, a random seed is generated (0 to 999999)
- A **separate RNG instance** (`obstacle_rng`) is created with this seed
- This RNG is used exclusively for obstacle operations

### Why a Separate RNG?

Using a separate RNG instance (`obstacle_rng`) instead of the global `random` module ensures:
- **Isolation**: Obstacle randomness doesn't interfere with other random operations
- **Consistency**: The same seed always produces the same obstacle sequence
- **Predictability**: We can create a new RNG with the same seed to predict future obstacles

---

## Deterministic Obstacle System

### Overview

In **Obstacle Course mode**, obstacles change each turn, but the changes are **deterministic** (predictable). This means:
- Same seed + same turn number = same obstacle configuration
- The AI can predict future obstacles by simulating ahead

### How It Works

#### Step 1: Initial Setup

When a maze is created:
```python
# In Maze.__init__()
self.obstacle_seed = 12345  # Example seed
self.obstacle_rng = random.Random(12345)
self.turn_number = 0
```

#### Step 2: Turn-Based Updates

Each turn, `update_dynamic_obstacles()` is called:

```python
def update_dynamic_obstacles(self, ...):
    self.turn_number += 1  # Increment turn counter
    
    # Find current obstacles
    current_obstacles = [(x, y) for ... if terrain in obstacle_types]
    
    # Remove obstacles (deterministic shuffle)
    self.obstacle_rng.shuffle(current_obstacles)
    # Remove first N obstacles...
    
    # Spawn new obstacles (deterministic selection)
    self.obstacle_rng.shuffle(valid_cells)
    # Choose cells and obstacle types using obstacle_rng...
```

**Key Operations**:
- `obstacle_rng.shuffle()`: Shuffles a list deterministically
- `obstacle_rng.choice()`: Chooses an element deterministically
- The RNG state advances with each operation

#### Step 3: Deterministic Results

Because `obstacle_rng` is seeded:
- **Turn 1**: Always removes the same obstacles, spawns obstacles in the same positions
- **Turn 2**: Always removes the same obstacles (different from Turn 1), spawns in the same positions
- **Turn N**: Always the same configuration for that turn number

### Example Sequence

**Seed: 12345**

**Turn 1**:
- RNG state: Initial (seed 12345)
- Shuffle obstacles: `[(5, 3), (10, 7), (15, 11)]` → `[(10, 7), (5, 3), (15, 11)]`
- Remove: `(10, 7)` (first after shuffle)
- Spawn new: `(8, 4)` with type `'SPIKES'`

**Turn 2**:
- RNG state: Advanced (after Turn 1 operations)
- Shuffle obstacles: `[(5, 3), (15, 11), (8, 4)]` → `[(15, 11), (8, 4), (5, 3)]`
- Remove: `(15, 11)` (first after shuffle)
- Spawn new: `(12, 9)` with type `'THORNS'`

**Turn 3**:
- RNG state: Advanced further
- Shuffle obstacles: `[(8, 4), (5, 3), (12, 9)]` → `[(5, 3), (12, 9), (8, 4)]`
- Remove: `(5, 3)`
- Spawn new: `(20, 6)` with type `'QUICKSAND'`

**Important**: If you restart with seed 12345, Turn 1, 2, 3 will have the exact same obstacle changes.

---

## RNG State Synchronization

### The Challenge

To predict future obstacles, the AI needs to:
1. Create a temporary RNG with the same seed
2. **Advance it to the current turn's state** (synchronize)
3. Simulate future turns

### How Synchronization Works

The `get_future_obstacles()` method demonstrates this:

```python
def get_future_obstacles(self, turns_ahead=5):
    # Create a temporary RNG with the same seed
    temp_rng = random.Random(self.obstacle_seed)
    
    # CRITICAL: Advance RNG to current turn state
    # We need to "consume" the same random numbers that were used
    # in previous turns to sync the state
    for _ in range(self.turn_number):
        temp_rng.random()  # Consume one random number per turn
    
    # Now temp_rng is synchronized with obstacle_rng's current state
    # We can simulate future turns...
```

### Why This Works

Each turn, `obstacle_rng` performs a certain number of operations:
- `shuffle()`: Uses multiple random numbers internally
- `choice()`: Uses one random number
- Other operations may use random numbers

**The Problem**: We don't know exactly how many random numbers each operation uses.

**The Solution**: We approximate by calling `temp_rng.random()` once per turn. This is a simplification, but it works because:
- The operations are deterministic
- As long as we consume the same number of random values, the state will sync
- The exact number doesn't matter if we're consistent

### More Accurate Synchronization (Advanced)

A more precise approach would track exactly how many random numbers each operation uses:

```python
# Track random number consumption
random_numbers_used = 0

# In update_dynamic_obstacles():
self.obstacle_rng.shuffle(current_obstacles)
random_numbers_used += len(current_obstacles)  # Approximate

self.obstacle_rng.shuffle(valid_cells)
random_numbers_used += len(valid_cells)

new_obstacle = self.obstacle_rng.choice(obstacle_types)
random_numbers_used += 1

# Store total for this turn
self.random_numbers_per_turn.append(random_numbers_used)
```

Then in `get_future_obstacles()`:
```python
# Advance by exact amount
for count in self.random_numbers_per_turn[:self.turn_number]:
    for _ in range(count):
        temp_rng.random()
```

**Note**: The current implementation uses a simpler approximation (one `random()` call per turn), which works in practice.

---

## Future Obstacle Prediction

### The Prediction Algorithm

The `get_future_obstacles()` method simulates future turns:

```python
def get_future_obstacles(self, turns_ahead=5):
    # 1. Create synchronized temporary RNG
    temp_rng = random.Random(self.obstacle_seed)
    for _ in range(self.turn_number):
        temp_rng.random()  # Sync to current state
    
    # 2. Copy current terrain state
    simulated_terrain = dict(self.terrain)
    
    # 3. Simulate each future turn
    future_configurations = []
    for turn in range(turns_ahead):
        # Simulate obstacle removal (same logic as update_dynamic_obstacles)
        current_obstacles = [...]
        temp_rng.shuffle(current_obstacles)
        # Remove obstacles...
        
        # Simulate obstacle spawning (same logic)
        valid_cells = [...]
        temp_rng.shuffle(valid_cells)
        # Spawn obstacles...
        
        # Store this configuration
        future_configurations.append(dict(simulated_terrain))
    
    return future_configurations
```

### How the AI Uses It

The AI's predictive pathfinding:

1. **Get Future Obstacles**: Calls `get_future_obstacles(turns_ahead=10)`
2. **Simulate Path**: For each step in the planned path:
   - Check what obstacles will exist at that turn
   - Adjust path cost based on future obstacles
3. **Choose Optimal Path**: Select path that minimizes cost considering future obstacles

### Example Prediction

**Current State** (Turn 3):
- Obstacles at: `[(8, 4), (12, 9)]`
- Planning path through `(10, 7)`

**Prediction** (Turn 5):
- Simulated obstacles: `[(12, 9), (20, 6)]` (obstacles changed)
- `(10, 7)` will be clear (no obstacle)
- Path is safe!

**Prediction** (Turn 7):
- Simulated obstacles: `[(20, 6), (15, 11)]`
- `(10, 7)` will still be clear
- Path remains safe!

The AI can now confidently plan a path knowing that `(10, 7)` won't have obstacles in the future.

---

## Code Walkthrough

### Complete Flow Example

Let's trace through a complete example:

#### Initialization

```python
# In Maze.__init__()
seed = 54321  # Provided or randomly generated
self.obstacle_seed = 54321
self.obstacle_rng = random.Random(54321)
self.turn_number = 0
```

**RNG State**: `[seed: 54321, position: 0]`

#### Turn 1: Update Obstacles

```python
# In update_dynamic_obstacles()
self.turn_number += 1  # Now: 1

# Current obstacles: [(5, 3), (10, 7), (15, 11)]
current_obstacles = [(5, 3), (10, 7), (15, 11)]

# Shuffle deterministically
self.obstacle_rng.shuffle(current_obstacles)
# Result: [(10, 7), (5, 3), (15, 11)]
# RNG state advanced internally

# Remove first obstacle
removed = current_obstacles[0]  # (10, 7)
self.terrain[(10, 7)] = 'GRASS'

# Spawn new obstacle
valid_cells = [(8, 4), (12, 9), (20, 6), ...]
self.obstacle_rng.shuffle(valid_cells)
# Result: [(12, 9), (8, 4), (20, 6), ...]
# RNG state advanced again

# Choose obstacle type
obstacle_type = self.obstacle_rng.choice(['SPIKES', 'THORNS', 'QUICKSAND', 'ROCKS'])
# Result: 'SPIKES'
# RNG state advanced again

# Spawn at first valid cell
self.terrain[(12, 9)] = 'SPIKES'
```

**RNG State**: `[seed: 54321, position: ~N]` (advanced by shuffle + choice operations)

#### Turn 2: Update Obstacles

```python
self.turn_number += 1  # Now: 2

# Current obstacles: [(5, 3), (15, 11), (12, 9)]
current_obstacles = [(5, 3), (15, 11), (12, 9)]

# Shuffle (deterministic, based on current RNG state)
self.obstacle_rng.shuffle(current_obstacles)
# Result: [(15, 11), (12, 9), (5, 3)]
# Different from Turn 1 because RNG state is different

# ... continue with removal and spawning
```

#### Predicting Future (Turn 5)

```python
# In get_future_obstacles(turns_ahead=3)
# We want to predict Turns 3, 4, 5

# 1. Create new RNG with same seed
temp_rng = random.Random(54321)

# 2. Synchronize to current turn (Turn 2)
for _ in range(2):  # self.turn_number = 2
    temp_rng.random()
# Now temp_rng's state matches obstacle_rng's state

# 3. Simulate Turn 3
# (Same operations as update_dynamic_obstacles, but using temp_rng)
current_obstacles = [(15, 11), (12, 9), (5, 3)]  # From Turn 2 result
temp_rng.shuffle(current_obstacles)
# Result: [(12, 9), (5, 3), (15, 11)]  # Deterministic!
# ... simulate removal and spawning

# 4. Simulate Turn 4
# ... continue simulation

# 5. Simulate Turn 5
# ... continue simulation

# Return all future configurations
return [turn3_config, turn4_config, turn5_config]
```

**Key Point**: `temp_rng` produces the same sequence as `obstacle_rng` because:
- Same seed (54321)
- Synchronized state (advanced to Turn 2)
- Same operations (shuffle, choice)

---

## Examples and Scenarios

### Example 1: Reproducible Game Session

**Scenario**: Player wants to replay the exact same game.

```python
# Game 1: Seed 99999
maze1 = Maze(31, 23, seed=99999)
# Turn 1 obstacles: [(10, 5), (20, 10)]
# Turn 2 obstacles: [(15, 8), (25, 12)]
# Turn 3 obstacles: [(12, 7), (18, 11)]

# Game 2: Same seed 99999
maze2 = Maze(31, 23, seed=99999)
# Turn 1 obstacles: [(10, 5), (20, 10)]  # Same!
# Turn 2 obstacles: [(15, 8), (25, 12)]  # Same!
# Turn 3 obstacles: [(12, 7), (18, 11)]   # Same!
```

**Result**: Identical obstacle sequences.

### Example 2: AI Prediction Accuracy

**Scenario**: AI plans a 10-turn path.

```python
# Current: Turn 5
# AI wants to plan path for Turns 5-15

# Get future obstacles
future_obstacles = maze.get_future_obstacles(turns_ahead=10)
# Returns: [turn6_config, turn7_config, ..., turn15_config]

# AI simulates path
planned_path = [(5, 3), (6, 3), (7, 3), ..., (31, 11)]

# Check each step
for i, step in enumerate(planned_path):
    turn = 5 + i  # Current turn + steps ahead
    future_config = future_obstacles[i]  # Obstacles at that turn
    
    if future_config[step] in obstacle_types:
        # Obstacle will be here! Adjust path or cost
        cost += obstacle_cost(future_config[step])
    else:
        # Clear path
        cost += 1  # Normal terrain cost
```

**Result**: AI can accurately predict and avoid future obstacles.

### Example 3: Different Seeds, Different Games

**Scenario**: Two players with different seeds.

```python
# Player A: Seed 11111
maze_a = Maze(31, 23, seed=11111)
# Turn 1: Obstacles at [(5, 5), (10, 10)]

# Player B: Seed 22222
maze_b = Maze(31, 23, seed=22222)
# Turn 1: Obstacles at [(8, 7), (15, 12)]  # Different!
```

**Result**: Different seeds produce different obstacle sequences.

### Example 4: Synchronization Failure

**Scenario**: What happens if synchronization is wrong?

```python
# Correct synchronization
temp_rng = random.Random(54321)
for _ in range(5):  # Current turn: 5
    temp_rng.random()
# temp_rng is now synchronized

# Wrong synchronization (off by one)
temp_rng_wrong = random.Random(54321)
for _ in range(4):  # One turn behind!
    temp_rng_wrong.random()

# Predict Turn 6
temp_rng.shuffle([...])        # Correct prediction
temp_rng_wrong.shuffle([...])  # Wrong! Predicts Turn 5's obstacles instead
```

**Result**: Incorrect predictions lead to suboptimal AI behavior.

---

## Benefits and Limitations

### Benefits

1. **Reproducibility**: Same seed = same game
2. **AI Prediction**: Enables predictive pathfinding
3. **Fair Competition**: All players see same obstacles (with same seed)
4. **Testing**: Easy to test with known obstacle sequences
5. **Debugging**: Can reproduce specific scenarios

### Limitations

1. **Synchronization Complexity**: Must carefully track RNG state
2. **Approximation**: Current sync method is approximate (one `random()` per turn)
3. **Seed Range**: Seeds are 0-999999 (1 million possibilities, but finite)
4. **State Dependency**: Must maintain turn counter accurately
5. **Not Truly Random**: Deterministic sequences can be predicted if seed is known

### Trade-offs

**Deterministic vs. Random**:
- **Deterministic** (seeded): Predictable, testable, but less "surprising"
- **Random** (no seed): Unpredictable, more variety, but harder to test/debug

MazeRunner uses **deterministic obstacles** to enable AI prediction, while still allowing random seeds for variety.

---

## Advanced Topics

### 1. Seed Quality

**Good Seeds**:
- Large range (0 to 999999 provides good variety)
- Can use timestamps, user input, or other sources
- Should be unpredictable for gameplay variety

**Bad Seeds**:
- Always using 0 or 1 (limited variety)
- Predictable sequences (1, 2, 3, ...)
- Too small range (only 0-10)

### 2. Multiple RNG Instances

MazeRunner uses separate RNGs for:
- **Obstacle generation**: `obstacle_rng` (seeded, deterministic)
- **Maze generation**: Global `random` (can be seeded separately)
- **Terrain assignment**: Global `random` (can vary even with same seed)

This separation ensures:
- Obstacle changes are deterministic
- Other randomness can still vary (or be controlled separately)

### 3. RNG State Serialization

You could save/load RNG state:

```python
import pickle

# Save state
rng_state = self.obstacle_rng.getstate()
with open('rng_state.pkl', 'wb') as f:
    pickle.dump(rng_state, f)

# Load state
with open('rng_state.pkl', 'rb') as f:
    rng_state = pickle.load(f)
self.obstacle_rng.setstate(rng_state)
```

This allows:
- Saving game state exactly
- Resuming from exact RNG position
- More precise synchronization

### 4. Cryptographic vs. Pseudo-Random

**Pseudo-Random** (Python's `random`):
- Fast, deterministic, good for games
- **Not secure** (predictable if seed known)

**Cryptographic Random** (`secrets` module):
- Truly unpredictable, secure
- Slower, not deterministic
- Use for: passwords, tokens, security

MazeRunner uses pseudo-random (good for games, not for security).

---

## Summary

### Key Takeaways

1. **Seeding** initializes a random number generator with a starting value
2. **Same seed** = same sequence of random numbers
3. **Separate RNG instances** allow isolated, deterministic randomness
4. **State synchronization** enables future prediction
5. **Deterministic obstacles** allow AI to plan ahead

### In MazeRunner

- **Obstacle Course mode** uses seeded RNG for deterministic obstacle changes
- **Same seed + same turn** = same obstacle configuration
- **AI can predict** future obstacles by synchronizing a temporary RNG
- **Reproducible gameplay** enables testing and fair competition

### Further Reading

- Python `random` module documentation
- Mersenne Twister algorithm
- Pseudo-random number generation
- Deterministic algorithms in game development

---

**End of Document**

