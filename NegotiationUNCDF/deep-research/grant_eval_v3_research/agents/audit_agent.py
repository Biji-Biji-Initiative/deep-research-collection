#!/usr/bin/env python3
"""
Audit Agent for Agentic Deep Research System
Tracks everything for compliance, learning, and governance
"""

import json
import time
import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

from .base_agent import BaseAgent, AgentResult, AgentStatus, AgentContext

class ComplianceLevel(Enum):
    """Compliance checking levels"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    STRICT = "strict"

class AuditEventType(Enum):
    """Types of audit events"""
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    AGENT_EXECUTION = "agent_execution"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "configuration_change"
    ERROR_OCCURRENCE = "error_occurrence"
    SECURITY_EVENT = "security_event"
    PERFORMANCE_ALERT = "performance_alert"

@dataclass
class AuditEvent:
    """Individual audit event"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    agent_name: Optional[str]
    session_id: str
    event_data: Dict[str, Any]
    compliance_status: str
    risk_level: str
    metadata: Dict[str, Any]

class AuditAgent(BaseAgent):
    """Agent that provides comprehensive audit and compliance tracking"""
    
    def __init__(self, config: Dict[str, Any], context: AgentContext):
        super().__init__("audit_agent", config, context)
        
        # Audit configuration
        self.compliance_checks = config.get("compliance_checks", ["data_privacy", "api_usage", "cost_limits"])
        self.audit_level = ComplianceLevel(config.get("audit_level", "comprehensive"))
        self.retention_days = config.get("retention_days", 90)
        self.real_time_monitoring = config.get("real_time_monitoring", True)
        
        # Audit state
        self.audit_events = []
        self.compliance_violations = []
        self.audit_session_id = None
        
        # Initialize audit log
        self.initialize_audit_log()
        
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute audit analysis"""
        start_time = time.time()
        self.set_status(AgentStatus.RUNNING)
        
        try:
            self.logger.info("Starting audit analysis...")
            
            # Start audit session
            self.audit_session_id = await self.start_audit_session(input_data)
            
            # Collect audit data
            audit_data = await self.collect_audit_data(input_data)
            
            # Perform compliance checks
            compliance_results = await self.perform_compliance_checks(audit_data)
            
            # Analyze security implications
            security_analysis = await self.analyze_security(audit_data)
            
            # Generate audit report
            audit_report = await self.generate_audit_report(
                audit_data, compliance_results, security_analysis
            )
            
            # Save audit trail
            await self.save_audit_trail(audit_report)
            
            execution_time = time.time() - start_time
            
            result_data = {
                "audit_session_id": self.audit_session_id,
                "audit_report": audit_report,
                "compliance_results": compliance_results,
                "security_analysis": security_analysis,
                "events_audited": len(audit_data.get("events", [])),
                "violations_found": len(compliance_results.get("violations", [])),
                "audit_summary": self.create_audit_summary(audit_report)
            }
            
            result = self.create_result(
                status=AgentStatus.COMPLETED,
                result_data=result_data,
                execution_time=execution_time,
                confidence=self.calculate_audit_confidence(audit_report)
            )
            
            await self.end_audit_session("success")
            
            self.logger.info(f"Audit analysis completed: {len(audit_data.get('events', []))} events audited")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Audit analysis failed: {e}")
            
            await self.end_audit_session("error", str(e))
            
            return self.create_result(
                status=AgentStatus.FAILED,
                result_data={"error_details": str(e)},
                execution_time=execution_time,
                error=str(e)
            )
        finally:
            self.set_status(AgentStatus.IDLE)
            
    def initialize_audit_log(self):
        """Initialize audit logging system"""
        audit_log_dir = self.agent_dir / "audit_logs"
        audit_log_dir.mkdir(exist_ok=True)
        
        # Create audit event log file
        self.audit_log_file = audit_log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        # Log audit system initialization
        init_event = AuditEvent(
            event_id=self.generate_event_id(),
            event_type=AuditEventType.SYSTEM_START,
            timestamp=datetime.now(),
            agent_name=self.name,
            session_id=self.context.session_id,
            event_data={"audit_level": self.audit_level.value},
            compliance_status="compliant",
            risk_level="low",
            metadata={"initialized": True}
        )
        
        self.log_audit_event(init_event)
        
    def generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.now().isoformat()
        content = f"{timestamp}_{self.context.session_id}_{len(self.audit_events)}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
        
    def log_audit_event(self, event: AuditEvent):
        """Log audit event to file and memory"""
        self.audit_events.append(event)
        
        # Write to audit log file
        with open(self.audit_log_file, 'a') as f:
            event_dict = asdict(event)
            event_dict['timestamp'] = event.timestamp.isoformat()
            event_dict['event_type'] = event.event_type.value
            f.write(json.dumps(event_dict) + '\n')
            
    async def start_audit_session(self, input_data: Dict[str, Any]) -> str:
        """Start new audit session"""
        session_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session_event = AuditEvent(
            event_id=self.generate_event_id(),
            event_type=AuditEventType.SYSTEM_START,
            timestamp=datetime.now(),
            agent_name=self.name,
            session_id=session_id,
            event_data={
                "session_type": "audit_analysis",
                "input_data_keys": list(input_data.keys()),
                "compliance_checks": self.compliance_checks
            },
            compliance_status="pending",
            risk_level="medium",
            metadata={"session_start": True}
        )
        
        self.log_audit_event(session_event)
        
        self.logger.info(f"Started audit session: {session_id}")
        return session_id
        
    async def end_audit_session(self, status: str, error: str = None):
        """End audit session"""
        if not self.audit_session_id:
            return
            
        end_event = AuditEvent(
            event_id=self.generate_event_id(),
            event_type=AuditEventType.SYSTEM_STOP,
            timestamp=datetime.now(),
            agent_name=self.name,
            session_id=self.audit_session_id,
            event_data={
                "session_status": status,
                "error": error,
                "events_processed": len(self.audit_events),
                "violations_found": len(self.compliance_violations)
            },
            compliance_status="completed",
            risk_level="low" if status == "success" else "high",
            metadata={"session_end": True}
        )
        
        self.log_audit_event(end_event)
        
    async def collect_audit_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect comprehensive audit data"""
        audit_data = {
            "collection_timestamp": datetime.now().isoformat(),
            "events": [],
            "system_state": {},
            "agent_activities": {},
            "resource_usage": {},
            "security_context": {}
        }
        
        # Collect events from all agents
        audit_data["events"] = await self.collect_agent_events()
        
        # Collect system state information
        audit_data["system_state"] = await self.collect_system_state()
        
        # Collect agent activity logs
        audit_data["agent_activities"] = await self.collect_agent_activities()
        
        # Collect resource usage data
        audit_data["resource_usage"] = await self.collect_resource_usage()
        
        # Collect security context
        audit_data["security_context"] = await self.collect_security_context()
        
        self.logger.info(f"Collected audit data: {len(audit_data['events'])} events")
        return audit_data
        
    async def collect_agent_events(self) -> List[Dict[str, Any]]:
        """Collect events from all agent execution histories"""
        events = []
        
        agents_dir = self.context.research_root / "agents"
        if not agents_dir.exists():
            return events
            
        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir() or agent_dir.name == self.name:
                continue
                
            # Collect execution history
            history_file = agent_dir / "execution_history.jsonl"
            if history_file.exists():
                try:
                    with open(history_file, 'r') as f:
                        for line in f:
                            event_data = json.loads(line.strip())
                            event_data["source_agent"] = agent_dir.name
                            events.append(event_data)
                except Exception as e:
                    self.logger.warning(f"Failed to collect events from {agent_dir.name}: {e}")
                    
        return events
        
    async def collect_system_state(self) -> Dict[str, Any]:
        """Collect current system state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.context.session_id,
            "workspace_root": str(self.context.workspace_root),
            "research_root": str(self.context.research_root),
            "current_iteration": self.context.current_iteration,
            "available_agents": self.get_available_agents(),
            "system_resources": self.get_system_resources()
        }
        
    def get_available_agents(self) -> List[str]:
        """Get list of available agents"""
        agents_dir = self.context.research_root / "agents"
        if not agents_dir.exists():
            return []
            
        return [d.name for d in agents_dir.iterdir() if d.is_dir()]
        
    def get_system_resources(self) -> Dict[str, Any]:
        """Get system resource information"""
        try:
            import psutil
            return {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "disk_free_gb": psutil.disk_usage('/').free / (1024**3),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
        except ImportError:
            return {"error": "psutil not available"}
            
    async def collect_agent_activities(self) -> Dict[str, Any]:
        """Collect agent activity summaries"""
        activities = {}
        
        agents_dir = self.context.research_root / "agents"
        if not agents_dir.exists():
            return activities
            
        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
                
            agent_name = agent_dir.name
            activities[agent_name] = {
                "last_execution": self.get_last_execution_time(agent_dir),
                "execution_count": self.get_execution_count(agent_dir),
                "success_rate": self.get_success_rate(agent_dir),
                "average_duration": self.get_average_duration(agent_dir)
            }
            
        return activities
        
    def get_last_execution_time(self, agent_dir: Path) -> Optional[str]:
        """Get last execution time for agent"""
        history_file = agent_dir / "execution_history.jsonl"
        if not history_file.exists():
            return None
            
        try:
            with open(history_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1].strip())
                    return last_entry.get("timestamp")
        except Exception:
            pass
        return None
        
    def get_execution_count(self, agent_dir: Path) -> int:
        """Get total execution count for agent"""
        history_file = agent_dir / "execution_history.jsonl"
        if not history_file.exists():
            return 0
            
        try:
            with open(history_file, 'r') as f:
                return len(f.readlines())
        except Exception:
            return 0
            
    def get_success_rate(self, agent_dir: Path) -> float:
        """Get success rate for agent"""
        history_file = agent_dir / "execution_history.jsonl"
        if not history_file.exists():
            return 0.0
            
        try:
            successes = 0
            total = 0
            with open(history_file, 'r') as f:
                for line in f:
                    entry = json.loads(line.strip())
                    total += 1
                    if entry.get("status") == "completed":
                        successes += 1
            return successes / total if total > 0 else 0.0
        except Exception:
            return 0.0
            
    def get_average_duration(self, agent_dir: Path) -> float:
        """Get average execution duration for agent"""
        history_file = agent_dir / "execution_history.jsonl"
        if not history_file.exists():
            return 0.0
            
        try:
            durations = []
            with open(history_file, 'r') as f:
                for line in f:
                    entry = json.loads(line.strip())
                    if "execution_time" in entry:
                        durations.append(entry["execution_time"])
            return sum(durations) / len(durations) if durations else 0.0
        except Exception:
            return 0.0
            
    async def collect_resource_usage(self) -> Dict[str, Any]:
        """Collect resource usage data"""
        try:
            import psutil
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "network_io": dict(psutil.net_io_counters()._asdict()),
                "process_count": len(psutil.pids())
            }
        except ImportError:
            return {"error": "Resource monitoring not available"}
            
    async def collect_security_context(self) -> Dict[str, Any]:
        """Collect security-related context"""
        return {
            "api_key_configured": bool(os.environ.get("OPENAI_API_KEY")),
            "file_permissions": self.check_file_permissions(),
            "network_access": True,  # Simplified check
            "sensitive_data_paths": self.identify_sensitive_paths()
        }
        
    def check_file_permissions(self) -> Dict[str, Any]:
        """Check file permissions for key directories"""
        permissions = {}
        
        key_paths = [
            self.context.workspace_root,
            self.context.research_root,
            self.agent_dir
        ]
        
        for path in key_paths:
            try:
                permissions[str(path)] = {
                    "readable": os.access(path, os.R_OK),
                    "writable": os.access(path, os.W_OK),
                    "executable": os.access(path, os.X_OK)
                }
            except Exception as e:
                permissions[str(path)] = {"error": str(e)}
                
        return permissions
        
    def identify_sensitive_paths(self) -> List[str]:
        """Identify paths that may contain sensitive data"""
        sensitive_patterns = [
            "**/config/**/*.yaml",
            "**/config/**/*.json", 
            "**/logs/**/*.log",
            "**/memory/**/*.json",
            "**/results/**/*.json"
        ]
        
        sensitive_paths = []
        for pattern in sensitive_patterns:
            paths = list(self.context.research_root.glob(pattern))
            sensitive_paths.extend([str(p) for p in paths])
            
        return sensitive_paths[:20]  # Limit output
        
    async def perform_compliance_checks(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive compliance checks"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks_performed": [],
            "violations": [],
            "warnings": [],
            "compliance_score": 0.0
        }
        
        # Perform each configured compliance check
        for check_type in self.compliance_checks:
            check_result = await self.perform_single_compliance_check(check_type, audit_data)
            results["checks_performed"].append(check_result)
            
            if check_result.get("violations"):
                results["violations"].extend(check_result["violations"])
            if check_result.get("warnings"):
                results["warnings"].extend(check_result["warnings"])
                
        # Calculate overall compliance score
        total_checks = len(results["checks_performed"])
        passing_checks = len([c for c in results["checks_performed"] if c.get("status") == "pass"])
        results["compliance_score"] = passing_checks / total_checks if total_checks > 0 else 1.0
        
        self.logger.info(f"Compliance checks completed: {results['compliance_score']:.2%} passing")
        return results
        
    async def perform_single_compliance_check(self, check_type: str, 
                                            audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform single compliance check"""
        check_result = {
            "check_type": check_type,
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "violations": [],
            "warnings": [],
            "details": {}
        }
        
        try:
            if check_type == "data_privacy":
                check_result = await self.check_data_privacy(audit_data)
            elif check_type == "api_usage":
                check_result = await self.check_api_usage(audit_data)
            elif check_type == "cost_limits":
                check_result = await self.check_cost_limits(audit_data)
            elif check_type == "resource_usage":
                check_result = await self.check_resource_usage(audit_data)
            else:
                check_result["status"] = "skipped"
                check_result["details"] = {"reason": f"Unknown check type: {check_type}"}
                
        except Exception as e:
            check_result["status"] = "error"
            check_result["details"] = {"error": str(e)}
            
        return check_result
        
    async def check_data_privacy(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data privacy compliance"""
        violations = []
        warnings = []
        
        # Check for sensitive data in logs
        sensitive_paths = audit_data.get("security_context", {}).get("sensitive_data_paths", [])
        if len(sensitive_paths) > 50:
            violations.append("Excessive number of sensitive data files detected")
            
        # Check file permissions
        permissions = audit_data.get("security_context", {}).get("file_permissions", {})
        for path, perms in permissions.items():
            if perms.get("writable") and "config" in path:
                warnings.append(f"Configuration directory is writable: {path}")
                
        return {
            "check_type": "data_privacy",
            "status": "fail" if violations else "pass",
            "violations": violations,
            "warnings": warnings,
            "details": {
                "sensitive_files_count": len(sensitive_paths),
                "writable_config_paths": len([p for p, perms in permissions.items() 
                                            if perms.get("writable") and "config" in p])
            }
        }
        
    async def check_api_usage(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check API usage compliance"""
        violations = []
        warnings = []
        
        # Check for API key exposure
        if not audit_data.get("security_context", {}).get("api_key_configured"):
            warnings.append("No API key configured - some functionality may be limited")
            
        # Check execution frequency
        events = audit_data.get("events", [])
        recent_events = [e for e in events 
                        if datetime.fromisoformat(e.get("timestamp", "2023-01-01")) > 
                        datetime.now() - timedelta(hours=1)]
        
        if len(recent_events) > 100:
            violations.append("Excessive API usage detected in the last hour")
            
        return {
            "check_type": "api_usage",
            "status": "fail" if violations else "pass", 
            "violations": violations,
            "warnings": warnings,
            "details": {
                "recent_events_count": len(recent_events),
                "total_events": len(events)
            }
        }
        
    async def check_cost_limits(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check cost limits compliance"""
        violations = []
        warnings = []
        
        # Estimate costs based on execution data
        events = audit_data.get("events", [])
        estimated_cost = len(events) * 0.10  # Simplified cost estimation
        
        if estimated_cost > 50.0:
            violations.append(f"Estimated cost ${estimated_cost:.2f} exceeds $50 limit")
        elif estimated_cost > 25.0:
            warnings.append(f"Estimated cost ${estimated_cost:.2f} approaching limits")
            
        return {
            "check_type": "cost_limits",
            "status": "fail" if violations else "pass",
            "violations": violations,
            "warnings": warnings,
            "details": {
                "estimated_cost": estimated_cost,
                "events_analyzed": len(events)
            }
        }
        
    async def check_resource_usage(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check resource usage compliance"""
        violations = []
        warnings = []
        
        resource_data = audit_data.get("resource_usage", {})
        
        cpu_percent = resource_data.get("cpu_percent", 0)
        memory_percent = resource_data.get("memory_percent", 0)
        disk_percent = resource_data.get("disk_percent", 0)
        
        if cpu_percent > 90:
            violations.append(f"High CPU usage: {cpu_percent:.1f}%")
        elif cpu_percent > 70:
            warnings.append(f"Elevated CPU usage: {cpu_percent:.1f}%")
            
        if memory_percent > 90:
            violations.append(f"High memory usage: {memory_percent:.1f}%")
        elif memory_percent > 70:
            warnings.append(f"Elevated memory usage: {memory_percent:.1f}%")
            
        if disk_percent > 95:
            violations.append(f"Low disk space: {100-disk_percent:.1f}% free")
            
        return {
            "check_type": "resource_usage",
            "status": "fail" if violations else "pass",
            "violations": violations,
            "warnings": warnings,
            "details": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            }
        }
        
    async def analyze_security(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security implications"""
        security_analysis = {
            "timestamp": datetime.now().isoformat(),
            "risk_level": "low",
            "security_events": [],
            "recommendations": [],
            "threat_indicators": []
        }
        
        # Analyze events for security implications
        events = audit_data.get("events", [])
        
        # Check for repeated failures (potential attack indicator)
        failure_events = [e for e in events if e.get("status") != "completed"]
        if len(failure_events) > 10:
            security_analysis["threat_indicators"].append(
                f"High failure rate detected: {len(failure_events)} failures"
            )
            security_analysis["risk_level"] = "medium"
            
        # Check for unusual activity patterns
        recent_events = [e for e in events 
                        if datetime.fromisoformat(e.get("timestamp", "2023-01-01")) > 
                        datetime.now() - timedelta(minutes=30)]
        
        if len(recent_events) > 50:
            security_analysis["threat_indicators"].append("High activity burst detected")
            
        # Generate security recommendations
        if security_analysis["threat_indicators"]:
            security_analysis["recommendations"].extend([
                "Monitor system for unusual patterns",
                "Review authentication logs",
                "Consider implementing rate limiting"
            ])
        else:
            security_analysis["recommendations"].append("Security posture appears normal")
            
        return security_analysis
        
    async def generate_audit_report(self, audit_data: Dict[str, Any], 
                                  compliance_results: Dict[str, Any],
                                  security_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        return {
            "report_id": f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "audit_session_id": self.audit_session_id,
            "audit_period": {
                "start": (datetime.now() - timedelta(hours=24)).isoformat(),
                "end": datetime.now().isoformat()
            },
            "executive_summary": self.create_executive_summary(
                audit_data, compliance_results, security_analysis
            ),
            "compliance_summary": {
                "overall_score": compliance_results.get("compliance_score", 0.0),
                "checks_performed": len(compliance_results.get("checks_performed", [])),
                "violations_count": len(compliance_results.get("violations", [])),
                "warnings_count": len(compliance_results.get("warnings", []))
            },
            "security_summary": {
                "risk_level": security_analysis.get("risk_level", "unknown"),
                "threat_indicators": len(security_analysis.get("threat_indicators", [])),
                "recommendations_count": len(security_analysis.get("recommendations", []))
            },
            "system_health": self.assess_system_health(audit_data),
            "recommendations": self.generate_recommendations(
                compliance_results, security_analysis
            ),
            "detailed_findings": {
                "compliance_results": compliance_results,
                "security_analysis": security_analysis,
                "audit_data_summary": self.summarize_audit_data(audit_data)
            }
        }
        
    def create_executive_summary(self, audit_data: Dict[str, Any],
                               compliance_results: Dict[str, Any], 
                               security_analysis: Dict[str, Any]) -> str:
        """Create executive summary of audit findings"""
        compliance_score = compliance_results.get("compliance_score", 0.0)
        violations_count = len(compliance_results.get("violations", []))
        risk_level = security_analysis.get("risk_level", "unknown")
        
        if compliance_score >= 0.9 and violations_count == 0 and risk_level == "low":
            return "System operating within normal parameters with no significant compliance or security concerns."
        elif compliance_score >= 0.7 and violations_count <= 2:
            return f"System generally compliant with {violations_count} minor violations requiring attention."
        else:
            return f"System requires attention: {violations_count} compliance violations and {risk_level} security risk level."
            
    def assess_system_health(self, audit_data: Dict[str, Any]) -> Dict[str, str]:
        """Assess overall system health"""
        agent_activities = audit_data.get("agent_activities", {})
        
        # Calculate average success rate across agents
        success_rates = [activity.get("success_rate", 0.0) for activity in agent_activities.values()]
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 1.0
        
        # Assess health
        if avg_success_rate >= 0.9:
            health_status = "excellent"
        elif avg_success_rate >= 0.8:
            health_status = "good"
        elif avg_success_rate >= 0.6:
            health_status = "fair"
        else:
            health_status = "poor"
            
        return {
            "overall_health": health_status,
            "average_success_rate": f"{avg_success_rate:.2%}",
            "active_agents": str(len(agent_activities)),
            "assessment_timestamp": datetime.now().isoformat()
        }
        
    def generate_recommendations(self, compliance_results: Dict[str, Any],
                               security_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Compliance-based recommendations
        if compliance_results.get("violations"):
            recommendations.append("Address compliance violations immediately")
            
        if compliance_results.get("warnings"):
            recommendations.append("Review and resolve compliance warnings")
            
        # Security-based recommendations
        security_recs = security_analysis.get("recommendations", [])
        recommendations.extend(security_recs)
        
        # General recommendations
        recommendations.extend([
            "Regular audit monitoring should continue",
            "Review and update compliance policies quarterly"
        ])
        
        return list(set(recommendations))  # Remove duplicates
        
    def summarize_audit_data(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize audit data for report"""
        return {
            "events_analyzed": len(audit_data.get("events", [])),
            "agents_monitored": len(audit_data.get("agent_activities", {})),
            "data_collection_timestamp": audit_data.get("collection_timestamp"),
            "system_resources_monitored": bool(audit_data.get("resource_usage")),
            "security_context_analyzed": bool(audit_data.get("security_context"))
        }
        
    async def save_audit_trail(self, audit_report: Dict[str, Any]):
        """Save comprehensive audit trail"""
        # Save main audit report
        report_file = self.results_dir / f"audit_report_{audit_report['report_id']}.json"
        with open(report_file, 'w') as f:
            json.dump(audit_report, f, indent=2, default=str)
            
        # Update audit trail index
        trail_index_file = self.memory_dir / "audit_trail_index.json"
        trail_index = []
        if trail_index_file.exists():
            with open(trail_index_file, 'r') as f:
                trail_index = json.load(f)
                
        trail_index.append({
            "report_id": audit_report["report_id"],
            "generated_at": audit_report["generated_at"],
            "compliance_score": audit_report["compliance_summary"]["overall_score"],
            "risk_level": audit_report["security_summary"]["risk_level"],
            "violations_count": audit_report["compliance_summary"]["violations_count"]
        })
        
        # Keep only recent entries
        trail_index = trail_index[-100:]
        
        with open(trail_index_file, 'w') as f:
            json.dump(trail_index, f, indent=2, default=str)
            
        self.logger.info(f"Saved audit trail: {report_file}")
        
    def calculate_audit_confidence(self, audit_report: Dict[str, Any]) -> float:
        """Calculate confidence in audit results"""
        base_confidence = 0.85
        
        # Adjust based on data completeness
        data_summary = audit_report["detailed_findings"]["audit_data_summary"]
        events_count = data_summary.get("events_analyzed", 0)
        agents_count = data_summary.get("agents_monitored", 0)
        
        completeness_factor = min((events_count / 10) + (agents_count / 5), 1.0) * 0.1
        
        # Adjust based on compliance score
        compliance_score = audit_report["compliance_summary"]["overall_score"]
        compliance_factor = compliance_score * 0.05
        
        return min(base_confidence + completeness_factor + compliance_factor, 1.0)
        
    def create_audit_summary(self, audit_report: Dict[str, Any]) -> Dict[str, Any]:
        """Create concise audit summary"""
        return {
            "audit_timestamp": audit_report["generated_at"],
            "compliance_status": "passing" if audit_report["compliance_summary"]["overall_score"] >= 0.8 else "needs_attention",
            "security_status": audit_report["security_summary"]["risk_level"],
            "system_health": audit_report["system_health"]["overall_health"],
            "action_required": len(audit_report["detailed_findings"]["compliance_results"].get("violations", [])) > 0,
            "next_audit_recommended": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
    def get_audit_metrics(self) -> Dict[str, Any]:
        """Get audit agent metrics"""
        return {
            "events_logged": len(self.audit_events),
            "violations_detected": len(self.compliance_violations),
            "audit_level": self.audit_level.value,
            "retention_days": self.retention_days,
            "last_audit_session": self.audit_session_id,
            "compliance_checks_enabled": self.compliance_checks
        }