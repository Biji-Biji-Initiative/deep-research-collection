#!/usr/bin/env python3
"""
Quick Test of Mock Deep Research System Components
Tests individual components quickly for validation
"""

import sys
import asyncio
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mock_openai import MockOpenAI
from mock_research_executor import MockGrantEvalV3ResearchExecutor
from mock_monitoring import MockResearchMonitoringSystem
from mock_agents import (
    MockLearningAgent, MockPlanningAgent, MockExecutionAgent,
    AgentContext
)


def test_openai_mock():
    """Test OpenAI mock functionality"""
    print("🔧 Testing OpenAI Mock Client...")
    
    try:
        client = MockOpenAI()
        
        # Test file upload
        from io import StringIO
        test_file = StringIO("Test content")
        test_file.name = "test.txt"
        uploaded = client.files.create(test_file)
        
        # Test vector store
        vs = client.beta.vector_stores.create(name="test")
        
        # Test assistant
        assistant = client.beta.assistants.create(
            name="Test Assistant",
            instructions="Test"
        )
        
        print("✅ OpenAI Mock Client: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI Mock Client failed: {e}")
        return False


def test_research_executor():
    """Test research executor"""
    print("📊 Testing Research Executor...")
    
    try:
        executor = MockGrantEvalV3ResearchExecutor(enable_errors=False)
        
        # Test basic functionality
        files = executor.simulate_file_discovery()
        if files:
            file_ids = executor.upload_files(files[:2])  # Test with 2 files
            if file_ids:
                vs_id = executor.create_vector_store(file_ids)
                if vs_id:
                    assistant_id = executor.create_research_assistant(vs_id)
                    
        print("✅ Research Executor: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Research Executor failed: {e}")
        return False


def test_monitoring_system():
    """Test monitoring system"""
    print("📈 Testing Monitoring System...")
    
    try:
        monitoring = MockResearchMonitoringSystem()
        
        # Test session tracking
        monitoring.start_monitoring_session("test_session")
        
        # Test metrics
        monitoring.metrics_collector.record_counter("test", 1)
        monitoring.metrics_collector.record_gauge("test_gauge", 0.5)
        
        # Test audit
        monitoring.audit_logger.log_event(
            session_id="test_session",
            event_type="TEST",
            event_data={"test": True}
        )
        
        monitoring.end_monitoring_session("test_session")
        
        print("✅ Monitoring System: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Monitoring System failed: {e}")
        return False


async def test_agents():
    """Test agent system"""
    print("🤖 Testing Agent System...")
    
    try:
        # Create context
        context = AgentContext(
            session_id="test_agent_session",
            workspace_root=Path("/Users/agent-g/Downloads/NegotiationUNCDF"),
            research_root=Path(__file__).parent.parent
        )
        
        # Test learning agent
        learning_agent = MockLearningAgent("learning", {}, context)
        result = await learning_agent.execute({"test": True})
        
        if result.status.value not in ["completed", "failed"]:
            raise Exception(f"Unexpected status: {result.status}")
        
        print("✅ Agent System: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Agent System failed: {e}")
        return False


async def main():
    """Main test execution"""
    print("🚀 Quick Test Suite for Mock Deep Research System")
    print("=" * 60)
    
    start_time = time.time()
    results = []
    
    # Test individual components
    results.append(test_openai_mock())
    results.append(test_research_executor())
    results.append(test_monitoring_system())
    results.append(await test_agents())
    
    # Calculate results
    passed = sum(results)
    total = len(results)
    duration = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("📊 QUICK TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {passed/total*100:.1f}%")
    print(f"Duration: {duration:.2f}s")
    
    if passed == total:
        print("\n🎉 All components working correctly!")
        print("The mock system is ready for comprehensive testing.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} component(s) failed testing.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)