#!/usr/bin/env python3
"""
Grant Evaluation v3 Deep Research Executor
Comprehensive, self-healing research with full logging and verification
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from openai import OpenAI
from datetime import datetime
import traceback

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WORKSPACE_ROOT = "/Users/agent-g/Downloads/NegotiationUNCDF"
RESEARCH_ROOT = Path(__file__).parent.parent

class GrantEvalV3ResearchExecutor:
    def __init__(self, api_key: str):
        """Initialize the research executor with comprehensive logging"""
        self.client = OpenAI(api_key=api_key, timeout=3600)
        self.research_results = {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Setup comprehensive logging
        self._setup_logging()
        
        # Log initialization
        self.logger.info(f"🔧 Research Executor initialized with session ID: {self.session_id}")
        self.logger.info(f"📁 Research root: {RESEARCH_ROOT}")
        self.logger.info(f"🏠 Workspace root: {WORKSPACE_ROOT}")
        
    def _setup_logging(self):
        """Setup comprehensive logging for all operations"""
        log_dir = RESEARCH_ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create session-specific log file
        log_file = log_dir / f"research_session_{self.session_id}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(f"GrantEvalV3Research_{self.session_id}")
        self.logger.info("📝 Logging system initialized")
        
    def log_api_response(self, operation: str, response: Any, error: Optional[str] = None):
        """Log all API responses for debugging and self-healing"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "response_id": getattr(response, 'id', None),
            "status": getattr(response, 'status', None),
            "error": error,
            "response_attributes": [attr for attr in dir(response) if not attr.startswith('_')],
            "response_dict": self._safe_dict(response)
        }
        
        # Save to session log
        self.logger.info(f"🔍 API Response Log: {json.dumps(log_entry, indent=2, default=str)}")
        
        # Save detailed response to file
        response_log_file = RESEARCH_ROOT / "logs" / f"api_responses_{self.session_id}.jsonl"
        with open(response_log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def _safe_dict(self, obj: Any) -> Dict[str, Any]:
        """Safely convert object to dictionary for logging"""
        try:
            if hasattr(obj, '__dict__'):
                return {k: str(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
            elif hasattr(obj, 'model_dump'):
                return obj.model_dump()
            else:
                return {"type": str(type(obj)), "str": str(obj)}
        except Exception as e:
            return {"error": f"Could not serialize: {e}"}
    
    def create_vector_store(self, files: List[Path]) -> Optional[str]:
        """Create vector store with comprehensive logging"""
        try:
            self.logger.info("🔧 Creating vector store...")
            
            # Log the request
            request_data = {
                "name": "grant_eval_v3_analysis",
                "metadata": {
                    "purpose": "Grant Evaluation v3 system analysis",
                    "session_id": self.session_id,
                    "created_at": datetime.now().isoformat()
                }
            }
            self.logger.info(f"📤 Vector store creation request: {json.dumps(request_data, indent=2)}")
            
            # Create vector store
            response = self.client.vector_stores.create(**request_data)
            
            # Log the response
            self.log_api_response("vector_store_create", response)
            
            vector_store_id = response.id
            self.logger.info(f"✅ Vector store created: {vector_store_id}")
            
            # Add files with detailed logging
            successful_uploads = 0
            failed_uploads = 0
            
            for file_path in files:
                if file_path.exists() and file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if not content.strip():
                            self.logger.warning(f"⚠️  Skipping empty file: {file_path.name}")
                            continue
                        
                        # Upload file
                        file_id = self._upload_file(file_path, content)
                        if file_id:
                            # Add to vector store
                            self.client.vector_stores.files.create(
                                vector_store_id=vector_store_id,
                                file_id=file_id
                            )
                            successful_uploads += 1
                            self.logger.info(f"   📄 Added: {file_path.name}")
                        else:
                            failed_uploads += 1
                            
                    except Exception as e:
                        failed_uploads += 1
                        self.logger.error(f"   ❌ Failed to process {file_path.name}: {e}")
                        continue
            
            self.logger.info(f"📊 File upload summary: {successful_uploads} successful, {failed_uploads} failed")
            return vector_store_id
            
        except Exception as e:
            self.logger.error(f"❌ Error creating vector store: {e}")
            self.logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
            return None
    
    def _upload_file(self, file_path: Path, content: str) -> Optional[str]:
        """Upload file with comprehensive error handling and logging"""
        try:
            # Create temporary file
            temp_file = Path(f"/tmp/{file_path.name}_{self.session_id}")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Upload to OpenAI
            with open(temp_file, 'rb') as f:
                response = self.client.files.create(
                    file=f,
                    purpose="assistants"
                )
            
            # Log the upload response
            self.log_api_response("file_upload", response)
            
            # Clean up
            temp_file.unlink()
            
            return response.id
            
        except Exception as e:
            self.logger.error(f"❌ Error uploading {file_path.name}: {e}")
            self.logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
            return None
    
    def execute_deep_research(self, vector_store_id: str) -> Dict[str, Any]:
        """Execute deep research with comprehensive logging"""
        try:
            self.logger.info("🚀 Starting deep research analysis...")
            
            # Load research prompt
            prompt_file = RESEARCH_ROOT / "config" / "research_prompt.md"
            if not prompt_file.exists():
                # Fallback to deep_research folder
                prompt_file = Path(__file__).parent.parent.parent / "grant_eval_v3_deep_research_prompt.md"
            
            if not prompt_file.exists():
                raise FileNotFoundError(f"Research prompt not found: {prompt_file}")
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                research_prompt = f.read()
            
            self.logger.info(f"📋 Research prompt loaded from: {prompt_file}")
            
            # Create research input
            research_input = f"""
{research_prompt}

## 🔍 EXECUTION INSTRUCTIONS

Please analyze the Grant Evaluation v3 system using the files provided in the vector store. 
Focus on the specific analysis requirements outlined above and provide structured findings.

Use the file search capabilities to examine:
1. Current implementation code in grant_eval_v3/evaluation/
2. Historical implementations in evaluation_agent/ and evaluation_agent_v2/
3. Supporting infrastructure and documentation
4. Implementation plans and specifications

Provide your analysis in the exact format specified in the research output format section.
"""
            
            # Log the research request
            request_data = {
                "model": "o4-mini-deep-research",
                "input": research_input,
                "background": True,
                "tools": [
                    {
                        "type": "file_search",
                        "vector_store_ids": [vector_store_id]
                    },
                    {
                        "type": "code_interpreter",
                        "container": {"type": "auto"}
                    }
                ]
            }
            
            self.logger.info(f"📤 Research request: {json.dumps({**request_data, 'input': '[TRUNCATED]'}, indent=2)}")
            
            # Execute research
            response = self.client.responses.create(**request_data)
            
            # Log the response
            self.log_api_response("deep_research_create", response)
            
            self.logger.info(f"✅ Deep research started successfully!")
            self.logger.info(f"🆔 Response ID: {response.id}")
            self.logger.info(f"📊 Status: {response.status}")
            
            return {
                "response_id": response.id,
                "status": response.status,
                "started_at": datetime.now().isoformat(),
                "vector_store_id": vector_store_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error starting deep research: {e}")
            self.logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
            return {"error": str(e)}
    
    def monitor_research_progress(self, response_id: str, max_wait_time: int = 3600) -> Dict[str, Any]:
        """Monitor research progress with comprehensive logging"""
        self.logger.info(f"⏳ Monitoring research progress (max wait: {max_wait_time}s)...")
        
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < max_wait_time:
            try:
                check_count += 1
                self.logger.info(f"🔄 Progress check #{check_count}")
                
                # Check response status
                response = self.client.responses.retrieve(response_id)
                
                # Log every status check
                self.log_api_response(f"progress_check_{check_count}", response)
                
                self.logger.info(f"   📊 Status: {response.status}")
                
                if response.status == "completed":
                    self.logger.info("   ✅ Research completed successfully!")
                    return {
                        "status": "completed",
                        "response_id": response_id,
                        "completed_at": datetime.now().isoformat(),
                        "check_count": check_count
                    }
                elif response.status == "failed":
                    error_msg = getattr(response, 'error', 'Unknown error')
                    self.logger.error(f"   ❌ Research failed: {error_msg}")
                    return {
                        "status": "failed",
                        "response_id": response_id,
                        "error": error_msg,
                        "check_count": check_count
                    }
                elif response.status == "in_progress":
                    self.logger.info("   🔄 Research in progress...")
                else:
                    self.logger.info(f"   ⏳ Status: {response.status}")
                
                # Wait before next check
                self.logger.info("   🔄 Waiting 60 seconds before next check...")
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"   ⚠️  Error checking status: {e}")
                self.logger.error(f"   🔍 Full traceback: {traceback.format_exc()}")
                time.sleep(60)
        
        self.logger.warning(f"   ⏰ Timeout reached after {check_count} checks")
        return {
            "status": "timeout",
            "response_id": response_id,
            "message": "Research timeout reached",
            "check_count": check_count
        }
    
    def retrieve_research_results(self, response_id: str) -> Dict[str, Any]:
        """Retrieve research results with comprehensive error handling"""
        try:
            self.logger.info(f"📊 Retrieving research results...")
            
            # Get the response
            response = self.client.responses.retrieve(response_id)
            
            # Log the retrieval response
            self.log_api_response("results_retrieval", response)
            
            if response.status == "completed":
                # Try to get results - log what we actually have
                self.logger.info("✅ Research completed, examining response structure...")
                
                # Log all available attributes
                available_attrs = [attr for attr in dir(response) if not attr.startswith('_')]
                self.logger.info(f"📋 Available response attributes: {available_attrs}")
                
                # Try to extract content from various possible locations
                result_data = {
                    "response_id": response_id,
                    "status": response.status,
                    "retrieved_at": datetime.now().isoformat(),
                    "available_attributes": available_attrs,
                    "response_content": self._safe_dict(response)
                }
                
                # Check for content in common locations
                for attr in ['content', 'output', 'result', 'data']:
                    if hasattr(response, attr):
                        value = getattr(response, attr)
                        self.logger.info(f"📄 Found {attr}: {type(value)} - {str(value)[:200]}...")
                        result_data[f"attr_{attr}"] = value
                
                # NEW: Extract the actual analysis content
                if hasattr(response, 'output') and response.output:
                    self.logger.info("🔍 Extracting analysis content from output...")
                    analysis_content = self._extract_analysis_content(response.output)
                    if analysis_content:
                        result_data["extracted_analysis"] = analysis_content
                        self.logger.info("✅ Successfully extracted analysis content!")
                    else:
                        self.logger.warning("⚠️  Could not extract analysis content from output")
                
                self.logger.info("   ✅ Results structure analyzed successfully!")
                
                return result_data
            else:
                self.logger.warning(f"   ⚠️  Research not complete: {response.status}")
                return {
                    "status": response.status,
                    "response_id": response_id,
                    "message": "Research not complete"
                }
                
        except Exception as e:
            self.logger.error(f"   ❌ Error retrieving results: {e}")
            self.logger.error(f"   🔍 Full traceback: {traceback.format_exc()}")
            return {"error": str(e)}
    
    def _extract_analysis_content(self, output_data: Any) -> Optional[Dict[str, Any]]:
        """Extract human-readable analysis content from the deep research output"""
        try:
            if not output_data:
                return None
            
            # Convert to string if it's not already
            if isinstance(output_data, str):
                output_str = output_data
            else:
                output_str = str(output_data)
            
            # Look for the actual analysis content
            analysis_content = {}
            
            # Parse the output to find different types of content
            if "ResponseOutputMessage" in output_str:
                # Extract the main analysis text
                import re
                
                # Find the main analysis text
                text_match = re.search(r'ResponseOutputText\([^)]*text="([^"]*)"', output_str)
                if text_match:
                    analysis_text = text_match.group(1)
                    # Unescape the text
                    analysis_text = analysis_text.replace('\\n', '\n').replace('\\"', '"')
                    analysis_content["main_analysis"] = analysis_text
                    self.logger.info(f"📝 Extracted main analysis ({len(analysis_text)} characters)")
                
                # Find reasoning items
                reasoning_items = re.findall(r'ResponseReasoningItem\([^)]*\)', output_str)
                if reasoning_items:
                    analysis_content["reasoning_items"] = reasoning_items
                    self.logger.info(f"🧠 Found {len(reasoning_items)} reasoning items")
                
                # Find code interpreter calls
                code_calls = re.findall(r'ResponseCodeInterpreterToolCall\([^)]*\)', output_str)
                if code_calls:
                    analysis_content["code_interpreter_calls"] = code_calls
                    self.logger.info(f"💻 Found {len(code_calls)} code interpreter calls")
                
                # Find tool usage
                tool_usage = re.findall(r'FileSearchTool\([^)]*\)', output_str)
                if tool_usage:
                    analysis_content["file_search_usage"] = tool_usage
                    self.logger.info(f"🔍 Found {len(tool_usage)} file search tool usages")
            
            # If we found analysis content, create a clean summary
            if analysis_content:
                # Create a clean, readable summary
                clean_summary = {
                    "extraction_timestamp": datetime.now().isoformat(),
                    "content_types_found": list(analysis_content.keys()),
                    "analysis_summary": self._create_analysis_summary(analysis_content)
                }
                
                # Add the raw extracted content
                clean_summary["extracted_content"] = analysis_content
                
                return clean_summary
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting analysis content: {e}")
            self.logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
            return None
    
    def _create_analysis_summary(self, analysis_content: Dict[str, Any]) -> Dict[str, Any]:
        """Create a clean summary of the extracted analysis"""
        summary = {
            "extraction_success": True,
            "content_overview": {}
        }
        
        try:
            # Summarize main analysis
            if "main_analysis" in analysis_content:
                main_text = analysis_content["main_analysis"]
                summary["content_overview"]["main_analysis"] = {
                    "length": len(main_text),
                    "preview": main_text[:500] + "..." if len(main_text) > 500 else main_text,
                    "sections": self._identify_analysis_sections(main_text)
                }
            
            # Summarize reasoning items
            if "reasoning_items" in analysis_content:
                summary["content_overview"]["reasoning_items"] = {
                    "count": len(analysis_content["reasoning_items"]),
                    "types": list(set([item.split("type='")[1].split("'")[0] if "type='" in item else "unknown" for item in analysis_content["reasoning_items"]]))
                }
            
            # Summarize tool usage
            if "code_interpreter_calls" in analysis_content:
                summary["content_overview"]["code_interpreter_calls"] = {
                    "count": len(analysis_content["code_interpreter_calls"]),
                    "statuses": list(set([call.split("status='")[1].split("'")[0] if "status='" in call else "unknown" for call in analysis_content["code_interpreter_calls"]]))
                }
            
            if "file_search_usage" in analysis_content:
                summary["content_overview"]["file_search_usage"] = {
                    "count": len(analysis_content["file_search_usage"])
                }
            
        except Exception as e:
            self.logger.error(f"❌ Error creating analysis summary: {e}")
            summary["extraction_success"] = False
            summary["error"] = str(e)
        
        return summary
    
    def _identify_analysis_sections(self, text: str) -> List[str]:
        """Identify main sections in the analysis text"""
        try:
            sections = []
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('### ') and len(line) > 4:
                    section_title = line[4:].strip()
                    sections.append(section_title)
                elif line.startswith('## ') and len(line) > 3:
                    section_title = line[3:].strip()
                    sections.append(section_title)
                elif line.startswith('# ') and len(line) > 2:
                    section_title = line[2:].strip()
                    sections.append(section_title)
            
            return sections[:10]  # Limit to first 10 sections
            
        except Exception as e:
            self.logger.error(f"❌ Error identifying analysis sections: {e}")
            return []
    
    def save_results(self, results: Dict[str, Any]):
        """Save all results with comprehensive metadata"""
        if not results:
            self.logger.error("❌ No results to save")
            return
            
        # Create results directory
        results_dir = RESEARCH_ROOT / "results" / self.session_id
        results_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"💾 Saving research results to {results_dir}...")
        
        # Save detailed results
        results_file = results_dir / "research_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        self.logger.info(f"   📄 Detailed results: {results_file}")
        
        # Save session summary
        summary_file = results_dir / "session_summary.md"
        self._generate_session_summary(results, summary_file)
        self.logger.info(f"   📋 Session summary: {summary_file}")
        
        # Save configuration
        config_file = results_dir / "session_config.json"
        config = {
            "session_id": self.session_id,
            "workspace_root": WORKSPACE_ROOT,
            "research_root": str(RESEARCH_ROOT),
            "started_at": datetime.now().isoformat(),
            "model_used": "o4-mini-deep-research",
            "files_analyzed": self._get_analyzed_files()
        }
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2, default=str)
        self.logger.info(f"   ⚙️  Session config: {config_file}")
        
        # Copy logs to results directory
        log_source = RESEARCH_ROOT / "logs" / f"research_session_{self.session_id}.log"
        log_dest = results_dir / "session.log"
        if log_source.exists():
            import shutil
            shutil.copy2(log_source, log_dest)
            self.logger.info(f"   📝 Session log: {log_dest}")
        
        # Copy API response logs
        api_log_source = RESEARCH_ROOT / "logs" / f"api_responses_{self.session_id}.jsonl"
        api_log_dest = results_dir / "api_responses.jsonl"
        if api_log_source.exists():
            import shutil
            shutil.copy2(api_log_source, api_log_dest)
            self.logger.info(f"   🔍 API response log: {api_log_dest}")
    
    def _generate_session_summary(self, results: Dict[str, Any], output_file: Path):
        """Generate comprehensive session summary"""
        with open(output_file, 'w') as f:
            f.write(f"# Grant Evaluation v3 Research Session Summary\n\n")
            f.write(f"**Session ID**: {self.session_id}\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Session Execution\n\n")
            f.write(f"**Model Used**: o4-mini-deep-research\n")
            f.write(f"**Response ID**: {results.get('response_id', 'Unknown')}\n")
            f.write(f"**Status**: {results.get('status', 'Unknown')}\n")
            f.write(f"**Retrieved**: {results.get('retrieved_at', 'Unknown')}\n\n")
            
            if results.get("available_attributes"):
                f.write("## Response Structure Analysis\n\n")
                f.write("**Available Response Attributes**:\n")
                for attr in results.get("available_attributes", []):
                    f.write(f"- {attr}\n")
                f.write("\n")
            
            if results.get("error"):
                f.write("## Errors Encountered\n\n")
                f.write(f"**Error**: {results['error']}\n\n")
            
            # NEW: Add extracted analysis summary
            if results.get("extracted_analysis"):
                f.write("## Extracted Analysis Content\n\n")
                extracted = results["extracted_analysis"]
                f.write(f"**Content Types Found**: {', '.join(extracted.get('content_types_found', []))}\n\n")
                
                if "analysis_summary" in extracted:
                    summary = extracted["analysis_summary"]
                    if "content_overview" in summary:
                        f.write("**Content Overview**:\n")
                        for content_type, details in summary["content_overview"].items():
                            if isinstance(details, dict):
                                f.write(f"- **{content_type}**: {details.get('count', 'N/A')} items\n")
                                if "sections" in details and details["sections"]:
                                    f.write(f"  - Sections: {', '.join(details['sections'][:5])}\n")
                            else:
                                f.write(f"- **{content_type}**: {details}\n")
                        f.write("\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. Review the detailed results and API response logs\n")
            f.write("2. Analyze the extracted analysis content\n")
            f.write("3. Use the findings to improve the Grant Evaluation v3 system\n")
            f.write("4. Re-run research if needed with corrected approach\n")
    
    def _get_analyzed_files(self) -> List[str]:
        """Get list of files that were analyzed"""
        analyzed_files = []
        
        # Core v3 system files
        v3_paths = [
            "grant_eval_v3/evaluation/skills/rubric_mining/",
            "grant_eval_v3/evaluation/agents/",
            "grant_eval_v3/evaluation/skills/retrieval/",
            "grant_eval_v3/evaluation/skills/scoring/",
            "grant_eval_v3/evaluation/infra/",
            "grant_eval_v3/docs/",
            "grant_eval_v3/projects/",
            "grant_eval_v3/runs/"
        ]
        
        # Historical implementation files
        historical_paths = [
            "evaluation_agent/",
            "evaluation_agent_v2/"
        ]
        
        # Supporting infrastructure
        infrastructure_paths = [
            "deep_research/",
            "evaluation_framework/",
            "conversion_engine/"
        ]
        
        # Add all paths
        all_paths = v3_paths + historical_paths + infrastructure_paths
        
        for path_str in all_paths:
            path = Path(WORKSPACE_ROOT) / path_str
            if path.exists():
                if path.is_dir():
                    # For directories, find all Python, Markdown, and text files
                    for file_path in path.rglob("*"):
                        if file_path.is_file() and file_path.suffix.lower() in ['.py', '.md', '.txt', '.csv', '.json', '.yaml', '.yml']:
                            analyzed_files.append(str(file_path.relative_to(Path(WORKSPACE_ROOT))))
                else:
                    # For individual files, add them directly
                    analyzed_files.append(str(path.relative_to(Path(WORKSPACE_ROOT))))
        
        return analyzed_files
    
    def _identify_analysis_files(self) -> List[Path]:
        """Identify files and directories to analyze"""
        files_to_analyze = []
        workspace_path = Path(WORKSPACE_ROOT)
        
        # Core v3 system files
        v3_paths = [
            "grant_eval_v3/evaluation/skills/rubric_mining/",
            "grant_eval_v3/evaluation/agents/",
            "grant_eval_v3/evaluation/skills/retrieval/",
            "grant_eval_v3/evaluation/skills/scoring/",
            "grant_eval_v3/evaluation/infra/",
            "grant_eval_v3/docs/",
            "grant_eval_v3/projects/",
            "grant_eval_v3/runs/"
        ]
        
        # Historical implementation files
        historical_paths = [
            "evaluation_agent/",
            "evaluation_agent_v2/"
        ]
        
        # Supporting infrastructure
        infrastructure_paths = [
            "deep_research/",
            "evaluation_framework/",
            "conversion_engine/"
        ]
        
        # Add all paths
        all_paths = v3_paths + historical_paths + infrastructure_paths
        
        for path_str in all_paths:
            path = workspace_path / path_str
            if path.exists():
                if path.is_dir():
                    # For directories, find all Python, Markdown, and text files
                    for file_path in path.rglob("*"):
                        if file_path.is_file() and file_path.suffix.lower() in ['.py', '.md', '.txt', '.csv', '.json', '.yaml', '.yml']:
                            files_to_analyze.append(file_path)
                else:
                    # For individual files, add them directly
                    files_to_analyze.append(file_path)
                self.logger.info(f"   📂 {path_str}")
        
        return files_to_analyze
    
    def run_complete_analysis(self, max_wait_time: int = 3600):
        """Run the complete research analysis workflow with comprehensive logging"""
        self.logger.info("🎯 Starting Grant Evaluation v3 Deep Research Analysis")
        self.logger.info("=" * 70)
        
        try:
            # Step 1: Identify files to analyze
            self.logger.info("📁 Identifying files for analysis...")
            files_to_analyze = self._identify_analysis_files()
            
            if not files_to_analyze:
                self.logger.error("❌ No files found for analysis")
                return False
            
            self.logger.info(f"✅ Found {len(files_to_analyze)} files for analysis")
            
            # Step 2: Create vector store
            self.logger.info("🔧 Creating vector store for analysis...")
            vector_store_id = self.create_vector_store(files_to_analyze)
            
            if not vector_store_id:
                self.logger.error("❌ Failed to create vector store")
                return False
            
            # Step 3: Execute deep research
            self.logger.info("🚀 Executing deep research analysis...")
            research_start = self.execute_deep_research(vector_store_id)
            
            if "error" in research_start:
                self.logger.error(f"❌ Failed to start research: {research_start['error']}")
                return False
            
            # Step 4: Monitor progress
            self.logger.info("⏳ Monitoring research progress...")
            progress = self.monitor_research_progress(
                research_start["response_id"], 
                max_wait_time
            )
            
            # Step 5: Retrieve results
            if progress.get("status") == "completed":
                self.logger.info("📊 Retrieving research results...")
                results = self.retrieve_research_results(progress["response_id"])
                
                # Step 6: Save results
                self.save_results(results)
                
                self.logger.info("🎉 Deep Research Analysis Complete!")
                self.logger.info(f"📁 Check the results directory: {RESEARCH_ROOT}/results/{self.session_id}")
                return True
            else:
                self.logger.warning(f"⚠️  Research did not complete: {progress.get('status', 'Unknown')}")
                if progress.get("error"):
                    self.logger.error(f"   Error: {progress['error']}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Critical error in research workflow: {e}")
            self.logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
            return False

def main():
    """Main execution function"""
    print("🔍 Grant Evaluation v3 Deep Research Executor")
    print("=" * 50)
    
    # Check API key
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY is not set. Export it in your environment before running.")
        print("   For example: export OPENAI_API_KEY=...\n")
        return
    
    # Initialize executor
    executor = GrantEvalV3ResearchExecutor(OPENAI_API_KEY)
    
    # Run complete analysis
    success = executor.run_complete_analysis()
    
    if success:
        print("\n✅ Analysis completed successfully!")
        print(f"📁 Check the results directory: {RESEARCH_ROOT}/results/{executor.session_id}")
        print("\nNext steps:")
        print("1. Review the detailed results and logs")
        print("2. Analyze the API response structure")
        print("3. Update the executor based on findings")
    else:
        print("\n❌ Analysis failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
