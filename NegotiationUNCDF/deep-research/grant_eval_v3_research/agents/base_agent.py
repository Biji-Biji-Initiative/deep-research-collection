#!/usr/bin/env python3
"""
Base Agent Class for Agentic Deep Research System
Provides common functionality for all specialized agents
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import traceback

class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class AgentResult:
    """Standardized agent result structure"""
    agent_name: str
    status: AgentStatus
    result_data: Dict[str, Any]
    execution_time: float
    timestamp: datetime
    error: Optional[str] = None
    confidence: Optional[float] = None
    metrics: Dict[str, Any] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}
        if self.recommendations is None:
            self.recommendations = []

@dataclass
class AgentContext:
    """Context information shared between agents"""
    session_id: str
    workspace_root: Path
    research_root: Path
    current_iteration: int = 0
    previous_results: Dict[str, Any] = None
    shared_memory: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.previous_results is None:
            self.previous_results = {}
        if self.shared_memory is None:
            self.shared_memory = {}

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, config: Dict[str, Any], context: AgentContext):
        """Initialize base agent"""
        self.name = name
        self.config = config
        self.context = context
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"Agent.{name}")
        
        # Agent-specific directories
        self.agent_dir = context.research_root / "agents" / name
        self.memory_dir = self.agent_dir / "memory"
        self.results_dir = self.agent_dir / "results"
        
        # Ensure directories exist
        self.agent_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize agent state
        self.execution_history = []
        self.performance_metrics = {}
        self.learned_patterns = {}
        
        self.logger.info(f"Agent {name} initialized with config: {list(config.keys())}")
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute the agent's main functionality"""
        pass
    
    def get_status(self) -> AgentStatus:
        """Get current agent status"""
        return self.status
        
    def set_status(self, status: AgentStatus):
        """Set agent status"""
        self.status = status
        self.logger.debug(f"Status changed to: {status.value}")
        
    def load_memory(self, memory_type: str) -> Dict[str, Any]:
        """Load agent memory of specific type"""
        memory_file = self.memory_dir / f"{memory_type}_memory.json"
        
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    memory = json.load(f)
                self.logger.debug(f"Loaded {memory_type} memory: {len(memory)} entries")
                return memory
            except Exception as e:
                self.logger.error(f"Failed to load {memory_type} memory: {e}")
                
        return {}
        
    def save_memory(self, memory_type: str, data: Dict[str, Any]):
        """Save agent memory of specific type"""
        memory_file = self.memory_dir / f"{memory_type}_memory.json"
        
        try:
            with open(memory_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            self.logger.debug(f"Saved {memory_type} memory: {len(data)} entries")
        except Exception as e:
            self.logger.error(f"Failed to save {memory_type} memory: {e}")
            
    def update_memory(self, memory_type: str, key: str, value: Any):
        """Update specific entry in agent memory"""
        memory = self.load_memory(memory_type)
        memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.context.session_id
        }
        self.save_memory(memory_type, memory)
        
    def get_memory(self, memory_type: str, key: str, default: Any = None) -> Any:
        """Get specific entry from agent memory"""
        memory = self.load_memory(memory_type)
        entry = memory.get(key, {})
        return entry.get("value", default)
        
    def record_execution(self, result: AgentResult):
        """Record execution result in history"""
        execution_record = {
            "timestamp": result.timestamp.isoformat(),
            "status": result.status.value,
            "execution_time": result.execution_time,
            "confidence": result.confidence,
            "error": result.error,
            "metrics": result.metrics,
            "session_id": self.context.session_id
        }
        
        self.execution_history.append(execution_record)
        
        # Save to file
        history_file = self.agent_dir / "execution_history.jsonl"
        with open(history_file, 'a') as f:
            f.write(json.dumps(execution_record) + '\n')
            
        # Update performance metrics
        self.update_performance_metrics(result)
        
    def update_performance_metrics(self, result: AgentResult):
        """Update agent performance metrics"""
        if result.status == AgentStatus.COMPLETED:
            self.performance_metrics["success_count"] = self.performance_metrics.get("success_count", 0) + 1
            
            # Update execution time stats
            exec_times = self.performance_metrics.get("execution_times", [])
            exec_times.append(result.execution_time)
            self.performance_metrics["execution_times"] = exec_times[-100:]  # Keep last 100
            
            # Update average execution time
            self.performance_metrics["avg_execution_time"] = sum(exec_times) / len(exec_times)
            
            # Update confidence stats
            if result.confidence is not None:
                confidences = self.performance_metrics.get("confidences", [])
                confidences.append(result.confidence)
                self.performance_metrics["confidences"] = confidences[-100:]  # Keep last 100
                self.performance_metrics["avg_confidence"] = sum(confidences) / len(confidences)
                
        else:
            self.performance_metrics["failure_count"] = self.performance_metrics.get("failure_count", 0) + 1
            
        # Calculate success rate
        success = self.performance_metrics.get("success_count", 0)
        failure = self.performance_metrics.get("failure_count", 0)
        total = success + failure
        if total > 0:
            self.performance_metrics["success_rate"] = success / total
            
        # Save metrics
        metrics_file = self.agent_dir / "performance_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(self.performance_metrics, f, indent=2, default=str)
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.performance_metrics.copy()
        
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in execution history"""
        if len(self.execution_history) < 5:
            return {"patterns": [], "insights": []}
            
        patterns = {}
        
        # Analyze success/failure patterns
        recent_results = [entry["status"] for entry in self.execution_history[-20:]]
        success_streak = 0
        failure_streak = 0
        
        for status in reversed(recent_results):
            if status == "completed":
                success_streak += 1
                failure_streak = 0
            else:
                failure_streak += 1
                success_streak = 0
                
        patterns["current_success_streak"] = success_streak
        patterns["current_failure_streak"] = failure_streak
        
        # Analyze execution time trends
        recent_times = [entry["execution_time"] for entry in self.execution_history[-10:]]
        if len(recent_times) >= 5:
            first_half = recent_times[:len(recent_times)//2]
            second_half = recent_times[len(recent_times)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            patterns["execution_time_trend"] = "improving" if second_avg < first_avg else "degrading"
            patterns["execution_time_change"] = (second_avg - first_avg) / first_avg
            
        # Analyze confidence trends
        recent_confidences = [
            entry["confidence"] for entry in self.execution_history[-10:] 
            if entry["confidence"] is not None
        ]
        if len(recent_confidences) >= 5:
            first_half = recent_confidences[:len(recent_confidences)//2]
            second_half = recent_confidences[len(recent_confidences)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            patterns["confidence_trend"] = "improving" if second_avg > first_avg else "degrading"
            patterns["confidence_change"] = (second_avg - first_avg) / first_avg
            
        # Generate insights
        insights = []
        if patterns.get("current_failure_streak", 0) > 3:
            insights.append("Multiple consecutive failures detected - may need intervention")
        if patterns.get("execution_time_trend") == "degrading":
            insights.append("Execution time is increasing - performance may be degrading")
        if patterns.get("confidence_trend") == "degrading":
            insights.append("Confidence scores are declining - model may need retraining")
            
        self.learned_patterns = patterns
        return {"patterns": patterns, "insights": insights}
        
    def should_adapt(self) -> Tuple[bool, str]:
        """Determine if agent should adapt its behavior"""
        patterns = self.analyze_patterns()
        
        # Check if adaptation is needed
        if patterns["patterns"].get("current_failure_streak", 0) > 2:
            return True, "Multiple failures - need strategy change"
            
        if patterns["patterns"].get("execution_time_change", 0) > 0.5:
            return True, "Performance degradation - need optimization"
            
        success_rate = self.performance_metrics.get("success_rate", 1.0)
        if success_rate < 0.7:
            return True, "Low success rate - need improvement"
            
        return False, "Performance acceptable"
        
    def adapt_strategy(self, reason: str) -> Dict[str, Any]:
        """Adapt agent strategy based on performance"""
        adaptations = {}
        
        if "failure" in reason.lower():
            # Increase retry attempts
            current_retries = self.config.get("max_retries", 3)
            adaptations["max_retries"] = min(current_retries + 1, 10)
            
        if "performance" in reason.lower() or "optimization" in reason.lower():
            # Reduce batch sizes or increase timeouts
            current_timeout = self.config.get("timeout", 300)
            adaptations["timeout"] = min(current_timeout * 1.2, 3600)
            
        if "success rate" in reason.lower():
            # Enable more conservative settings
            adaptations["conservative_mode"] = True
            adaptations["confidence_threshold"] = max(
                self.config.get("confidence_threshold", 0.7) - 0.1, 0.5
            )
            
        # Apply adaptations
        for key, value in adaptations.items():
            self.config[key] = value
            
        self.logger.info(f"Adapted strategy: {adaptations} (Reason: {reason})")
        
        # Save adapted config
        config_file = self.agent_dir / "adapted_config.json"
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)
            
        return adaptations
        
    def create_result(self, status: AgentStatus, result_data: Dict[str, Any], 
                     execution_time: float, error: str = None, 
                     confidence: float = None) -> AgentResult:
        """Create standardized agent result"""
        result = AgentResult(
            agent_name=self.name,
            status=status,
            result_data=result_data,
            execution_time=execution_time,
            timestamp=datetime.now(),
            error=error,
            confidence=confidence,
            metrics=self.get_performance_metrics()
        )
        
        # Record execution
        self.record_execution(result)
        
        return result
        
    def save_result(self, result: AgentResult, filename: str = None):
        """Save agent result to file"""
        if filename is None:
            filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        result_file = self.results_dir / filename
        
        with open(result_file, 'w') as f:
            # Convert result to dictionary for JSON serialization
            result_dict = asdict(result)
            result_dict["timestamp"] = result.timestamp.isoformat()
            result_dict["status"] = result.status.value
            json.dump(result_dict, f, indent=2, default=str)
            
        self.logger.debug(f"Result saved to: {result_file}")
        
    def load_result(self, filename: str) -> Optional[AgentResult]:
        """Load agent result from file"""
        result_file = self.results_dir / filename
        
        if not result_file.exists():
            return None
            
        try:
            with open(result_file, 'r') as f:
                result_dict = json.load(f)
                
            # Convert back to AgentResult
            result_dict["status"] = AgentStatus(result_dict["status"])
            result_dict["timestamp"] = datetime.fromisoformat(result_dict["timestamp"])
            
            return AgentResult(**result_dict)
            
        except Exception as e:
            self.logger.error(f"Failed to load result from {filename}: {e}")
            return None
            
    def cleanup_old_results(self, max_age_days: int = 30):
        """Clean up old result files"""
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)
        
        cleaned_count = 0
        for result_file in self.results_dir.glob("*.json"):
            if result_file.stat().st_mtime < cutoff_time:
                result_file.unlink()
                cleaned_count += 1
                
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} old result files")
            
    def get_agent_info(self) -> Dict[str, Any]:
        """Get comprehensive agent information"""
        return {
            "name": self.name,
            "status": self.status.value,
            "config": self.config,
            "performance_metrics": self.performance_metrics,
            "execution_count": len(self.execution_history),
            "learned_patterns": self.learned_patterns,
            "directories": {
                "agent_dir": str(self.agent_dir),
                "memory_dir": str(self.memory_dir),
                "results_dir": str(self.results_dir)
            }
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Perform agent health check"""
        health_status = {
            "agent_name": self.name,
            "status": self.status.value,
            "healthy": True,
            "checks": {}
        }
        
        try:
            # Check directories
            health_status["checks"]["directories"] = {
                "agent_dir_exists": self.agent_dir.exists(),
                "memory_dir_exists": self.memory_dir.exists(),
                "results_dir_exists": self.results_dir.exists()
            }
            
            # Check recent performance
            success_rate = self.performance_metrics.get("success_rate", 1.0)
            health_status["checks"]["performance"] = {
                "success_rate": success_rate,
                "success_rate_ok": success_rate >= 0.7
            }
            
            # Check for recent activity
            recent_activity = len([
                entry for entry in self.execution_history[-10:]
                if (datetime.now() - datetime.fromisoformat(entry["timestamp"])).days < 7
            ]) > 0
            health_status["checks"]["activity"] = {
                "recent_activity": recent_activity
            }
            
            # Overall health
            health_status["healthy"] = all([
                all(health_status["checks"]["directories"].values()),
                health_status["checks"]["performance"]["success_rate_ok"],
                health_status["checks"]["activity"]["recent_activity"] or len(self.execution_history) == 0
            ])
            
        except Exception as e:
            health_status["healthy"] = False
            health_status["error"] = str(e)
            
        return health_status