#!/usr/bin/env python3
"""
Learning Agent for Agentic Deep Research System
Analyzes past performance and extracts patterns to improve future executions
"""

import json
import time
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict, Counter
import statistics
import numpy as np
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentResult, AgentStatus, AgentContext

@dataclass
class LearningPattern:
    """Represents a learned pattern"""
    pattern_type: str
    description: str
    confidence: float
    occurrences: int
    success_correlation: float
    conditions: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

@dataclass
class PerformanceInsight:
    """Represents a performance insight"""
    insight_type: str
    title: str
    description: str
    impact_score: float
    evidence: List[str]
    recommendations: List[str]
    confidence: float
    timestamp: datetime

class LearningAgent(BaseAgent):
    """Agent that learns from past executions to improve future performance"""
    
    def __init__(self, config: Dict[str, Any], context: AgentContext):
        super().__init__("learning_agent", config, context)
        
        # Learning configuration
        self.learning_rate = config.get("learning_rate", 0.1)
        self.pattern_threshold = config.get("pattern_threshold", 0.7)
        self.memory_window = config.get("memory_window", 100)
        self.min_confidence = config.get("min_confidence", 0.6)
        
        # Learning state
        self.discovered_patterns = []
        self.performance_insights = []
        self.learning_history = []
        
        # Load existing knowledge
        self.load_learned_knowledge()
        
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute learning analysis"""
        start_time = time.time()
        self.set_status(AgentStatus.RUNNING)
        
        try:
            self.logger.info("Starting learning analysis...")
            
            # Collect data from all agents
            agent_data = await self.collect_agent_data()
            
            # Analyze performance patterns
            patterns = await self.analyze_performance_patterns(agent_data)
            
            # Extract insights
            insights = await self.extract_insights(agent_data, patterns)
            
            # Generate recommendations
            recommendations = await self.generate_recommendations(patterns, insights)
            
            # Update knowledge base
            await self.update_knowledge_base(patterns, insights)
            
            # Calculate learning confidence
            confidence = self.calculate_learning_confidence(patterns, insights)
            
            result_data = {
                "patterns_discovered": len(patterns),
                "insights_generated": len(insights),
                "recommendations": recommendations,
                "patterns": patterns,
                "insights": insights,
                "learning_summary": self.create_learning_summary(patterns, insights)
            }
            
            execution_time = time.time() - start_time
            result = self.create_result(
                status=AgentStatus.COMPLETED,
                result_data=result_data,
                execution_time=execution_time,
                confidence=confidence
            )
            
            self.logger.info(f"Learning analysis completed: {len(patterns)} patterns, {len(insights)} insights")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Learning analysis failed: {e}")
            
            return self.create_result(
                status=AgentStatus.FAILED,
                result_data={"error_details": str(e)},
                execution_time=execution_time,
                error=str(e)
            )
        finally:
            self.set_status(AgentStatus.IDLE)
            
    async def collect_agent_data(self) -> Dict[str, Any]:
        """Collect execution data from all agents"""
        agent_data = {
            "execution_histories": {},
            "performance_metrics": {},
            "results": {},
            "configurations": {}
        }
        
        # Collect data from all agent directories
        agents_dir = self.context.research_root / "agents"
        if not agents_dir.exists():
            return agent_data
            
        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir() or agent_dir.name == self.name:
                continue
                
            agent_name = agent_dir.name
            
            # Load execution history
            history_file = agent_dir / "execution_history.jsonl"
            if history_file.exists():
                history = []
                try:
                    with open(history_file, 'r') as f:
                        for line in f:
                            history.append(json.loads(line.strip()))
                    agent_data["execution_histories"][agent_name] = history
                except Exception as e:
                    self.logger.warning(f"Failed to load history for {agent_name}: {e}")
                    
            # Load performance metrics
            metrics_file = agent_dir / "performance_metrics.json"
            if metrics_file.exists():
                try:
                    with open(metrics_file, 'r') as f:
                        agent_data["performance_metrics"][agent_name] = json.load(f)
                except Exception as e:
                    self.logger.warning(f"Failed to load metrics for {agent_name}: {e}")
                    
            # Load recent results
            results_dir = agent_dir / "results"
            if results_dir.exists():
                recent_results = []
                for result_file in results_dir.glob("*.json"):
                    try:
                        with open(result_file, 'r') as f:
                            recent_results.append(json.load(f))
                    except Exception as e:
                        continue
                        
                # Keep only recent results (last 20)
                recent_results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                agent_data["results"][agent_name] = recent_results[:20]
                
            # Load configuration
            config_file = agent_dir / "adapted_config.json"
            if not config_file.exists():
                config_file = self.context.research_root / "config" / "config.yaml"
                
            if config_file.exists():
                try:
                    if config_file.suffix == '.json':
                        with open(config_file, 'r') as f:
                            agent_data["configurations"][agent_name] = json.load(f)
                    else:
                        import yaml
                        with open(config_file, 'r') as f:
                            config = yaml.safe_load(f)
                            agent_data["configurations"][agent_name] = config.get("agents", {}).get(agent_name, {})
                except Exception as e:
                    self.logger.warning(f"Failed to load config for {agent_name}: {e}")
                    
        self.logger.info(f"Collected data from {len(agent_data['execution_histories'])} agents")
        return agent_data
        
    async def analyze_performance_patterns(self, agent_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze patterns in agent performance"""
        patterns = []
        
        for agent_name, history in agent_data["execution_histories"].items():
            if len(history) < 5:  # Need minimum data for pattern analysis
                continue
                
            # Analyze success/failure patterns
            success_pattern = self.analyze_success_patterns(agent_name, history)
            if success_pattern:
                patterns.append(success_pattern)
                
            # Analyze execution time patterns
            time_pattern = self.analyze_time_patterns(agent_name, history)
            if time_pattern:
                patterns.append(time_pattern)
                
            # Analyze confidence patterns
            confidence_pattern = self.analyze_confidence_patterns(agent_name, history)
            if confidence_pattern:
                patterns.append(confidence_pattern)
                
            # Analyze error patterns
            error_pattern = self.analyze_error_patterns(agent_name, history)
            if error_pattern:
                patterns.append(error_pattern)
                
        # Cross-agent patterns
        cross_patterns = self.analyze_cross_agent_patterns(agent_data)
        patterns.extend(cross_patterns)
        
        # Filter patterns by confidence threshold
        significant_patterns = [
            p for p in patterns 
            if p.get("confidence", 0) >= self.pattern_threshold
        ]
        
        self.logger.info(f"Discovered {len(significant_patterns)} significant patterns")
        return significant_patterns
        
    def analyze_success_patterns(self, agent_name: str, history: List[Dict]) -> Optional[Dict]:
        """Analyze success/failure patterns for an agent"""
        if len(history) < 10:
            return None
            
        # Get recent success/failure sequence
        recent_results = [entry.get("status") == "completed" for entry in history[-20:]]
        
        # Calculate success rate trends
        first_half = recent_results[:len(recent_results)//2]
        second_half = recent_results[len(recent_results)//2:]
        
        first_success_rate = sum(first_half) / len(first_half)
        second_success_rate = sum(second_half) / len(second_half)
        
        trend = "improving" if second_success_rate > first_success_rate else "declining"
        trend_strength = abs(second_success_rate - first_success_rate)
        
        if trend_strength < 0.1:  # Not significant
            return None
            
        # Identify potential causes
        conditions = {}
        if trend == "declining":
            # Look for common factors in failures
            failed_entries = [e for e in history[-20:] if e.get("status") != "completed"]
            if failed_entries:
                error_types = [e.get("error", "unknown")[:50] for e in failed_entries]
                most_common_error = Counter(error_types).most_common(1)[0][0]
                conditions["common_failure_cause"] = most_common_error
                
        pattern = {
            "pattern_type": "success_trend",
            "agent_name": agent_name,
            "description": f"Success rate {trend} from {first_success_rate:.2%} to {second_success_rate:.2%}",
            "confidence": min(trend_strength * 2, 1.0),  # Scale to 0-1
            "conditions": conditions,
            "trend": trend,
            "trend_strength": trend_strength,
            "recommendations": self.get_success_trend_recommendations(trend, conditions)
        }
        
        return pattern
        
    def analyze_time_patterns(self, agent_name: str, history: List[Dict]) -> Optional[Dict]:
        """Analyze execution time patterns"""
        execution_times = [
            entry.get("execution_time", 0) for entry in history[-20:]
            if entry.get("execution_time") is not None
        ]
        
        if len(execution_times) < 10:
            return None
            
        # Calculate time trend
        first_half = execution_times[:len(execution_times)//2]
        second_half = execution_times[len(execution_times)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        change_ratio = (second_avg - first_avg) / first_avg if first_avg > 0 else 0
        
        if abs(change_ratio) < 0.2:  # Less than 20% change not significant
            return None
            
        trend = "increasing" if change_ratio > 0 else "decreasing"
        
        # Detect outliers that might indicate issues
        std_dev = statistics.stdev(execution_times)
        mean_time = statistics.mean(execution_times)
        outliers = [t for t in execution_times if abs(t - mean_time) > 2 * std_dev]
        
        conditions = {
            "change_ratio": change_ratio,
            "average_time": second_avg,
            "outlier_count": len(outliers)
        }
        
        pattern = {
            "pattern_type": "execution_time_trend",
            "agent_name": agent_name,
            "description": f"Execution time {trend} by {abs(change_ratio):.1%}",
            "confidence": min(abs(change_ratio), 1.0),
            "conditions": conditions,
            "trend": trend,
            "recommendations": self.get_time_trend_recommendations(trend, conditions)
        }
        
        return pattern
        
    def analyze_confidence_patterns(self, agent_name: str, history: List[Dict]) -> Optional[Dict]:
        """Analyze confidence score patterns"""
        confidence_scores = [
            entry.get("confidence") for entry in history[-20:]
            if entry.get("confidence") is not None
        ]
        
        if len(confidence_scores) < 10:
            return None
            
        # Calculate confidence trend
        first_half = confidence_scores[:len(confidence_scores)//2]
        second_half = confidence_scores[len(confidence_scores)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        change_ratio = (second_avg - first_avg) / first_avg if first_avg > 0 else 0
        
        if abs(change_ratio) < 0.1:  # Less than 10% change not significant
            return None
            
        trend = "increasing" if change_ratio > 0 else "decreasing"
        
        conditions = {
            "change_ratio": change_ratio,
            "average_confidence": second_avg,
            "below_threshold_count": len([c for c in second_half if c < self.min_confidence])
        }
        
        pattern = {
            "pattern_type": "confidence_trend",
            "agent_name": agent_name,
            "description": f"Confidence {trend} by {abs(change_ratio):.1%}",
            "confidence": min(abs(change_ratio) * 2, 1.0),
            "conditions": conditions,
            "trend": trend,
            "recommendations": self.get_confidence_trend_recommendations(trend, conditions)
        }
        
        return pattern
        
    def analyze_error_patterns(self, agent_name: str, history: List[Dict]) -> Optional[Dict]:
        """Analyze error patterns"""
        error_entries = [
            entry for entry in history[-50:]
            if entry.get("error") is not None
        ]
        
        if len(error_entries) < 3:
            return None
            
        # Categorize errors
        error_types = {}
        for entry in error_entries:
            error_msg = entry.get("error", "")
            # Simple error categorization
            if "timeout" in error_msg.lower():
                error_type = "timeout"
            elif "connection" in error_msg.lower():
                error_type = "connection"
            elif "rate limit" in error_msg.lower():
                error_type = "rate_limit"
            elif "authentication" in error_msg.lower():
                error_type = "auth"
            else:
                error_type = "other"
                
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
        # Find most common error type
        most_common_error, error_count = max(error_types.items(), key=lambda x: x[1])
        
        if error_count < 2:
            return None
            
        error_rate = len(error_entries) / len(history[-50:])
        
        conditions = {
            "most_common_error": most_common_error,
            "error_count": error_count,
            "error_rate": error_rate,
            "error_distribution": error_types
        }
        
        pattern = {
            "pattern_type": "error_pattern",
            "agent_name": agent_name,
            "description": f"Recurring {most_common_error} errors ({error_count} occurrences)",
            "confidence": min(error_count / 10, 1.0),
            "conditions": conditions,
            "recommendations": self.get_error_pattern_recommendations(most_common_error, conditions)
        }
        
        return pattern
        
    def analyze_cross_agent_patterns(self, agent_data: Dict[str, Any]) -> List[Dict]:
        """Analyze patterns across multiple agents"""
        patterns = []
        
        # Analyze correlation between agent performances
        agent_performances = {}
        for agent_name, history in agent_data["execution_histories"].items():
            if len(history) >= 10:
                recent_success_rate = sum(
                    1 for entry in history[-10:] if entry.get("status") == "completed"
                ) / 10
                agent_performances[agent_name] = recent_success_rate
                
        if len(agent_performances) >= 2:
            # Look for correlated failures
            low_performers = [name for name, rate in agent_performances.items() if rate < 0.7]
            if len(low_performers) >= 2:
                pattern = {
                    "pattern_type": "cross_agent_failure",
                    "description": f"Multiple agents underperforming: {', '.join(low_performers)}",
                    "confidence": len(low_performers) / len(agent_performances),
                    "conditions": {
                        "low_performers": low_performers,
                        "performance_rates": {name: agent_performances[name] for name in low_performers}
                    },
                    "recommendations": [
                        "Investigate common infrastructure issues",
                        "Check for shared configuration problems",
                        "Review resource constraints"
                    ]
                }
                patterns.append(pattern)
                
        return patterns
        
    def get_success_trend_recommendations(self, trend: str, conditions: Dict) -> List[str]:
        """Get recommendations for success trend patterns"""
        recommendations = []
        
        if trend == "declining":
            recommendations.extend([
                "Investigate root cause of recent failures",
                "Consider reverting recent configuration changes",
                "Implement additional error handling"
            ])
            
            if "common_failure_cause" in conditions:
                recommendations.append(f"Address recurring issue: {conditions['common_failure_cause']}")
                
        else:  # improving
            recommendations.extend([
                "Document successful approaches for future reference",
                "Consider applying similar patterns to other agents"
            ])
            
        return recommendations
        
    def get_time_trend_recommendations(self, trend: str, conditions: Dict) -> List[str]:
        """Get recommendations for time trend patterns"""
        recommendations = []
        
        if trend == "increasing":
            recommendations.extend([
                "Investigate performance bottlenecks",
                "Consider optimizing resource allocation",
                "Review timeout configurations"
            ])
            
            if conditions.get("outlier_count", 0) > 2:
                recommendations.append("Investigate outlier executions for issues")
                
        else:  # decreasing
            recommendations.extend([
                "Document optimization approaches",
                "Consider if faster execution affects quality"
            ])
            
        return recommendations
        
    def get_confidence_trend_recommendations(self, trend: str, conditions: Dict) -> List[str]:
        """Get recommendations for confidence trend patterns"""
        recommendations = []
        
        if trend == "decreasing":
            recommendations.extend([
                "Review model performance and accuracy",
                "Consider retraining or fine-tuning",
                "Investigate data quality issues"
            ])
            
            if conditions.get("below_threshold_count", 0) > 3:
                recommendations.append("Increase confidence thresholds or implement human review")
                
        else:  # increasing
            recommendations.extend([
                "Monitor for overconfidence issues",
                "Validate improved confidence with accuracy metrics"
            ])
            
        return recommendations
        
    def get_error_pattern_recommendations(self, error_type: str, conditions: Dict) -> List[str]:
        """Get recommendations for error patterns"""
        recommendations = []
        
        if error_type == "timeout":
            recommendations.extend([
                "Increase timeout configurations",
                "Implement request chunking",
                "Add retry logic with exponential backoff"
            ])
        elif error_type == "connection":
            recommendations.extend([
                "Implement connection pooling",
                "Add network retry logic",
                "Check network infrastructure"
            ])
        elif error_type == "rate_limit":
            recommendations.extend([
                "Implement rate limiting with backoff",
                "Distribute requests across time",
                "Consider upgrading API limits"
            ])
        elif error_type == "auth":
            recommendations.extend([
                "Check API key validity",
                "Implement token refresh logic",
                "Review authentication configuration"
            ])
        else:
            recommendations.extend([
                f"Investigate recurring {error_type} errors",
                "Implement specific error handling",
                "Add detailed logging for debugging"
            ])
            
        return recommendations
        
    async def extract_insights(self, agent_data: Dict[str, Any], patterns: List[Dict]) -> List[Dict]:
        """Extract actionable insights from patterns and data"""
        insights = []
        
        # System-level insights
        system_insight = self.extract_system_insights(agent_data, patterns)
        if system_insight:
            insights.append(system_insight)
            
        # Agent-specific insights
        for agent_name in agent_data["execution_histories"].keys():
            agent_patterns = [p for p in patterns if p.get("agent_name") == agent_name]
            if agent_patterns:
                agent_insight = self.extract_agent_insights(agent_name, agent_patterns, agent_data)
                if agent_insight:
                    insights.append(agent_insight)
                    
        # Performance insights
        perf_insight = self.extract_performance_insights(agent_data)
        if perf_insight:
            insights.append(perf_insight)
            
        return insights
        
    def extract_system_insights(self, agent_data: Dict[str, Any], patterns: List[Dict]) -> Optional[Dict]:
        """Extract system-level insights"""
        cross_agent_patterns = [p for p in patterns if p.get("pattern_type") == "cross_agent_failure"]
        if not cross_agent_patterns:
            return None
            
        insight = {
            "insight_type": "system_health",
            "title": "System-Wide Performance Issues",
            "description": "Multiple agents showing degraded performance",
            "impact_score": 0.8,
            "evidence": [p["description"] for p in cross_agent_patterns],
            "recommendations": [
                "Investigate shared infrastructure",
                "Review system resource allocation",
                "Check for configuration drift"
            ],
            "confidence": max(p.get("confidence", 0) for p in cross_agent_patterns),
            "timestamp": datetime.now()
        }
        
        return insight
        
    def extract_agent_insights(self, agent_name: str, patterns: List[Dict], agent_data: Dict[str, Any]) -> Optional[Dict]:
        """Extract insights for a specific agent"""
        if not patterns:
            return None
            
        # Prioritize patterns by confidence and impact
        high_confidence_patterns = [p for p in patterns if p.get("confidence", 0) > 0.7]
        if not high_confidence_patterns:
            return None
            
        # Create insight
        insight = {
            "insight_type": "agent_performance",
            "title": f"{agent_name} Performance Analysis",
            "description": f"Key patterns identified for {agent_name}",
            "impact_score": statistics.mean([p.get("confidence", 0) for p in high_confidence_patterns]),
            "evidence": [p["description"] for p in high_confidence_patterns],
            "recommendations": [],
            "confidence": max(p.get("confidence", 0) for p in high_confidence_patterns),
            "timestamp": datetime.now(),
            "agent_name": agent_name
        }
        
        # Aggregate recommendations
        all_recommendations = []
        for pattern in high_confidence_patterns:
            all_recommendations.extend(pattern.get("recommendations", []))
        insight["recommendations"] = list(set(all_recommendations))  # Remove duplicates
        
        return insight
        
    def extract_performance_insights(self, agent_data: Dict[str, Any]) -> Optional[Dict]:
        """Extract overall performance insights"""
        all_metrics = agent_data.get("performance_metrics", {})
        if not all_metrics:
            return None
            
        # Calculate system-wide metrics
        success_rates = [
            metrics.get("success_rate", 1.0) 
            for metrics in all_metrics.values()
            if "success_rate" in metrics
        ]
        
        if not success_rates:
            return None
            
        avg_success_rate = statistics.mean(success_rates)
        min_success_rate = min(success_rates)
        
        insight = {
            "insight_type": "performance_summary",
            "title": "System Performance Summary",
            "description": f"Average success rate: {avg_success_rate:.1%}, Minimum: {min_success_rate:.1%}",
            "impact_score": 1 - avg_success_rate,  # Higher impact if lower success rate
            "evidence": [
                f"{len(success_rates)} agents analyzed",
                f"Success rate range: {min_success_rate:.1%} - {max(success_rates):.1%}"
            ],
            "recommendations": self.get_performance_recommendations(avg_success_rate, min_success_rate),
            "confidence": 0.9,
            "timestamp": datetime.now()
        }
        
        return insight
        
    def get_performance_recommendations(self, avg_rate: float, min_rate: float) -> List[str]:
        """Get recommendations based on performance metrics"""
        recommendations = []
        
        if avg_rate < 0.8:
            recommendations.extend([
                "Investigate system-wide performance issues",
                "Review recent configuration changes",
                "Consider implementing circuit breakers"
            ])
            
        if min_rate < 0.5:
            recommendations.extend([
                "Identify and address worst-performing agents",
                "Implement agent-specific optimizations",
                "Consider disabling problematic agents temporarily"
            ])
            
        if avg_rate > 0.95:
            recommendations.extend([
                "System performing well - consider increasing complexity",
                "Document current successful approaches"
            ])
            
        return recommendations
        
    async def generate_recommendations(self, patterns: List[Dict], insights: List[Dict]) -> List[str]:
        """Generate prioritized recommendations"""
        all_recommendations = []
        
        # Collect all recommendations with weights
        recommendation_weights = {}
        
        for pattern in patterns:
            confidence = pattern.get("confidence", 0)
            for rec in pattern.get("recommendations", []):
                recommendation_weights[rec] = max(
                    recommendation_weights.get(rec, 0), confidence
                )
                
        for insight in insights:
            impact = insight.get("impact_score", 0)
            confidence = insight.get("confidence", 0)
            weight = (impact + confidence) / 2
            
            for rec in insight.get("recommendations", []):
                recommendation_weights[rec] = max(
                    recommendation_weights.get(rec, 0), weight
                )
                
        # Sort recommendations by weight
        sorted_recommendations = sorted(
            recommendation_weights.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Return top recommendations
        return [rec for rec, weight in sorted_recommendations[:10]]
        
    async def update_knowledge_base(self, patterns: List[Dict], insights: List[Dict]):
        """Update persistent knowledge base"""
        # Save patterns
        patterns_file = self.memory_dir / "discovered_patterns.json"
        existing_patterns = []
        if patterns_file.exists():
            with open(patterns_file, 'r') as f:
                existing_patterns = json.load(f)
                
        # Add new patterns with timestamp
        for pattern in patterns:
            pattern["discovered_at"] = datetime.now().isoformat()
            existing_patterns.append(pattern)
            
        # Keep only recent patterns (last 1000)
        existing_patterns = existing_patterns[-1000:]
        
        with open(patterns_file, 'w') as f:
            json.dump(existing_patterns, f, indent=2, default=str)
            
        # Save insights
        insights_file = self.memory_dir / "performance_insights.json"
        existing_insights = []
        if insights_file.exists():
            with open(insights_file, 'r') as f:
                existing_insights = json.load(f)
                
        # Add new insights
        for insight in insights:
            insight["generated_at"] = datetime.now().isoformat()
            existing_insights.append(insight)
            
        # Keep only recent insights
        existing_insights = existing_insights[-500:]
        
        with open(insights_file, 'w') as f:
            json.dump(existing_insights, f, indent=2, default=str)
            
        self.logger.info(f"Updated knowledge base: {len(patterns)} patterns, {len(insights)} insights")
        
    def calculate_learning_confidence(self, patterns: List[Dict], insights: List[Dict]) -> float:
        """Calculate confidence in learning results"""
        if not patterns and not insights:
            return 0.0
            
        # Base confidence on pattern quality and insight impact
        pattern_confidences = [p.get("confidence", 0) for p in patterns]
        insight_impacts = [i.get("impact_score", 0) for i in insights]
        
        if pattern_confidences:
            avg_pattern_confidence = statistics.mean(pattern_confidences)
        else:
            avg_pattern_confidence = 0
            
        if insight_impacts:
            avg_insight_impact = statistics.mean(insight_impacts)
        else:
            avg_insight_impact = 0
            
        # Weight patterns and insights equally
        overall_confidence = (avg_pattern_confidence + avg_insight_impact) / 2
        
        # Adjust based on data quantity
        data_quantity_factor = min(len(patterns) + len(insights), 10) / 10
        
        return overall_confidence * data_quantity_factor
        
    def create_learning_summary(self, patterns: List[Dict], insights: List[Dict]) -> Dict[str, Any]:
        """Create summary of learning results"""
        return {
            "total_patterns": len(patterns),
            "total_insights": len(insights),
            "pattern_types": list(set(p.get("pattern_type", "unknown") for p in patterns)),
            "insight_types": list(set(i.get("insight_type", "unknown") for i in insights)),
            "high_confidence_patterns": len([p for p in patterns if p.get("confidence", 0) > 0.8]),
            "high_impact_insights": len([i for i in insights if i.get("impact_score", 0) > 0.7]),
            "learning_timestamp": datetime.now().isoformat()
        }
        
    def load_learned_knowledge(self):
        """Load existing learned patterns and insights"""
        # Load patterns
        patterns_file = self.memory_dir / "discovered_patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    self.discovered_patterns = json.load(f)
                self.logger.info(f"Loaded {len(self.discovered_patterns)} learned patterns")
            except Exception as e:
                self.logger.warning(f"Failed to load learned patterns: {e}")
                
        # Load insights
        insights_file = self.memory_dir / "performance_insights.json"
        if insights_file.exists():
            try:
                with open(insights_file, 'r') as f:
                    self.performance_insights = json.load(f)
                self.logger.info(f"Loaded {len(self.performance_insights)} performance insights")
            except Exception as e:
                self.logger.warning(f"Failed to load performance insights: {e}")
                
    def get_relevant_patterns(self, context: Dict[str, Any]) -> List[Dict]:
        """Get patterns relevant to current context"""
        relevant_patterns = []
        
        for pattern in self.discovered_patterns:
            # Simple relevance scoring - could be more sophisticated
            relevance_score = 0
            
            # Agent-specific patterns
            if pattern.get("agent_name") == context.get("agent_name"):
                relevance_score += 0.5
                
            # Pattern type relevance
            if context.get("task_type") in pattern.get("description", ""):
                relevance_score += 0.3
                
            # Recency bonus
            pattern_date = datetime.fromisoformat(pattern.get("discovered_at", "2023-01-01"))
            days_old = (datetime.now() - pattern_date).days
            if days_old < 30:
                relevance_score += 0.2
                
            if relevance_score > 0.5:
                pattern["relevance_score"] = relevance_score
                relevant_patterns.append(pattern)
                
        # Sort by relevance
        relevant_patterns.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return relevant_patterns[:10]  # Return top 10 most relevant