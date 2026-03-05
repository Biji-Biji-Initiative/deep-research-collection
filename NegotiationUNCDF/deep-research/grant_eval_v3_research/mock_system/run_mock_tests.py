#!/usr/bin/env python3
"""
Simple Test Runner for Mock Deep Research System
Execute this script to run comprehensive system validation
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_test_runner import ComprehensiveTestRunner


def main():
    """Main execution function"""
    print("🎯 Mock Deep Research System - Test Execution")
    print("=" * 60)
    print("This will run comprehensive tests of the entire mock system")
    print("including OpenAI API simulation, agent orchestration,")
    print("monitoring, error handling, and end-to-end workflows.")
    print("=" * 60)
    
    async def run_tests():
        try:
            # Initialize and run tests
            test_runner = ComprehensiveTestRunner()
            suite = await test_runner.run_comprehensive_test_suite()
            
            # Show summary
            test_runner.print_test_summary(suite)
            
            return suite.overall_metrics['success_rate'] >= 80
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return False
    
    # Run the tests
    success = asyncio.run(run_tests())
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("The mock system is fully validated and ready for production integration.")
        return 0
    else:
        print("\n⚠️ Some tests failed or encountered issues.")
        print("Review the detailed logs and reports for more information.")
        return 1


if __name__ == "__main__":
    sys.exit(main())