#!/usr/bin/env python3
"""
Planning Agent for Agentic Deep Research System
Creates optimized execution strategies based on learned patterns and context
"""

import json
import time
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import random

from .base_agent import BaseAgent, AgentResult, AgentStatus, AgentContext

class StrategyType(Enum):
    """Types of execution strategies"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"
    HIERARCHICAL = "hierarchical"
    PROBABILISTIC = "probabilistic"

class OptimizationTarget(Enum):
    """Optimization targets for strategies"""
    ACCURACY = "accuracy"
    SPEED = "speed"
    COST = "cost"
    RELIABILITY = "reliability"
    COMPLETENESS = "completeness"

@dataclass
class ExecutionStep:
    """Individual execution step in a strategy"""
    step_id: str
    agent_name: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    expected_duration: float
    priority: int
    retry_policy: Dict[str, Any]
    success_criteria: Dict[str, Any]
    fallback_steps: List[str] = None
    
    def __post_init__(self):
        if self.fallback_steps is None:
            self.fallback_steps = []

@dataclass
class ExecutionStrategy:
    """Complete execution strategy"""
    strategy_id: str
    strategy_type: StrategyType
    optimization_targets: List[OptimizationTarget]
    steps: List[ExecutionStep]
    estimated_duration: float
    estimated_cost: float
    success_probability: float
    contingency_plans: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    
@dataclass
class PlanningContext:
    """Context for planning decisions"""
    task_requirements: Dict[str, Any]
    available_agents: List[str]
    resource_constraints: Dict[str, Any]
    historical_performance: Dict[str, Any]
    learned_patterns: List[Dict[str, Any]]
    time_constraints: Optional[timedelta] = None
    cost_constraints: Optional[float] = None

class PlanningAgent(BaseAgent):
    """Agent that creates optimized execution strategies"""
    
    def __init__(self, config: Dict[str, Any], context: AgentContext):
        super().__init__("planning_agent", config, context)
        
        # Planning configuration
        self.strategy_types = config.get("strategy_types", ["sequential", "parallel", "adaptive"])
        self.optimization_targets = config.get("optimization_targets", ["accuracy", "speed", "cost"])
        self.planning_horizon = config.get("planning_horizon", 10)
        self.contingency_plans = config.get("contingency_plans", 3)
        
        # Planning state
        self.generated_strategies = []
        self.strategy_performance_history = {}
        self.optimization_weights = self.initialize_optimization_weights()
        
        # Load planning knowledge
        self.load_planning_knowledge()
        
    def initialize_optimization_weights(self) -> Dict[str, float]:
        """Initialize weights for different optimization targets"""
        return {
            OptimizationTarget.ACCURACY.value: 0.3,
            OptimizationTarget.SPEED.value: 0.2,
            OptimizationTarget.COST.value: 0.2,
            OptimizationTarget.RELIABILITY.value: 0.2,
            OptimizationTarget.COMPLETENESS.value: 0.1
        }
        
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute planning process"""
        start_time = time.time()
        self.set_status(AgentStatus.RUNNING)
        
        try:
            self.logger.info("Starting strategy planning...")
            
            # Parse input requirements
            planning_context = self.parse_planning_context(input_data)
            
            # Load relevant patterns from learning agent
            relevant_patterns = await self.load_relevant_patterns(planning_context)
            
            # Generate candidate strategies
            candidate_strategies = await self.generate_candidate_strategies(
                planning_context, relevant_patterns
            )
            
            # Evaluate and rank strategies
            ranked_strategies = await self.evaluate_strategies(
                candidate_strategies, planning_context
            )
            
            # Select optimal strategy
            optimal_strategy = await self.select_optimal_strategy(
                ranked_strategies, planning_context
            )
            
            # Generate contingency plans
            contingency_plans = await self.generate_contingency_plans(
                optimal_strategy, planning_context
            )
            
            # Create execution plan
            execution_plan = await self.create_execution_plan(
                optimal_strategy, contingency_plans
            )
            
            # Save strategy for future learning
            await self.save_strategy(optimal_strategy, execution_plan)
            
            result_data = {
                "optimal_strategy": asdict(optimal_strategy),
                "execution_plan": execution_plan,
                "candidate_strategies_count": len(candidate_strategies),
                "contingency_plans": contingency_plans,
                "planning_context": asdict(planning_context),
                "planning_summary": self.create_planning_summary(
                    optimal_strategy, candidate_strategies
                )
            }
            
            execution_time = time.time() - start_time
            confidence = self.calculate_planning_confidence(
                optimal_strategy, ranked_strategies
            )
            
            result = self.create_result(
                status=AgentStatus.COMPLETED,
                result_data=result_data,
                execution_time=execution_time,
                confidence=confidence
            )
            
            self.logger.info(f"Strategy planning completed: {optimal_strategy.strategy_type.value}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Strategy planning failed: {e}")
            
            return self.create_result(
                status=AgentStatus.FAILED,
                result_data={"error_details": str(e)},
                execution_time=execution_time,
                error=str(e)
            )
        finally:
            self.set_status(AgentStatus.IDLE)
            
    def parse_planning_context(self, input_data: Dict[str, Any]) -> PlanningContext:
        """Parse input data into planning context"""
        return PlanningContext(
            task_requirements=input_data.get("task_requirements", {}),
            available_agents=input_data.get("available_agents", []),
            resource_constraints=input_data.get("resource_constraints", {}),
            historical_performance=input_data.get("historical_performance", {}),
            learned_patterns=input_data.get("learned_patterns", []),
            time_constraints=self.parse_time_constraints(
                input_data.get("time_constraints")
            ),
            cost_constraints=input_data.get("cost_constraints")
        )
        
    def parse_time_constraints(self, time_constraint) -> Optional[timedelta]:
        """Parse time constraints from various formats"""
        if time_constraint is None:
            return None
        elif isinstance(time_constraint, (int, float)):
            return timedelta(seconds=time_constraint)
        elif isinstance(time_constraint, str):
            # Parse string formats like "1h", "30m", "2h30m"
            import re
            match = re.match(r'(\d+)([hms])', time_constraint)
            if match:
                value, unit = match.groups()
                value = int(value)
                if unit == 'h':
                    return timedelta(hours=value)
                elif unit == 'm':
                    return timedelta(minutes=value)
                elif unit == 's':
                    return timedelta(seconds=value)
        elif isinstance(time_constraint, timedelta):
            return time_constraint
        return None
        
    async def load_relevant_patterns(self, context: PlanningContext) -> List[Dict[str, Any]]:
        """Load relevant patterns from learning agent"""
        patterns = []
        
        # Try to load from learning agent's memory
        learning_agent_dir = self.context.research_root / "agents" / "learning_agent"
        patterns_file = learning_agent_dir / "memory" / "discovered_patterns.json"
        
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    all_patterns = json.load(f)
                    
                # Filter patterns relevant to current context
                for pattern in all_patterns:
                    if self.is_pattern_relevant(pattern, context):
                        patterns.append(pattern)
                        
                self.logger.info(f"Loaded {len(patterns)} relevant patterns")
                
            except Exception as e:
                self.logger.warning(f"Failed to load patterns: {e}")
                
        return patterns
        
    def is_pattern_relevant(self, pattern: Dict[str, Any], context: PlanningContext) -> bool:
        """Check if a pattern is relevant to current context"""
        # Agent-specific relevance
        if pattern.get("agent_name") in context.available_agents:
            return True
            
        # Task-specific relevance
        task_type = context.task_requirements.get("type", "")
        if task_type and task_type in pattern.get("description", ""):
            return True
            
        # Performance-related relevance
        if pattern.get("pattern_type") in ["success_trend", "execution_time_trend"]:
            return True
            
        return False
        
    async def generate_candidate_strategies(self, context: PlanningContext, 
                                          patterns: List[Dict[str, Any]]) -> List[ExecutionStrategy]:
        """Generate candidate execution strategies"""
        candidates = []
        
        # Generate strategies for each strategy type
        for strategy_type_str in self.strategy_types:
            try:
                strategy_type = StrategyType(strategy_type_str)
                
                if strategy_type == StrategyType.SEQUENTIAL:
                    candidates.extend(
                        await self.generate_sequential_strategies(context, patterns)
                    )
                elif strategy_type == StrategyType.PARALLEL:
                    candidates.extend(
                        await self.generate_parallel_strategies(context, patterns)
                    )
                elif strategy_type == StrategyType.ADAPTIVE:
                    candidates.extend(
                        await self.generate_adaptive_strategies(context, patterns)
                    )
                elif strategy_type == StrategyType.HIERARCHICAL:
                    candidates.extend(
                        await self.generate_hierarchical_strategies(context, patterns)
                    )
                elif strategy_type == StrategyType.PROBABILISTIC:
                    candidates.extend(
                        await self.generate_probabilistic_strategies(context, patterns)
                    )
                    
            except ValueError:
                self.logger.warning(f"Unknown strategy type: {strategy_type_str}")
                continue
                
        self.logger.info(f"Generated {len(candidates)} candidate strategies")
        return candidates
        
    async def generate_sequential_strategies(self, context: PlanningContext, 
                                           patterns: List[Dict[str, Any]]) -> List[ExecutionStrategy]:
        """Generate sequential execution strategies"""
        strategies = []
        
        # Basic sequential strategy
        steps = []
        step_id = 0
        
        # Learning phase
        if "learning_agent" in context.available_agents:
            steps.append(ExecutionStep(
                step_id=f"seq_step_{step_id}",
                agent_name="learning_agent",
                action="analyze_patterns",
                parameters={"analysis_depth": "comprehensive"},
                dependencies=[],
                expected_duration=300,  # 5 minutes
                priority=1,
                retry_policy={"max_retries": 2, "backoff": "exponential"},
                success_criteria={"confidence": 0.7}
            ))
            step_id += 1
            
        # Planning phase (this agent)
        steps.append(ExecutionStep(
            step_id=f"seq_step_{step_id}",
            agent_name="planning_agent",
            action="refine_strategy",
            parameters={"optimization_target": "accuracy"},
            dependencies=[f"seq_step_{step_id-1}"] if steps else [],
            expected_duration=180,  # 3 minutes
            priority=2,
            retry_policy={"max_retries": 1, "backoff": "linear"},
            success_criteria={"confidence": 0.8}
        ))
        step_id += 1
        
        # Improvement phase
        if "improvement_agent" in context.available_agents:
            steps.append(ExecutionStep(
                step_id=f"seq_step_{step_id}",
                agent_name="improvement_agent",
                action="optimize_execution",
                parameters={"target_metrics": ["accuracy", "speed"]},
                dependencies=[f"seq_step_{step_id-1}"],
                expected_duration=240,  # 4 minutes
                priority=3,
                retry_policy={"max_retries": 2, "backoff": "exponential"},
                success_criteria={"improvement_score": 0.05}
            ))
            step_id += 1
            
        # Execution phase
        if "execution_agent" in context.available_agents:
            steps.append(ExecutionStep(
                step_id=f"seq_step_{step_id}",
                agent_name="execution_agent",
                action="execute_research",
                parameters=context.task_requirements,
                dependencies=[f"seq_step_{step_id-1}"],
                expected_duration=3600,  # 1 hour
                priority=4,
                retry_policy={"max_retries": 1, "backoff": "exponential"},
                success_criteria={"completion": True}
            ))
            step_id += 1
            
        # Review phase
        if "review_agent" in context.available_agents:
            steps.append(ExecutionStep(
                step_id=f"seq_step_{step_id}",
                agent_name="review_agent",
                action="evaluate_results",
                parameters={"review_criteria": "comprehensive"},
                dependencies=[f"seq_step_{step_id-1}"],
                expected_duration=600,  # 10 minutes
                priority=5,
                retry_policy={"max_retries": 2, "backoff": "linear"},
                success_criteria={"quality_score": 0.8}
            ))
            
        strategy = ExecutionStrategy(
            strategy_id=f"sequential_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            strategy_type=StrategyType.SEQUENTIAL,
            optimization_targets=[OptimizationTarget.ACCURACY, OptimizationTarget.RELIABILITY],
            steps=steps,
            estimated_duration=sum(step.expected_duration for step in steps),
            estimated_cost=self.estimate_strategy_cost(steps),
            success_probability=0.85,
            contingency_plans=[],
            metadata={"description": "Sequential execution with all agents"},
            created_at=datetime.now()
        )
        
        strategies.append(strategy)
        return strategies
        
    async def generate_parallel_strategies(self, context: PlanningContext, 
                                         patterns: List[Dict[str, Any]]) -> List[ExecutionStrategy]:
        """Generate parallel execution strategies"""
        strategies = []
        
        # Check if parallel execution is feasible
        if len(context.available_agents) < 2:
            return strategies
            
        steps = []
        step_id = 0
        
        # Parallel analysis phase
        parallel_steps = []
        if "learning_agent" in context.available_agents:
            parallel_steps.append(ExecutionStep(
                step_id=f"par_step_{step_id}",
                agent_name="learning_agent",
                action="analyze_patterns",
                parameters={"analysis_depth": "standard", "parallel_safe": True},
                dependencies=[],
                expected_duration=200,  # Faster in parallel
                priority=1,
                retry_policy={"max_retries": 2, "backoff": "exponential"},
                success_criteria={"confidence": 0.6}
            ))
            step_id += 1
            
        if "improvement_agent" in context.available_agents:
            parallel_steps.append(ExecutionStep(
                step_id=f"par_step_{step_id}",
                agent_name="improvement_agent",
                action="prepare_optimizations",
                parameters={"parallel_safe": True},
                dependencies=[],
                expected_duration=180,
                priority=1,
                retry_policy={"max_retries": 2, "backoff": "exponential"},
                success_criteria={"preparation_complete": True}
            ))
            step_id += 1
            
        steps.extend(parallel_steps)
        
        # Synchronization step
        if parallel_steps:
            sync_dependencies = [step.step_id for step in parallel_steps]
            steps.append(ExecutionStep(
                step_id=f"par_step_{step_id}",
                agent_name="planning_agent",
                action="synchronize_results",
                parameters={"merge_strategy": "best_practices"},
                dependencies=sync_dependencies,
                expected_duration=60,
                priority=2,
                retry_policy={"max_retries": 1, "backoff": "linear"},
                success_criteria={"sync_complete": True}
            ))
            step_id += 1
            
        # Execution phase
        if "execution_agent" in context.available_agents:
            steps.append(ExecutionStep(
                step_id=f"par_step_{step_id}",
                agent_name="execution_agent",
                action="execute_research",
                parameters=context.task_requirements,
                dependencies=[f"par_step_{step_id-1}"],
                expected_duration=3200,  # Slightly faster due to preparation
                priority=3,
                retry_policy={"max_retries": 1, "backoff": "exponential"},
                success_criteria={"completion": True}
            ))
            
        strategy = ExecutionStrategy(
            strategy_id=f"parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            strategy_type=StrategyType.PARALLEL,
            optimization_targets=[OptimizationTarget.SPEED, OptimizationTarget.ACCURACY],
            steps=steps,
            estimated_duration=max(
                max(step.expected_duration for step in parallel_steps) if parallel_steps else 0,
                sum(step.expected_duration for step in steps if step not in parallel_steps)
            ),
            estimated_cost=self.estimate_strategy_cost(steps) * 1.2,  # Parallel overhead
            success_probability=0.78,  # Slightly lower due to coordination complexity
            contingency_plans=[],
            metadata={"description": "Parallel execution with synchronization"},
            created_at=datetime.now()
        )
        
        strategies.append(strategy)
        return strategies
        
    async def generate_adaptive_strategies(self, context: PlanningContext, 
                                         patterns: List[Dict[str, Any]]) -> List[ExecutionStrategy]:
        """Generate adaptive execution strategies that adjust based on runtime conditions"""
        strategies = []
        
        steps = []
        step_id = 0
        
        # Initial assessment
        steps.append(ExecutionStep(
            step_id=f"adapt_step_{step_id}",
            agent_name="learning_agent" if "learning_agent" in context.available_agents else "planning_agent",
            action="assess_conditions",
            parameters={"assessment_type": "runtime_conditions"},
            dependencies=[],
            expected_duration=120,
            priority=1,
            retry_policy={"max_retries": 3, "backoff": "exponential"},
            success_criteria={"assessment_complete": True}
        ))
        step_id += 1
        
        # Adaptive decision point
        steps.append(ExecutionStep(
            step_id=f"adapt_step_{step_id}",
            agent_name="planning_agent",
            action="make_adaptive_decision",
            parameters={
                "decision_criteria": ["performance_trend", "resource_availability", "time_remaining"],
                "fallback_strategies": ["sequential", "parallel"]
            },
            dependencies=[f"adapt_step_{step_id-1}"],
            expected_duration=90,
            priority=2,
            retry_policy={"max_retries": 2, "backoff": "linear"},
            success_criteria={"decision_made": True}
        ))
        step_id += 1
        
        # Conditional execution branches
        for branch_type in ["optimistic", "conservative"]:
            branch_steps = self.create_conditional_branch(
                branch_type, context, step_id, f"adapt_step_{step_id-1}"
            )
            steps.extend(branch_steps)
            step_id += len(branch_steps)
            
        strategy = ExecutionStrategy(
            strategy_id=f"adaptive_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            strategy_type=StrategyType.ADAPTIVE,
            optimization_targets=[OptimizationTarget.RELIABILITY, OptimizationTarget.SPEED],
            steps=steps,
            estimated_duration=self.estimate_adaptive_duration(steps, patterns),
            estimated_cost=self.estimate_strategy_cost(steps) * 0.9,  # Adaptive optimization
            success_probability=0.82,
            contingency_plans=[],
            metadata={"description": "Adaptive strategy with runtime decision making"},
            created_at=datetime.now()
        )
        
        strategies.append(strategy)
        return strategies
        
    async def generate_hierarchical_strategies(self, context: PlanningContext, 
                                             patterns: List[Dict[str, Any]]) -> List[ExecutionStrategy]:
        """Generate hierarchical execution strategies with multiple levels"""
        strategies = []
        
        # Only generate if we have enough agents for hierarchy
        if len(context.available_agents) < 3:
            return strategies
            
        steps = []
        step_id = 0
        
        # Level 1: Strategic planning
        steps.append(ExecutionStep(
            step_id=f"hier_step_{step_id}",
            agent_name="planning_agent",
            action="strategic_planning",
            parameters={"planning_level": "strategic", "horizon": "long_term"},
            dependencies=[],
            expected_duration=300,
            priority=1,
            retry_policy={"max_retries": 2, "backoff": "exponential"},
            success_criteria={"strategic_plan_complete": True}
        ))
        step_id += 1
        
        # Level 2: Tactical planning
        steps.append(ExecutionStep(
            step_id=f"hier_step_{step_id}",
            agent_name="improvement_agent" if "improvement_agent" in context.available_agents else "planning_agent",
            action="tactical_planning",
            parameters={"planning_level": "tactical", "horizon": "medium_term"},
            dependencies=[f"hier_step_{step_id-1}"],
            expected_duration=240,
            priority=2,
            retry_policy={"max_retries": 2, "backoff": "exponential"},
            success_criteria={"tactical_plan_complete": True}
        ))
        step_id += 1
        
        # Level 3: Operational execution
        steps.append(ExecutionStep(
            step_id=f"hier_step_{step_id}",
            agent_name="execution_agent" if "execution_agent" in context.available_agents else "planning_agent",
            action="operational_execution",
            parameters=context.task_requirements,
            dependencies=[f"hier_step_{step_id-1}"],
            expected_duration=3000,
            priority=3,
            retry_policy={"max_retries": 1, "backoff": "exponential"},
            success_criteria={"execution_complete": True}
        ))
        step_id += 1
        
        # Level 4: Review and feedback
        if "review_agent" in context.available_agents:
            steps.append(ExecutionStep(
                step_id=f"hier_step_{step_id}",
                agent_name="review_agent",
                action="hierarchical_review",
                parameters={"review_levels": ["operational", "tactical", "strategic"]},
                dependencies=[f"hier_step_{step_id-1}"],
                expected_duration=450,
                priority=4,
                retry_policy={"max_retries": 2, "backoff": "linear"},
                success_criteria={"multi_level_review_complete": True}
            ))
            
        strategy = ExecutionStrategy(
            strategy_id=f"hierarchical_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            strategy_type=StrategyType.HIERARCHICAL,
            optimization_targets=[OptimizationTarget.COMPLETENESS, OptimizationTarget.ACCURACY],
            steps=steps,
            estimated_duration=sum(step.expected_duration for step in steps),
            estimated_cost=self.estimate_strategy_cost(steps) * 1.1,  # Hierarchy overhead
            success_probability=0.88,  # Higher due to multiple planning levels
            contingency_plans=[],
            metadata={"description": "Hierarchical strategy with multiple planning levels"},
            created_at=datetime.now()
        )
        
        strategies.append(strategy)
        return strategies
        
    async def generate_probabilistic_strategies(self, context: PlanningContext, 
                                              patterns: List[Dict[str, Any]]) -> List[ExecutionStrategy]:
        """Generate probabilistic strategies with uncertainty modeling"""
        strategies = []
        
        # Estimate probabilities from patterns
        success_probabilities = self.estimate_step_probabilities(context, patterns)
        
        steps = []
        step_id = 0
        
        # Probabilistic execution with multiple paths
        for path_name in ["high_confidence", "medium_confidence", "low_confidence"]:
            path_steps = self.create_probabilistic_path(
                path_name, context, success_probabilities, step_id
            )
            steps.extend(path_steps)
            step_id += len(path_steps)
            
        strategy = ExecutionStrategy(
            strategy_id=f"probabilistic_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            strategy_type=StrategyType.PROBABILISTIC,
            optimization_targets=[OptimizationTarget.RELIABILITY, OptimizationTarget.COST],
            steps=steps,
            estimated_duration=self.estimate_probabilistic_duration(steps, success_probabilities),
            estimated_cost=self.estimate_strategy_cost(steps) * 0.8,  # Cost optimized
            success_probability=self.calculate_composite_probability(steps, success_probabilities),
            contingency_plans=[],
            metadata={"description": "Probabilistic strategy with uncertainty handling"},
            created_at=datetime.now()
        )
        
        strategies.append(strategy)
        return strategies
        
    def create_conditional_branch(self, branch_type: str, context: PlanningContext, 
                                 start_id: int, dependency: str) -> List[ExecutionStep]:
        """Create conditional execution branch"""
        steps = []
        
        if branch_type == "optimistic":
            # Fast path with minimal checks
            steps.append(ExecutionStep(
                step_id=f"opt_step_{start_id}",
                agent_name="execution_agent" if "execution_agent" in context.available_agents else "planning_agent",
                action="fast_execution",
                parameters={**context.task_requirements, "speed_priority": True},
                dependencies=[dependency],
                expected_duration=2400,  # Faster execution
                priority=3,
                retry_policy={"max_retries": 1, "backoff": "linear"},
                success_criteria={"completion": True, "speed_target_met": True}
            ))
        else:  # conservative
            # Careful path with extensive validation
            steps.append(ExecutionStep(
                step_id=f"cons_step_{start_id}",
                agent_name="execution_agent" if "execution_agent" in context.available_agents else "planning_agent",
                action="careful_execution",
                parameters={**context.task_requirements, "accuracy_priority": True},
                dependencies=[dependency],
                expected_duration=4200,  # Slower but more thorough
                priority=3,
                retry_policy={"max_retries": 3, "backoff": "exponential"},
                success_criteria={"completion": True, "accuracy_target_met": True}
            ))
            
        return steps
        
    def estimate_step_probabilities(self, context: PlanningContext, 
                                  patterns: List[Dict[str, Any]]) -> Dict[str, float]:
        """Estimate success probabilities for different types of steps"""
        probabilities = {}
        
        # Default probabilities
        default_probs = {
            "learning_agent": 0.85,
            "planning_agent": 0.90,
            "improvement_agent": 0.80,
            "execution_agent": 0.75,
            "audit_agent": 0.95,
            "review_agent": 0.88
        }
        
        # Adjust based on patterns
        for pattern in patterns:
            agent_name = pattern.get("agent_name")
            if agent_name in default_probs:
                if pattern.get("pattern_type") == "success_trend":
                    if pattern.get("trend") == "improving":
                        default_probs[agent_name] *= 1.1
                    else:
                        default_probs[agent_name] *= 0.9
                        
        return default_probs
        
    def create_probabilistic_path(self, path_name: str, context: PlanningContext, 
                                 probabilities: Dict[str, float], start_id: int) -> List[ExecutionStep]:
        """Create probabilistic execution path"""
        steps = []
        
        # Adjust parameters based on confidence level
        if path_name == "high_confidence":
            duration_factor = 0.8
            retry_count = 1
        elif path_name == "medium_confidence":
            duration_factor = 1.0
            retry_count = 2
        else:  # low_confidence
            duration_factor = 1.3
            retry_count = 3
            
        step = ExecutionStep(
            step_id=f"prob_{path_name}_{start_id}",
            agent_name="execution_agent" if "execution_agent" in context.available_agents else "planning_agent",
            action="probabilistic_execution",
            parameters={
                **context.task_requirements, 
                "confidence_level": path_name,
                "probability_threshold": probabilities.get("execution_agent", 0.75)
            },
            dependencies=[],
            expected_duration=3600 * duration_factor,
            priority=1,
            retry_policy={"max_retries": retry_count, "backoff": "exponential"},
            success_criteria={"completion": True, "confidence_met": True}
        )
        
        steps.append(step)
        return steps
        
    def estimate_adaptive_duration(self, steps: List[ExecutionStep], 
                                  patterns: List[Dict[str, Any]]) -> float:
        """Estimate duration for adaptive strategy"""
        base_duration = sum(step.expected_duration for step in steps)
        
        # Adjust based on historical adaptation patterns
        adaptation_factor = 1.0
        for pattern in patterns:
            if "adaptive" in pattern.get("description", "").lower():
                if pattern.get("trend") == "improving":
                    adaptation_factor *= 0.95
                else:
                    adaptation_factor *= 1.05
                    
        return base_duration * adaptation_factor
        
    def estimate_probabilistic_duration(self, steps: List[ExecutionStep], 
                                       probabilities: Dict[str, float]) -> float:
        """Estimate duration for probabilistic strategy considering success rates"""
        total_duration = 0
        
        for step in steps:
            base_duration = step.expected_duration
            agent_prob = probabilities.get(step.agent_name, 0.8)
            
            # Account for retries
            max_retries = step.retry_policy.get("max_retries", 1)
            expected_attempts = 1 + (max_retries * (1 - agent_prob))
            
            total_duration += base_duration * expected_attempts
            
        return total_duration
        
    def calculate_composite_probability(self, steps: List[ExecutionStep], 
                                      probabilities: Dict[str, float]) -> float:
        """Calculate composite success probability for strategy"""
        composite_prob = 1.0
        
        for step in steps:
            step_prob = probabilities.get(step.agent_name, 0.8)
            
            # Account for retries
            max_retries = step.retry_policy.get("max_retries", 1)
            step_success_prob = 1 - ((1 - step_prob) ** (max_retries + 1))
            
            composite_prob *= step_success_prob
            
        return composite_prob
        
    def estimate_strategy_cost(self, steps: List[ExecutionStep]) -> float:
        """Estimate cost of executing a strategy"""
        # Simple cost model based on duration and agent type
        cost_per_minute = {
            "learning_agent": 0.05,
            "planning_agent": 0.03,
            "improvement_agent": 0.04,
            "execution_agent": 0.10,  # Most expensive due to API calls
            "audit_agent": 0.02,
            "review_agent": 0.06
        }
        
        total_cost = 0
        for step in steps:
            agent_cost = cost_per_minute.get(step.agent_name, 0.05)
            duration_minutes = step.expected_duration / 60
            total_cost += agent_cost * duration_minutes
            
        return total_cost
        
    async def evaluate_strategies(self, strategies: List[ExecutionStrategy], 
                                context: PlanningContext) -> List[Tuple[ExecutionStrategy, float]]:
        """Evaluate and rank strategies"""
        scored_strategies = []
        
        for strategy in strategies:
            score = await self.calculate_strategy_score(strategy, context)
            scored_strategies.append((strategy, score))
            
        # Sort by score (higher is better)
        scored_strategies.sort(key=lambda x: x[1], reverse=True)
        
        self.logger.info(f"Evaluated {len(strategies)} strategies, top score: {scored_strategies[0][1]:.3f}")
        
        return scored_strategies
        
    async def calculate_strategy_score(self, strategy: ExecutionStrategy, 
                                     context: PlanningContext) -> float:
        """Calculate score for a strategy"""
        score = 0
        
        # Base score from success probability
        score += strategy.success_probability * 40
        
        # Time constraints penalty/bonus
        if context.time_constraints:
            time_limit = context.time_constraints.total_seconds()
            if strategy.estimated_duration <= time_limit:
                score += 20 * (1 - strategy.estimated_duration / time_limit)
            else:
                score -= 30 * (strategy.estimated_duration / time_limit - 1)
                
        # Cost constraints penalty/bonus
        if context.cost_constraints:
            if strategy.estimated_cost <= context.cost_constraints:
                score += 15 * (1 - strategy.estimated_cost / context.cost_constraints)
            else:
                score -= 25 * (strategy.estimated_cost / context.cost_constraints - 1)
                
        # Optimization target alignment
        for target in strategy.optimization_targets:
            weight = self.optimization_weights.get(target.value, 0.1)
            score += weight * 10
            
        # Strategy type bonus based on context
        if strategy.strategy_type == StrategyType.ADAPTIVE:
            score += 5  # Bonus for adaptability
        elif strategy.strategy_type == StrategyType.PARALLEL and len(context.available_agents) > 2:
            score += 8  # Bonus for parallelization when possible
        elif strategy.strategy_type == StrategyType.SEQUENTIAL:
            score += 3  # Small bonus for reliability
            
        return max(0, score)  # Ensure non-negative score
        
    async def select_optimal_strategy(self, ranked_strategies: List[Tuple[ExecutionStrategy, float]], 
                                    context: PlanningContext) -> ExecutionStrategy:
        """Select optimal strategy from ranked candidates"""
        if not ranked_strategies:
            raise ValueError("No strategies to choose from")
            
        # Select top strategy
        optimal_strategy = ranked_strategies[0][0]
        
        self.logger.info(f"Selected optimal strategy: {optimal_strategy.strategy_type.value} "
                        f"(score: {ranked_strategies[0][1]:.3f})")
        
        return optimal_strategy
        
    async def generate_contingency_plans(self, strategy: ExecutionStrategy, 
                                       context: PlanningContext) -> List[Dict[str, Any]]:
        """Generate contingency plans for strategy"""
        contingency_plans = []
        
        # Failure recovery plan
        contingency_plans.append({
            "trigger": "step_failure",
            "condition": "any_step_fails",
            "action": "retry_with_fallback",
            "parameters": {
                "max_fallback_attempts": 2,
                "fallback_strategy": "sequential"
            }
        })
        
        # Resource constraint plan
        contingency_plans.append({
            "trigger": "resource_constraint",
            "condition": "execution_time_exceeded",
            "action": "switch_to_fast_mode",
            "parameters": {
                "reduced_accuracy_threshold": 0.1,
                "skip_optional_steps": True
            }
        })
        
        # Quality threshold plan
        contingency_plans.append({
            "trigger": "quality_threshold",
            "condition": "quality_below_threshold",
            "action": "iterate_improvement",
            "parameters": {
                "max_iterations": 2,
                "improvement_threshold": 0.05
            }
        })
        
        return contingency_plans
        
    async def create_execution_plan(self, strategy: ExecutionStrategy, 
                                  contingency_plans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create detailed execution plan"""
        return {
            "strategy_id": strategy.strategy_id,
            "execution_order": [step.step_id for step in strategy.steps],
            "step_details": {step.step_id: asdict(step) for step in strategy.steps},
            "estimated_timeline": {
                "total_duration": strategy.estimated_duration,
                "start_time": datetime.now().isoformat(),
                "estimated_completion": (datetime.now() + timedelta(seconds=strategy.estimated_duration)).isoformat()
            },
            "resource_requirements": self.calculate_resource_requirements(strategy),
            "success_criteria": self.extract_success_criteria(strategy),
            "contingency_plans": contingency_plans,
            "monitoring_points": self.identify_monitoring_points(strategy)
        }
        
    def calculate_resource_requirements(self, strategy: ExecutionStrategy) -> Dict[str, Any]:
        """Calculate resource requirements for strategy"""
        agents_needed = list(set(step.agent_name for step in strategy.steps))
        max_concurrent = len([step for step in strategy.steps if not step.dependencies])
        
        return {
            "agents_required": agents_needed,
            "max_concurrent_agents": max_concurrent,
            "estimated_cost": strategy.estimated_cost,
            "estimated_duration": strategy.estimated_duration,
            "memory_requirements": "standard",  # Could be calculated more precisely
            "network_requirements": "moderate"
        }
        
    def extract_success_criteria(self, strategy: ExecutionStrategy) -> Dict[str, Any]:
        """Extract success criteria from strategy steps"""
        criteria = {}
        
        for step in strategy.steps:
            criteria[step.step_id] = step.success_criteria
            
        criteria["overall"] = {
            "all_steps_complete": True,
            "success_probability_threshold": 0.7,
            "quality_threshold": 0.8
        }
        
        return criteria
        
    def identify_monitoring_points(self, strategy: ExecutionStrategy) -> List[Dict[str, Any]]:
        """Identify key monitoring points in strategy"""
        monitoring_points = []
        
        # Monitor after each step
        for i, step in enumerate(strategy.steps):
            monitoring_points.append({
                "point_id": f"monitor_{i}",
                "trigger": "step_completion",
                "step_id": step.step_id,
                "metrics_to_check": ["completion_status", "execution_time", "quality_score"],
                "alert_conditions": ["step_failure", "timeout", "low_quality"]
            })
            
        # Overall strategy monitoring
        monitoring_points.append({
            "point_id": "strategy_monitor",
            "trigger": "continuous",
            "metrics_to_check": ["overall_progress", "resource_usage", "cost_tracking"],
            "alert_conditions": ["budget_exceeded", "time_exceeded", "quality_degradation"]
        })
        
        return monitoring_points
        
    async def save_strategy(self, strategy: ExecutionStrategy, execution_plan: Dict[str, Any]):
        """Save strategy for future learning"""
        strategy_data = {
            "strategy": asdict(strategy),
            "execution_plan": execution_plan,
            "created_at": datetime.now().isoformat()
        }
        
        strategy_file = self.memory_dir / f"strategy_{strategy.strategy_id}.json"
        with open(strategy_file, 'w') as f:
            json.dump(strategy_data, f, indent=2, default=str)
            
        # Also save to planning history
        self.generated_strategies.append(strategy_data)
        
        # Keep only recent strategies
        self.generated_strategies = self.generated_strategies[-50:]
        
        history_file = self.memory_dir / "strategy_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.generated_strategies, f, indent=2, default=str)
            
    def calculate_planning_confidence(self, optimal_strategy: ExecutionStrategy, 
                                    ranked_strategies: List[Tuple[ExecutionStrategy, float]]) -> float:
        """Calculate confidence in planning results"""
        if len(ranked_strategies) < 2:
            return 0.7  # Default confidence for single strategy
            
        top_score = ranked_strategies[0][1]
        second_score = ranked_strategies[1][1]
        
        # Higher confidence if top strategy significantly outperforms others
        score_gap = (top_score - second_score) / max(top_score, 1)
        
        # Base confidence from strategy success probability
        base_confidence = optimal_strategy.success_probability
        
        # Combine factors
        planning_confidence = (base_confidence * 0.7) + (score_gap * 0.3)
        
        return min(max(planning_confidence, 0.0), 1.0)
        
    def create_planning_summary(self, optimal_strategy: ExecutionStrategy, 
                               candidate_strategies: List[ExecutionStrategy]) -> Dict[str, Any]:
        """Create summary of planning process"""
        return {
            "planning_timestamp": datetime.now().isoformat(),
            "candidates_generated": len(candidate_strategies),
            "optimal_strategy_type": optimal_strategy.strategy_type.value,
            "optimization_targets": [target.value for target in optimal_strategy.optimization_targets],
            "estimated_metrics": {
                "duration": optimal_strategy.estimated_duration,
                "cost": optimal_strategy.estimated_cost,
                "success_probability": optimal_strategy.success_probability
            },
            "strategy_breakdown": {
                "total_steps": len(optimal_strategy.steps),
                "agents_involved": list(set(step.agent_name for step in optimal_strategy.steps)),
                "critical_path": self.identify_critical_path(optimal_strategy)
            }
        }
        
    def identify_critical_path(self, strategy: ExecutionStrategy) -> List[str]:
        """Identify critical path through strategy steps"""
        # Simple implementation - could be more sophisticated with proper critical path analysis
        critical_steps = []
        
        # Find steps with no dependencies (starting points)
        start_steps = [step for step in strategy.steps if not step.dependencies]
        
        if start_steps:
            # Follow the longest path
            current_step = max(start_steps, key=lambda x: x.expected_duration)
            critical_steps.append(current_step.step_id)
            
            # Continue following dependencies (simplified)
            while True:
                next_steps = [
                    step for step in strategy.steps 
                    if current_step.step_id in step.dependencies
                ]
                if not next_steps:
                    break
                current_step = max(next_steps, key=lambda x: x.expected_duration)
                critical_steps.append(current_step.step_id)
                
        return critical_steps
        
    def load_planning_knowledge(self):
        """Load existing planning knowledge and history"""
        # Load strategy history
        history_file = self.memory_dir / "strategy_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self.generated_strategies = json.load(f)
                self.logger.info(f"Loaded {len(self.generated_strategies)} historical strategies")
            except Exception as e:
                self.logger.warning(f"Failed to load strategy history: {e}")
                
        # Load strategy performance data
        performance_file = self.memory_dir / "strategy_performance.json"
        if performance_file.exists():
            try:
                with open(performance_file, 'r') as f:
                    self.strategy_performance_history = json.load(f)
                self.logger.info(f"Loaded performance data for {len(self.strategy_performance_history)} strategies")
            except Exception as e:
                self.logger.warning(f"Failed to load strategy performance: {e}")