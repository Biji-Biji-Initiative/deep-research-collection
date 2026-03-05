#!/usr/bin/env python3
"""
Review Agent for Agentic Deep Research System
Evaluates results and decides on iterations for continuous improvement
"""

import json
import time
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

from .base_agent import BaseAgent, AgentResult, AgentStatus, AgentContext

class QualityMetric(Enum):
    """Quality metrics for evaluation"""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    INSIGHT_DEPTH = "insight_depth"
    ACTIONABILITY = "actionability"

class ReviewCriteria(Enum):
    """Review criteria levels"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    COMPREHENSIVE = "comprehensive"

class IterationDecision(Enum):
    """Iteration decision types"""
    ACCEPT = "accept"
    MINOR_REVISION = "minor_revision"
    MAJOR_REVISION = "major_revision"
    REJECT = "reject"

@dataclass
class QualityAssessment:
    """Quality assessment result"""
    metric: QualityMetric
    score: float
    explanation: str
    evidence: List[str]
    improvement_suggestions: List[str]

@dataclass
class ReviewDecision:
    """Review decision with rationale"""
    decision: IterationDecision
    overall_score: float
    quality_assessments: List[QualityAssessment]
    rationale: str
    required_improvements: List[str]
    estimated_effort: str
    confidence: float

class ReviewAgent(BaseAgent):
    """Agent that evaluates results and decides on iterations"""
    
    def __init__(self, config: Dict[str, Any], context: AgentContext):
        super().__init__("review_agent", config, context)
        
        # Review configuration
        self.quality_metrics = [QualityMetric(qm) for qm in config.get("quality_metrics", 
                               ["completeness", "accuracy", "relevance", "insight_depth"])]
        self.review_criteria = ReviewCriteria(config.get("review_criteria", "standard"))
        self.iteration_threshold = config.get("iteration_threshold", 0.8)
        self.max_iterations = config.get("max_iterations", 3)
        
        # Review state
        self.review_history = []
        self.iteration_count = 0
        self.quality_standards = self.initialize_quality_standards()
        
    def initialize_quality_standards(self) -> Dict[str, float]:
        """Initialize quality standards based on review criteria"""
        if self.review_criteria == ReviewCriteria.BASIC:
            return {
                QualityMetric.COMPLETENESS.value: 0.6,
                QualityMetric.ACCURACY.value: 0.7,
                QualityMetric.RELEVANCE.value: 0.6,
                QualityMetric.INSIGHT_DEPTH.value: 0.5,
                QualityMetric.ACTIONABILITY.value: 0.5
            }
        elif self.review_criteria == ReviewCriteria.STANDARD:
            return {
                QualityMetric.COMPLETENESS.value: 0.75,
                QualityMetric.ACCURACY.value: 0.8,
                QualityMetric.RELEVANCE.value: 0.75,
                QualityMetric.INSIGHT_DEPTH.value: 0.7,
                QualityMetric.ACTIONABILITY.value: 0.7
            }
        elif self.review_criteria == ReviewCriteria.STRICT:
            return {
                QualityMetric.COMPLETENESS.value: 0.85,
                QualityMetric.ACCURACY.value: 0.9,
                QualityMetric.RELEVANCE.value: 0.85,
                QualityMetric.INSIGHT_DEPTH.value: 0.8,
                QualityMetric.ACTIONABILITY.value: 0.8
            }
        else:  # COMPREHENSIVE
            return {
                QualityMetric.COMPLETENESS.value: 0.9,
                QualityMetric.ACCURACY.value: 0.95,
                QualityMetric.RELEVANCE.value: 0.9,
                QualityMetric.INSIGHT_DEPTH.value: 0.85,
                QualityMetric.ACTIONABILITY.value: 0.85
            }
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute review and evaluation process"""
        start_time = time.time()
        self.set_status(AgentStatus.RUNNING)
        
        try:
            self.logger.info("Starting review and evaluation...")
            
            # Extract results to review
            results_to_review = await self.extract_results(input_data)
            
            # Perform quality assessment
            quality_assessments = await self.assess_quality(results_to_review)
            
            # Make iteration decision
            review_decision = await self.make_iteration_decision(
                quality_assessments, input_data
            )
            
            # Generate improvement recommendations
            recommendations = await self.generate_improvement_recommendations(
                review_decision, results_to_review
            )
            
            # Update review history
            await self.update_review_history(review_decision, quality_assessments)
            
            # Determine next actions
            next_actions = await self.determine_next_actions(review_decision, input_data)
            
            execution_time = time.time() - start_time
            
            result_data = {
                "review_decision": asdict(review_decision),
                "quality_assessments": [asdict(qa) for qa in quality_assessments],
                "improvement_recommendations": recommendations,
                "next_actions": next_actions,
                "iteration_count": self.iteration_count,
                "review_summary": self.create_review_summary(review_decision, quality_assessments)
            }
            
            result = self.create_result(
                status=AgentStatus.COMPLETED,
                result_data=result_data,
                execution_time=execution_time,
                confidence=review_decision.confidence
            )
            
            self.logger.info(f"Review completed: {review_decision.decision.value}")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Review failed: {e}")
            
            return self.create_result(
                status=AgentStatus.FAILED,
                result_data={"error_details": str(e)},
                execution_time=execution_time,
                error=str(e)
            )
        finally:
            self.set_status(AgentStatus.IDLE)
            
    async def extract_results(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract results from various sources for review"""
        results = {
            "execution_results": input_data.get("execution_results", {}),
            "research_outputs": input_data.get("research_outputs", {}),
            "agent_outputs": {},
            "system_metrics": {}
        }
        
        # Collect outputs from all agents
        results["agent_outputs"] = await self.collect_agent_outputs()
        
        # Collect system metrics
        results["system_metrics"] = await self.collect_system_metrics()
        
        return results
        
    async def collect_agent_outputs(self) -> Dict[str, Any]:
        """Collect outputs from all agents"""
        agent_outputs = {}
        
        agents_dir = self.context.research_root / "agents"
        if not agents_dir.exists():
            return agent_outputs
            
        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir() or agent_dir.name == self.name:
                continue
                
            agent_name = agent_dir.name
            results_dir = agent_dir / "results"
            
            if results_dir.exists():
                # Get most recent result
                result_files = list(results_dir.glob("*.json"))
                if result_files:
                    latest_result = max(result_files, key=lambda f: f.stat().st_mtime)
                    try:
                        with open(latest_result, 'r') as f:
                            agent_outputs[agent_name] = json.load(f)
                    except Exception as e:
                        self.logger.warning(f"Failed to load result for {agent_name}: {e}")
                        
        return agent_outputs
        
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-wide metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "performance_metrics": {},
            "resource_metrics": {},
            "error_metrics": {}
        }
        
        # Collect performance data
        try:
            # This would normally collect from monitoring systems
            metrics["performance_metrics"] = {
                "average_response_time": 2.3,
                "success_rate": 0.87,
                "throughput": 15.2
            }
        except Exception as e:
            self.logger.warning(f"Failed to collect performance metrics: {e}")
            
        return metrics
        
    async def assess_quality(self, results: Dict[str, Any]) -> List[QualityAssessment]:
        """Assess quality across all metrics"""
        assessments = []
        
        for metric in self.quality_metrics:
            assessment = await self.assess_single_metric(metric, results)
            assessments.append(assessment)
            
        return assessments
        
    async def assess_single_metric(self, metric: QualityMetric, 
                                 results: Dict[str, Any]) -> QualityAssessment:
        """Assess a single quality metric"""
        if metric == QualityMetric.COMPLETENESS:
            return await self.assess_completeness(results)
        elif metric == QualityMetric.ACCURACY:
            return await self.assess_accuracy(results)
        elif metric == QualityMetric.RELEVANCE:
            return await self.assess_relevance(results)
        elif metric == QualityMetric.INSIGHT_DEPTH:
            return await self.assess_insight_depth(results)
        elif metric == QualityMetric.ACTIONABILITY:
            return await self.assess_actionability(results)
        else:
            return QualityAssessment(
                metric=metric,
                score=0.5,
                explanation="Unknown metric",
                evidence=[],
                improvement_suggestions=[]
            )
            
    async def assess_completeness(self, results: Dict[str, Any]) -> QualityAssessment:
        """Assess completeness of results"""
        evidence = []
        score = 0.0
        
        # Check execution results
        execution_results = results.get("execution_results", {})
        if execution_results.get("success"):
            score += 0.3
            evidence.append("Execution completed successfully")
        else:
            evidence.append("Execution did not complete successfully")
            
        # Check agent outputs
        agent_outputs = results.get("agent_outputs", {})
        completed_agents = len([output for output in agent_outputs.values() 
                              if output.get("status") == "completed"])
        total_agents = len(agent_outputs)
        
        if total_agents > 0:
            agent_completion_rate = completed_agents / total_agents
            score += agent_completion_rate * 0.4
            evidence.append(f"{completed_agents}/{total_agents} agents completed successfully")
        
        # Check research outputs
        research_outputs = results.get("research_outputs", {})
        if research_outputs:
            score += 0.3
            evidence.append("Research outputs available")
        else:
            evidence.append("No research outputs found")
            
        improvement_suggestions = []
        if score < 0.7:
            improvement_suggestions.extend([
                "Ensure all agents complete successfully",
                "Verify research execution produces outputs",
                "Check for missing components in the pipeline"
            ])
            
        return QualityAssessment(
            metric=QualityMetric.COMPLETENESS,
            score=min(score, 1.0),
            explanation=f"Completeness assessed based on execution success and output availability",
            evidence=evidence,
            improvement_suggestions=improvement_suggestions
        )
        
    async def assess_accuracy(self, results: Dict[str, Any]) -> QualityAssessment:
        """Assess accuracy of results"""
        evidence = []
        score = 0.7  # Default score (would be more sophisticated in practice)
        
        # Check for error indicators
        execution_results = results.get("execution_results", {})
        if execution_results.get("error"):
            score -= 0.2
            evidence.append(f"Execution error detected: {execution_results.get('error')}")
            
        # Check agent confidence scores
        agent_outputs = results.get("agent_outputs", {})
        confidence_scores = []
        
        for agent_name, output in agent_outputs.items():
            if isinstance(output, dict) and "confidence" in output:
                confidence_scores.append(output["confidence"])
                evidence.append(f"{agent_name} confidence: {output['confidence']:.2f}")
                
        if confidence_scores:
            avg_confidence = statistics.mean(confidence_scores)
            score = (score + avg_confidence) / 2
            
        improvement_suggestions = []
        if score < 0.8:
            improvement_suggestions.extend([
                "Review execution for errors and inconsistencies",
                "Validate outputs against expected results",
                "Improve agent confidence through better training"
            ])
            
        return QualityAssessment(
            metric=QualityMetric.ACCURACY,
            score=score,
            explanation="Accuracy assessed based on error rates and confidence scores",
            evidence=evidence,
            improvement_suggestions=improvement_suggestions
        )
        
    async def assess_relevance(self, results: Dict[str, Any]) -> QualityAssessment:
        """Assess relevance of results"""
        evidence = []
        score = 0.75  # Default relevance score
        
        # Check if results align with input requirements
        execution_results = results.get("execution_results", {})
        if "research_results" in execution_results:
            score += 0.15
            evidence.append("Research results present and aligned with requirements")
            
        # Check agent output relevance
        agent_outputs = results.get("agent_outputs", {})
        relevant_outputs = 0
        total_outputs = len(agent_outputs)
        
        for agent_name, output in agent_outputs.items():
            if isinstance(output, dict) and output.get("result_data"):
                relevant_outputs += 1
                evidence.append(f"{agent_name} produced relevant output")
                
        if total_outputs > 0:
            relevance_rate = relevant_outputs / total_outputs
            score = (score + relevance_rate) / 2
            
        improvement_suggestions = []
        if score < 0.8:
            improvement_suggestions.extend([
                "Ensure outputs directly address the research questions",
                "Review agent configurations for task alignment",
                "Validate result relevance against original objectives"
            ])
            
        return QualityAssessment(
            metric=QualityMetric.RELEVANCE,
            score=score,
            explanation="Relevance assessed based on alignment with requirements",
            evidence=evidence,
            improvement_suggestions=improvement_suggestions
        )
        
    async def assess_insight_depth(self, results: Dict[str, Any]) -> QualityAssessment:
        """Assess depth of insights generated"""
        evidence = []
        score = 0.6  # Conservative default
        
        # Check for presence of analytical outputs
        execution_results = results.get("execution_results", {})
        research_outputs = results.get("research_outputs", {})
        
        if research_outputs and isinstance(research_outputs, dict):
            if "analysis" in str(research_outputs).lower():
                score += 0.2
                evidence.append("Analysis content detected in research outputs")
                
            if "insight" in str(research_outputs).lower():
                score += 0.15
                evidence.append("Insights explicitly mentioned in outputs")
                
        # Check agent outputs for depth indicators
        agent_outputs = results.get("agent_outputs", {})
        depth_indicators = ["pattern", "correlation", "trend", "implication", "recommendation"]
        
        depth_found = 0
        for agent_name, output in agent_outputs.items():
            output_text = str(output).lower()
            for indicator in depth_indicators:
                if indicator in output_text:
                    depth_found += 1
                    break
                    
        if len(agent_outputs) > 0:
            depth_ratio = depth_found / len(agent_outputs)
            score = (score + depth_ratio * 0.2) 
            evidence.append(f"Depth indicators found in {depth_found}/{len(agent_outputs)} agent outputs")
            
        improvement_suggestions = []
        if score < 0.8:
            improvement_suggestions.extend([
                "Enhance analytical depth in research prompts",
                "Request explicit pattern identification and analysis",
                "Include more sophisticated reasoning in agent instructions"
            ])
            
        return QualityAssessment(
            metric=QualityMetric.INSIGHT_DEPTH,
            score=min(score, 1.0),
            explanation="Insight depth assessed based on analytical content indicators",
            evidence=evidence,
            improvement_suggestions=improvement_suggestions
        )
        
    async def assess_actionability(self, results: Dict[str, Any]) -> QualityAssessment:
        """Assess actionability of results"""
        evidence = []
        score = 0.5  # Default score
        
        # Look for actionable elements
        all_text = str(results).lower()
        actionable_indicators = ["recommend", "suggest", "should", "action", "next step", "implement"]
        
        found_indicators = [indicator for indicator in actionable_indicators if indicator in all_text]
        if found_indicators:
            score += min(len(found_indicators) * 0.1, 0.4)
            evidence.append(f"Actionable language found: {', '.join(found_indicators)}")
            
        # Check for specific recommendations
        agent_outputs = results.get("agent_outputs", {})
        recommendation_count = 0
        
        for agent_name, output in agent_outputs.items():
            if isinstance(output, dict) and "recommendation" in str(output).lower():
                recommendation_count += 1
                evidence.append(f"{agent_name} provided recommendations")
                
        if agent_outputs:
            recommendation_ratio = recommendation_count / len(agent_outputs)
            score = (score + recommendation_ratio * 0.3)
            
        improvement_suggestions = []
        if score < 0.7:
            improvement_suggestions.extend([
                "Include specific action items in research outputs",
                "Ensure recommendations are concrete and implementable",
                "Structure outputs to highlight next steps"
            ])
            
        return QualityAssessment(
            metric=QualityMetric.ACTIONABILITY,
            score=min(score, 1.0),
            explanation="Actionability assessed based on recommendations and next steps",
            evidence=evidence,
            improvement_suggestions=improvement_suggestions
        )
        
    async def make_iteration_decision(self, assessments: List[QualityAssessment], 
                                    input_data: Dict[str, Any]) -> ReviewDecision:
        """Make decision on whether iteration is needed"""
        # Calculate overall score
        scores = [assessment.score for assessment in assessments]
        overall_score = statistics.mean(scores) if scores else 0.0
        
        # Check against quality standards
        below_standard_count = 0
        required_improvements = []
        
        for assessment in assessments:
            standard = self.quality_standards.get(assessment.metric.value, 0.7)
            if assessment.score < standard:
                below_standard_count += 1
                required_improvements.extend(assessment.improvement_suggestions)
                
        # Make decision based on score and standards
        if overall_score >= self.iteration_threshold and below_standard_count == 0:
            decision = IterationDecision.ACCEPT
            rationale = f"Results meet quality standards (score: {overall_score:.2f})"
            estimated_effort = "none"
        elif overall_score >= self.iteration_threshold * 0.9 and below_standard_count <= 1:
            decision = IterationDecision.MINOR_REVISION
            rationale = f"Results mostly meet standards but need minor improvements (score: {overall_score:.2f})"
            estimated_effort = "low"
        elif overall_score >= self.iteration_threshold * 0.7 and below_standard_count <= 2:
            decision = IterationDecision.MAJOR_REVISION
            rationale = f"Results need significant improvement (score: {overall_score:.2f})"
            estimated_effort = "medium"
        else:
            decision = IterationDecision.REJECT
            rationale = f"Results do not meet minimum standards (score: {overall_score:.2f})"
            estimated_effort = "high"
            
        # Check iteration limits
        if self.iteration_count >= self.max_iterations and decision != IterationDecision.ACCEPT:
            decision = IterationDecision.ACCEPT
            rationale += f" (Max iterations {self.max_iterations} reached - accepting current results)"
            
        confidence = self.calculate_decision_confidence(assessments, overall_score)
        
        return ReviewDecision(
            decision=decision,
            overall_score=overall_score,
            quality_assessments=assessments,
            rationale=rationale,
            required_improvements=list(set(required_improvements)),  # Remove duplicates
            estimated_effort=estimated_effort,
            confidence=confidence
        )
        
    def calculate_decision_confidence(self, assessments: List[QualityAssessment], 
                                    overall_score: float) -> float:
        """Calculate confidence in the review decision"""
        # Base confidence on score consistency
        scores = [assessment.score for assessment in assessments]
        if len(scores) > 1:
            score_std = statistics.stdev(scores)
            consistency_factor = max(0, 1 - score_std)  # Higher consistency = higher confidence
        else:
            consistency_factor = 0.8
            
        # Adjust for extreme scores
        if overall_score > 0.9 or overall_score < 0.3:
            extremity_factor = 0.9  # High confidence for clear cases
        else:
            extremity_factor = 0.7  # Lower confidence for borderline cases
            
        # Combine factors
        confidence = (consistency_factor * 0.6) + (extremity_factor * 0.4)
        
        return min(max(confidence, 0.1), 1.0)
        
    async def generate_improvement_recommendations(self, decision: ReviewDecision, 
                                                 results: Dict[str, Any]) -> List[str]:
        """Generate specific improvement recommendations"""
        recommendations = []
        
        # Include improvement suggestions from quality assessments
        for assessment in decision.quality_assessments:
            recommendations.extend(assessment.improvement_suggestions)
            
        # Add decision-specific recommendations
        if decision.decision == IterationDecision.MINOR_REVISION:
            recommendations.append("Focus on addressing the lowest-scoring quality metrics")
        elif decision.decision == IterationDecision.MAJOR_REVISION:
            recommendations.extend([
                "Consider revising the overall approach",
                "Review and update agent configurations",
                "Increase analytical depth and specificity"
            ])
        elif decision.decision == IterationDecision.REJECT:
            recommendations.extend([
                "Fundamental revision required",
                "Review original requirements and objectives",
                "Consider alternative approaches or methodologies"
            ])
            
        # Remove duplicates and limit to top recommendations
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:10]
        
    async def update_review_history(self, decision: ReviewDecision, 
                                  assessments: List[QualityAssessment]):
        """Update review history for learning"""
        review_record = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.context.session_id,
            "iteration_count": self.iteration_count,
            "decision": decision.decision.value,
            "overall_score": decision.overall_score,
            "confidence": decision.confidence,
            "quality_scores": {
                assessment.metric.value: assessment.score 
                for assessment in assessments
            },
            "rationale": decision.rationale
        }
        
        self.review_history.append(review_record)
        
        # Save to file
        history_file = self.memory_dir / "review_history.jsonl"
        with open(history_file, 'a') as f:
            f.write(json.dumps(review_record) + '\n')
            
        # Increment iteration count if revision needed
        if decision.decision in [IterationDecision.MINOR_REVISION, IterationDecision.MAJOR_REVISION]:
            self.iteration_count += 1
            
    async def determine_next_actions(self, decision: ReviewDecision, 
                                   input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine next actions based on review decision"""
        next_actions = {
            "primary_action": decision.decision.value,
            "priority": "high" if decision.decision != IterationDecision.ACCEPT else "low",
            "estimated_effort": decision.estimated_effort,
            "specific_actions": []
        }
        
        if decision.decision == IterationDecision.ACCEPT:
            next_actions["specific_actions"] = [
                "Finalize results",
                "Generate final report",
                "Archive session data"
            ]
        elif decision.decision == IterationDecision.MINOR_REVISION:
            next_actions["specific_actions"] = [
                "Address specific quality gaps",
                "Re-run affected components",
                "Validate improvements"
            ]
        elif decision.decision == IterationDecision.MAJOR_REVISION:
            next_actions["specific_actions"] = [
                "Revise approach and strategy",
                "Update agent configurations",
                "Re-execute full pipeline",
                "Comprehensive re-evaluation"
            ]
        else:  # REJECT
            next_actions["specific_actions"] = [
                "Fundamental redesign required",
                "Review original objectives",
                "Consider alternative methodologies",
                "Escalate for expert review"
            ]
            
        return next_actions
        
    def create_review_summary(self, decision: ReviewDecision, 
                            assessments: List[QualityAssessment]) -> Dict[str, Any]:
        """Create concise review summary"""
        return {
            "review_timestamp": datetime.now().isoformat(),
            "decision": decision.decision.value,
            "overall_score": round(decision.overall_score, 3),
            "confidence": round(decision.confidence, 3),
            "iteration_count": self.iteration_count,
            "quality_breakdown": {
                assessment.metric.value: round(assessment.score, 3)
                for assessment in assessments
            },
            "meets_standards": decision.decision == IterationDecision.ACCEPT,
            "improvement_areas": len(decision.required_improvements),
            "estimated_effort": decision.estimated_effort,
            "next_review_needed": decision.decision != IterationDecision.ACCEPT
        }
        
    def get_review_metrics(self) -> Dict[str, Any]:
        """Get review agent metrics"""
        if not self.review_history:
            return {"no_reviews": True}
            
        recent_reviews = self.review_history[-10:]
        
        # Calculate metrics
        avg_score = statistics.mean([r["overall_score"] for r in recent_reviews])
        accept_rate = len([r for r in recent_reviews if r["decision"] == "accept"]) / len(recent_reviews)
        avg_confidence = statistics.mean([r["confidence"] for r in recent_reviews])
        
        return {
            "total_reviews": len(self.review_history),
            "current_iteration": self.iteration_count,
            "average_score": round(avg_score, 3),
            "acceptance_rate": round(accept_rate, 3),
            "average_confidence": round(avg_confidence, 3),
            "review_criteria": self.review_criteria.value,
            "quality_standards": self.quality_standards
        }