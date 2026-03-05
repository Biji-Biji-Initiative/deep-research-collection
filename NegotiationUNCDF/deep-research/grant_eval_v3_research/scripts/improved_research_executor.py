#!/usr/bin/env python3
"""
IMPROVED Grant Evaluation v3 Deep Research Executor
Enhanced version with better content extraction, error handling, and monitoring
Addresses issues identified from previous run: 20250830_202518
"""

import os
import json
import time
import logging
import re
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from openai import OpenAI
from datetime import datetime
import traceback
from dataclasses import dataclass
from enum import Enum

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WORKSPACE_ROOT = "/Users/agent-g/Downloads/NegotiationUNCDF"
RESEARCH_ROOT = Path(__file__).parent.parent

class ResearchStatus(Enum):
    """Research execution status"""
    INITIALIZING = "initializing"
    PREPARING_FILES = "preparing_files"
    CREATING_VECTOR_STORE = "creating_vector_store"
    STARTING_RESEARCH = "starting_research"
    MONITORING_PROGRESS = "monitoring_progress"
    EXTRACTING_CONTENT = "extracting_content"
    SAVING_RESULTS = "saving_results"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ProgressMetrics:
    """Track detailed progress metrics"""
    stage: ResearchStatus
    start_time: datetime
    files_processed: int = 0
    total_files: int = 0
    api_calls_made: int = 0
    errors_encountered: int = 0
    current_operation: str = ""
    estimated_completion: Optional[datetime] = None

class ImprovedGrantEvalV3ResearchExecutor:
    """Enhanced research executor with improved content extraction and monitoring"""
    
    def __init__(self, api_key: str, debug_mode: bool = True):
        """Initialize with enhanced configuration"""
        self.client = OpenAI(api_key=api_key, timeout=3600)
        self.debug_mode = debug_mode
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Enhanced tracking
        self.progress = ProgressMetrics(
            stage=ResearchStatus.INITIALIZING,
            start_time=datetime.now()
        )
        self.research_results = {}
        self.api_response_history = []
        self.extraction_attempts = []
        
        # Setup enhanced logging
        self._setup_enhanced_logging()
        
        # Performance tracking
        self.performance_metrics = {
            "token_usage": {"input": 0, "output": 0},
            "api_call_times": [],
            "processing_times": {},
            "extraction_success_rate": 0.0
        }
        
        self.logger.info(f"🚀 Enhanced Research Executor initialized")
        self.logger.info(f"   Session ID: {self.session_id}")
        self.logger.info(f"   Debug Mode: {self.debug_mode}")
        self.logger.info(f"   Research Root: {RESEARCH_ROOT}")
        
    def _setup_enhanced_logging(self):
        """Enhanced logging with multiple output formats"""
        log_dir = RESEARCH_ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create session-specific log files
        session_log = log_dir / f"enhanced_session_{self.session_id}.log"
        debug_log = log_dir / f"debug_{self.session_id}.log"
        api_log = log_dir / f"api_detailed_{self.session_id}.jsonl"
        
        # Configure multi-level logging
        logging.basicConfig(
            level=logging.DEBUG if self.debug_mode else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(session_log),
                logging.FileHandler(debug_log, mode='w'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(f"ImprovedResearch_{self.session_id}")
        self.api_logger = logging.getLogger(f"APIDetails_{self.session_id}")
        
        # Create file handler for API logs
        api_handler = logging.FileHandler(api_log)
        api_handler.setLevel(logging.INFO)
        self.api_logger.addHandler(api_handler)
        
        self.logger.info("✅ Enhanced logging system initialized")
        
    def _update_progress(self, stage: ResearchStatus, operation: str = "", **kwargs):
        """Update progress tracking with detailed metrics"""
        self.progress.stage = stage
        self.progress.current_operation = operation
        
        # Update specific metrics
        for key, value in kwargs.items():
            if hasattr(self.progress, key):
                setattr(self.progress, key, value)
                
        # Log progress update
        elapsed = (datetime.now() - self.progress.start_time).total_seconds()
        self.logger.info(f"📊 Progress Update: {stage.value}")
        self.logger.info(f"   Operation: {operation}")
        self.logger.info(f"   Elapsed: {elapsed:.1f}s")
        
        if self.progress.total_files > 0:
            completion_pct = (self.progress.files_processed / self.progress.total_files) * 100
            self.logger.info(f"   Files: {self.progress.files_processed}/{self.progress.total_files} ({completion_pct:.1f}%)")
            
    def enhanced_api_call(self, operation: str, api_call_func, *args, **kwargs) -> Tuple[Any, bool]:
        """Enhanced API call wrapper with retry logic and detailed tracking"""
        max_retries = 3
        backoff_factor = 2
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                self.logger.debug(f"🔄 API Call: {operation} (attempt {attempt + 1})")
                
                # Execute API call
                response = api_call_func(*args, **kwargs)
                
                # Track timing
                call_time = time.time() - start_time
                self.performance_metrics["api_call_times"].append(call_time)
                self.progress.api_calls_made += 1
                
                # Enhanced logging
                self.log_enhanced_api_response(operation, response, call_time)
                
                self.logger.info(f"✅ API Call successful: {operation} ({call_time:.2f}s)")
                return response, True
                
            except Exception as e:
                wait_time = backoff_factor ** attempt
                self.progress.errors_encountered += 1
                
                self.logger.warning(f"⚠️ API Call failed: {operation} (attempt {attempt + 1})")
                self.logger.warning(f"   Error: {str(e)}")
                
                if attempt < max_retries - 1:
                    self.logger.info(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"❌ API Call failed after {max_retries} attempts: {operation}")
                    self.logger.error(f"   Final error: {str(e)}")
                    return None, False
                    
    def log_enhanced_api_response(self, operation: str, response: Any, call_time: float):
        """Enhanced API response logging with structured data extraction"""
        try:
            # Extract basic information
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "call_time": call_time,
                "response_id": getattr(response, 'id', None),
                "status": getattr(response, 'status', None),
                "model": getattr(response, 'model', None),
                "usage": {}
            }
            
            # Extract usage information if available
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                if hasattr(usage, 'input_tokens'):
                    response_data["usage"]["input_tokens"] = usage.input_tokens
                    self.performance_metrics["token_usage"]["input"] += usage.input_tokens
                if hasattr(usage, 'output_tokens'):
                    response_data["usage"]["output_tokens"] = usage.output_tokens
                    self.performance_metrics["token_usage"]["output"] += usage.output_tokens
                if hasattr(usage, 'total_tokens'):
                    response_data["usage"]["total_tokens"] = usage.total_tokens
                    
            # Extract output structure information
            if hasattr(response, 'output') and response.output:
                response_data["output_structure"] = self._analyze_output_structure(response.output)
                
            # Store for history
            self.api_response_history.append(response_data)
            
            # Log to API logger
            self.api_logger.info(json.dumps(response_data))
            
            if self.debug_mode:
                self.logger.debug(f"📋 API Response Details: {json.dumps(response_data, indent=2)}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to log API response: {e}")
            
    def _analyze_output_structure(self, output: Any) -> Dict[str, Any]:
        """Analyze the structure of the API response output"""
        structure = {
            "type": str(type(output)),
            "is_list": isinstance(output, list),
            "length": len(output) if hasattr(output, '__len__') else None,
            "item_types": [],
            "message_items": 0,
            "reasoning_items": 0,
            "tool_calls": 0
        }
        
        try:
            if isinstance(output, list):
                for item in output:
                    item_type = str(type(item))
                    structure["item_types"].append(item_type)
                    
                    # Count specific item types
                    if 'Message' in item_type:
                        structure["message_items"] += 1
                    elif 'Reasoning' in item_type:
                        structure["reasoning_items"] += 1
                    elif 'ToolCall' in item_type:
                        structure["tool_calls"] += 1
                        
            return structure
            
        except Exception as e:
            structure["analysis_error"] = str(e)
            return structure
            
    def create_vector_store_enhanced(self, files: List[Path]) -> Optional[str]:
        """Enhanced vector store creation with better error handling"""
        self._update_progress(
            ResearchStatus.CREATING_VECTOR_STORE, 
            "Creating vector store with enhanced error handling",
            total_files=len(files)
        )
        
        try:
            # Create vector store with enhanced metadata
            request_data = {
                "name": f"grant_eval_v3_enhanced_{self.session_id}",
                "metadata": {
                    "purpose": "Enhanced Grant Evaluation v3 system analysis",
                    "session_id": self.session_id,
                    "created_at": datetime.now().isoformat(),
                    "executor_version": "improved",
                    "total_files": len(files),
                    "analysis_mode": "comprehensive"
                }
            }
            
            self.logger.info(f"🔧 Creating enhanced vector store...")
            self.logger.debug(f"   Request: {json.dumps(request_data, indent=2)}")
            
            # Create with retry logic
            response, success = self.enhanced_api_call(
                "vector_store_create",
                self.client.vector_stores.create,
                **request_data
            )
            
            if not success or not response:
                self.logger.error("❌ Failed to create vector store")
                return None
                
            vector_store_id = response.id
            self.logger.info(f"✅ Vector store created: {vector_store_id}")
            
            # Enhanced file processing
            return self._process_files_enhanced(vector_store_id, files)
            
        except Exception as e:
            self.logger.error(f"❌ Error in enhanced vector store creation: {e}")
            self.logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            return None
            
    def _process_files_enhanced(self, vector_store_id: str, files: List[Path]) -> str:
        """Enhanced file processing with detailed progress tracking"""
        successful_uploads = 0
        failed_uploads = []
        
        self.logger.info(f"📄 Processing {len(files)} files for vector store...")
        
        for i, file_path in enumerate(files):
            self._update_progress(
                ResearchStatus.CREATING_VECTOR_STORE,
                f"Processing {file_path.name}",
                files_processed=i
            )
            
            if not self._is_valid_file(file_path):
                failed_uploads.append({"file": file_path.name, "reason": "Invalid file"})
                continue
                
            try:
                # Enhanced file upload with content validation
                file_id = self._upload_file_enhanced(file_path)
                if file_id:
                    # Add to vector store with retry
                    _, success = self.enhanced_api_call(
                        f"vector_store_file_add_{file_path.name}",
                        self.client.vector_stores.files.create,
                        vector_store_id=vector_store_id,
                        file_id=file_id
                    )
                    
                    if success:
                        successful_uploads += 1
                        self.logger.info(f"   ✅ Added: {file_path.name}")
                    else:
                        failed_uploads.append({"file": file_path.name, "reason": "Failed to add to vector store"})
                else:
                    failed_uploads.append({"file": file_path.name, "reason": "Upload failed"})
                    
            except Exception as e:
                failed_uploads.append({"file": file_path.name, "reason": str(e)})
                self.logger.error(f"   ❌ Failed to process {file_path.name}: {e}")
                
        # Final processing summary
        self.logger.info(f"📊 File processing complete:")
        self.logger.info(f"   ✅ Successful: {successful_uploads}")
        self.logger.info(f"   ❌ Failed: {len(failed_uploads)}")
        
        if failed_uploads and self.debug_mode:
            self.logger.debug(f"   Failed files: {json.dumps(failed_uploads, indent=2)}")
            
        if successful_uploads == 0:
            raise RuntimeError("No files were successfully uploaded")
            
        return vector_store_id
        
    def _is_valid_file(self, file_path: Path) -> bool:
        """Enhanced file validation"""
        if not file_path.exists() or not file_path.is_file():
            return False
            
        # Check file size (max 100MB for API)
        if file_path.stat().st_size > 100 * 1024 * 1024:
            self.logger.warning(f"⚠️ File too large: {file_path.name} ({file_path.stat().st_size / 1024 / 1024:.1f}MB)")
            return False
            
        # Check if file has content
        try:
            if file_path.suffix.lower() in ['.txt', '.md', '.py', '.json', '.yaml', '.yml', '.csv']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        self.logger.warning(f"⚠️ Empty file: {file_path.name}")
                        return False
        except Exception as e:
            self.logger.warning(f"⚠️ Could not validate {file_path.name}: {e}")
            return False
            
        return True
        
    def _upload_file_enhanced(self, file_path: Path) -> Optional[str]:
        """Enhanced file upload with better error handling"""
        try:
            # Read and validate content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not content.strip():
                return None
                
            # Create temporary file with metadata
            temp_file = Path(f"/tmp/{file_path.stem}_{self.session_id}{file_path.suffix}")
            
            # Add metadata header for better context
            enhanced_content = self._add_file_metadata(file_path, content)
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
                
            # Upload with retry logic
            with open(temp_file, 'rb') as f:
                response, success = self.enhanced_api_call(
                    f"file_upload_{file_path.name}",
                    self.client.files.create,
                    file=f,
                    purpose="assistants"
                )
                
            # Cleanup
            temp_file.unlink(missing_ok=True)
            
            if success and response:
                return response.id
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Enhanced upload failed for {file_path.name}: {e}")
            return None
            
    def _add_file_metadata(self, file_path: Path, content: str) -> str:
        """Add helpful metadata to files for better analysis"""
        metadata_header = f"""
# FILE METADATA
# File: {file_path.name}
# Path: {file_path.relative_to(Path(WORKSPACE_ROOT)) if Path(WORKSPACE_ROOT) in file_path.parents else file_path}
# Size: {len(content)} characters
# Analysis Session: {self.session_id}
# Added: {datetime.now().isoformat()}

# ORIGINAL CONTENT BEGINS BELOW
{'=' * 50}

"""
        return metadata_header + content
        
    def execute_deep_research_enhanced(self, vector_store_id: str) -> Dict[str, Any]:
        """Enhanced deep research execution with improved model parameters"""
        self._update_progress(
            ResearchStatus.STARTING_RESEARCH,
            "Starting enhanced deep research analysis"
        )
        
        try:
            # Load research prompt
            prompt_file = RESEARCH_ROOT / "config" / "research_prompt.md"
            if not prompt_file.exists():
                # Fallback locations
                fallback_locations = [
                    Path(__file__).parent.parent.parent / "grant_eval_v3_deep_research_prompt.md",
                    RESEARCH_ROOT / "prompts" / "research_prompt.md"
                ]
                
                for fallback in fallback_locations:
                    if fallback.exists():
                        prompt_file = fallback
                        break
                        
                if not prompt_file.exists():
                    raise FileNotFoundError("Research prompt not found in any location")
                    
            with open(prompt_file, 'r', encoding='utf-8') as f:
                research_prompt = f.read()
                
            self.logger.info(f"📋 Research prompt loaded from: {prompt_file}")
            
            # Enhanced research input with better instructions
            enhanced_input = self._create_enhanced_research_input(research_prompt)
            
            # Enhanced request configuration
            request_data = {
                "model": "o3-deep-research-2025-06-26",  # Use the newer model
                "input": enhanced_input,
                "background": True,
                "max_output_tokens": 32000,  # Increased for comprehensive analysis
                "tools": [
                    {
                        "type": "file_search",
                        "vector_store_ids": [vector_store_id],
                        "max_num_results": 20,  # More comprehensive search
                        "ranking_options": {
                            "ranker": "auto",
                            "score_threshold": 0.3  # Lower threshold for broader search
                        }
                    },
                    {
                        "type": "code_interpreter",
                        "container": {"type": "auto"}
                    }
                ],
                "reasoning": {
                    "effort": "high",  # Request more thorough reasoning
                    "generate_summary": True
                },
                "text": {
                    "format": {"type": "text"},
                    "verbosity": "high"  # Request detailed output
                },
                "metadata": {
                    "session_id": self.session_id,
                    "executor_version": "improved",
                    "analysis_mode": "comprehensive"
                }
            }
            
            self.logger.info("🚀 Executing enhanced deep research...")
            self.logger.debug(f"📤 Request configuration: {json.dumps({**request_data, 'input': '[TRUNCATED]'}, indent=2)}")
            
            # Execute with enhanced error handling
            response, success = self.enhanced_api_call(
                "deep_research_enhanced",
                self.client.responses.create,
                **request_data
            )
            
            if not success or not response:
                raise RuntimeError("Failed to start enhanced deep research")
                
            self.logger.info(f"✅ Enhanced deep research started!")
            self.logger.info(f"🆔 Response ID: {response.id}")
            self.logger.info(f"📊 Status: {response.status}")
            
            return {
                "response_id": response.id,
                "status": response.status,
                "started_at": datetime.now().isoformat(),
                "vector_store_id": vector_store_id,
                "model_used": request_data["model"],
                "enhanced_features": True
            }
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced deep research failed: {e}")
            self.logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            return {"error": str(e)}
            
    def _create_enhanced_research_input(self, base_prompt: str) -> str:
        """Create enhanced research input with better instructions"""
        enhanced_instructions = f"""
{base_prompt}

## 🔍 ENHANCED EXECUTION INSTRUCTIONS

**CRITICAL**: This is an enhanced analysis session with improved content extraction capabilities.
Please provide your analysis in a structured, comprehensive format that can be easily parsed and extracted.

### Analysis Requirements:
1. **Structured Output**: Use clear headings and sections as specified in the research output format
2. **Comprehensive Coverage**: Analyze ALL components systematically
3. **Evidence-Based Findings**: Support all conclusions with specific code references
4. **Actionable Recommendations**: Provide specific, implementable improvement suggestions

### File Analysis Strategy:
Use the file search tool extensively to examine:
- Current v3 implementation: `grant_eval_v3/evaluation/`
- Historical implementations: `evaluation_agent/` and `evaluation_agent_v2/`
- Supporting infrastructure: `deep_research/`, `evaluation_framework/`, `conversion_engine/`
- Documentation and specifications

### Quality Requirements:
- Provide percentage completeness estimates for each component
- Identify specific blocking issues with code references
- Include concrete examples of problems found
- Prioritize recommendations by impact and effort

### Output Format:
Structure your response exactly as specified in the research prompt, ensuring:
- Clear section headers (### Executive Summary, ### Current State Assessment, etc.)
- Detailed analysis with specific findings
- Concrete recommendations with priority levels
- Implementation timeline with realistic estimates

**Session Info**: {self.session_id}
**Executor**: Enhanced v2.0 with improved content extraction
**Analysis Mode**: Comprehensive system assessment

Please begin your analysis now.
"""
        
        return enhanced_instructions
        
    def monitor_research_progress_enhanced(self, response_id: str, max_wait_time: int = 3600) -> Dict[str, Any]:
        """Enhanced progress monitoring with adaptive polling"""
        self._update_progress(
            ResearchStatus.MONITORING_PROGRESS,
            f"Monitoring research progress (max wait: {max_wait_time}s)"
        )
        
        start_time = time.time()
        check_count = 0
        consecutive_queued = 0
        
        # Adaptive polling intervals
        polling_intervals = [30, 60, 90, 120]  # Start with shorter intervals
        
        while time.time() - start_time < max_wait_time:
            try:
                check_count += 1
                elapsed = time.time() - start_time
                
                self.logger.info(f"🔄 Progress check #{check_count} (elapsed: {elapsed:.1f}s)")
                
                # Check response status with enhanced error handling
                response, success = self.enhanced_api_call(
                    f"progress_check_{check_count}",
                    self.client.responses.retrieve,
                    response_id
                )
                
                if not success or not response:
                    self.logger.warning(f"⚠️ Failed to check progress (attempt {check_count})")
                    time.sleep(30)
                    continue
                    
                self.logger.info(f"   📊 Status: {response.status}")
                
                if response.status == "completed":
                    self.logger.info("   ✅ Research completed successfully!")
                    return {
                        "status": "completed",
                        "response_id": response_id,
                        "completed_at": datetime.now().isoformat(),
                        "total_checks": check_count,
                        "elapsed_time": elapsed
                    }
                    
                elif response.status == "failed":
                    error_details = self._extract_error_details(response)
                    self.logger.error(f"   ❌ Research failed: {error_details}")
                    return {
                        "status": "failed",
                        "response_id": response_id,
                        "error": error_details,
                        "total_checks": check_count,
                        "elapsed_time": elapsed
                    }
                    
                elif response.status == "in_progress":
                    consecutive_queued = 0
                    self.logger.info("   🔄 Research actively processing...")
                    
                    # Try to extract partial progress if available
                    self._log_partial_progress(response)
                    
                elif response.status == "queued":
                    consecutive_queued += 1
                    self.logger.info(f"   ⏳ Still queued (consecutive: {consecutive_queued})")
                    
                    if consecutive_queued > 10:  # More than 10 minutes queued
                        self.logger.warning("   ⚠️ Extended queue time detected")
                        
                else:
                    self.logger.info(f"   📊 Status: {response.status}")
                    
                # Adaptive polling interval
                if response.status == "queued" and consecutive_queued < 3:
                    wait_time = polling_intervals[0]  # 30s for initial queued state
                elif response.status == "in_progress":
                    wait_time = polling_intervals[2]  # 90s for active processing
                else:
                    wait_time = polling_intervals[1]  # 60s for other states
                    
                self.logger.info(f"   ⏱️ Waiting {wait_time}s before next check...")
                time.sleep(wait_time)
                
            except Exception as e:
                self.logger.error(f"   ❌ Error in progress monitoring: {e}")
                self.logger.error(f"   🔍 Traceback: {traceback.format_exc()}")
                time.sleep(60)
                
        self.logger.warning(f"   ⏰ Timeout reached after {check_count} checks ({elapsed:.1f}s)")
        return {
            "status": "timeout",
            "response_id": response_id,
            "message": f"Research timeout after {elapsed:.1f}s",
            "total_checks": check_count,
            "elapsed_time": elapsed
        }
        
    def _extract_error_details(self, response: Any) -> str:
        """Extract detailed error information from response"""
        try:
            if hasattr(response, 'error') and response.error:
                return str(response.error)
            elif hasattr(response, 'incomplete_details') and response.incomplete_details:
                return f"Incomplete: {response.incomplete_details}"
            else:
                return "Unknown error - check response attributes"
        except Exception as e:
            return f"Error extracting error details: {e}"
            
    def _log_partial_progress(self, response: Any):
        """Log any available partial progress information"""
        try:
            if hasattr(response, 'output') and response.output:
                output_count = len(response.output) if hasattr(response.output, '__len__') else 0
                if output_count > 0:
                    self.logger.info(f"      🔍 Partial output available: {output_count} items")
        except Exception as e:
            self.logger.debug(f"   🔍 Could not extract partial progress: {e}")
            
    def retrieve_research_results_enhanced(self, response_id: str) -> Dict[str, Any]:
        """Enhanced results retrieval with comprehensive content extraction"""
        self._update_progress(
            ResearchStatus.EXTRACTING_CONTENT,
            "Retrieving and extracting research results"
        )
        
        try:
            self.logger.info(f"📊 Retrieving enhanced research results...")
            
            # Get the response with enhanced error handling
            response, success = self.enhanced_api_call(
                "results_retrieval_enhanced",
                self.client.responses.retrieve,
                response_id
            )
            
            if not success or not response:
                return {"error": "Failed to retrieve research results"}
                
            if response.status != "completed":
                self.logger.warning(f"   ⚠️ Research not completed: {response.status}")
                return {
                    "status": response.status,
                    "response_id": response_id,
                    "message": f"Research status: {response.status}"
                }
                
            self.logger.info("✅ Research completed, performing enhanced content extraction...")
            
            # Enhanced extraction process
            result_data = self._perform_enhanced_extraction(response)
            
            # Validate extraction success
            extraction_success = self._validate_extraction(result_data)
            self.performance_metrics["extraction_success_rate"] = 1.0 if extraction_success else 0.0
            
            if extraction_success:
                self.logger.info("✅ Enhanced content extraction successful!")
            else:
                self.logger.warning("⚠️ Extraction partially successful - review results")
                
            return result_data
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced results retrieval failed: {e}")
            self.logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            return {"error": str(e)}
            
    def _perform_enhanced_extraction(self, response: Any) -> Dict[str, Any]:
        """Perform comprehensive content extraction with multiple strategies"""
        extraction_data = {
            "response_id": response.id,
            "status": response.status,
            "retrieved_at": datetime.now().isoformat(),
            "extraction_version": "enhanced_v2.0",
            "extraction_attempts": []
        }
        
        # Strategy 1: Direct attribute access
        try:
            direct_content = self._extract_direct_content(response)
            if direct_content:
                extraction_data["direct_extraction"] = direct_content
                self.extraction_attempts.append({"method": "direct", "success": True})
                self.logger.info("✅ Direct content extraction successful")
        except Exception as e:
            self.extraction_attempts.append({"method": "direct", "success": False, "error": str(e)})
            self.logger.warning(f"⚠️ Direct extraction failed: {e}")
            
        # Strategy 2: Output array processing
        try:
            output_content = self._extract_output_content(response)
            if output_content:
                extraction_data["output_extraction"] = output_content
                self.extraction_attempts.append({"method": "output", "success": True})
                self.logger.info("✅ Output array extraction successful")
        except Exception as e:
            self.extraction_attempts.append({"method": "output", "success": False, "error": str(e)})
            self.logger.warning(f"⚠️ Output extraction failed: {e}")
            
        # Strategy 3: Reasoning extraction
        try:
            reasoning_content = self._extract_reasoning_content(response)
            if reasoning_content:
                extraction_data["reasoning_extraction"] = reasoning_content
                self.extraction_attempts.append({"method": "reasoning", "success": True})
                self.logger.info("✅ Reasoning extraction successful")
        except Exception as e:
            self.extraction_attempts.append({"method": "reasoning", "success": False, "error": str(e)})
            self.logger.warning(f"⚠️ Reasoning extraction failed: {e}")
            
        # Strategy 4: Comprehensive text analysis
        try:
            text_content = self._extract_comprehensive_text(response)
            if text_content:
                extraction_data["text_extraction"] = text_content
                self.extraction_attempts.append({"method": "text", "success": True})
                self.logger.info("✅ Comprehensive text extraction successful")
        except Exception as e:
            self.extraction_attempts.append({"method": "text", "success": False, "error": str(e)})
            self.logger.warning(f"⚠️ Text extraction failed: {e}")
            
        # Combine and synthesize results
        extraction_data["synthesized_content"] = self._synthesize_extracted_content(extraction_data)
        extraction_data["extraction_summary"] = self._create_extraction_summary(extraction_data)
        
        return extraction_data
        
    def _extract_direct_content(self, response: Any) -> Optional[Dict[str, Any]]:
        """Extract content using direct attribute access"""
        content = {}
        
        # Check common content attributes
        content_attrs = ['content', 'text', 'message', 'output_text']
        for attr in content_attrs:
            if hasattr(response, attr):
                value = getattr(response, attr)
                if value:
                    content[attr] = str(value)
                    
        # Check for usage statistics
        if hasattr(response, 'usage') and response.usage:
            content["usage_stats"] = self._extract_usage_stats(response.usage)
            
        return content if content else None
        
    def _extract_output_content(self, response: Any) -> Optional[Dict[str, Any]]:
        """Extract content from the output array with comprehensive parsing"""
        if not hasattr(response, 'output') or not response.output:
            return None
            
        output_data = {
            "total_items": len(response.output),
            "item_types": {},
            "messages": [],
            "reasoning_items": [],
            "tool_calls": [],
            "extracted_text": ""
        }
        
        try:
            for i, item in enumerate(response.output):
                item_type = str(type(item))
                output_data["item_types"][item_type] = output_data["item_types"].get(item_type, 0) + 1
                
                # Extract message content
                if hasattr(item, 'content') and item.content:
                    if isinstance(item.content, list):
                        for content_item in item.content:
                            if hasattr(content_item, 'text'):
                                text_content = content_item.text
                                output_data["messages"].append({
                                    "index": i,
                                    "text": text_content,
                                    "length": len(text_content),
                                    "type": str(type(content_item))
                                })
                                output_data["extracted_text"] += text_content + "\n\n"
                                
                # Extract reasoning content
                if 'Reasoning' in item_type:
                    reasoning_data = {
                        "index": i,
                        "id": getattr(item, 'id', None),
                        "summary": getattr(item, 'summary', None),
                        "status": getattr(item, 'status', None),
                    }
                    
                    # Try to extract reasoning content
                    if hasattr(item, 'content') and item.content:
                        reasoning_data["content"] = str(item.content)
                    elif hasattr(item, 'encrypted_content') and item.encrypted_content:
                        reasoning_data["encrypted_content"] = str(item.encrypted_content)
                        
                    output_data["reasoning_items"].append(reasoning_data)
                    
                # Extract tool calls
                if hasattr(item, 'code') or 'ToolCall' in item_type:
                    tool_data = {
                        "index": i,
                        "id": getattr(item, 'id', None),
                        "type": str(type(item)),
                        "status": getattr(item, 'status', None),
                    }
                    
                    if hasattr(item, 'code'):
                        tool_data["code"] = item.code
                    if hasattr(item, 'outputs'):
                        tool_data["outputs"] = str(item.outputs)
                        
                    output_data["tool_calls"].append(tool_data)
                    
        except Exception as e:
            output_data["extraction_error"] = str(e)
            
        return output_data
        
    def _extract_reasoning_content(self, response: Any) -> Optional[Dict[str, Any]]:
        """Extract reasoning content with special handling"""
        reasoning_data = {
            "reasoning_effort": None,
            "reasoning_summary": None,
            "reasoning_items_found": 0
        }
        
        try:
            # Check for reasoning attribute
            if hasattr(response, 'reasoning') and response.reasoning:
                reasoning = response.reasoning
                if hasattr(reasoning, 'effort'):
                    reasoning_data["reasoning_effort"] = str(reasoning.effort)
                if hasattr(reasoning, 'summary'):
                    reasoning_data["reasoning_summary"] = str(reasoning.summary)
                    
            # Count reasoning items from output
            if hasattr(response, 'output') and response.output:
                reasoning_count = 0
                for item in response.output:
                    if 'Reasoning' in str(type(item)):
                        reasoning_count += 1
                reasoning_data["reasoning_items_found"] = reasoning_count
                
            return reasoning_data if any(v for v in reasoning_data.values() if v is not None) else None
            
        except Exception as e:
            reasoning_data["extraction_error"] = str(e)
            return reasoning_data
            
    def _extract_comprehensive_text(self, response: Any) -> Optional[Dict[str, Any]]:
        """Extract all possible text content using comprehensive analysis"""
        text_data = {
            "full_response_text": "",
            "structured_content": {},
            "analysis_sections": [],
            "total_characters": 0
        }
        
        try:
            # Convert entire response to text for analysis
            full_text = str(response)
            text_data["full_response_text"] = full_text
            text_data["total_characters"] = len(full_text)
            
            # Extract structured analysis content using regex patterns
            analysis_patterns = {
                "executive_summary": r"### Executive Summary\s*(.*?)(?=###|\Z)",
                "current_state": r"### Current State Assessment\s*(.*?)(?=###|\Z)",
                "historical_learning": r"### Historical Learning Analysis\s*(.*?)(?=###|\Z)",
                "improvement_opportunities": r"### Improvement Opportunities\s*(.*?)(?=###|\Z)",
                "implementation_roadmap": r"### Implementation Roadmap\s*(.*?)(?=###|\Z)",
                "recommendations": r"### Recommendations\s*(.*?)(?=###|\Z)"
            }
            
            for section, pattern in analysis_patterns.items():
                matches = re.findall(pattern, full_text, re.DOTALL | re.IGNORECASE)
                if matches:
                    content = matches[0].strip()
                    if content and len(content) > 50:  # Only include substantial content
                        text_data["structured_content"][section] = content
                        text_data["analysis_sections"].append(section)
                        
            return text_data if text_data["structured_content"] else None
            
        except Exception as e:
            text_data["extraction_error"] = str(e)
            return text_data
            
    def _synthesize_extracted_content(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize all extracted content into a unified analysis"""
        synthesis = {
            "synthesis_timestamp": datetime.now().isoformat(),
            "best_content_source": None,
            "analysis_content": {},
            "content_quality_score": 0.0,
            "extraction_confidence": 0.0
        }
        
        try:
            # Determine best content source
            sources = []
            
            if "output_extraction" in extraction_data and extraction_data["output_extraction"].get("extracted_text"):
                sources.append({
                    "name": "output_extraction",
                    "content": extraction_data["output_extraction"]["extracted_text"],
                    "quality": len(extraction_data["output_extraction"]["extracted_text"])
                })
                
            if "text_extraction" in extraction_data:
                text_ext = extraction_data["text_extraction"]
                if text_ext.get("structured_content"):
                    sources.append({
                        "name": "text_extraction",
                        "content": text_ext["structured_content"],
                        "quality": len(text_ext.get("structured_content", {}))
                    })
                    
            # Select best source
            if sources:
                best_source = max(sources, key=lambda x: x["quality"])
                synthesis["best_content_source"] = best_source["name"]
                synthesis["analysis_content"] = best_source["content"]
                synthesis["content_quality_score"] = min(best_source["quality"] / 10000, 1.0)  # Normalize
                
            # Calculate extraction confidence
            successful_methods = sum(1 for attempt in self.extraction_attempts if attempt.get("success", False))
            total_methods = len(self.extraction_attempts) if self.extraction_attempts else 1
            synthesis["extraction_confidence"] = successful_methods / total_methods
            
            return synthesis
            
        except Exception as e:
            synthesis["synthesis_error"] = str(e)
            return synthesis
            
    def _create_extraction_summary(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive summary of extraction results"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "extraction_methods_attempted": len(self.extraction_attempts),
            "successful_extractions": sum(1 for a in self.extraction_attempts if a.get("success")),
            "content_sources_found": [],
            "analysis_quality_indicators": {},
            "recommendations": []
        }
        
        try:
            # Identify content sources
            for key in extraction_data.keys():
                if key.endswith("_extraction") and extraction_data[key]:
                    summary["content_sources_found"].append(key)
                    
            # Analyze content quality
            if "synthesized_content" in extraction_data:
                synth = extraction_data["synthesized_content"]
                summary["analysis_quality_indicators"] = {
                    "best_source": synth.get("best_content_source"),
                    "quality_score": synth.get("content_quality_score", 0.0),
                    "confidence": synth.get("extraction_confidence", 0.0)
                }
                
            # Generate recommendations
            if summary["successful_extractions"] == 0:
                summary["recommendations"].append("No content successfully extracted - check API response format")
            elif summary["analysis_quality_indicators"].get("quality_score", 0) < 0.5:
                summary["recommendations"].append("Low content quality detected - review extraction methods")
            else:
                summary["recommendations"].append("Content extraction successful - proceed with analysis")
                
        except Exception as e:
            summary["summary_error"] = str(e)
            
        return summary
        
    def _validate_extraction(self, result_data: Dict[str, Any]) -> bool:
        """Validate that extraction was successful"""
        try:
            # Check if we have any extracted content
            if "synthesized_content" not in result_data:
                return False
                
            synth = result_data["synthesized_content"]
            
            # Check quality indicators
            quality_score = synth.get("content_quality_score", 0.0)
            confidence = synth.get("extraction_confidence", 0.0)
            
            # Consider successful if we have reasonable quality and confidence
            return quality_score > 0.3 and confidence > 0.5
            
        except Exception as e:
            self.logger.error(f"❌ Extraction validation error: {e}")
            return False
            
    def _extract_usage_stats(self, usage: Any) -> Dict[str, Any]:
        """Extract usage statistics from response"""
        stats = {}
        
        try:
            for attr in ['input_tokens', 'output_tokens', 'total_tokens', 'input_tokens_details', 'output_tokens_details']:
                if hasattr(usage, attr):
                    value = getattr(usage, attr)
                    if value is not None:
                        stats[attr] = value
                        
        except Exception as e:
            stats["extraction_error"] = str(e)
            
        return stats
        
    def save_enhanced_results(self, results: Dict[str, Any]):
        """Save results with comprehensive analysis and metadata"""
        self._update_progress(
            ResearchStatus.SAVING_RESULTS,
            "Saving enhanced research results"
        )
        
        if not results:
            self.logger.error("❌ No results to save")
            return
            
        # Create enhanced results directory structure
        results_dir = RESEARCH_ROOT / "results" / self.session_id
        results_dir.mkdir(parents=True, exist_ok=True)
        
        analysis_dir = results_dir / "analysis"
        analysis_dir.mkdir(exist_ok=True)
        
        logs_dir = results_dir / "logs"  
        logs_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"💾 Saving enhanced results to {results_dir}...")
        
        try:
            # Save main results with enhanced metadata
            enhanced_results = {
                **results,
                "session_metadata": {
                    "session_id": self.session_id,
                    "executor_version": "enhanced_v2.0",
                    "saved_at": datetime.now().isoformat(),
                    "performance_metrics": self.performance_metrics,
                    "extraction_attempts": self.extraction_attempts,
                    "api_call_history": len(self.api_response_history)
                }
            }
            
            results_file = results_dir / "enhanced_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_results, f, indent=2, default=str)
            self.logger.info(f"   📄 Enhanced results: {results_file}")
            
            # Save extracted analysis as markdown if available
            if "synthesized_content" in results and results["synthesized_content"].get("analysis_content"):
                self._save_extracted_analysis_markdown(results, analysis_dir)
                
            # Save performance metrics
            self._save_performance_metrics(analysis_dir)
            
            # Save API response history
            self._save_api_history(logs_dir)
            
            # Generate comprehensive session summary
            self._generate_enhanced_session_summary(enhanced_results, results_dir)
            
            # Save configuration and metadata
            self._save_session_configuration(results_dir)
            
            # Copy logs with enhanced naming
            self._copy_enhanced_logs(logs_dir)
            
            self.logger.info("✅ Enhanced results saved successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save enhanced results: {e}")
            self.logger.error(f"🔍 Traceback: {traceback.format_exc()}")
            
    def _save_extracted_analysis_markdown(self, results: Dict[str, Any], analysis_dir: Path):
        """Save the extracted analysis in a clean markdown format"""
        try:
            synth = results["synthesized_content"]
            analysis_content = synth.get("analysis_content", "")
            
            analysis_file = analysis_dir / "EXTRACTED_ANALYSIS.md"
            
            with open(analysis_file, 'w', encoding='utf-8') as f:
                f.write("# Grant Evaluation v3 - Deep Research Analysis\n\n")
                f.write(f"**Session ID**: {self.session_id}\n")
                f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Executor**: Enhanced v2.0\n")
                f.write(f"**Content Source**: {synth.get('best_content_source', 'Unknown')}\n")
                f.write(f"**Quality Score**: {synth.get('content_quality_score', 0.0):.2f}\n")
                f.write(f"**Extraction Confidence**: {synth.get('extraction_confidence', 0.0):.2f}\n\n")
                f.write("---\n\n")
                
                if isinstance(analysis_content, str):
                    f.write(analysis_content)
                elif isinstance(analysis_content, dict):
                    for section, content in analysis_content.items():
                        f.write(f"## {section.replace('_', ' ').title()}\n\n")
                        f.write(f"{content}\n\n")
                else:
                    f.write(f"Analysis Content:\n{str(analysis_content)}")
                    
            self.logger.info(f"   📋 Extracted analysis: {analysis_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save analysis markdown: {e}")
            
    def _save_performance_metrics(self, analysis_dir: Path):
        """Save detailed performance metrics"""
        try:
            metrics = {
                **self.performance_metrics,
                "session_duration": (datetime.now() - self.progress.start_time).total_seconds(),
                "progress_metrics": {
                    "stage": self.progress.stage.value,
                    "files_processed": self.progress.files_processed,
                    "total_files": self.progress.total_files,
                    "api_calls_made": self.progress.api_calls_made,
                    "errors_encountered": self.progress.errors_encountered
                },
                "extraction_analysis": {
                    "methods_attempted": len(self.extraction_attempts),
                    "successful_methods": [a for a in self.extraction_attempts if a.get("success")],
                    "failed_methods": [a for a in self.extraction_attempts if not a.get("success")]
                }
            }
            
            metrics_file = analysis_dir / "performance_metrics.json"
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, default=str)
            self.logger.info(f"   📊 Performance metrics: {metrics_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save performance metrics: {e}")
            
    def _save_api_history(self, logs_dir: Path):
        """Save detailed API call history"""
        try:
            api_history_file = logs_dir / "api_call_history.json"
            with open(api_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.api_response_history, f, indent=2, default=str)
            self.logger.info(f"   📞 API history: {api_history_file}")
            
            # Also save as JSONL for easier parsing
            api_history_jsonl = logs_dir / "api_call_history.jsonl"
            with open(api_history_jsonl, 'w', encoding='utf-8') as f:
                for entry in self.api_response_history:
                    f.write(json.dumps(entry) + '\n')
            self.logger.info(f"   📞 API history (JSONL): {api_history_jsonl}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save API history: {e}")
            
    def _generate_enhanced_session_summary(self, results: Dict[str, Any], results_dir: Path):
        """Generate comprehensive session summary"""
        try:
            summary_file = results_dir / "ENHANCED_SESSION_SUMMARY.md"
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("# Enhanced Grant Evaluation v3 Research Session Summary\n\n")
                
                # Session Information
                f.write("## Session Information\n\n")
                f.write(f"**Session ID**: {self.session_id}\n")
                f.write(f"**Executor Version**: Enhanced v2.0\n")
                f.write(f"**Started**: {self.progress.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Completed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Total Duration**: {(datetime.now() - self.progress.start_time).total_seconds():.1f} seconds\n")
                f.write(f"**Final Stage**: {self.progress.stage.value}\n\n")
                
                # Execution Summary
                f.write("## Execution Summary\n\n")
                f.write(f"**Files Processed**: {self.progress.files_processed}/{self.progress.total_files}\n")
                f.write(f"**API Calls Made**: {self.progress.api_calls_made}\n")
                f.write(f"**Errors Encountered**: {self.progress.errors_encountered}\n\n")
                
                # Performance Metrics
                f.write("## Performance Metrics\n\n")
                if self.performance_metrics["token_usage"]["input"] > 0:
                    f.write(f"**Input Tokens**: {self.performance_metrics['token_usage']['input']:,}\n")
                    f.write(f"**Output Tokens**: {self.performance_metrics['token_usage']['output']:,}\n")
                    f.write(f"**Total Tokens**: {self.performance_metrics['token_usage']['input'] + self.performance_metrics['token_usage']['output']:,}\n")
                
                if self.performance_metrics["api_call_times"]:
                    avg_time = sum(self.performance_metrics["api_call_times"]) / len(self.performance_metrics["api_call_times"])
                    f.write(f"**Average API Call Time**: {avg_time:.2f} seconds\n")
                    
                f.write(f"**Extraction Success Rate**: {self.performance_metrics['extraction_success_rate']:.1%}\n\n")
                
                # Content Extraction Analysis
                if "synthesized_content" in results:
                    synth = results["synthesized_content"]
                    f.write("## Content Extraction Analysis\n\n")
                    f.write(f"**Best Content Source**: {synth.get('best_content_source', 'None')}\n")
                    f.write(f"**Content Quality Score**: {synth.get('content_quality_score', 0.0):.2f}/1.0\n")
                    f.write(f"**Extraction Confidence**: {synth.get('extraction_confidence', 0.0):.1%}\n")
                    
                    if "extraction_summary" in results:
                        summary = results["extraction_summary"]
                        f.write(f"**Methods Attempted**: {summary.get('extraction_methods_attempted', 0)}\n")
                        f.write(f"**Successful Extractions**: {summary.get('successful_extractions', 0)}\n")
                        
                        recommendations = summary.get("recommendations", [])
                        if recommendations:
                            f.write(f"\n**Extraction Recommendations**:\n")
                            for rec in recommendations:
                                f.write(f"- {rec}\n")
                    f.write("\n")
                
                # Research Results Summary
                f.write("## Research Results Summary\n\n")
                f.write(f"**Response ID**: {results.get('response_id', 'Unknown')}\n")
                f.write(f"**Research Status**: {results.get('status', 'Unknown')}\n")
                
                if "enhanced_features" in results and results["enhanced_features"]:
                    f.write("**Enhanced Features**: ✅ Enabled\n")
                    
                f.write("\n")
                
                # Next Steps and Recommendations
                f.write("## Next Steps and Recommendations\n\n")
                
                if self.performance_metrics["extraction_success_rate"] > 0.8:
                    f.write("✅ **Extraction Status**: Highly successful\n")
                    f.write("📋 **Recommended Action**: Review the extracted analysis in `analysis/EXTRACTED_ANALYSIS.md`\n\n")
                elif self.performance_metrics["extraction_success_rate"] > 0.5:
                    f.write("⚠️ **Extraction Status**: Partially successful\n")
                    f.write("📋 **Recommended Action**: Review extraction logs and consider manual analysis\n\n")
                else:
                    f.write("❌ **Extraction Status**: Low success rate\n")
                    f.write("📋 **Recommended Action**: Investigate extraction failures in the logs\n\n")
                    
                f.write("### Improvement Areas for Next Run\n\n")
                if self.progress.errors_encountered > 0:
                    f.write("- Review and address API call errors\n")
                if self.performance_metrics["extraction_success_rate"] < 1.0:
                    f.write("- Investigate content extraction methods\n")
                    
                f.write("- Analyze performance metrics for optimization opportunities\n")
                f.write("- Review API response patterns for enhanced parsing\n\n")
                
                # File Locations
                f.write("## Generated Files\n\n")
                f.write("- **Main Results**: `enhanced_results.json`\n")
                f.write("- **Extracted Analysis**: `analysis/EXTRACTED_ANALYSIS.md`\n")  
                f.write("- **Performance Metrics**: `analysis/performance_metrics.json`\n")
                f.write("- **API History**: `logs/api_call_history.json`\n")
                f.write("- **Session Logs**: `logs/enhanced_session_*.log`\n")
                
            self.logger.info(f"   📋 Enhanced session summary: {summary_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate enhanced session summary: {e}")
            
    def _save_session_configuration(self, results_dir: Path):
        """Save session configuration and metadata"""
        try:
            config = {
                "session_id": self.session_id,
                "executor_version": "enhanced_v2.0",
                "created_at": datetime.now().isoformat(),
                "workspace_root": WORKSPACE_ROOT,
                "research_root": str(RESEARCH_ROOT),
                "debug_mode": self.debug_mode,
                "model_used": "o3-deep-research-2025-06-26",
                "enhancement_features": {
                    "adaptive_polling": True,
                    "multiple_extraction_strategies": True,
                    "comprehensive_error_handling": True,
                    "enhanced_content_synthesis": True,
                    "performance_metrics_tracking": True
                },
                "files_analyzed": self._get_analyzed_files_list(),
                "extraction_methods": [
                    "direct_attribute_access",
                    "output_array_processing", 
                    "reasoning_content_extraction",
                    "comprehensive_text_analysis"
                ]
            }
            
            config_file = results_dir / "session_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, default=str)
            self.logger.info(f"   ⚙️ Session config: {config_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save session configuration: {e}")
            
    def _copy_enhanced_logs(self, logs_dir: Path):
        """Copy all log files to results directory with enhanced naming"""
        try:
            import shutil
            
            # Copy main session log
            session_log_source = RESEARCH_ROOT / "logs" / f"enhanced_session_{self.session_id}.log"
            session_log_dest = logs_dir / "enhanced_session.log"
            if session_log_source.exists():
                shutil.copy2(session_log_source, session_log_dest)
                self.logger.info(f"   📝 Session log: {session_log_dest}")
                
            # Copy debug log
            debug_log_source = RESEARCH_ROOT / "logs" / f"debug_{self.session_id}.log"
            debug_log_dest = logs_dir / "debug_session.log"
            if debug_log_source.exists():
                shutil.copy2(debug_log_source, debug_log_dest)
                self.logger.info(f"   🔍 Debug log: {debug_log_dest}")
                
            # Copy detailed API log
            api_log_source = RESEARCH_ROOT / "logs" / f"api_detailed_{self.session_id}.jsonl"
            api_log_dest = logs_dir / "api_detailed.jsonl"
            if api_log_source.exists():
                shutil.copy2(api_log_source, api_log_dest)
                self.logger.info(f"   📞 API detailed log: {api_log_dest}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to copy enhanced logs: {e}")
            
    def _get_analyzed_files_list(self) -> List[str]:
        """Get comprehensive list of analyzed files"""
        analyzed_files = []
        
        try:
            # Define analysis paths
            analysis_paths = {
                "core_v3": [
                    "grant_eval_v3/evaluation/skills/rubric_mining/",
                    "grant_eval_v3/evaluation/agents/", 
                    "grant_eval_v3/evaluation/skills/retrieval/",
                    "grant_eval_v3/evaluation/skills/scoring/",
                    "grant_eval_v3/evaluation/infra/",
                    "grant_eval_v3/docs/",
                    "grant_eval_v3/projects/",
                    "grant_eval_v3/runs/"
                ],
                "historical": [
                    "evaluation_agent/",
                    "evaluation_agent_v2/"
                ],
                "infrastructure": [
                    "deep_research/",
                    "evaluation_framework/",
                    "conversion_engine/"
                ]
            }
            
            workspace_path = Path(WORKSPACE_ROOT)
            
            for category, paths in analysis_paths.items():
                for path_str in paths:
                    path = workspace_path / path_str
                    if path.exists():
                        if path.is_dir():
                            for file_path in path.rglob("*"):
                                if file_path.is_file() and file_path.suffix.lower() in ['.py', '.md', '.txt', '.csv', '.json', '.yaml', '.yml']:
                                    analyzed_files.append({
                                        "category": category,
                                        "relative_path": str(file_path.relative_to(workspace_path)),
                                        "size": file_path.stat().st_size,
                                        "modified": file_path.stat().st_mtime
                                    })
                        else:
                            analyzed_files.append({
                                "category": category,
                                "relative_path": str(path.relative_to(workspace_path)),
                                "size": path.stat().st_size,
                                "modified": path.stat().st_mtime
                            })
                            
        except Exception as e:
            self.logger.error(f"❌ Failed to get analyzed files list: {e}")
            
        return analyzed_files
        
    def _identify_analysis_files_enhanced(self) -> List[Path]:
        """Enhanced file identification with better filtering and validation"""
        self._update_progress(
            ResearchStatus.PREPARING_FILES,
            "Identifying and validating files for analysis"
        )
        
        files_to_analyze = []
        workspace_path = Path(WORKSPACE_ROOT)
        
        # Enhanced path definitions with priority levels
        analysis_paths = {
            "critical": [
                "grant_eval_v3/evaluation/skills/rubric_mining/",
                "grant_eval_v3/evaluation/agents/",
                "grant_eval_v3/evaluation/skills/retrieval/", 
                "grant_eval_v3/evaluation/skills/scoring/",
                "grant_eval_v3/evaluation/infra/"
            ],
            "important": [
                "evaluation_agent/EVALUATOR_V1.md",
                "evaluation_agent/scripts/run_evaluation.py",
                "evaluation_agent_v2/core/evaluator.py",
                "grant_eval_v3/docs/",
                "grant_eval_v3/projects/"
            ],
            "supporting": [
                "deep_research/",
                "evaluation_framework/",
                "conversion_engine/",
                "grant_eval_v3/runs/"
            ]
        }
        
        file_stats = {"critical": 0, "important": 0, "supporting": 0, "total": 0}
        
        self.logger.info("🔍 Enhanced file identification process...")
        
        for priority, paths in analysis_paths.items():
            self.logger.info(f"   📁 Processing {priority} files...")
            
            for path_str in paths:
                path = workspace_path / path_str
                if path.exists():
                    if path.is_dir():
                        for file_path in path.rglob("*"):
                            if self._is_analysis_worthy_file(file_path):
                                files_to_analyze.append(file_path)
                                file_stats[priority] += 1
                                file_stats["total"] += 1
                    elif path.is_file() and self._is_analysis_worthy_file(path):
                        files_to_analyze.append(path)
                        file_stats[priority] += 1
                        file_stats["total"] += 1
                        
        self.logger.info("📊 File identification summary:")
        for priority, count in file_stats.items():
            self.logger.info(f"   {priority.title()}: {count} files")
            
        return files_to_analyze
        
    def _is_analysis_worthy_file(self, file_path: Path) -> bool:
        """Enhanced file filtering for analysis worthiness"""
        if not file_path.is_file():
            return False
            
        # File extension filtering
        valid_extensions = {'.py', '.md', '.txt', '.csv', '.json', '.yaml', '.yml', '.toml'}
        if file_path.suffix.lower() not in valid_extensions:
            return False
            
        # Size filtering (skip very large files and very small files)
        try:
            size = file_path.stat().st_size
            if size > 10 * 1024 * 1024:  # Skip files larger than 10MB
                return False
            if size < 10:  # Skip tiny files
                return False
        except OSError:
            return False
            
        # Content filtering for text files
        if file_path.suffix.lower() in {'.py', '.md', '.txt', '.csv', '.yaml', '.yml'}:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        return False
                    # Skip files that are mostly comments or empty lines
                    lines = content.split('\n')
                    content_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
                    if len(content_lines) < 3:  # Need at least some content
                        return False
            except (UnicodeDecodeError, OSError):
                return False
                
        # Skip certain file patterns
        skip_patterns = {
            '__pycache__', '.git', '.venv', 'node_modules', '.DS_Store',
            'build', 'dist', '.egg-info', '.pytest_cache', '.mypy_cache'
        }
        
        if any(pattern in str(file_path) for pattern in skip_patterns):
            return False
            
        return True
        
    def run_enhanced_analysis(self, max_wait_time: int = 3600) -> bool:
        """Run the complete enhanced research analysis workflow"""
        self.logger.info("🚀 ENHANCED Grant Evaluation v3 Deep Research Analysis")
        self.logger.info("=" * 80)
        
        try:
            self._update_progress(ResearchStatus.INITIALIZING, "Starting enhanced analysis workflow")
            
            # Step 1: Enhanced file identification
            self.logger.info("📁 Step 1: Enhanced file identification...")
            files_to_analyze = self._identify_analysis_files_enhanced()
            
            if not files_to_analyze:
                self.logger.error("❌ No files found for analysis")
                return False
                
            self.logger.info(f"✅ Identified {len(files_to_analyze)} files for analysis")
            self._update_progress(ResearchStatus.PREPARING_FILES, f"Files identified: {len(files_to_analyze)}", total_files=len(files_to_analyze))
            
            # Step 2: Enhanced vector store creation
            self.logger.info("🔧 Step 2: Enhanced vector store creation...")
            vector_store_id = self.create_vector_store_enhanced(files_to_analyze)
            
            if not vector_store_id:
                self.logger.error("❌ Failed to create enhanced vector store")
                return False
                
            self.logger.info(f"✅ Enhanced vector store created: {vector_store_id}")
            
            # Step 3: Enhanced deep research execution
            self.logger.info("🚀 Step 3: Enhanced deep research execution...")
            research_start = self.execute_deep_research_enhanced(vector_store_id)
            
            if "error" in research_start:
                self.logger.error(f"❌ Failed to start enhanced research: {research_start['error']}")
                return False
                
            self.logger.info(f"✅ Enhanced deep research started successfully")
            
            # Step 4: Enhanced progress monitoring
            self.logger.info("⏳ Step 4: Enhanced progress monitoring...")
            progress = self.monitor_research_progress_enhanced(
                research_start["response_id"],
                max_wait_time
            )
            
            # Step 5: Enhanced results retrieval
            if progress.get("status") == "completed":
                self.logger.info("📊 Step 5: Enhanced results retrieval...")
                results = self.retrieve_research_results_enhanced(progress["response_id"])
                
                # Step 6: Enhanced results saving
                self.logger.info("💾 Step 6: Enhanced results saving...")
                self.save_enhanced_results(results)
                
                # Final status update
                self._update_progress(ResearchStatus.COMPLETED, "Enhanced analysis workflow completed successfully")
                
                self.logger.info("🎉 ENHANCED DEEP RESEARCH ANALYSIS COMPLETE!")
                self.logger.info(f"📁 Results directory: {RESEARCH_ROOT}/results/{self.session_id}")
                self.logger.info("✅ Check the following files for comprehensive analysis:")
                self.logger.info(f"   📋 Main Analysis: results/{self.session_id}/analysis/EXTRACTED_ANALYSIS.md")
                self.logger.info(f"   📊 Session Summary: results/{self.session_id}/ENHANCED_SESSION_SUMMARY.md")
                self.logger.info(f"   📈 Performance: results/{self.session_id}/analysis/performance_metrics.json")
                
                return True
            else:
                self._update_progress(ResearchStatus.FAILED, f"Research failed: {progress.get('status')}")
                self.logger.warning(f"⚠️ Enhanced research did not complete successfully")
                self.logger.warning(f"   Status: {progress.get('status', 'Unknown')}")
                if progress.get("error"):
                    self.logger.error(f"   Error: {progress['error']}")
                    
                # Still save what we have
                if progress.get("response_id"):
                    try:
                        partial_results = {"partial": True, **progress}
                        self.save_enhanced_results(partial_results)
                        self.logger.info("📊 Partial results saved for analysis")
                    except Exception as e:
                        self.logger.error(f"Failed to save partial results: {e}")
                        
                return False
                
        except Exception as e:
            self._update_progress(ResearchStatus.FAILED, f"Critical error: {str(e)}")
            self.logger.error(f"❌ Critical error in enhanced research workflow: {e}")
            self.logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
            return False
            
def main():
    """Enhanced main execution function"""
    print("🚀 ENHANCED Grant Evaluation v3 Deep Research Executor")
    print("=" * 60)
    print("Version: Enhanced v2.0")
    print("Improvements: Better content extraction, error handling, and monitoring")
    print()
    
    # Check API key
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY is not set. Export it in your environment before running.")
        print("   For example: export OPENAI_API_KEY=...\n")
        return False
        
    # Initialize enhanced executor
    print("🔧 Initializing Enhanced Research Executor...")
    executor = ImprovedGrantEvalV3ResearchExecutor(OPENAI_API_KEY, debug_mode=True)
    
    # Run enhanced analysis
    print("🚀 Starting Enhanced Analysis Workflow...")
    print()
    success = executor.run_enhanced_analysis(max_wait_time=3600)  # 1 hour max
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 ENHANCED ANALYSIS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📁 Results Location: {RESEARCH_ROOT}/results/{executor.session_id}")
        print()
        print("📋 Key Files Generated:")
        print(f"   📊 Main Analysis: analysis/EXTRACTED_ANALYSIS.md")
        print(f"   📈 Session Summary: ENHANCED_SESSION_SUMMARY.md") 
        print(f"   📊 Performance Data: analysis/performance_metrics.json")
        print(f"   🔍 Detailed Logs: logs/")
        print()
        print("🔄 Next Steps:")
        print("1. Review the extracted analysis for comprehensive insights")
        print("2. Check performance metrics for optimization opportunities")
        print("3. Use findings to implement Grant Eval v3 improvements")
        print("4. Consider running follow-up analysis if needed")
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ ENHANCED ANALYSIS FAILED")
        print("=" * 60)
        print(f"📁 Check logs for details: {RESEARCH_ROOT}/logs/")
        print(f"📊 Partial results may be in: {RESEARCH_ROOT}/results/{executor.session_id}")
        print()
        print("🔧 Troubleshooting:")
        print("1. Check the detailed logs for specific error messages")
        print("2. Verify all file paths and permissions are correct")
        print("3. Ensure OpenAI API key has sufficient credits")
        print("4. Consider running with different parameters if needed")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)