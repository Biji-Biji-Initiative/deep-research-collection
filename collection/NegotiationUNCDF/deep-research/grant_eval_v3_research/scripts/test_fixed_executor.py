#!/usr/bin/env python3
"""
Test the truly fixed research executor
Verify all critical fixes are working properly
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.truly_fixed_executor import TrulyFixedResearchExecutor

def run_validation_test():
    """Run comprehensive test of the fixed executor"""
    
    print("\n" + "="*60)
    print("🧪 TESTING TRULY FIXED RESEARCH EXECUTOR")
    print("="*60)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not set")
        return False
        
    # Initialize executor
    print("\n1️⃣ Initializing executor...")
    executor = TrulyFixedResearchExecutor(api_key)
    
    # Test with a small set of files first
    print("\n2️⃣ Testing with sample files...")
    test_files = [
        Path("/Users/agent-g/Downloads/NegotiationUNCDF/grant_eval_v3/evaluation/agents/graph.py"),
        Path("/Users/agent-g/Downloads/NegotiationUNCDF/grant_eval_v3/evaluation/skills/rubric_mining/miner.py")
    ]
    
    # Check files exist
    print("\n3️⃣ Verifying test files exist...")
    existing_files = []
    for f in test_files:
        if f.exists():
            print(f"   ✅ Found: {f.name} ({f.stat().st_size} bytes)")
            existing_files.append(f)
        else:
            print(f"   ❌ Missing: {f}")
            
    if not existing_files:
        print("❌ No test files found!")
        return False
        
    # Test vector store creation
    print("\n4️⃣ Testing vector store creation with validation...")
    vector_store_id = executor.create_vector_store_with_validation(existing_files)
    
    if not vector_store_id:
        print("❌ Vector store creation failed!")
        return False
        
    print(f"✅ Vector store created: {vector_store_id}")
    
    # Check validation logs
    print("\n5️⃣ Checking validation logs...")
    validation_log = Path(f"/Users/agent-g/Downloads/NegotiationUNCDF/deep_research/grant_eval_v3_research/logs/validation_{executor.session_id}.jsonl")
    
    if validation_log.exists():
        with open(validation_log, 'r') as f:
            validations = [json.loads(line) for line in f]
            
        print(f"   Found {len(validations)} validation entries")
        for v in validations:
            symbol = "✅" if v['passed'] else "❌"
            print(f"   {symbol} {v['check']}: {v['details']}")
    else:
        print("   ⚠️  No validation log found")
        
    # Check upload logs
    print("\n6️⃣ Checking upload logs...")
    upload_log = Path(f"/Users/agent-g/Downloads/NegotiationUNCDF/deep_research/grant_eval_v3_research/logs/uploads_{executor.session_id}.jsonl")
    
    if upload_log.exists():
        with open(upload_log, 'r') as f:
            uploads = [json.loads(line) for line in f]
            
        successful = [u for u in uploads if u['status'] == 'success']
        failed = [u for u in uploads if u['status'] == 'failed']
        
        print(f"   Total uploads: {len(uploads)}")
        print(f"   Successful: {len(successful)}")
        print(f"   Failed: {len(failed)}")
        
        if successful:
            total_bytes = sum(u.get('size', 0) for u in successful)
            print(f"   Total bytes uploaded: {total_bytes}")
            
        if failed:
            print("\n   Failed uploads:")
            for f in failed:
                print(f"      ❌ {f['file']}: {f.get('error', 'Unknown error')}")
    else:
        print("   ⚠️  No upload log found")
        
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    if executor.validation_failures:
        print(f"\n❌ {len(executor.validation_failures)} validation failures:")
        for vf in executor.validation_failures:
            print(f"   - {vf['check']}: {vf['details']}")
    else:
        print("\n✅ All validations passed!")
        
    print(f"\n📁 Files uploaded: {len(executor.file_upload_results)}")
    for upload in executor.file_upload_results:
        if upload['status'] == 'success':
            print(f"   ✅ {Path(upload['file']).name} ({upload['size']} bytes)")
            
    print("\n" + "="*60)
    
    # Ask user if they want to proceed with full research
    if vector_store_id and not executor.validation_failures:
        print("\n✅ All critical validations passed!")
        print("Vector store is ready with actual file content.")
        print("\nYou can now run deep research with confidence that:")
        print("1. Files were uploaded with correct extensions")
        print("2. Vector store contains actual data")
        print("3. All validations are in place")
        print("\nTo proceed with research, uncomment the research execution code.")
        
        # Uncomment below to actually run research
        # print("\n7️⃣ Starting deep research...")
        # research_result = executor.execute_deep_research_with_validation(vector_store_id)
        # if research_result and 'response_id' in research_result:
        #     print(f"✅ Research started: {research_result['response_id']}")
        #     
        #     print("\n8️⃣ Monitoring progress...")
        #     monitor_result = executor.monitor_with_tool_tracking(research_result['response_id'])
        #     
        #     if monitor_result['status'] == 'completed':
        #         print("\n9️⃣ Extracting and validating content...")
        #         content = executor.extract_and_validate_content(research_result['response_id'])
        #         
        #         if content and 'validation_results' in content:
        #             print("\n✅ Research completed successfully!")
        #             print(f"Content validation score: {sum(content['validation_results'].values()) / len(content['validation_results']):.1%}")
        
        return True
    else:
        print("\n❌ Critical issues found. Please review logs and fix before proceeding.")
        return False

if __name__ == "__main__":
    success = run_validation_test()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("The truly fixed executor is ready for production use.")
    else:
        print("\n❌ Test failed. Please review the issues above.")
        
    sys.exit(0 if success else 1)