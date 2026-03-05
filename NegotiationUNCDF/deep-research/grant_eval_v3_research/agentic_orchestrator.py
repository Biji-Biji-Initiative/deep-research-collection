#!/usr/bin/env python3
"""
Agentic Orchestrator for Deep Research System
Coordinates all agents in a self-improving research workflow
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Import configuration manager
import sys
sys.path.append(str(Path(__file__).parent / "config"))
from config_manager import ConfigManager, get_config_manager

# Import agents
from agents import (
    BaseAgent, AgentResult, AgentStatus, AgentContext,
    LearningAgent, PlanningAgent, ImprovementAgent,
    ExecutionAgent, AuditAgent, ReviewAgent
)

# Import monitoring system
sys.path.append(str(Path(__file__).parent / "scripts"))
from monitoring_audit_system import ResearchMonitoringSystem

class OrchestrationPhase(Enum):
    """Orchestration workflow phases"""
    INITIALIZATION = "initialization"
    LEARNING = "learning"
    PLANNING = "planning"
    IMPROVEMENT = "improvement"
    EXECUTION = "execution"
    REVIEW = "review"
    AUDIT = "audit"
    ITERATION_DECISION = "iteration_decision"
    COMPLETION = "completion"

@dataclass
class OrchestrationState:
    """Current orchestration state"""
    session_id: str
    phase: OrchestrationPhase
    iteration: int
    start_time: datetime
    agents_active: List[str]
    results: Dict[str, Any]
    errors: List[str]
    metrics: Dict[str, Any]

class AgenticOrchestrator:
    """Main orchestrator for the agentic deep research system"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the orchestrator"""
        # Load configuration
        if config_path:
            self.config_manager = ConfigManager(config_path)
        else:
            self.config_manager = get_config_manager()
            
        # Setup logging
        self.setup_logging()
        
        # Initialize state
        self.state = None
        self.agents = {}
        self.monitoring_system = None
        
        # Load system configuration
        self.system_config = self.config_manager.get_system_config()
        self.self_improvement_enabled = self.system_config.self_improvement_enabled
        self.max_iterations = 3  # Default max iterations
        
        self.logger.info("Agentic Orchestrator initialized")
        
    def setup_logging(self):
        """Setup orchestrator logging"""
        logging_config = self.config_manager.get_logging_config()
        
        # Create logs directory
        workspace_paths = self.config_manager.get_workspace_paths()
        log_dir = workspace_paths["logs_dir"]
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        log_file = log_dir / "orchestrator.log"
        
        logging.basicConfig(
            level=getattr(logging, logging_config.level),
            format=logging_config.format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("AgenticOrchestrator")
        
    async def initialize_system(self) -> bool:
        """Initialize the agentic system"""
        try:
            self.logger.info("Initializing agentic research system...")
            
            # Ensure directories exist
            self.config_manager.ensure_directories()
            
            # Initialize monitoring system
            workspace_paths = self.config_manager.get_workspace_paths()
            self.monitoring_system = ResearchMonitoringSystem(
                workspace_paths["research_root"]
            )
            
            # Create agent context
            context = AgentContext(
                session_id=self.generate_session_id(),
                workspace_root=workspace_paths["workspace_root"],
                research_root=workspace_paths["research_root"]
            )
            
            # Initialize agents
            await self.initialize_agents(context)
            
            # Initialize orchestration state
            self.state = OrchestrationState(
                session_id=context.session_id,
                phase=OrchestrationPhase.INITIALIZATION,
                iteration=0,
                start_time=datetime.now(),
                agents_active=[],
                results={},
                errors=[],
                metrics={}
            )
            
            self.logger.info(f"System initialized with session ID: {context.session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            return False
            
    async def initialize_agents(self, context: AgentContext):
        """Initialize all agents"""
        agent_configs = self.config_manager.get_all_agent_configs()
        
        for agent_name, agent_config in agent_configs.items():
            if not agent_config.enabled:
                self.logger.info(f"Skipping disabled agent: {agent_name}")
                continue
                
            try:
                if agent_name == "learning_agent":
                    self.agents[agent_name] = LearningAgent(agent_config.config, context)
                elif agent_name == "planning_agent":
                    self.agents[agent_name] = PlanningAgent(agent_config.config, context)
                elif agent_name == "improvement_agent":
                    self.agents[agent_name] = ImprovementAgent(agent_config.config, context)
                elif agent_name == "execution_agent":
                    self.agents[agent_name] = ExecutionAgent(agent_config.config, context)
                elif agent_name == "audit_agent":
                    self.agents[agent_name] = AuditAgent(agent_config.config, context)
                elif agent_name == "review_agent":
                    self.agents[agent_name] = ReviewAgent(agent_config.config, context)
                else:
                    self.logger.warning(f"Unknown agent type: {agent_name}")
                    continue
                    
                self.logger.info(f"Initialized agent: {agent_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize agent {agent_name}: {e}")
                
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"agentic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    async def run_research_workflow(self, research_request: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete agentic research workflow"""
        if not await self.initialize_system():
            return {"success": False, "error": "System initialization failed"}
            
        try:
            self.logger.info("Starting agentic research workflow...")
            
            # Start monitoring
            with self.monitoring_system.track_research_execution(self.state.session_id):
                
                workflow_results = {}
                
                # Main workflow loop
                while True:
                    # Execute current phase
                    phase_result = await self.execute_phase(research_request, workflow_results)
                    workflow_results[self.state.phase.value] = phase_result
                    
                    # Check for completion or failure
                    if self.state.phase == OrchestrationPhase.COMPLETION:
                        break
                    elif phase_result.get("status") == "failed":
                        self.logger.error(f"Phase {self.state.phase.value} failed")
                        break
                        
                    # Transition to next phase
                    next_phase = await self.determine_next_phase(phase_result)
                    if next_phase is None:
                        break
                        
                    await self.transition_phase(next_phase)
                    
                # Finalize results
                final_results = await self.finalize_results(workflow_results)
                
                self.logger.info("Agentic research workflow completed")
                return final_results
                
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": self.state.session_id if self.state else None
            }
            
    async def execute_phase(self, research_request: Dict[str, Any], 
                          previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute current orchestration phase"""
        self.logger.info(f"Executing phase: {self.state.phase.value}")
        
        try:
            if self.state.phase == OrchestrationPhase.LEARNING:
                return await self.execute_learning_phase(previous_results)
            elif self.state.phase == OrchestrationPhase.PLANNING:
                return await self.execute_planning_phase(research_request, previous_results)
            elif self.state.phase == OrchestrationPhase.IMPROVEMENT:
                return await self.execute_improvement_phase(previous_results)
            elif self.state.phase == OrchestrationPhase.EXECUTION:
                return await self.execute_execution_phase(research_request, previous_results)
            elif self.state.phase == OrchestrationPhase.REVIEW:
                return await self.execute_review_phase(previous_results)
            elif self.state.phase == OrchestrationPhase.AUDIT:
                return await self.execute_audit_phase(previous_results)
            elif self.state.phase == OrchestrationPhase.ITERATION_DECISION:
                return await self.execute_iteration_decision_phase(previous_results)
            else:
                return {"status": "skipped", "message": f"Unknown phase: {self.state.phase.value}"}
                
        except Exception as e:
            self.logger.error(f"Phase execution failed: {e}")
            return {"status": "failed", "error": str(e)}
            
    async def execute_learning_phase(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute learning phase"""
        if "learning_agent" not in self.agents:
            return {"status": "skipped", "message": "Learning agent not available"}
            
        learning_agent = self.agents["learning_agent"]
        
        # Prepare input for learning agent
        input_data = {
            "analysis_type": "comprehensive",
            "previous_results": previous_results,
            "session_context": {"iteration": self.state.iteration}
        }
        
        result = await learning_agent.execute(input_data)
        
        # Track metrics
        self.monitoring_system.track_insight("learning_patterns", result.confidence or 0.7)
        
        return {
            "status": "completed" if result.status == AgentStatus.COMPLETED else "failed",
            "agent_result": asdict(result),
            "patterns_discovered": result.result_data.get("patterns_discovered", 0),
            "insights_generated": result.result_data.get("insights_generated", 0)
        }
        
    async def execute_planning_phase(self, research_request: Dict[str, Any], 
                                   previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute planning phase"""
        if "planning_agent" not in self.agents:
            return {"status": "skipped", "message": "Planning agent not available"}
            
        planning_agent = self.agents["planning_agent"]
        
        # Prepare input for planning agent
        input_data = {
            "task_requirements": research_request,
            "available_agents": list(self.agents.keys()),
            "resource_constraints": {"max_duration": 3600, "max_cost": 50.0},
            "historical_performance": previous_results.get("learning", {}).get("agent_result", {}).get("result_data", {}),
            "learned_patterns": previous_results.get("learning", {}).get("agent_result", {}).get("result_data", {}).get("patterns", [])
        }
        
        result = await planning_agent.execute(input_data)
        
        return {
            "status": "completed" if result.status == AgentStatus.COMPLETED else "failed",
            "agent_result": asdict(result),
            "execution_plan": result.result_data.get("execution_plan", {}),
            "optimal_strategy": result.result_data.get("optimal_strategy", {})
        }
        
    async def execute_improvement_phase(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute improvement phase"""
        if "improvement_agent" not in self.agents:
            return {"status": "skipped", "message": "Improvement agent not available"}
            
        improvement_agent = self.agents["improvement_agent"]
        
        # Prepare input for improvement agent
        input_data = {
            "current_configuration": self.config_manager.get_raw_config(),
            "execution_plan": previous_results.get("planning", {}).get("execution_plan", {}),
            "optimization_data": previous_results.get("learning", {}).get("agent_result", {}).get("result_data", {})
        }
        
        result = await improvement_agent.execute(input_data)
        
        return {
            "status": "completed" if result.status == AgentStatus.COMPLETED else "failed",
            "agent_result": asdict(result),
            "improvements_implemented": result.result_data.get("improvements_implemented", 0),
            "total_improvement_score": result.result_data.get("total_improvement_score", 0)
        }
        
    async def execute_execution_phase(self, research_request: Dict[str, Any], 
                                    previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research execution phase"""
        if "execution_agent" not in self.agents:
            return {"status": "failed", "message": "Execution agent not available"}
            
        execution_agent = self.agents["execution_agent"]
        
        # Prepare input for execution agent
        input_data = {
            "research_request": research_request,
            "execution_plan": previous_results.get("planning", {}).get("execution_plan", {}),
            "optimizations": previous_results.get("improvement", {}).get("agent_result", {}).get("result_data", {})
        }
        
        result = await execution_agent.execute(input_data)
        
        # Track execution metrics
        if result.status == AgentStatus.COMPLETED:
            self.monitoring_system.track_insight("research_execution", result.confidence or 0.8)
            
        return {
            "status": "completed" if result.status == AgentStatus.COMPLETED else "failed",
            "agent_result": asdict(result),
            "research_results": result.result_data.get("research_results", {}),
            "execution_metrics": result.result_data.get("execution_metrics", {})
        }
        
    async def execute_review_phase(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute review phase"""
        if "review_agent" not in self.agents:
            return {"status": "skipped", "message": "Review agent not available"}
            
        review_agent = self.agents["review_agent"]
        
        # Prepare input for review agent
        input_data = {
            "execution_results": previous_results.get("execution", {}).get("research_results", {}),
            "research_outputs": previous_results.get("execution", {}).get("agent_result", {}).get("result_data", {}),
            "iteration_context": {"current_iteration": self.state.iteration}
        }
        
        result = await review_agent.execute(input_data)
        
        return {
            "status": "completed" if result.status == AgentStatus.COMPLETED else "failed",
            "agent_result": asdict(result),
            "review_decision": result.result_data.get("review_decision", {}),
            "quality_assessments": result.result_data.get("quality_assessments", [])
        }
        
    async def execute_audit_phase(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute audit phase"""
        if "audit_agent" not in self.agents:
            return {"status": "skipped", "message": "Audit agent not available"}
            
        audit_agent = self.agents["audit_agent"]
        
        # Prepare input for audit agent
        input_data = {
            "workflow_results": previous_results,
            "system_state": self.get_system_state(),
            "compliance_context": {"session_id": self.state.session_id, "iteration": self.state.iteration}
        }
        
        result = await audit_agent.execute(input_data)
        
        return {
            "status": "completed" if result.status == AgentStatus.COMPLETED else "failed",
            "agent_result": asdict(result),
            "audit_report": result.result_data.get("audit_report", {}),
            "compliance_results": result.result_data.get("compliance_results", {})
        }
        
    async def execute_iteration_decision_phase(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute iteration decision phase"""
        # Get review decision
        review_results = previous_results.get("review", {})
        review_decision = review_results.get("review_decision", {})
        
        decision = review_decision.get("decision", "accept")
        
        # Check iteration limits
        if self.state.iteration >= self.max_iterations:
            decision = "accept"
            rationale = f"Maximum iterations ({self.max_iterations}) reached"
        else:
            rationale = review_decision.get("rationale", "No specific rationale provided")
            
        return {
            "status": "completed",
            "iteration_decision": decision,
            "rationale": rationale,
            "current_iteration": self.state.iteration,
            "max_iterations": self.max_iterations,
            "should_iterate": decision in ["minor_revision", "major_revision"] and self.state.iteration < self.max_iterations
        }
        
    async def determine_next_phase(self, phase_result: Dict[str, Any]) -> Optional[OrchestrationPhase]:
        """Determine next phase based on current phase and results"""
        current_phase = self.state.phase
        
        if current_phase == OrchestrationPhase.INITIALIZATION:
            return OrchestrationPhase.LEARNING
        elif current_phase == OrchestrationPhase.LEARNING:
            return OrchestrationPhase.PLANNING
        elif current_phase == OrchestrationPhase.PLANNING:
            return OrchestrationPhase.IMPROVEMENT
        elif current_phase == OrchestrationPhase.IMPROVEMENT:
            return OrchestrationPhase.EXECUTION
        elif current_phase == OrchestrationPhase.EXECUTION:
            return OrchestrationPhase.REVIEW
        elif current_phase == OrchestrationPhase.REVIEW:
            return OrchestrationPhase.AUDIT
        elif current_phase == OrchestrationPhase.AUDIT:
            return OrchestrationPhase.ITERATION_DECISION
        elif current_phase == OrchestrationPhase.ITERATION_DECISION:
            # Check if iteration is needed
            should_iterate = phase_result.get("should_iterate", False)
            if should_iterate and self.self_improvement_enabled:
                self.state.iteration += 1
                self.logger.info(f"Starting iteration {self.state.iteration}")
                return OrchestrationPhase.LEARNING
            else:
                return OrchestrationPhase.COMPLETION
        else:
            return None
            
    async def transition_phase(self, next_phase: OrchestrationPhase):
        """Transition to next phase"""
        self.logger.info(f"Transitioning from {self.state.phase.value} to {next_phase.value}")
        self.state.phase = next_phase
        
        # Update metrics
        self.state.metrics[f"phase_{next_phase.value}_start"] = datetime.now().isoformat()
        
    def get_system_state(self) -> Dict[str, Any]:
        """Get current system state"""
        return {
            "session_id": self.state.session_id,
            "current_phase": self.state.phase.value,
            "iteration": self.state.iteration,
            "start_time": self.state.start_time.isoformat(),
            "active_agents": list(self.agents.keys()),
            "monitoring_enabled": self.monitoring_system is not None,
            "self_improvement_enabled": self.self_improvement_enabled
        }
        
    async def finalize_results(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize and package workflow results"""
        end_time = datetime.now()
        total_duration = (end_time - self.state.start_time).total_seconds()
        
        # Extract key results
        execution_results = workflow_results.get("execution", {}).get("research_results", {})
        review_summary = workflow_results.get("review", {}).get("agent_result", {}).get("result_data", {}).get("review_summary", {})
        audit_summary = workflow_results.get("audit", {}).get("agent_result", {}).get("result_data", {}).get("audit_summary", {})
        
        final_results = {
            "success": True,
            "session_id": self.state.session_id,
            "execution_summary": {
                "total_duration": total_duration,
                "iterations_completed": self.state.iteration,
                "phases_executed": list(workflow_results.keys()),
                "final_phase": self.state.phase.value
            },
            "research_results": execution_results,
            "quality_assessment": review_summary,
            "compliance_assessment": audit_summary,
            "workflow_details": workflow_results,
            "system_metrics": self.monitoring_system.get_status() if self.monitoring_system else {},
            "agent_performance": await self.collect_agent_performance(),
            "recommendations": self.extract_recommendations(workflow_results),
            "completed_at": end_time.isoformat()
        }
        
        # Save final results
        await self.save_final_results(final_results)
        
        return final_results
        
    async def collect_agent_performance(self) -> Dict[str, Any]:
        """Collect performance metrics from all agents"""
        performance = {}
        
        for agent_name, agent in self.agents.items():
            try:
                performance[agent_name] = agent.get_performance_metrics()
            except Exception as e:
                self.logger.warning(f"Failed to get performance metrics from {agent_name}: {e}")
                performance[agent_name] = {"error": str(e)}
                
        return performance
        
    def extract_recommendations(self, workflow_results: Dict[str, Any]) -> List[str]:
        """Extract recommendations from workflow results"""
        recommendations = []
        
        # Extract from review results
        review_results = workflow_results.get("review", {}).get("agent_result", {}).get("result_data", {})
        review_recommendations = review_results.get("improvement_recommendations", [])
        recommendations.extend(review_recommendations)
        
        # Extract from audit results
        audit_results = workflow_results.get("audit", {}).get("agent_result", {}).get("result_data", {})
        audit_report = audit_results.get("audit_report", {})
        audit_recommendations = audit_report.get("recommendations", [])
        recommendations.extend(audit_recommendations)
        
        # Extract from learning results
        learning_results = workflow_results.get("learning", {}).get("agent_result", {}).get("result_data", {})
        learning_recommendations = learning_results.get("recommendations", [])
        recommendations.extend(learning_recommendations)
        
        # Remove duplicates and limit
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:15]
        
    async def save_final_results(self, final_results: Dict[str, Any]):
        """Save final results to file"""
        try:
            workspace_paths = self.config_manager.get_workspace_paths()
            results_dir = workspace_paths["results_dir"]
            
            # Create session-specific results directory
            session_results_dir = results_dir / self.state.session_id
            session_results_dir.mkdir(parents=True, exist_ok=True)
            
            # Save main results file
            results_file = session_results_dir / "final_results.json"
            with open(results_file, 'w') as f:
                json.dump(final_results, f, indent=2, default=str)
                
            # Save workflow summary
            summary_file = session_results_dir / "workflow_summary.json"
            summary = {
                "session_id": self.state.session_id,
                "success": final_results["success"],
                "total_duration": final_results["execution_summary"]["total_duration"],
                "iterations": final_results["execution_summary"]["iterations_completed"],
                "quality_score": final_results.get("quality_assessment", {}).get("overall_score", 0),
                "compliance_status": final_results.get("compliance_assessment", {}).get("compliance_status", "unknown"),
                "recommendations_count": len(final_results.get("recommendations", [])),
                "completed_at": final_results["completed_at"]
            }
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
                
            self.logger.info(f"Final results saved to: {session_results_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to save final results: {e}")
            
    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "system_healthy": True,
            "components": {}
        }
        
        # Check configuration
        try:
            status = self.config_manager.get_status()
            health_status["components"]["configuration"] = {
                "healthy": status["config_valid"],
                "details": status
            }
        except Exception as e:
            health_status["components"]["configuration"] = {
                "healthy": False,
                "error": str(e)
            }
            health_status["system_healthy"] = False
            
        # Check agents
        agent_health = {}
        for agent_name, agent in self.agents.items():
            try:
                agent_status = await agent.health_check()
                agent_health[agent_name] = agent_status
                if not agent_status.get("healthy", False):
                    health_status["system_healthy"] = False
            except Exception as e:
                agent_health[agent_name] = {"healthy": False, "error": str(e)}
                health_status["system_healthy"] = False
                
        health_status["components"]["agents"] = agent_health
        
        # Check monitoring system
        if self.monitoring_system:
            try:
                monitoring_status = self.monitoring_system.get_status()
                health_status["components"]["monitoring"] = {
                    "healthy": monitoring_status.get("health_status") == "healthy",
                    "details": monitoring_status
                }
            except Exception as e:
                health_status["components"]["monitoring"] = {
                    "healthy": False,
                    "error": str(e)
                }
        else:
            health_status["components"]["monitoring"] = {
                "healthy": False,
                "error": "Monitoring system not initialized"
            }
            
        return health_status
        
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        if not self.state:
            return {
                "status": "not_initialized",
                "message": "Orchestrator not initialized"
            }
            
        elapsed_time = (datetime.now() - self.state.start_time).total_seconds()
        
        return {
            "status": "active" if self.state.phase != OrchestrationPhase.COMPLETION else "completed",
            "session_id": self.state.session_id,
            "current_phase": self.state.phase.value,
            "iteration": self.state.iteration,
            "elapsed_time": elapsed_time,
            "agents_available": len(self.agents),
            "monitoring_active": self.monitoring_system is not None,
            "self_improvement_enabled": self.self_improvement_enabled
        }

# CLI Interface
async def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agentic Deep Research System")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--request", type=str, help="Research request JSON file")
    parser.add_argument("--health-check", action="store_true", help="Perform health check")
    parser.add_argument("--status", action="store_true", help="Show orchestrator status")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = AgenticOrchestrator(Path(args.config) if args.config else None)
    
    if args.health_check:
        # Perform health check
        health_status = await orchestrator.health_check()
        print(json.dumps(health_status, indent=2))
        return
        
    if args.status:
        # Show status
        status = orchestrator.get_orchestrator_status()
        print(json.dumps(status, indent=2))
        return
        
    # Load research request
    if args.request:
        with open(args.request, 'r') as f:
            research_request = json.load(f)
    else:
        # Default research request
        research_request = {
            "type": "grant_evaluation_analysis",
            "scope": "comprehensive",
            "focus_areas": ["implementation_gaps", "performance_issues", "optimization_opportunities"],
            "output_format": "structured_analysis"
        }
    
    # Run workflow
    print("Starting agentic research workflow...")
    results = await orchestrator.run_research_workflow(research_request)
    
    # Display results summary
    if results.get("success"):
        print(f"✅ Workflow completed successfully!")
        print(f"Session ID: {results['session_id']}")
        print(f"Duration: {results['execution_summary']['total_duration']:.1f}s")
        print(f"Iterations: {results['execution_summary']['iterations_completed']}")
        print(f"Quality Score: {results.get('quality_assessment', {}).get('overall_score', 'N/A')}")
        print(f"Recommendations: {len(results.get('recommendations', []))}")
    else:
        print(f"❌ Workflow failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())