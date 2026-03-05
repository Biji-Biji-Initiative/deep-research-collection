#!/usr/bin/env python3
"""
Quick test to verify fast configuration is working
"""

import time
from mock_orchestrator import MockSystemConfig
from mock_openai import MockOpenAI
from mock_agents import MockLearningAgent, AgentContext
from pathlib import Path

def test_fast_config():
    print("Testing fast configuration...")
    
    # Test 1: Fast config creation
    config = MockSystemConfig.create_fast_config()
    print(f"✅ Fast config created: agent_multiplier={config.agent_processing_time_multiplier}, openai_multiplier={config.openai_delay_multiplier}")
    
    # Test 2: OpenAI client with fast delays
    client = MockOpenAI(delay_multiplier=config.openai_delay_multiplier)
    
    start_time = time.time()
    from io import StringIO
    test_file = StringIO("Test content")
    test_file.name = "test.txt"
    uploaded = client.files.create(test_file)
    upload_time = time.time() - start_time
    
    print(f"✅ File upload took {upload_time:.2f}s (should be ~0.05s)")
    
    # Test 3: Agent with fast processing
    context = AgentContext(
        session_id="test",
        workspace_root=Path("/tmp"),
        research_root=Path("/tmp")
    )
    
    agent_config = {
        "analysis_depth": "comprehensive", 
        "learning_rate": 0.1,
        "processing_multiplier": config.agent_processing_time_multiplier
    }
    
    agent = MockLearningAgent("test", agent_config, context)
    
    start_time = time.time()
    result = agent.simulate_processing_time(2.0, 4.0)
    processing_time = time.time() - start_time
    
    print(f"✅ Agent processing took {processing_time:.2f}s (should be ~0.2-0.4s)")
    
    print("🎉 Fast configuration test completed successfully!")

if __name__ == "__main__":
    test_fast_config()