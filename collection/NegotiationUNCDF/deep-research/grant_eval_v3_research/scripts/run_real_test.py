#!/usr/bin/env python3
"""
Run the truly fixed executor with REAL API calls
No more test mode - let's see what actually happens
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.truly_fixed_executor import TrulyFixedResearchExecutor

def run_real_execution():
    """Execute real research with full validation and monitoring"""
    
    print("\n" + "="*60)
    print("🚀 RUNNING REAL DEEP RESEARCH EXECUTION")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Setup API key from environment or file
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Try to read from .env file
        env_file = Path.home() / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"')
                        break
    
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found")
        print("Please set OPENAI_API_KEY environment variable or add to ~/.env")
        return False
    
    print("✅ API key found")
    
    # Initialize executor
    print("\n📦 Initializing truly fixed executor...")
    executor = TrulyFixedResearchExecutor(api_key)
    
    # Identify target files for analysis
    print("\n📁 Identifying target files...")
    workspace_root = Path("/Users/agent-g/Downloads/NegotiationUNCDF")
    
    target_files = []
    
    # Look for grant_eval_v3 files
    grant_eval_dir = workspace_root / "grant_eval_v3"
    if grant_eval_dir.exists():
        # Key implementation files
        key_files = [
            "evaluation/agents/graph.py",
            "evaluation/agents/registry.py", 
            "evaluation/skills/rubric_mining/miner.py",
            "evaluation/skills/scoring/scorer.py",
            "evaluation/models/base.py",
            "evaluation/utils/llm.py"
        ]
        
        for file_path in key_files:
            full_path = grant_eval_dir / file_path
            if full_path.exists():
                target_files.append(full_path)
                print(f"   ✅ Found: {file_path} ({full_path.stat().st_size:,} bytes)")
            else:
                print(f"   ⚠️  Missing: {file_path}")
    
    # Also include our research scripts for meta-analysis
    research_dir = workspace_root / "deep_research/grant_eval_v3_research"
    if research_dir.exists():
        research_files = [
            "scripts/research_executor.py",  # Original broken version
            "scripts/truly_fixed_executor.py",  # Fixed version
            "BRUTAL_TRUTH_LESSONS.md"  # Lessons learned
        ]
        
        for file_path in research_files:
            full_path = research_dir / file_path
            if full_path.exists():
                target_files.append(full_path)
                print(f"   ✅ Found: {file_path} ({full_path.stat().st_size:,} bytes)")
    
    if not target_files:
        print("\n❌ No target files found!")
        return False
    
    print(f"\n📊 Total files to analyze: {len(target_files)}")
    total_size = sum(f.stat().st_size for f in target_files)
    print(f"📏 Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    
    try:
        # Step 1: Create and validate vector store
        print("\n" + "="*40)
        print("STEP 1: CREATE VECTOR STORE")
        print("="*40)
        
        vector_store_id = executor.create_vector_store_with_validation(target_files)
        
        if not vector_store_id:
            print("❌ CRITICAL: Vector store creation failed!")
            return False
        
        print(f"\n✅ Vector store ready: {vector_store_id}")
        
        # Check validation failures so far
        if executor.validation_failures:
            print(f"\n⚠️  {len(executor.validation_failures)} validation issues found:")
            for vf in executor.validation_failures:
                print(f"   - {vf['check']}: {vf['details']}")
            print("\n❌ Cannot proceed with validation failures")
            return False
        
        # Step 2: Execute deep research
        print("\n" + "="*40)
        print("STEP 2: EXECUTE DEEP RESEARCH")
        print("="*40)
        
        research_result = executor.execute_deep_research_with_validation(vector_store_id)
        
        if not research_result or 'error' in research_result:
            print(f"❌ Research execution failed: {research_result}")
            return False
        
        response_id = research_result['response_id']
        print(f"\n✅ Research started: {response_id}")
        
        # Step 3: Monitor progress
        print("\n" + "="*40)
        print("STEP 3: MONITOR PROGRESS")
        print("="*40)
        
        monitor_result = executor.monitor_with_tool_tracking(
            response_id, 
            max_wait=1200  # 20 minutes max
        )
        
        if monitor_result['status'] != 'completed':
            print(f"❌ Research did not complete: {monitor_result}")
            return False
        
        print(f"\n✅ Research completed in {monitor_result['duration']:.1f} seconds")
        
        # Step 4: Extract and validate content
        print("\n" + "="*40)
        print("STEP 4: EXTRACT & VALIDATE CONTENT")
        print("="*40)
        
        content_result = executor.extract_and_validate_content(response_id)
        
        if not content_result or 'error' in content_result:
            print(f"❌ Content extraction failed: {content_result}")
            return False
        
        # Save results
        results_dir = research_dir / "results" / executor.session_id
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Save raw content
        content_file = results_dir / "analysis_content.md"
        with open(content_file, 'w') as f:
            f.write(f"# Deep Research Analysis\n")
            f.write(f"Session: {executor.session_id}\n")
            f.write(f"Response ID: {response_id}\n\n")
            f.write(content_result.get('raw_content', ''))
        
        print(f"\n📄 Content saved to: {content_file}")
        
        # Save execution summary
        summary = {
            "session_id": executor.session_id,
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": len(target_files),
            "total_size_bytes": total_size,
            "vector_store_id": vector_store_id,
            "response_id": response_id,
            "execution_time": monitor_result['duration'],
            "validation_results": content_result.get('validation_results', {}),
            "validation_failures": executor.validation_failures,
            "file_upload_results": executor.file_upload_results,
            "tool_execution_count": len(executor.tool_execution_log)
        }
        
        summary_file = results_dir / "execution_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📄 Summary saved to: {summary_file}")
        
        # Final validation report
        print("\n" + "="*60)
        print("📊 FINAL VALIDATION REPORT")
        print("="*60)
        
        validation_results = content_result.get('validation_results', {})
        if validation_results:
            passed = sum(validation_results.values())
            total = len(validation_results)
            score = passed / total if total > 0 else 0
            
            print(f"\nContent Validation Score: {score:.1%}")
            for check, result in validation_results.items():
                symbol = "✅" if result else "❌"
                print(f"   {symbol} {check}: {result}")
            
            if score < 0.5:
                print("\n⚠️  WARNING: Low validation score - content may be generic")
        
        print(f"\n📁 Files uploaded: {len(executor.file_upload_results)}")
        print(f"🔧 Tool executions: {len(executor.tool_execution_log)}")
        print(f"❌ Validation failures: {len(executor.validation_failures)}")
        
        # Check logs
        print("\n📄 Log files created:")
        log_dir = research_dir / "logs"
        for log_file in log_dir.glob(f"*{executor.session_id}*"):
            size = log_file.stat().st_size
            print(f"   - {log_file.name} ({size:,} bytes)")
        
        print("\n" + "="*60)
        print("✅ EXECUTION COMPLETE")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        print(traceback.format_exc())
        
        # Save error report
        error_file = research_dir / "logs" / f"error_{executor.session_id}.txt"
        with open(error_file, 'w') as f:
            f.write(f"Error at {datetime.now().isoformat()}\n")
            f.write(f"Session: {executor.session_id}\n\n")
            f.write(str(e) + "\n\n")
            f.write(traceback.format_exc())
        
        print(f"\n📄 Error details saved to: {error_file}")
        return False

if __name__ == "__main__":
    success = run_real_execution()
    
    if success:
        print("\n🎉 Real execution completed successfully!")
        print("Check the results and logs directories for detailed output.")
    else:
        print("\n❌ Execution failed. Check logs for details.")
    
    sys.exit(0 if success else 1)