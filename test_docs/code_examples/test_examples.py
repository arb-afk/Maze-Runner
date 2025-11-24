"""
Examples of different test types to clarify terminology.

This file demonstrates:
1. Unit Tests - Test individual functions in isolation
2. Integration Tests - Test components working together
3. Performance Tests - Measure speed and efficiency
"""

import sys
sys.path.insert(0, '.')

# ============================================================================
# UNIT TEST EXAMPLE
# ============================================================================

def test_get_cost_for_terrain_unit():
    """
    UNIT TEST: Tests a single function in isolation.
    
    This would be a true unit test if we mocked the dependencies.
    Currently it's more of an integration test because it uses real Maze.
    """
    from maze import Maze
    from config import TERRAIN_COSTS
    
    # Create minimal test setup
    maze = Maze(width=3, height=3)
    
    # Test the get_cost_for_terrain method (if it exists)
    # This tests ONE method in isolation
    for terrain_type, expected_cost in TERRAIN_COSTS.items():
        if terrain_type in ['START', 'GOAL', 'CHECKPOINT', 'REWARD']:
            continue  # Skip special types
        actual_cost = maze.get_cost_for_terrain(terrain_type)
        assert actual_cost == expected_cost, \
            f"get_cost_for_terrain('{terrain_type}') returned {actual_cost}, expected {expected_cost}"
    
    print("✅ Unit test: get_cost_for_terrain() works correctly")


# ============================================================================
# INTEGRATION TEST EXAMPLE (What we actually created)
# ============================================================================

def test_obstacles_replace_terrain_integration():
    """
    INTEGRATION TEST: Tests how multiple components work together.
    
    This is what test_terrain_obstacles.py actually is:
    - Uses real Maze objects
    - Tests assign_terrain() + get_cost() working together
    - Tests the interaction between terrain assignment and cost calculation
    """
    from maze import Maze
    
    maze = Maze(width=5, height=5)
    maze.assign_terrain(include_obstacles=True)
    
    # Test that terrain assignment and cost calculation work together
    for y in range(maze.height):
        for x in range(maze.width):
            if maze.is_passable(x, y):
                terrain = maze.terrain.get((x, y), 'GRASS')
                cost = maze.get_cost(x, y)
                # This tests the INTEGRATION of terrain dict + get_cost() method
                assert isinstance(terrain, str), "Terrain should be a string"
                assert cost > 0 or cost == float('inf'), "Cost should be positive or infinite"
    
    print("✅ Integration test: terrain assignment + cost calculation work together")


# ============================================================================
# PERFORMANCE TEST EXAMPLE (What test_algorithm_performance.py is)
# ============================================================================

def test_algorithm_performance_benchmark():
    """
    PERFORMANCE/BENCHMARK TEST: Measures speed, efficiency, resource usage.
    
    This is what test_algorithm_performance.py is:
    - Measures execution time
    - Counts nodes explored
    - Compares algorithms
    - Tests multiple iterations for statistical accuracy
    """
    import time
    from maze import Maze
    from pathfinding import Pathfinder
    
    maze = Maze(width=31, height=23)
    maze.assign_terrain(include_obstacles=False)
    
    start = maze.start_pos
    goal = maze.goal_pos
    
    if not start or not goal:
        return
    
    # Measure performance
    pf = Pathfinder(maze, 'MANHATTAN')
    
    t0 = time.perf_counter()
    result = pf.a_star(start, goal)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    
    # Performance assertions
    assert elapsed_ms < 10, f"Algorithm too slow: {elapsed_ms}ms"
    assert result.nodes_explored > 0, "Should explore some nodes"
    
    print(f"✅ Performance test: A* completed in {elapsed_ms:.2f}ms, explored {result.nodes_explored} nodes")


# ============================================================================
# TRUE UNIT TEST EXAMPLE (with mocking)
# ============================================================================

def test_heuristic_calculation_unit():
    """
    TRUE UNIT TEST: Tests a pure function with no dependencies.
    
    This would be a pure unit test - tests a function in complete isolation.
    """
    from pathfinding import Pathfinder
    
    # Create a minimal pathfinder (heuristic calculation doesn't need a real maze)
    # Actually, Pathfinder needs a maze, so this isn't a perfect example
    # But the heuristic functions themselves could be unit tested
    
    # Example: Test Manhattan distance calculation
    def manhattan_distance(pos1, pos2):
        """Pure function - no dependencies"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    # Unit test the pure function
    assert manhattan_distance((0, 0), (3, 4)) == 7
    assert manhattan_distance((1, 1), (1, 1)) == 0
    assert manhattan_distance((5, 2), (2, 5)) == 6
    
    print("✅ Unit test: manhattan_distance() pure function works correctly")


if __name__ == "__main__":
    print("=" * 70)
    print("TEST TYPE EXAMPLES")
    print("=" * 70)
    print()
    
    print("1. UNIT TEST (pure function):")
    test_heuristic_calculation_unit()
    print()
    
    print("2. INTEGRATION TEST (components working together):")
    test_obstacles_replace_terrain_integration()
    print()
    
    print("3. PERFORMANCE TEST (speed and efficiency):")
    test_algorithm_performance_benchmark()
    print()
    
    print("=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    print("• test_terrain_obstacles.py = INTEGRATION TEST")
    print("• test_algorithm_performance.py = PERFORMANCE/BENCHMARK TEST")
    print("• Neither are pure UNIT TESTS (they use real objects, not mocks)")
    print("=" * 70)

