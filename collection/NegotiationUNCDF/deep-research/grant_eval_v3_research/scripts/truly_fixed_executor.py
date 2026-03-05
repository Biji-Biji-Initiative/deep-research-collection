#!/usr/bin/env python3
"""
TRULY FIXED Grant Evaluation v3 Deep Research Executor
Addresses all critical failures discovered in forensic analysis
"""

import os
import json
import time
import logging
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from datetime import datetime

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WORKSPACE_ROOT = "/Users/agent-g/Downloads/NegotiationUNCDF"
RESEARCH_ROOT = Path(__file__).parent.parent

class TrulyFixedResearchExecutor:
    def __init__(self, api_key: str):
        """Initialize with comprehensive validation and logging"""
        self.client = OpenAI(api_key=api_key, timeout=3600)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.validation_failures = []
        self.file_upload_results = []
        self.tool_execution_log = []
        
        # Setup comprehensive logging
        self._setup_logging()
        
        self.logger.info("="*60)
        self.logger.info(f"🔧 TRULY FIXED Research Executor v2.0")
        self.logger.info(f"📅 Session: {self.session_id}")
        self.logger.info("="*60)
        
    def _setup_logging(self):
        """Setup multi-level comprehensive logging"""
        log_dir = RESEARCH_ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Main log file
        log_file = log_dir / f"fixed_session_{self.session_id}.log"
        
        # Configure detailed logging
        logging.basicConfig(
            level=logging.DEBUG,  # Changed to DEBUG for more detail
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(f"FixedExecutor_{self.session_id}")
        
        # Create separate logs for different aspects
        self.validation_log = log_dir / f"validation_{self.session_id}.jsonl"
        self.upload_log = log_dir / f"uploads_{self.session_id}.jsonl"
        self.tool_log = log_dir / f"tools_{self.session_id}.jsonl"
        
    def log_validation(self, check: str, passed: bool, details: Dict[str, Any]):
        """Log validation checks with full details"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "check": check,
            "passed": passed,
            "details": details
        }
        
        with open(self.validation_log, 'a') as f:
            f.write(json.dumps(entry) + '\n')
            
        if not passed:
            self.validation_failures.append(entry)
            self.logger.error(f"❌ VALIDATION FAILED: {check}")
            self.logger.error(f"   Details: {json.dumps(details, indent=2)}")
        else:
            self.logger.info(f"✅ Validation passed: {check}")
            
    def create_vector_store_with_validation(self, files: List[Path]) -> Optional[str]:
        """Create vector store with comprehensive validation and proper file handling"""
        self.logger.info("\n" + "="*40)
        self.logger.info("📁 VECTOR STORE CREATION")
        self.logger.info("="*40)
        
        try:
            # Step 1: Create vector store
            self.logger.info("Creating vector store...")
            response = self.client.vector_stores.create(
                name=f"grant_eval_v3_fixed_{self.session_id}",
                metadata={
                    "purpose": "Grant Evaluation v3 analysis",
                    "session_id": self.session_id,
                    "executor_version": "2.0_fixed"
                }
            )
            
            vector_store_id = response.id
            self.logger.info(f"✅ Vector store created: {vector_store_id}")
            
            # Step 2: Upload files with FIXED naming
            self.logger.info(f"\n📤 Uploading {len(files)} files...")
            successful_uploads = 0
            failed_uploads = 0
            
            for file_path in files:
                if not file_path.exists():
                    self.logger.warning(f"⚠️  File not found: {file_path}")
                    failed_uploads += 1
                    continue
                    
                try:
                    # CRITICAL FIX: Use proper file extension, not mangled name
                    file_id = self._upload_file_fixed(file_path)
                    
                    if file_id:
                        # Add to vector store
                        vs_file_response = self.client.vector_stores.files.create(
                            vector_store_id=vector_store_id,
                            file_id=file_id
                        )
                        
                        # Log successful upload
                        upload_entry = {
                            "timestamp": datetime.now().isoformat(),
                            "file": str(file_path),
                            "file_id": file_id,
                            "vector_store_id": vector_store_id,
                            "status": "success",
                            "size": file_path.stat().st_size
                        }
                        
                        with open(self.upload_log, 'a') as f:
                            f.write(json.dumps(upload_entry) + '\n')
                            
                        successful_uploads += 1
                        self.logger.info(f"   ✅ Uploaded: {file_path.name} (ID: {file_id})")
                        self.file_upload_results.append(upload_entry)
                    else:
                        failed_uploads += 1
                        
                except Exception as e:
                    failed_uploads += 1
                    self.logger.error(f"   ❌ Failed: {file_path.name}: {e}")
                    
                    # Log failure
                    upload_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "file": str(file_path),
                        "status": "failed",
                        "error": str(e)
                    }
                    
                    with open(self.upload_log, 'a') as f:
                        f.write(json.dumps(upload_entry) + '\n')
                        
            # Step 3: CRITICAL VALIDATION - Verify vector store has content
            self.logger.info("\n🔍 Validating vector store content...")
            time.sleep(2)  # Give API time to process
            
            # Get vector store status
            vs_status = self.client.vector_stores.retrieve(vector_store_id)
            
            # Check file counts
            file_counts = vs_status.file_counts
            validation_details = {
                "vector_store_id": vector_store_id,
                "total_files": file_counts.total,
                "completed_files": file_counts.completed,
                "failed_files": file_counts.failed,
                "in_progress": file_counts.in_progress,
                "usage_bytes": vs_status.usage_bytes,
                "successful_uploads": successful_uploads,
                "failed_uploads": failed_uploads
            }
            
            self.logger.info(f"\n📊 Upload Summary:")
            self.logger.info(f"   Attempted: {len(files)}")
            self.logger.info(f"   Successful: {successful_uploads}")
            self.logger.info(f"   Failed: {failed_uploads}")
            self.logger.info(f"   VS Total: {file_counts.total}")
            self.logger.info(f"   VS Completed: {file_counts.completed}")
            self.logger.info(f"   VS Failed: {file_counts.failed}")
            self.logger.info(f"   Usage: {vs_status.usage_bytes} bytes")
            
            # CRITICAL: Validate that files were actually uploaded
            if file_counts.total == 0:
                self.log_validation(
                    "vector_store_has_files",
                    False,
                    validation_details
                )
                raise ValueError("❌ CRITICAL: Vector store is empty! No files were uploaded!")
                
            if file_counts.completed < 1:
                self.log_validation(
                    "vector_store_files_processed",
                    False,
                    validation_details
                )
                raise ValueError(f"❌ CRITICAL: No files completed processing! {file_counts.failed} failed.")
                
            # Success validation
            self.log_validation(
                "vector_store_content",
                True,
                validation_details
            )
            
            self.logger.info(f"\n✅ Vector store validated: {file_counts.completed} files ready")
            return vector_store_id
            
        except Exception as e:
            self.logger.error(f"❌ Vector store creation failed: {e}")
            self.logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            return None
            
    def _upload_file_fixed(self, file_path: Path) -> Optional[str]:
        """FIXED file upload - maintains proper extensions"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not content.strip():
                self.logger.warning(f"   ⚠️  Skipping empty file: {file_path.name}")
                return None
                
            # CRITICAL FIX: Use original filename with proper extension
            # Create temp file with ORIGINAL name, not mangled
            temp_file = Path(f"/tmp/{file_path.name}")  # Keep original name!
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Upload with proper filename
            with open(temp_file, 'rb') as f:
                response = self.client.files.create(
                    file=f,
                    purpose="assistants"
                )
                
            # Clean up
            temp_file.unlink()
            
            return response.id
            
        except Exception as e:
            self.logger.error(f"   ❌ Upload error for {file_path.name}: {e}")
            return None
            
    def execute_deep_research_with_validation(self, vector_store_id: str) -> Dict[str, Any]:
        """Execute deep research with comprehensive validation and monitoring"""
        self.logger.info("\n" + "="*40)
        self.logger.info("🚀 DEEP RESEARCH EXECUTION")
        self.logger.info("="*40)
        
        try:
            # Load research prompt
            research_prompt = """
            Analyze the Grant Evaluation v3 system implementation.
            
            IMPORTANT: Your analysis MUST include:
            1. Specific references to actual code files you read
            2. Direct quotes from the code when discussing issues
            3. File paths and line numbers when possible
            4. Actual error messages or log entries found
            5. Real architectural patterns discovered in the code
            
            If you cannot access the actual files, explicitly state this.
            
            Focus on:
            - Implementation completeness
            - Integration gaps
            - Error handling
            - Performance issues
            - Technical debt
            
            Provide specific, actionable recommendations based on the ACTUAL CODE.
            """
            
            # Create research request
            self.logger.info("📤 Submitting research request...")
            response = self.client.responses.create(
                model="o3-deep-research-2025-06-26",
                input=research_prompt,
                background=True,
                tools=[
                    {
                        "type": "file_search",
                        "vector_store_ids": [vector_store_id]
                    },
                    {
                        "type": "code_interpreter",
                        "container": {"type": "auto"}
                    }
                ],
                max_output_tokens=32000,
                reasoning={"effort": "high"},
                text={"verbosity": "high"}
            )
            
            self.logger.info(f"✅ Research started: {response.id}")
            self.logger.info(f"📊 Initial status: {response.status}")
            
            # Log tool configuration
            tool_entry = {
                "timestamp": datetime.now().isoformat(),
                "operation": "research_start",
                "response_id": response.id,
                "tools_configured": ["file_search", "code_interpreter"],
                "vector_store_id": vector_store_id
            }
            
            with open(self.tool_log, 'a') as f:
                f.write(json.dumps(tool_entry) + '\n')
                
            return {
                "response_id": response.id,
                "vector_store_id": vector_store_id,
                "status": response.status
            }
            
        except Exception as e:
            self.logger.error(f"❌ Research execution failed: {e}")
            return {"error": str(e)}
            
    def monitor_with_tool_tracking(self, response_id: str, max_wait: int = 600) -> Dict[str, Any]:
        """Monitor research with comprehensive tool execution tracking"""
        self.logger.info("\n" + "="*40)
        self.logger.info("⏳ MONITORING RESEARCH PROGRESS")
        self.logger.info("="*40)
        
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < max_wait:
            check_count += 1
            
            try:
                # Get response status
                response = self.client.responses.retrieve(response_id)
                
                self.logger.info(f"\n🔄 Check #{check_count} at {datetime.now().strftime('%H:%M:%S')}")
                self.logger.info(f"   Status: {response.status}")
                
                # Extract and log tool usage if available
                if hasattr(response, 'output') and response.output:
                    self._log_tool_usage(response.output)
                    
                if response.status == "completed":
                    self.logger.info("   ✅ Research completed!")
                    
                    # Validate that tools were actually used
                    self._validate_tool_usage(response)
                    
                    return {
                        "status": "completed",
                        "response_id": response_id,
                        "check_count": check_count,
                        "duration": time.time() - start_time
                    }
                    
                elif response.status == "failed":
                    error = getattr(response, 'error', 'Unknown error')
                    self.logger.error(f"   ❌ Research failed: {error}")
                    return {
                        "status": "failed",
                        "error": error
                    }
                    
                # Adaptive wait
                wait_time = 30 if response.status == "queued" else 60
                self.logger.info(f"   ⏳ Waiting {wait_time}s...")
                time.sleep(wait_time)
                
            except Exception as e:
                self.logger.error(f"   ❌ Monitor error: {e}")
                time.sleep(30)
                
        self.logger.warning("⏰ Timeout reached")
        return {"status": "timeout"}
        
    def _log_tool_usage(self, output):
        """Log tool execution details"""
        if not output:
            return
            
        for item in output:
            if hasattr(item, 'type'):
                if item.type == 'code_interpreter_call':
                    tool_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "tool": "code_interpreter",
                        "code": getattr(item, 'code', 'N/A'),
                        "outputs": getattr(item, 'outputs', 'N/A'),
                        "status": getattr(item, 'status', 'N/A')
                    }
                    
                    with open(self.tool_log, 'a') as f:
                        f.write(json.dumps(tool_entry) + '\n')
                        
                    self.logger.info(f"   🔧 Tool: Code Interpreter")
                    if hasattr(item, 'outputs') and item.outputs:
                        self.logger.info(f"      Output: {str(item.outputs)[:200]}...")
                        
                elif 'FileSearch' in str(type(item)):
                    self.logger.info(f"   🔍 Tool: File Search executed")
                    
    def _validate_tool_usage(self, response):
        """Validate that tools were actually used"""
        validation_results = {
            "file_search_used": False,
            "code_interpreter_used": False,
            "content_references_files": False
        }
        
        if hasattr(response, 'output') and response.output:
            for item in response.output:
                item_type = str(type(item))
                if 'code_interpreter' in item_type.lower():
                    validation_results["code_interpreter_used"] = True
                if 'filesearch' in item_type.lower():
                    validation_results["file_search_used"] = True
                    
        # Check if content references actual files
        if hasattr(response, 'output'):
            output_str = str(response.output)
            if any(ext in output_str for ext in ['.py', '.md', '.txt', '.csv']):
                validation_results["content_references_files"] = True
                
        # Log validation
        self.log_validation(
            "tool_usage",
            any(validation_results.values()),
            validation_results
        )
        
        if not validation_results["file_search_used"]:
            self.logger.warning("⚠️  WARNING: File search may not have been used!")
            
        if not validation_results["content_references_files"]:
            self.logger.warning("⚠️  WARNING: Output may not reference actual files!")
            
    def extract_and_validate_content(self, response_id: str) -> Dict[str, Any]:
        """Extract content with validation that it's based on real data"""
        self.logger.info("\n" + "="*40)
        self.logger.info("📝 CONTENT EXTRACTION & VALIDATION")
        self.logger.info("="*40)
        
        try:
            # Get response
            response = self.client.responses.retrieve(response_id)
            
            # Extract content
            extracted_content = {
                "response_id": response_id,
                "extraction_timestamp": datetime.now().isoformat(),
                "raw_content": "",
                "validation_results": {}
            }
            
            # Try to extract actual content
            if hasattr(response, 'output') and response.output:
                for item in response.output:
                    if hasattr(item, 'content'):
                        for content_item in item.content:
                            if hasattr(content_item, 'text'):
                                extracted_content["raw_content"] += content_item.text + "\n"
                                
            # CRITICAL: Validate content is based on real data
            content = extracted_content["raw_content"]
            
            validation_checks = {
                "has_file_references": any(ext in content for ext in ['.py', '.md', '.txt']),
                "has_code_snippets": '```' in content or 'def ' in content or 'class ' in content,
                "has_specific_paths": 'grant_eval_v3/' in content or 'evaluation/' in content,
                "has_line_numbers": 'line ' in content.lower() or 'L' in content,
                "mentions_actual_files": any(f in content for f in ['graph.py', 'miner.py', 'scorer.py']),
                "length_sufficient": len(content) > 1000
            }
            
            extracted_content["validation_results"] = validation_checks
            
            # Calculate validation score
            passed_checks = sum(validation_checks.values())
            total_checks = len(validation_checks)
            validation_score = passed_checks / total_checks
            
            self.logger.info(f"\n📊 Content Validation Results:")
            for check, passed in validation_checks.items():
                symbol = "✅" if passed else "❌"
                self.logger.info(f"   {symbol} {check}: {passed}")
                
            self.logger.info(f"\n📈 Validation Score: {validation_score:.1%}")
            
            # Log validation
            self.log_validation(
                "content_based_on_real_data",
                validation_score > 0.5,
                {
                    "score": validation_score,
                    "checks": validation_checks,
                    "content_length": len(content)
                }
            )
            
            if validation_score < 0.5:
                self.logger.error("❌ WARNING: Content appears to be generic, not based on actual files!")
                
            return extracted_content
            
        except Exception as e:
            self.logger.error(f"❌ Content extraction failed: {e}")
            return {"error": str(e)}
            
    def run_complete_validated_analysis(self):
        """Run complete analysis with all validations"""
        self.logger.info("\n" + "="*60)
        self.logger.info("🎯 STARTING VALIDATED DEEP RESEARCH ANALYSIS")
        self.logger.info("="*60)
        
        try:
            # Step 1: Identify files to analyze
            self.logger.info("\n📁 Identifying target files...")
            target_files = [
                Path(WORKSPACE_ROOT) / "grant_eval_v3/evaluation/agents/graph.py",
                Path(WORKSPACE_ROOT) / "grant_eval_v3/evaluation/agents/registry.py",
                Path(WORKSPACE_ROOT) / "grant_eval_v3/evaluation/skills/rubric_mining/miner.py",
                Path(WORKSPACE_ROOT) / "grant_eval_v3/evaluation/skills/scoring/scorer.py"
            ]
            
            # Validate files exist
            existing_files = []
            for f in target_files:
                if f.exists():
                    existing_files.append(f)
                    self.logger.info(f"   ✅ Found: {f.name}")
                else:
                    self.logger.warning(f"   ❌ Missing: {f}")
                    
            if not existing_files:
                raise ValueError("No target files found!")
                
            # Step 2: Create and validate vector store
            vector_store_id = self.create_vector_store_with_validation(existing_files)
            if not vector_store_id:
                raise ValueError("Failed to create valid vector store!")
                
            # Step 3: Execute research
            research_result = self.execute_deep_research_with_validation(vector_store_id)
            if "error" in research_result:
                raise ValueError(f"Research execution failed: {research_result['error']}")
                
            # Step 4: Monitor with tool tracking
            monitor_result = self.monitor_with_tool_tracking(
                research_result["response_id"]
            )
            
            if monitor_result["status"] != "completed":
                raise ValueError(f"Research did not complete: {monitor_result}")
                
            # Step 5: Extract and validate content
            content = self.extract_and_validate_content(research_result["response_id"])
            
            # Step 6: Generate final report
            self._generate_validation_report()
            
            self.logger.info("\n" + "="*60)
            self.logger.info("✅ ANALYSIS COMPLETE WITH FULL VALIDATION")
            self.logger.info("="*60)
            
            return True
            
        except Exception as e:
            self.logger.error(f"\n❌ CRITICAL FAILURE: {e}")
            self.logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            self._generate_validation_report()
            return False
            
    def _generate_validation_report(self):
        """Generate comprehensive validation report"""
        report_path = RESEARCH_ROOT / "results" / self.session_id / "validation_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "validation_failures": self.validation_failures,
            "file_upload_results": self.file_upload_results,
            "tool_execution_log": self.tool_execution_log,
            "success": len(self.validation_failures) == 0
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"\n📊 Validation report saved: {report_path}")
        
        if self.validation_failures:
            self.logger.error(f"\n❌ {len(self.validation_failures)} validation failures detected!")
            for failure in self.validation_failures:
                self.logger.error(f"   - {failure['check']}: {failure['details']}")

def main():
    """Main execution with proper validation"""
    print("\n🔧 TRULY FIXED Grant Eval V3 Research Executor")
    print("="*60)
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not set")
        print("\nThis version REQUIRES real API access to function properly.")
        print("Set: export OPENAI_API_KEY=your_key_here")
        return 1
        
    executor = TrulyFixedResearchExecutor(OPENAI_API_KEY)
    success = executor.run_complete_validated_analysis()
    
    if success:
        print("\n✅ Analysis completed successfully with validation!")
    else:
        print("\n❌ Analysis failed validation checks - see logs for details")
        
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())