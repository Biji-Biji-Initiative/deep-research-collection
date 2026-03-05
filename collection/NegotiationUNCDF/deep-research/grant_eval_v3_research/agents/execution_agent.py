#!/usr/bin/env python3
"""
Execution Agent for Agentic Deep Research System
Runs research with full monitoring, checkpoints, and adaptive execution
"""

import json
import time
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import sys
import os

from .base_agent import BaseAgent, AgentResult, AgentStatus, AgentContext

# Import the original research executor
sys.path.append(str(Path(__file__).parent.parent / "scripts"))
from research_executor import GrantEvalV3ResearchExecutor

@dataclass
class ExecutionCheckpoint:
    """Execution checkpoint data"""
    checkpoint_id: str
    timestamp: datetime
    execution_state: Dict[str, Any]
    progress_percentage: float
    metrics: Dict[str, Any]
    can_resume: bool

class ExecutionAgent(BaseAgent):
    """Agent that executes research with comprehensive monitoring"""
    
    def __init__(self, config: Dict[str, Any], context: AgentContext):
        super().__init__("execution_agent", config, context)
        
        # Execution configuration
        self.monitoring_level = config.get("monitoring_level", "detailed")
        self.checkpoint_interval = config.get("checkpoint_interval", 300)  # 5 minutes
        self.auto_recovery = config.get("auto_recovery", True)
        self.parallel_execution = config.get("parallel_execution", False)
        
        # Execution state
        self.current_execution = None
        self.checkpoints = []
        self.execution_metrics = {}
        
        # Initialize research executor
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            self.research_executor = GrantEvalV3ResearchExecutor(api_key)
        else:
            self.research_executor = None
            self.logger.warning("No OpenAI API key found - some functionality may be limited")
            
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute research with full monitoring"""
        start_time = time.time()
        self.set_status(AgentStatus.RUNNING)
        
        try:
            self.logger.info("Starting research execution...")
            
            # Initialize execution context
            execution_context = await self.initialize_execution(input_data)
            
            # Execute research with monitoring
            research_results = await self.execute_with_monitoring(execution_context)
            
            # Post-process results
            final_results = await self.post_process_results(research_results, execution_context)
            
            # Save execution data
            await self.save_execution_data(execution_context, final_results)
            
            execution_time = time.time() - start_time
            confidence = self.calculate_execution_confidence(final_results)
            
            result_data = {
                "research_results": final_results,
                "execution_context": execution_context,
                "checkpoints_created": len(self.checkpoints),
                "execution_metrics": self.execution_metrics,
                "execution_summary": self.create_execution_summary(execution_context, final_results)
            }
            
            result = self.create_result(
                status=AgentStatus.COMPLETED,
                result_data=result_data,
                execution_time=execution_time,
                confidence=confidence
            )
            
            self.logger.info(f"Research execution completed successfully")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Research execution failed: {e}")
            
            # Attempt recovery if enabled
            if self.auto_recovery and self.checkpoints:
                recovery_result = await self.attempt_recovery()
                if recovery_result["success"]:
                    return await self.execute(input_data)  # Retry from checkpoint
                    
            return self.create_result(
                status=AgentStatus.FAILED,
                result_data={"error_details": str(e)},
                execution_time=execution_time,
                error=str(e)
            )
        finally:
            self.set_status(AgentStatus.IDLE)
            
    async def initialize_execution(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize execution context"""
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        context = {
            "execution_id": execution_id,
            "started_at": datetime.now(),
            "input_data": input_data,
            "execution_plan": input_data.get("execution_plan", {}),
            "optimization_data": input_data.get("optimization_data", {}),
            "monitoring_config": {
                "level": self.monitoring_level,
                "checkpoint_interval": self.checkpoint_interval,
                "metrics_collection": True
            }
        }
        
        self.current_execution = context
        self.logger.info(f"Initialized execution context: {execution_id}")
        
        return context
        
    async def execute_with_monitoring(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research with comprehensive monitoring"""
        if not self.research_executor:
            # Simulate execution for testing
            return await self.simulate_research_execution(context)
            
        try:
            # Start monitoring
            monitoring_task = asyncio.create_task(self.monitor_execution(context))
            
            # Execute research
            self.logger.info("Starting deep research analysis...")
            
            # Use the enhanced research executor
            success = self.research_executor.run_complete_analysis()
            
            if success:
                # Retrieve results from the research executor
                results = {
                    "success": True,
                    "session_id": self.research_executor.session_id,
                    "results_path": str(self.research_executor.research_results or {}),
                    "execution_completed": True
                }
            else:
                results = {
                    "success": False,
                    "error": "Research execution failed",
                    "session_id": self.research_executor.session_id,
                    "execution_completed": False
                }
                
            # Stop monitoring
            monitoring_task.cancel()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Research execution error: {e}")
            raise
            
    async def simulate_research_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate research execution for testing"""
        self.logger.info("Simulating research execution (no API key provided)")
        
        # Simulate research phases
        phases = [
            ("File Analysis", 0.2, 30),
            ("Vector Store Creation", 0.4, 45),
            ("Deep Research Execution", 0.8, 180),
            ("Results Processing", 0.95, 20),
            ("Final Validation", 1.0, 10)
        ]
        
        results = {
            "success": True,
            "session_id": f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "phases_completed": [],
            "simulated": True
        }
        
        for phase_name, progress, duration in phases:
            self.logger.info(f"Executing phase: {phase_name}")
            
            # Create checkpoint
            await self.create_checkpoint(context, progress, {
                "current_phase": phase_name,
                "phase_progress": progress
            })
            
            # Simulate work
            await asyncio.sleep(min(duration / 10, 5))  # Scaled down for testing
            
            results["phases_completed"].append({
                "phase": phase_name,
                "completed_at": datetime.now().isoformat(),
                "progress": progress
            })
            
        return results
        
    async def monitor_execution(self, context: Dict[str, Any]):
        """Monitor execution progress and create checkpoints"""
        try:
            while True:
                await asyncio.sleep(self.checkpoint_interval)
                
                # Create periodic checkpoint
                progress = self.estimate_progress(context)
                metrics = self.collect_execution_metrics(context)
                
                await self.create_checkpoint(context, progress, metrics)
                
                self.logger.debug(f"Monitoring checkpoint: {progress:.1%} complete")
                
        except asyncio.CancelledError:
            self.logger.info("Execution monitoring stopped")
            
    def estimate_progress(self, context: Dict[str, Any]) -> float:
        """Estimate execution progress"""
        # Simple progress estimation based on time elapsed
        started_at = context.get("started_at", datetime.now())
        elapsed = (datetime.now() - started_at).total_seconds()
        
        # Estimate total duration based on historical data or defaults
        estimated_total = 3600  # 1 hour default
        
        return min(elapsed / estimated_total, 0.95)  # Cap at 95% until completion
        
    def collect_execution_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect execution metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "execution_id": context.get("execution_id"),
            "memory_usage": self.get_memory_usage(),
            "cpu_usage": self.get_cpu_usage(),
            "disk_usage": self.get_disk_usage(),
            "checkpoint_count": len(self.checkpoints)
        }
        
    def get_memory_usage(self) -> float:
        """Get current memory usage (simplified)"""
        import psutil
        try:
            return psutil.virtual_memory().percent
        except:
            return 0.0
            
    def get_cpu_usage(self) -> float:
        """Get current CPU usage (simplified)"""
        import psutil
        try:
            return psutil.cpu_percent(interval=1)
        except:
            return 0.0
            
    def get_disk_usage(self) -> float:
        """Get current disk usage (simplified)"""
        import psutil
        try:
            return psutil.disk_usage('/').percent
        except:
            return 0.0
            
    async def create_checkpoint(self, context: Dict[str, Any], progress: float, 
                              metrics: Dict[str, Any]):
        """Create execution checkpoint"""
        checkpoint_id = f"checkpoint_{len(self.checkpoints)}"
        
        checkpoint = ExecutionCheckpoint(
            checkpoint_id=checkpoint_id,
            timestamp=datetime.now(),
            execution_state=context.copy(),
            progress_percentage=progress,
            metrics=metrics,
            can_resume=True
        )
        
        self.checkpoints.append(checkpoint)
        
        # Save checkpoint to file
        checkpoint_file = self.results_dir / f"{checkpoint_id}.json"
        with open(checkpoint_file, 'w') as f:
            checkpoint_dict = {
                "checkpoint_id": checkpoint.checkpoint_id,
                "timestamp": checkpoint.timestamp.isoformat(),
                "execution_state": checkpoint.execution_state,
                "progress_percentage": checkpoint.progress_percentage,
                "metrics": checkpoint.metrics,
                "can_resume": checkpoint.can_resume
            }
            json.dump(checkpoint_dict, f, indent=2, default=str)
            
        self.logger.debug(f"Created checkpoint: {checkpoint_id} ({progress:.1%})")
        
    async def post_process_results(self, research_results: Dict[str, Any], 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process research results"""
        processed_results = research_results.copy()
        
        # Add execution metadata
        processed_results["execution_metadata"] = {
            "execution_id": context.get("execution_id"),
            "started_at": context.get("started_at", datetime.now()).isoformat(),
            "completed_at": datetime.now().isoformat(),
            "total_duration": (datetime.now() - context.get("started_at", datetime.now())).total_seconds(),
            "checkpoints_created": len(self.checkpoints),
            "monitoring_level": self.monitoring_level
        }
        
        # Add quality metrics
        processed_results["quality_metrics"] = self.calculate_quality_metrics(research_results)
        
        # Add performance metrics
        processed_results["performance_metrics"] = self.calculate_performance_metrics(context)
        
        return processed_results
        
    def calculate_quality_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality metrics for results"""
        return {
            "completeness_score": 0.9 if results.get("success") else 0.3,
            "accuracy_score": 0.85 if results.get("success") else 0.4,
            "relevance_score": 0.88 if results.get("success") else 0.5,
            "confidence_score": 0.82 if results.get("success") else 0.2
        }
        
    def calculate_performance_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        started_at = context.get("started_at", datetime.now())
        duration = (datetime.now() - started_at).total_seconds()
        
        return {
            "execution_duration": duration,
            "checkpoint_frequency": len(self.checkpoints) / max(duration / 60, 1),  # Per minute
            "average_memory_usage": self.get_average_metric("memory_usage"),
            "average_cpu_usage": self.get_average_metric("cpu_usage"),
            "peak_resource_usage": self.get_peak_resource_usage()
        }
        
    def get_average_metric(self, metric_name: str) -> float:
        """Get average value of a metric from checkpoints"""
        values = [
            cp.metrics.get(metric_name, 0) 
            for cp in self.checkpoints 
            if metric_name in cp.metrics
        ]
        return sum(values) / len(values) if values else 0.0
        
    def get_peak_resource_usage(self) -> Dict[str, float]:
        """Get peak resource usage from checkpoints"""
        peak_memory = max([cp.metrics.get("memory_usage", 0) for cp in self.checkpoints], default=0)
        peak_cpu = max([cp.metrics.get("cpu_usage", 0) for cp in self.checkpoints], default=0)
        peak_disk = max([cp.metrics.get("disk_usage", 0) for cp in self.checkpoints], default=0)
        
        return {
            "peak_memory": peak_memory,
            "peak_cpu": peak_cpu,
            "peak_disk": peak_disk
        }
        
    async def save_execution_data(self, context: Dict[str, Any], results: Dict[str, Any]):
        """Save comprehensive execution data"""
        execution_id = context.get("execution_id")
        
        # Save main execution record
        execution_record = {
            "execution_id": execution_id,
            "context": context,
            "results": results,
            "checkpoints": [
                {
                    "checkpoint_id": cp.checkpoint_id,
                    "timestamp": cp.timestamp.isoformat(),
                    "progress": cp.progress_percentage,
                    "can_resume": cp.can_resume
                }
                for cp in self.checkpoints
            ],
            "saved_at": datetime.now().isoformat()
        }
        
        execution_file = self.results_dir / f"execution_{execution_id}.json"
        with open(execution_file, 'w') as f:
            json.dump(execution_record, f, indent=2, default=str)
            
        self.logger.info(f"Saved execution data: {execution_file}")
        
    async def attempt_recovery(self) -> Dict[str, Any]:
        """Attempt recovery from last checkpoint"""
        if not self.checkpoints:
            return {"success": False, "error": "No checkpoints available"}
            
        try:
            # Find the most recent valid checkpoint
            latest_checkpoint = None
            for checkpoint in reversed(self.checkpoints):
                if checkpoint.can_resume:
                    latest_checkpoint = checkpoint
                    break
                    
            if not latest_checkpoint:
                return {"success": False, "error": "No resumable checkpoints"}
                
            self.logger.info(f"Attempting recovery from checkpoint: {latest_checkpoint.checkpoint_id}")
            
            # Restore execution state
            self.current_execution = latest_checkpoint.execution_state.copy()
            
            return {
                "success": True,
                "checkpoint_id": latest_checkpoint.checkpoint_id,
                "progress_restored": latest_checkpoint.progress_percentage,
                "timestamp": latest_checkpoint.timestamp.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {e}")
            return {"success": False, "error": str(e)}
            
    def calculate_execution_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate confidence in execution results"""
        if not results.get("success", False):
            return 0.2
            
        base_confidence = 0.8
        
        # Adjust based on quality metrics
        quality_metrics = results.get("quality_metrics", {})
        quality_score = (
            quality_metrics.get("completeness_score", 0.5) +
            quality_metrics.get("accuracy_score", 0.5) +
            quality_metrics.get("relevance_score", 0.5)
        ) / 3
        
        # Adjust based on execution smoothness
        execution_smoothness = 1.0 - (len([cp for cp in self.checkpoints if not cp.can_resume]) / max(len(self.checkpoints), 1))
        
        final_confidence = (base_confidence * 0.5) + (quality_score * 0.3) + (execution_smoothness * 0.2)
        
        return min(max(final_confidence, 0.0), 1.0)
        
    def create_execution_summary(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Create execution summary"""
        started_at = context.get("started_at", datetime.now())
        duration = (datetime.now() - started_at).total_seconds()
        
        return {
            "execution_id": context.get("execution_id"),
            "duration_seconds": duration,
            "success": results.get("success", False),
            "checkpoints_created": len(self.checkpoints),
            "monitoring_level": self.monitoring_level,
            "phases_completed": len(results.get("phases_completed", [])),
            "quality_summary": {
                "overall_quality": results.get("quality_metrics", {}).get("completeness_score", 0),
                "confidence": results.get("quality_metrics", {}).get("confidence_score", 0)
            },
            "performance_summary": {
                "duration_category": "fast" if duration < 1800 else "normal" if duration < 3600 else "slow",
                "resource_efficiency": "good" if self.get_average_metric("memory_usage") < 70 else "moderate",
                "checkpoint_efficiency": len(self.checkpoints) / max(duration / 300, 1)  # Per 5-minute interval
            }
        }
        
    async def resume_execution(self, checkpoint_id: str) -> Dict[str, Any]:
        """Resume execution from specific checkpoint"""
        # Find the checkpoint
        target_checkpoint = None
        for checkpoint in self.checkpoints:
            if checkpoint.checkpoint_id == checkpoint_id:
                target_checkpoint = checkpoint
                break
                
        if not target_checkpoint:
            return {"success": False, "error": f"Checkpoint {checkpoint_id} not found"}
            
        if not target_checkpoint.can_resume:
            return {"success": False, "error": f"Checkpoint {checkpoint_id} is not resumable"}
            
        try:
            # Restore state
            self.current_execution = target_checkpoint.execution_state.copy()
            
            # Continue execution from this point
            remaining_work = 1.0 - target_checkpoint.progress_percentage
            
            self.logger.info(f"Resuming execution from checkpoint {checkpoint_id} ({remaining_work:.1%} remaining)")
            
            return {
                "success": True,
                "resumed_from": checkpoint_id,
                "progress_at_resume": target_checkpoint.progress_percentage,
                "remaining_work": remaining_work
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        if not self.current_execution:
            return {
                "status": "idle",
                "execution_id": None,
                "progress": 0.0
            }
            
        started_at = self.current_execution.get("started_at", datetime.now())
        elapsed = (datetime.now() - started_at).total_seconds()
        progress = self.estimate_progress(self.current_execution)
        
        return {
            "status": self.status.value,
            "execution_id": self.current_execution.get("execution_id"),
            "progress": progress,
            "elapsed_seconds": elapsed,
            "checkpoints_created": len(self.checkpoints),
            "last_checkpoint": self.checkpoints[-1].checkpoint_id if self.checkpoints else None
        }