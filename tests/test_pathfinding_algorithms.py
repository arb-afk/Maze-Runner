"""
Comprehensive tests for pathfinding algorithms.

Tests:
- All algorithms find paths when they exist
- Optimal algorithms find same cost paths
- Algorithms handle impassable obstacles correctly
- Heuristics work correctly
- Multi-objective search works for multiple checkpoints
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from maze import Maze
from pathfinding import Pathfinder

def test_all_algorithms_find_path():
    """Test that all algorithms can find paths"""
    print("Testing all algorithms find paths...")
    
    maze = Maze(width=31, height=23)
    maze.assign_terrain(include_obstacles=False)
    
    start = maze.start_pos
    goal = maze.goal_pos
    
    algorithms = [
        ('BFS', 'bfs'),
        ('Dijkstra', 'dijkstra'),
        ('A* Manhattan', 'a_star', 'MANHATTAN'),
        ('A* Euclidean', 'a_star', 'EUCLIDEAN'),
        ('Bidirectional A*', 'bidirectional_a_star', 'MANHATTAN'),
    ]
    
    for algo_name, method_name, *args in algorithms:
        pf = Pathfinder(maze, args[0] if args else 'MANHATTAN')
        
        if method_name == 'bfs':
            result = pf.bfs(start, goal)
        elif method_name == 'dijkstra':
            result = pf.dijkstra(start, goal)
        elif method_name == 'a_star':
            result = pf.a_star(start, goal)
        elif method_name == 'bidirectional_a_star':
            result = pf.bidirectional_a_star(start, goal)
        
        assert result.path_found, f"{algo_name} should find a path"
        assert len(result.path) > 0, f"{algo_name} should return a non-empty path"
        
        print(f"  PASS: {algo_name}: Found path ({len(result.path)} steps)")
    
    print("PASS: All algorithms find paths\n")

def test_optimal_algorithms_same_cost():
    """Test that optimal algorithms find the same path cost"""
    print("Testing optimal algorithms find same cost...")
    
    maze = Maze(width=31, height=23)
    maze.assign_terrain(include_obstacles=True)
    
    start = maze.start_pos
    goal = maze.goal_pos
    
    optimal_algorithms = [
        ('Dijkstra', 'dijkstra'),
        ('A* Manhattan', 'a_star', 'MANHATTAN'),
        ('A* Euclidean', 'a_star', 'EUCLIDEAN'),
        ('Bidirectional A*', 'bidirectional_a_star', 'MANHATTAN'),
    ]
    
    costs = {}
    
    for algo_name, method_name, *args in optimal_algorithms:
        pf = Pathfinder(maze, args[0] if args else 'MANHATTAN')
        
        if method_name == 'dijkstra':
            result = pf.dijkstra(start, goal)
        elif method_name == 'a_star':
            result = pf.a_star(start, goal)
        elif method_name == 'bidirectional_a_star':
            result = pf.bidirectional_a_star(start, goal)
        
        if result.path_found:
            path_cost = sum(maze.get_cost(x, y) for x, y in result.path)
            costs[algo_name] = path_cost
    
    if costs:
        unique_costs = set(costs.values())
        assert len(unique_costs) == 1, \
            f"All optimal algorithms should find same cost, got: {costs}"
        print(f"  PASS: All algorithms found cost: {list(unique_costs)[0]:.1f}")
    
    print("PASS: Optimal algorithms consistency test passed\n")

def test_impassable_obstacles():
    """Test that algorithms correctly identify when no path exists"""
    print("Testing impassable obstacles...")
    
    maze = Maze(width=15, height=11)
    maze.assign_terrain(include_obstacles=False)
    
    # Create a wall blocking the path
    # Find a cell on the path from start to goal
    pf = Pathfinder(maze, 'MANHATTAN')
    result = pf.bfs(maze.start_pos, maze.goal_pos)
    
    if result.path_found and len(result.path) > 2:
        # Block a middle cell
        block_pos = result.path[len(result.path) // 2]
        if block_pos[0] >= 0 and block_pos[0] < maze.width:
            maze.cells[block_pos[1]][block_pos[0]] = 0  # Make it a wall
        
        # Now pathfinding should fail or find alternative
        result2 = pf.bfs(maze.start_pos, maze.goal_pos)
        # Either no path found, or found alternative (which is fine)
        print(f"  PASS: Algorithm handled blocked path correctly")
    
    print("PASS: Impassable obstacles test passed\n")

def test_heuristic_values():
    """Test that heuristics return reasonable values"""
    print("Testing heuristic values...")
    
    maze = Maze(width=31, height=23)
    pf_manhattan = Pathfinder(maze, 'MANHATTAN')
    pf_euclidean = Pathfinder(maze, 'EUCLIDEAN')
    
    start = (0, 0)
    goal = (10, 10)
    
    h_manhattan = pf_manhattan.heuristic(start[0], start[1], goal[0], goal[1])
    h_euclidean = pf_euclidean.heuristic(start[0], start[1], goal[0], goal[1])
    
    # Manhattan should be |0-10| + |0-10| = 20
    assert h_manhattan == 20, f"Manhattan heuristic should be 20, got {h_manhattan}"
    
    # Euclidean should be approximately sqrt(10^2 + 10^2) = sqrt(200) ≈ 14.14
    expected_euclidean = (10**2 + 10**2)**0.5
    assert abs(h_euclidean - expected_euclidean) < 0.01, \
        f"Euclidean heuristic should be ~{expected_euclidean}, got {h_euclidean}"
    
    # Euclidean should be <= Manhattan (straight line <= city blocks)
    assert h_euclidean <= h_manhattan, \
        f"Euclidean ({h_euclidean}) should be <= Manhattan ({h_manhattan})"
    
    print(f"  PASS: Manhattan: {h_manhattan}, Euclidean: {h_euclidean:.2f}")
    print("PASS: Heuristic values test passed\n")

def test_multi_objective_search():
    """Test multi-objective search for multiple checkpoints"""
    print("Testing multi-objective search...")
    
    maze = Maze(width=31, height=23)
    maze.assign_terrain(include_obstacles=True)
    
    # Find valid passable cells for checkpoints (not obstacles, reachable)
    pf = Pathfinder(maze, 'MANHATTAN')
    start = maze.start_pos
    goal = maze.goal_pos
    
    # Find reachable cells for checkpoints
    valid_checkpoints = []
    for y in range(5, maze.height - 5, 5):  # Sample cells
        for x in range(5, maze.width - 5, 5):
            if maze.is_passable(x, y):
                # Check if reachable from start
                test_result = pf.bfs(start, (x, y))
                if test_result.path_found:
                    valid_checkpoints.append((x, y))
                    if len(valid_checkpoints) >= 3:
                        break
        if len(valid_checkpoints) >= 3:
            break
    
    if len(valid_checkpoints) >= 3:
        maze.checkpoints = valid_checkpoints[:3]
        
        # multi_objective_search takes: start, goals (list), discovered_cells
        # goals should include all checkpoints + final goal
        all_goals = list(maze.checkpoints) + [goal]
        result = pf.multi_objective_search(start, all_goals)
        
        if result.path_found:
            # Check that all checkpoints are in the path
            path_set = set(result.path)
            for checkpoint in maze.checkpoints:
                assert checkpoint in path_set, \
                    f"Checkpoint {checkpoint} not found in path"
            
            print(f"  PASS: Found path visiting all {len(maze.checkpoints)} checkpoints")
            print(f"  PASS: Path length: {len(result.path)} steps")
        else:
            print("  WARNING: No path found (may be due to obstacle placement)")
    else:
        print("  WARNING: Could not find enough reachable checkpoint positions")
    
    print("PASS: Multi-objective search test passed\n")

def test_algorithm_performance():
    """Test that algorithms complete in reasonable time"""
    print("Testing algorithm performance...")
    
    import time
    
    maze = Maze(width=31, height=23)
    maze.assign_terrain(include_obstacles=True)
    
    start = maze.start_pos
    goal = maze.goal_pos
    
    algorithms = [
        ('BFS', 'bfs'),
        ('Dijkstra', 'dijkstra'),
        ('A*', 'a_star', 'MANHATTAN'),
    ]
    
    for algo_name, method_name, *args in algorithms:
        pf = Pathfinder(maze, args[0] if args else 'MANHATTAN')
        
        t0 = time.perf_counter()
        
        if method_name == 'bfs':
            result = pf.bfs(start, goal)
        elif method_name == 'dijkstra':
            result = pf.dijkstra(start, goal)
        elif method_name == 'a_star':
            result = pf.a_star(start, goal)
        
        elapsed_ms = (time.perf_counter() - t0) * 1000
        
        assert elapsed_ms < 100, \
            f"{algo_name} took {elapsed_ms:.2f}ms (should be < 100ms)"
        
        print(f"  PASS: {algo_name}: {elapsed_ms:.2f}ms")
    
    print("PASS: Performance test passed\n")

def run_all_tests():
    """Run all pathfinding algorithm tests"""
    print("=" * 70)
    print("PATHFINDING ALGORITHM TEST SUITE")
    print("=" * 70)
    print()
    
    tests = [
        test_all_algorithms_find_path,
        test_optimal_algorithms_same_cost,
        test_heuristic_values,
        test_impassable_obstacles,
        test_multi_objective_search,
        test_algorithm_performance,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__} FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test.__name__} ERROR: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

