"""
Run all test suites.

This script runs all test files in the tests directory.
"""

import sys
import os
import importlib.util

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_test_file(test_file):
    """Run a single test file"""
    print(f"\n{'='*70}")
    print(f"Running: {test_file}")
    print('='*70)
    
    spec = importlib.util.spec_from_file_location("test_module", test_file)
    module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(module)
        if hasattr(module, 'run_all_tests'):
            return module.run_all_tests()
        else:
            print(f"⚠️  {test_file} does not have run_all_tests() function")
            return True
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("MAZERUNNER COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [
        'test_maze_generation.py',
        'test_pathfinding_algorithms.py',
        'test_player_movement.py',
        'test_game_modes.py',
    ]
    
    results = {}
    
    for test_file in test_files:
        test_path = os.path.join(tests_dir, test_file)
        if os.path.exists(test_path):
            results[test_file] = run_test_file(test_path)
        else:
            print(f"⚠️  Test file not found: {test_file}")
            results[test_file] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_file, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_file}")
    
    print("=" * 70)
    print(f"TOTAL: {passed}/{total} test suites passed")
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

