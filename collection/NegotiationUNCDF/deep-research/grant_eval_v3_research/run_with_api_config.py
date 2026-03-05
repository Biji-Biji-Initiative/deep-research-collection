#!/usr/bin/env python3
"""
Enhanced Real Test Executor with Comprehensive API Key Management
Uses the new API configuration system for robust key handling
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from config.api_config import get_api_config_manager, ensure_openai_api_key, print_api_status
    from scripts.truly_fixed_executor import TrulyFixedResearchExecutor
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure you're running this from the project root directory")
    sys.exit(1)

def main():
    """Main execution function with comprehensive API key handling"""
    
    print("\n" + "="*70)
    print("🚀 DEEP RESEARCH SYSTEM - ENHANCED REAL EXECUTION")
    print("="*70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Step 1: Configure API keys
    print("\n🔧 STEP 1: API KEY CONFIGURATION")
    print("-" * 40)
    
    try:
        # Try to get API key with our new system
        api_key = ensure_openai_api_key(interactive=True)
        print("✅ OpenAI API key successfully configured")
        
    except RuntimeError as e:
        print(f"❌ API key configuration failed: {e}")
        print("\n💡 Suggested actions:")
        print("1. Run: python setup_api_keys.py")
        print("2. Or set environment variable: export OPENAI_API_KEY=your_key")
        print("3. Or create ~/.env file with your key")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during API setup: {e}")
        return False
    
    # Step 2: Show configuration status
    print("\n📊 STEP 2: CONFIGURATION STATUS")
    print("-" * 40)
    print_api_status()
    
    # Step 3: Initialize and run executor
    print(f"\n🚀 STEP 3: EXECUTE DEEP RESEARCH")
    print("-" * 40)
    
    try:
        success = run_real_execution(api_key)
        return success
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Execution failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_real_execution(api_key: str) -> bool:
    """Execute real research with full validation and monitoring"""
    
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
        print("\n" + "="*50)
        print("PHASE 1: CREATE & VALIDATE VECTOR STORE")
        print("="*50)
        
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
        print("\n" + "="*50)
        print("PHASE 2: EXECUTE DEEP RESEARCH ANALYSIS")
        print("="*50)
        
        research_result = executor.execute_deep_research_with_validation(vector_store_id)
        
        if not research_result or 'error' in research_result:
            print(f"❌ Research execution failed: {research_result}")
            return False
        
        response_id = research_result['response_id']
        print(f"\n✅ Research started: {response_id}")
        
        # Step 3: Monitor progress
        print("\n" + "="*50)
        print("PHASE 3: MONITOR EXECUTION PROGRESS")
        print("="*50)
        
        monitor_result = executor.monitor_with_tool_tracking(
            response_id, 
            max_wait=1200  # 20 minutes max
        )
        
        if monitor_result['status'] != 'completed':
            print(f"❌ Research did not complete: {monitor_result}")
            return False
        
        print(f"\n✅ Research completed in {monitor_result['duration']:.1f} seconds")
        
        # Step 4: Extract and validate content
        print("\n" + "="*50)
        print("PHASE 4: EXTRACT & VALIDATE RESULTS")
        print("="*50)
        
        content_result = executor.extract_and_validate_content(response_id)
        
        if not content_result or 'error' in content_result:
            print(f"❌ Content extraction failed: {content_result}")
            return False
        
        # Save results with enhanced metadata
        results_dir = research_dir / "results" / executor.session_id
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Save raw content
        content_file = results_dir / "deep_research_analysis.md"
        with open(content_file, 'w') as f:
            f.write(f"# Deep Research Analysis Report\n\n")
            f.write(f"**Session ID:** `{executor.session_id}`\n")
            f.write(f"**Response ID:** `{response_id}`\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n")
            f.write(f"**Execution Time:** {monitor_result['duration']:.1f} seconds\n")
            f.write(f"**Files Analyzed:** {len(target_files)}\n")
            f.write(f"**Total Size:** {total_size:,} bytes\n\n")
            f.write("---\n\n")
            f.write(content_result.get('raw_content', ''))
        
        print(f"\n📄 Analysis report saved: {content_file}")
        
        # Create enhanced execution summary
        api_manager = get_api_config_manager()
        api_status = api_manager.get_status()
        
        summary = {
            "execution_metadata": {
                "session_id": executor.session_id,
                "timestamp": datetime.now().isoformat(),
                "response_id": response_id,
                "execution_time_seconds": monitor_result['duration'],
                "vector_store_id": vector_store_id
            },
            "input_analysis": {
                "files_analyzed": len(target_files),
                "total_size_bytes": total_size,
                "average_file_size": total_size // len(target_files) if target_files else 0,
                "file_list": [str(f) for f in target_files]
            },
            "api_configuration": {
                "openai_configured": api_status["openai_configured"],
                "openai_valid": api_status["openai_valid"],
                "ready_for_execution": api_status["ready_for_execution"],
                "configuration_sources": api_status["sources_checked"]
            },
            "execution_results": {
                "validation_results": content_result.get('validation_results', {}),
                "validation_failures": executor.validation_failures,
                "file_upload_results": executor.file_upload_results,
                "tool_execution_count": len(executor.tool_execution_log),
                "tool_execution_log": executor.tool_execution_log
            },
            "quality_metrics": {
                "content_validation_score": None,
                "validation_checks_passed": 0,
                "total_validation_checks": 0
            }
        }
        
        # Calculate quality metrics
        validation_results = content_result.get('validation_results', {})
        if validation_results:
            passed = sum(validation_results.values())
            total = len(validation_results)
            summary["quality_metrics"].update({
                "content_validation_score": passed / total if total > 0 else 0,
                "validation_checks_passed": passed,
                "total_validation_checks": total
            })
        
        summary_file = results_dir / "execution_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"📄 Detailed summary saved: {summary_file}")
        
        # Final validation report
        print("\n" + "="*70)
        print("📊 EXECUTION COMPLETION REPORT")
        print("="*70)
        
        validation_results = content_result.get('validation_results', {})
        if validation_results:
            passed = sum(validation_results.values())
            total = len(validation_results)
            score = passed / total if total > 0 else 0
            
            print(f"\n🎯 Content Quality Score: {score:.1%} ({passed}/{total} checks passed)")
            for check, result in validation_results.items():
                symbol = "✅" if result else "❌"
                print(f"   {symbol} {check}")
            
            if score >= 0.8:
                print("\n🎉 HIGH QUALITY: Analysis appears comprehensive and specific")
            elif score >= 0.6:
                print("\n✅ GOOD QUALITY: Analysis is reasonable with minor issues")
            elif score >= 0.4:
                print("\n⚠️  MODERATE QUALITY: Analysis may be somewhat generic")
            else:
                print("\n❌ LOW QUALITY: Analysis appears generic or incomplete")
        else:
            print("\n⚠️  No validation results available")
        
        print(f"\n📊 Execution Statistics:")
        print(f"   📁 Files processed: {len(executor.file_upload_results)}")
        print(f"   🔧 Tool executions: {len(executor.tool_execution_log)}")
        print(f"   ❌ Validation failures: {len(executor.validation_failures)}")
        print(f"   ⏱️  Total runtime: {monitor_result['duration']:.1f} seconds")
        
        # Show log file locations
        print(f"\n📄 Generated Files:")
        print(f"   📝 Analysis: {content_file}")
        print(f"   📊 Summary: {summary_file}")
        
        log_dir = research_dir / "logs"
        log_files = list(log_dir.glob(f"*{executor.session_id}*"))
        if log_files:
            print(f"   📋 Logs: {len(log_files)} files in {log_dir}")
            for log_file in log_files:
                size = log_file.stat().st_size
                print(f"     - {log_file.name} ({size:,} bytes)")
        
        print("\n" + "="*70)
        print("✅ DEEP RESEARCH EXECUTION COMPLETED SUCCESSFULLY")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ CRITICAL EXECUTION ERROR: {e}")
        import traceback
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        
        # Save comprehensive error report
        error_dir = research_dir / "logs" / "errors"
        error_dir.mkdir(parents=True, exist_ok=True)
        
        error_file = error_dir / f"error_{executor.session_id}_{int(time.time())}.txt"
        with open(error_file, 'w') as f:
            f.write(f"DEEP RESEARCH EXECUTION ERROR\n")
            f.write("="*50 + "\n\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Session ID: {executor.session_id}\n")
            f.write(f"API Key Status: {'Configured' if api_key else 'Missing'}\n")
            f.write(f"Target Files: {len(target_files)}\n\n")
            f.write(f"Error Message:\n{str(e)}\n\n")
            f.write("Full Traceback:\n")
            f.write(traceback.format_exc())
            
            if hasattr(executor, 'validation_failures') and executor.validation_failures:
                f.write(f"\nValidation Failures ({len(executor.validation_failures)}):\n")
                for vf in executor.validation_failures:
                    f.write(f"- {vf['check']}: {vf['details']}\n")
        
        print(f"\n📄 Error report saved to: {error_file}")
        return False

def check_requirements():
    """Check system requirements before execution"""
    print("\n🔍 Checking System Requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check required modules
    required_modules = ['openai', 'pathlib', 'json', 'yaml']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Install with: pip install openai pyyaml")
        return False
    
    print("✅ System requirements satisfied")
    return True

if __name__ == "__main__":
    print("🧠 Deep Research System - Enhanced Execution")
    
    # Check requirements first
    if not check_requirements():
        sys.exit(1)
    
    try:
        success = main()
        
        if success:
            print("\n🎉 EXECUTION SUCCESSFUL!")
            print("Check the results directory for detailed analysis output.")
            print("Thank you for using the Deep Research System!")
        else:
            print("\n❌ EXECUTION FAILED")
            print("Check error logs for details or run: python setup_api_keys.py")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Execution cancelled by user. Goodbye!")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)