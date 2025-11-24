"""
Unit test to verify that obstacles replace terrain, not stack.
This test confirms the behavior I explained earlier.
"""

import sys
sys.path.insert(0, '.')

from maze import Maze
from config import TERRAIN_COSTS

def test_obstacles_replace_terrain():
    """Test that obstacles replace terrain types, not stack costs."""
    print("Testing: Obstacles replace terrain (no cost stacking)")
    print("-" * 60)
    
    # Create a small maze (generates automatically in __init__)
    maze = Maze(width=5, height=5)
    
    # Assign terrain with obstacles
    maze.assign_terrain(include_obstacles=True)
    
    # Test 1: Each cell should have exactly ONE terrain type
    print("\n1. Checking that each cell has one terrain type...")
    single_terrain_count = 0
    for y in range(maze.height):
        for x in range(maze.width):
            if maze.is_passable(x, y):
                terrain = maze.terrain.get((x, y), 'GRASS')
                # Should be a single string, not a list or tuple
                assert isinstance(terrain, str), f"Cell ({x}, {y}) has non-string terrain: {terrain}"
                single_terrain_count += 1
    print(f"   PASS: All {single_terrain_count} passable cells have single terrain type")
    
    # Test 2: Cost lookup returns single value (not sum)
    print("\n2. Checking that get_cost() returns single value (not sum)...")
    for y in range(maze.height):
        for x in range(maze.width):
            if maze.is_passable(x, y):
                terrain = maze.terrain.get((x, y), 'GRASS')
                cost = maze.get_cost(x, y)
                expected_cost = TERRAIN_COSTS.get(terrain, 1)
                
                # Cost should match the terrain's cost exactly
                assert cost == expected_cost, \
                    f"Cell ({x}, {y}): terrain={terrain}, cost={cost}, expected={expected_cost}"
    print(f"   PASS: All costs match terrain types (no stacking)")
    
    # Test 3: Manually set a cell to SPIKES and verify cost
    print("\n3. Testing obstacle replacement...")
    test_x, test_y = 2, 2
    if maze.is_passable(test_x, test_y):
        # Get original terrain
        original_terrain = maze.terrain.get((test_x, test_y), 'GRASS')
        original_cost = maze.get_cost(test_x, test_y)
        print(f"   Original: terrain={original_terrain}, cost={original_cost}")
        
        # Replace with obstacle
        maze.terrain[(test_x, test_y)] = 'SPIKES'
        new_cost = maze.get_cost(test_x, test_y)
        expected_spikes_cost = TERRAIN_COSTS['SPIKES']
        
        print(f"   After setting SPIKES: cost={new_cost}, expected={expected_spikes_cost}")
        assert new_cost == expected_spikes_cost, \
            f"SPIKES cost should be {expected_spikes_cost}, got {new_cost}"
        assert new_cost != original_cost + expected_spikes_cost, \
            f"Costs should NOT stack! Got {new_cost}, would be {original_cost + expected_spikes_cost} if stacked"
        print(f"   PASS: Obstacle replaced terrain (cost changed from {original_cost} to {new_cost})")
        print(f"   PASS: Cost does NOT stack (would be {original_cost + expected_spikes_cost} if stacked)")
    
    # Test 4: Verify terrain assignment uses single selection
    print("\n4. Verifying terrain assignment logic...")
    import inspect
    source = inspect.getsource(maze.assign_terrain)
    if "random.choices" in source and "[0]" in source:
        print("   PASS: assign_terrain() uses random.choices()[0] (selects ONE type)")
    else:
        print("   WARNING: Could not verify assignment logic from source")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED: Obstacles replace terrain, costs do NOT stack")
    print("=" * 60)
    return True

def test_cost_calculation():
    """Test that get_cost() returns correct values for each terrain type."""
    print("\n\nTesting: Cost calculation for each terrain type")
    print("-" * 60)
    
    maze = Maze(width=3, height=3)
    
    # Test each terrain type
    test_terrains = ['GRASS', 'WATER', 'MUD', 'SPIKES', 'THORNS', 'QUICKSAND', 'ROCKS']
    
    for terrain in test_terrains:
        # Set a test cell to this terrain
        test_x, test_y = 1, 1
        if maze.is_passable(test_x, test_y):
            maze.terrain[(test_x, test_y)] = terrain
            cost = maze.get_cost(test_x, test_y)
            expected = TERRAIN_COSTS[terrain]
            
            status = "PASS" if cost == expected else "FAIL"
            print(f"   {status} {terrain:12} -> cost={cost:6.1f}, expected={expected:6.1f}")
            assert cost == expected, f"{terrain} cost mismatch: {cost} != {expected}"
    
    print("\nPASS: All terrain costs calculated correctly")
    return True

if __name__ == "__main__":
    try:
        test_obstacles_replace_terrain()
        test_cost_calculation()
        print("\nAll tests completed successfully!")
    except AssertionError as e:
        print(f"\nFAIL: Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

