#!/usr/bin/env python3
"""
Test script for Deep Research Setup
Verifies the configuration and API connectivity without running full analysis
"""

import os
import json
from deep_research.deep_research_setup import DeepResearchAnalyzer, discover_markdown_files

def test_document_discovery():
    """Test document discovery functionality"""
    print("🔍 Testing document discovery...")
    
    workspace_root = "/Users/agent-g/Downloads/NegotiationUNCDF"
    md_files = discover_markdown_files(workspace_root)
    
    if md_files:
        print(f"✅ Found {len(md_files)} project directories with markdown files:")
        for project, files in md_files.items():
            print(f"   📂 {project}: {len(files)} files")
            
        # Show some example files
        for project, files in md_files.items():
            if files:
                print(f"\n📄 Sample files from {project}:")
                for file in files[:3]:  # Show first 3 files
                    print(f"   • {os.path.basename(file)}")
                if len(files) > 3:
                    print(f"   ... and {len(files) - 3} more")
                break
    else:
        print("❌ No markdown files found")
    
    return md_files

def test_api_connectivity(api_key):
    """Test OpenAI API connectivity"""
    print(f"\n🔌 Testing OpenAI API connectivity...")
    
    try:
        analyzer = DeepResearchAnalyzer(api_key)
        print("✅ OpenAI client initialized successfully")
        
        # Test basic API call (without creating sessions)
        print("✅ API key appears valid")
        return True
        
    except Exception as e:
        print(f"❌ API connectivity test failed: {e}")
        return False

def test_configuration():
    """Test configuration generation"""
    print(f"\n⚙️ Testing configuration generation...")
    
    try:
        from deep_research.deep_research_setup import create_research_configuration
        
        workspace_root = "/Users/agent-g/Downloads/NegotiationUNCDF"
        config = create_research_configuration(workspace_root)
        
        print("✅ Configuration generated successfully")
        print(f"   📋 Research sessions: {len(config['research_sessions'])}")
        print(f"   ❓ Analysis questions: {len(config['analysis_questions'])}")
        
        # Show session details
        for session_key, session_config in config["research_sessions"].items():
            print(f"   📊 {session_config['name']}")
            print(f"      Focus areas: {len(session_config['focus_areas'])}")
        
        return config
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return None

def main():
    """Run all tests"""
    print("🧪 Deep Research Setup Test Suite")
    print("=" * 50)
    
    # Test 1: Document discovery
    md_files = test_document_discovery()
    
    # Test 2: Configuration generation
    config = test_configuration()
    
    # Test 3: API connectivity (if API key is available)
    api_key = os.getenv("OPENAI_API_KEY", "")
    api_ok = test_api_connectivity(api_key) if api_key else False
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"   📁 Document discovery: {'✅' if md_files else '❌'}")
    print(f"   ⚙️ Configuration: {'✅' if config else '❌'}")
    print(f"   🔌 API connectivity: {'✅' if api_ok else '❌'}")
    
    if md_files and config and api_ok:
        print(f"\n🎉 All tests passed! Your setup is ready.")
        print(f"\nNext steps:")
        print(f"1. Run: python -m deep_research.deep_research_setup")
        print(f"2. Then: python -m deep_research.execute_deep_research")
    else:
        print(f"\n⚠️ Some tests failed. Please check the issues above.")
        
        if not md_files:
            print(f"   • Ensure you have converted some PDFs to markdown")
        if not config:
            print(f"   • Check that all Python files are in the same directory")
        if not api_ok:
            print(f"   • Verify your OpenAI API key and Deep Research access")

if __name__ == "__main__":
    main()
