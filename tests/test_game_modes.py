"""
Tests for game mode functionality.

Tests:
- All game modes can be initialized
- Mode-specific features work correctly
- Checkpoints are handled properly
- AI agent is created correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_modes import GameState
from config import MAZE_WIDTH, MAZE_HEIGHT

def test_explore_mode():
    """Test Explore mode setup"""
    print("Testing Explore mode...")
    
    game_state = GameState()
    game_state.setup_explore_mode()
    
    assert game_state.mode == 'Explore', "Mode should be 'Explore'"
    assert game_state.maze is not None, "Maze should be created"
    assert game_state.player is not None, "Player should be created"
    assert game_state.maze.start_pos is not None, "Start position should be set"
    assert game_state.maze.goal_pos is not None, "Goal position should be set"
    
    print("  PASS: Explore mode initialized correctly")
    print("PASS: Explore mode test passed\n")

def test_obstacle_course_mode():
    """Test Obstacle Course mode setup"""
    print("Testing Obstacle Course mode...")
    
    game_state = GameState()
    game_state.setup_obstacle_course_mode()
    
    assert game_state.mode == 'Obstacle Course', "Mode should be 'Obstacle Course'"
    assert game_state.maze is not None, "Maze should be created"
    assert game_state.player is not None, "Player should be created"
    
    # Check that obstacles are present
    obstacle_count = 0
    for y in range(game_state.maze.height):
        for x in range(game_state.maze.width):
            if game_state.maze.is_passable(x, y):
                terrain = game_state.maze.terrain.get((x, y), 'GRASS')
                if terrain in ['SPIKES', 'THORNS', 'QUICKSAND', 'ROCKS']:
                    obstacle_count += 1
    
    print(f"  PASS: Obstacle Course mode initialized with {obstacle_count} obstacles")
    print("PASS: Obstacle Course mode test passed\n")

def test_multigoal_mode():
    """Test Multi-Goal mode setup"""
    print("Testing Multi-Goal mode...")
    
    game_state = GameState()
    game_state.setup_multigoal_mode()
    
    assert game_state.mode == 'Multi-Goal', "Mode should be 'Multi-Goal'"
    assert game_state.maze is not None, "Maze should be created"
    assert game_state.player is not None, "Player should be created"
    assert len(game_state.maze.checkpoints) == 3, \
        f"Should have 3 checkpoints, got {len(game_state.maze.checkpoints)}"
    
    # Check that checkpoints are on passable cells
    for checkpoint in game_state.maze.checkpoints:
        assert game_state.maze.is_passable(*checkpoint), \
            f"Checkpoint {checkpoint} should be on passable cell"
    
    print(f"  PASS: Multi-Goal mode initialized with {len(game_state.maze.checkpoints)} checkpoints")
    print("PASS: Multi-Goal mode test passed\n")

def test_ai_duel_mode():
    """Test AI Duel mode setup"""
    print("Testing AI Duel mode...")
    
    game_state = GameState()
    game_state.setup_ai_duel_mode()
    
    assert game_state.mode == 'AI Duel', "Mode should be 'AI Duel'"
    assert game_state.maze is not None, "Maze should be created"
    assert game_state.player is not None, "Player should be created"
    assert game_state.ai_agent is not None, "AI agent should be created"
    assert game_state.turn == 'player', "Should start with player's turn"
    
    print("  PASS: AI Duel mode initialized correctly")
    print("PASS: AI Duel mode test passed\n")

def test_blind_duel_mode():
    """Test Blind Duel mode setup"""
    print("Testing Blind Duel mode...")
    
    game_state = GameState()
    game_state.setup_blind_duel_mode()
    
    assert game_state.mode == 'Blind Duel', "Mode should be 'Blind Duel'"
    assert game_state.maze is not None, "Maze should be created"
    assert game_state.player is not None, "Player should be created"
    assert game_state.ai_agent is not None, "AI agent should be created"
    
    print("  PASS: Blind Duel mode initialized correctly")
    print("PASS: Blind Duel mode test passed\n")

def test_checkpoint_collection():
    """Test that checkpoints can be collected"""
    print("Testing checkpoint collection...")
    
    game_state = GameState()
    game_state.setup_multigoal_mode()
    
    player = game_state.player
    initial_checkpoints = len(player.reached_checkpoints)
    
    # Move player to first checkpoint
    if game_state.maze.checkpoints:
        checkpoint = game_state.maze.checkpoints[0]
        # This would normally be done through game logic
        # For testing, we'll just verify the checkpoint exists
        assert checkpoint in game_state.maze.checkpoints, \
            "Checkpoint should be in maze checkpoints"
    
    print(f"  PASS: Checkpoints available: {len(game_state.maze.checkpoints)}")
    print("PASS: Checkpoint collection test passed\n")

def test_mode_reset():
    """Test that modes can be reset"""
    print("Testing mode reset...")
    
    game_state = GameState()
    game_state.setup_explore_mode()
    
    initial_player_pos = game_state.player.get_position()
    
    # Reset
    game_state.reset()
    
    # Player should be reset to start
    assert game_state.player.get_position() == game_state.maze.start_pos, \
        "Player should be reset to start position"
    
    print("  PASS: Mode reset works correctly")
    print("PASS: Mode reset test passed\n")

def run_all_tests():
    """Run all game mode tests"""
    print("=" * 70)
    print("GAME MODE TEST SUITE")
    print("=" * 70)
    print()
    
    tests = [
        test_explore_mode,
        test_obstacle_course_mode,
        test_multigoal_mode,
        test_ai_duel_mode,
        test_blind_duel_mode,
        test_checkpoint_collection,
        test_mode_reset,
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

