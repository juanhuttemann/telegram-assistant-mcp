#!/usr/bin/env python3
"""
Test runner for Telegram MCP Agent tests.
"""
import subprocess
import sys
import os

def run_test(test_name, description):
    """Run a single test and report results."""
    print(f"\n{'='*60}")
    print(f"RUNNING: {test_name}")
    print(f"Description: {description}")
    print('='*60)
    
    try:
        result = subprocess.run([sys.executable, f"tests/{test_name}"], 
                              capture_output=False, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        if result.returncode == 0:
            print(f"\n[PASS] {test_name} completed successfully!")
            return True
        else:
            print(f"\n[FAIL] {test_name} failed with return code {result.returncode}")
            return False
    except Exception as e:
        print(f"\n[ERROR] {test_name} failed with error: {e}")
        return False

def main():
    """Run all tests."""
    print("TELEGRAM MCP AGENT - TEST RUNNER")
    print("=" * 60)
    
    tests = [
        ("test_all_features.py", "Basic feature test with 30s interaction (~40 seconds)"),
        ("test_telegram_service.py", "Comprehensive test with 3 scenarios (~5 minutes)")
    ]
    
    print(f"\nFound {len(tests)} test files:")
    for i, (test_name, description) in enumerate(tests, 1):
        print(f"  {i}. {test_name} - {description}")
    
    print("\nOptions:")
    print("  1. Run basic feature test only (quick)")
    print("  2. Run interactive test only (comprehensive)")  
    print("  3. Run all tests")
    print("  4. Exit")
    
    try:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            run_test(tests[0][0], tests[0][1])
        elif choice == "2":
            run_test(tests[1][0], tests[1][1])
        elif choice == "3":
            print("\n[INFO] Running all tests...")
            for test_name, description in tests:
                success = run_test(test_name, description)
                if not success:
                    print(f"\n[WARN] Test {test_name} failed, but continuing with remaining tests...")
            print("\n[DONE] All tests completed!")
        elif choice == "4":
            print("Goodbye!")
            return
        else:
            print("Invalid choice. Please select 1-4.")
            return
            
    except KeyboardInterrupt:
        print("\n\n[WARN] Tests interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Error running tests: {e}")

if __name__ == "__main__":
    main()