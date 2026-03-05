#!/usr/bin/env python3
"""
Test Script for Agentic Deep Research System
Tests the complete integration and functionality
"""

import os
import json
import asyncio
from pathlib import Path
import logging
from datetime import datetime

# Setup test environment
def setup_test_environment():
    """Setup test environment and dependencies"""
    print("Setting up test environment...")
    
    # Ensure all required packages are available
    try:
        import yaml
        import psutil
        import numpy
        print("✅ All required packages available")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        return False
        
    # Check directory structure
    base_dir = Path(__file__).parent
    required_dirs = ["config", "agents", "scripts"]
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if not dir_path.exists():
            print(f"❌ Missing directory: {dir_path}")
            return False
        print(f"✅ Found directory: {dir_name}")
        
    return True

async def test_configuration_system():
    """Test configuration system"""
    print("\n🧪 Testing Configuration System...")
    
    try:
        from config.config_manager import ConfigManager
        
        # Test configuration loading
        config_manager = ConfigManager()
        
        # Test basic configuration access
        system_config = config_manager.get_system_config()
        print(f"✅ System config loaded: {system_config.name}")
        
        # Test agent configurations
        agents = config_manager.get_enabled_agents()
        print(f"✅ Enabled agents: {', '.join(agents)}")
        
        # Test workspace paths
        paths = config_manager.get_workspace_paths()
        print(f"✅ Workspace paths configured: {len(paths)} paths")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def test_individual_agents():
    """Test individual agent initialization"""
    print("\n🧪 Testing Individual Agents...")
    
    try:
        from agents import AgentContext
        from agents.learning_agent import LearningAgent
        from agents.planning_agent import PlanningAgent
        from agents.improvement_agent import ImprovementAgent
        from agents.execution_agent import ExecutionAgent
        from agents.audit_agent import AuditAgent
        from agents.review_agent import ReviewAgent
        
        # Create test context
        base_dir = Path(__file__).parent
        context = AgentContext(
            session_id="test_session",
            workspace_root=base_dir.parent.parent,
            research_root=base_dir
        )
        
        # Test each agent
        agent_classes = [
            ("LearningAgent", LearningAgent),
            ("PlanningAgent", PlanningAgent), 
            ("ImprovementAgent", ImprovementAgent),
            ("ExecutionAgent", ExecutionAgent),
            ("AuditAgent", AuditAgent),
            ("ReviewAgent", ReviewAgent)
        ]
        
        for agent_name, agent_class in agent_classes:
            try:
                # Create simple test config
                test_config = {"enabled": True}
                agent = agent_class(test_config, context)
                
                # Test health check
                health = await agent.health_check()
                status = "healthy" if health.get("healthy") else "unhealthy"
                print(f"✅ {agent_name} initialized and {status}")
                
            except Exception as e:
                print(f"❌ {agent_name} failed: {e}")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

async def test_monitoring_system():
    """Test monitoring system"""
    print("\n🧪 Testing Monitoring System...")
    
    try:
        from scripts.monitoring_audit_system import ResearchMonitoringSystem
        
        # Initialize monitoring system
        base_dir = Path(__file__).parent
        monitoring = ResearchMonitoringSystem(base_dir)
        
        # Test basic functionality
        status = monitoring.get_status()
        print(f"✅ Monitoring system initialized: {status['health_status']}")
        
        # Test metrics tracking
        monitoring.track_api_call("test_operation", tokens=100)
        monitoring.track_insight("test_insight", confidence=0.8)
        
        print("✅ Metrics tracking functional")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")
        return False

async def test_orchestrator_initialization():
    """Test orchestrator initialization"""
    print("\n🧪 Testing Orchestrator Initialization...")
    
    try:
        from agentic_orchestrator import AgenticOrchestrator
        
        # Initialize orchestrator
        orchestrator = AgenticOrchestrator()
        
        # Test health check
        health = await orchestrator.health_check()
        print(f"✅ Orchestrator health check: {'healthy' if health['system_healthy'] else 'unhealthy'}")
        
        # Test status
        status = orchestrator.get_orchestrator_status()
        print(f"✅ Orchestrator status: {status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False

async def test_basic_workflow():
    """Test basic workflow execution (simulation)"""
    print("\n🧪 Testing Basic Workflow...")
    
    try:
        from agentic_orchestrator import AgenticOrchestrator
        
        # Initialize orchestrator
        orchestrator = AgenticOrchestrator()
        
        # Create test research request
        research_request = {
            "type": "test_analysis",
            "scope": "basic",
            "focus_areas": ["testing"],
            "output_format": "test_results"
        }
        
        print("🚀 Starting test workflow execution...")
        
        # Run workflow (this will be simulated since no API key)
        results = await orchestrator.run_research_workflow(research_request)
        
        if results.get("success"):
            print(f"✅ Workflow completed successfully!")
            print(f"   Session ID: {results['session_id']}")
            print(f"   Duration: {results['execution_summary']['total_duration']:.1f}s")
            print(f"   Phases: {len(results['execution_summary']['phases_executed'])}")
            return True
        else:
            print(f"❌ Workflow failed: {results.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run comprehensive system test"""
    print("🎯 Starting Comprehensive Agentic System Test")
    print("=" * 60)
    
    # Setup
    if not setup_test_environment():
        print("\n❌ Test environment setup failed")
        return False
        
    # Individual component tests
    tests = [
        ("Configuration System", test_configuration_system),
        ("Individual Agents", test_individual_agents),
        ("Monitoring System", test_monitoring_system),
        ("Orchestrator Initialization", test_orchestrator_initialization),
        ("Basic Workflow", test_basic_workflow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            results[test_name] = False
            print(f"\n{test_name}: ❌ FAILED - {e}")
            
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:30} {status}")
        
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - System is ready for use!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed - Please review and fix issues")
        return False

def create_sample_research_request():
    """Create sample research request file"""
    sample_request = {
        "type": "grant_evaluation_analysis",
        "scope": "comprehensive", 
        "focus_areas": [
            "implementation_gaps",
            "performance_issues",
            "architectural_patterns",
            "optimization_opportunities"
        ],
        "analysis_depth": "comprehensive",
        "output_format": {
            "structured": True,
            "include_code_examples": True,
            "include_recommendations": True,
            "confidence_scores": True
        },
        "constraints": {
            "max_duration": 3600,
            "max_cost": 25.0,
            "quality_threshold": 0.8
        },
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "created_by": "agentic_system_test",
            "description": "Sample research request for testing the agentic deep research system"
        }
    }
    
    request_file = Path(__file__).parent / "sample_research_request.json"
    with open(request_file, 'w') as f:
        json.dump(sample_request, f, indent=2)
        
    print(f"📄 Sample research request created: {request_file}")
    return request_file

def display_usage_instructions():
    """Display usage instructions"""
    print("\n" + "=" * 60)
    print("📚 USAGE INSTRUCTIONS")
    print("=" * 60)
    print("\n1. Basic Usage (CLI):")
    print("   python agentic_orchestrator.py")
    print("   python agentic_orchestrator.py --request sample_research_request.json")
    print("\n2. Health Check:")
    print("   python agentic_orchestrator.py --health-check")
    print("\n3. Status Check:")
    print("   python agentic_orchestrator.py --status")
    print("\n4. Custom Configuration:")
    print("   python agentic_orchestrator.py --config path/to/config.yaml")
    print("\n5. Environment Variables:")
    print("   export OPENAI_API_KEY=your_api_key_here  # For actual research")
    print("   export AGENTIC_RESEARCH_DEBUG=true       # For debug mode")
    print("\n6. Key Features:")
    print("   - Self-improving research with learning from past runs")
    print("   - Multiple specialized agents working in coordination")
    print("   - Comprehensive monitoring and audit trails")
    print("   - Quality assessment with automatic iteration")
    print("   - Configurable optimization targets and constraints")
    print("\n7. Output Locations:")
    print("   - Results: deep_research/grant_eval_v3_research/results/")
    print("   - Logs: deep_research/grant_eval_v3_research/logs/")
    print("   - Agent Memory: deep_research/grant_eval_v3_research/agents/*/memory/")

async def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Agentic Deep Research System")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive test suite")
    parser.add_argument("--quick", action="store_true", help="Run quick smoke test")
    parser.add_argument("--create-sample", action="store_true", help="Create sample request file")
    parser.add_argument("--instructions", action="store_true", help="Show usage instructions")
    
    args = parser.parse_args()
    
    if args.instructions:
        display_usage_instructions()
        return
        
    if args.create_sample:
        create_sample_research_request()
        return
        
    if args.quick:
        # Quick smoke test
        print("🔥 Quick Smoke Test")
        success = await test_configuration_system()
        if success:
            print("\n✅ Quick test passed - System basics are working")
        else:
            print("\n❌ Quick test failed - Check configuration")
        return
        
    # Default: comprehensive test
    success = await run_comprehensive_test()
    
    if success:
        print("\n🎯 Creating sample files for immediate use...")
        create_sample_research_request()
        display_usage_instructions()

if __name__ == "__main__":
    asyncio.run(main())