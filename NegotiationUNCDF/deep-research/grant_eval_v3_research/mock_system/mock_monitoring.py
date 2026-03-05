#!/usr/bin/env python3
"""
Mock Monitoring and Metrics System for Testing Deep Research Architecture
Simulates comprehensive monitoring, alerting, and performance tracking
"""

import json
import time
import random
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import uuid


class MockMetricType(Enum):
    """Types of metrics tracked"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class MockAlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MockMetric:
    """Mock metric data point"""
    name: str
    type: MockMetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MockAlert:
    """Mock alert notification"""
    id: str
    severity: MockAlertSeverity
    title: str
    message: str
    timestamp: datetime
    metric_name: Optional[str] = None
    threshold: Optional[float] = None
    actual_value: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class MockAuditEntry:
    """Mock audit log entry"""
    id: str
    session_id: str
    timestamp: datetime
    event_type: str
    event_data: Dict[str, Any]
    user: Optional[str] = None
    result: Optional[str] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None


class MockMetricsCollector:
    """Mock metrics collection system"""
    
    def __init__(self, buffer_size: int = 1000, skip_background: bool = False):
        self.metrics_buffer = deque(maxlen=buffer_size)
        self.aggregated_metrics = defaultdict(list)
        self.metric_summaries = defaultdict(dict)
        self.lock = threading.Lock()
        self.logger = logging.getLogger(f"{__name__}.MockMetricsCollector")
        
        # Start background aggregation (conditionally)
        if not skip_background:
            self.aggregation_thread = threading.Thread(target=self._background_aggregation, daemon=True)
            self.aggregation_thread.start()
        else:
            self.aggregation_thread = None
    
    def record_metric(self, metric: MockMetric):
        """Record a single metric"""
        with self.lock:
            self.metrics_buffer.append(metric)
            self.aggregated_metrics[metric.name].append(metric)
            self._update_summary(metric)
    
    def record_counter(self, name: str, value: float = 1, tags: Dict[str, str] = None):
        """Record a counter metric"""
        metric = MockMetric(
            name=name,
            type=MockMetricType.COUNTER,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        self.record_metric(metric)
    
    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a gauge metric"""
        metric = MockMetric(
            name=name,
            type=MockMetricType.GAUGE,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        self.record_metric(metric)
    
    def record_timer(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Record a timer metric"""
        metric = MockMetric(
            name=name,
            type=MockMetricType.TIMER,
            value=duration,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        self.record_metric(metric)
    
    def _update_summary(self, metric: MockMetric):
        """Update metric summary statistics"""
        name = metric.name
        if name not in self.metric_summaries:
            self.metric_summaries[name] = {
                "count": 0,
                "sum": 0,
                "min": float('inf'),
                "max": float('-inf'),
                "last_value": None,
                "last_updated": None
            }
        
        summary = self.metric_summaries[name]
        summary["count"] += 1
        summary["sum"] += metric.value
        summary["min"] = min(summary["min"], metric.value)
        summary["max"] = max(summary["max"], metric.value)
        summary["last_value"] = metric.value
        summary["last_updated"] = metric.timestamp
    
    def _background_aggregation(self):
        """Background thread for metric aggregation"""
        while True:
            try:
                time.sleep(30)  # Aggregate every 30 seconds
                self._perform_aggregation()
            except Exception as e:
                self.logger.error(f"Aggregation error: {e}")
    
    def _perform_aggregation(self):
        """Perform periodic metric aggregation"""
        with self.lock:
            # Clean old metrics (keep last hour)
            cutoff_time = datetime.now() - timedelta(hours=1)
            for metric_name in list(self.aggregated_metrics.keys()):
                self.aggregated_metrics[metric_name] = [
                    m for m in self.aggregated_metrics[metric_name] 
                    if m.timestamp > cutoff_time
                ]
    
    def get_metric_summary(self, metric_name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        with self.lock:
            if metric_name in self.metric_summaries:
                summary = self.metric_summaries[metric_name].copy()
                if summary["count"] > 0:
                    summary["average"] = summary["sum"] / summary["count"]
                return summary
            return {}
    
    def get_all_metrics(self) -> List[Dict[str, Any]]:
        """Get all current metrics"""
        with self.lock:
            return [asdict(metric) for metric in self.metrics_buffer]
    
    def get_metric_names(self) -> List[str]:
        """Get list of all metric names"""
        with self.lock:
            return list(self.metric_summaries.keys())


class MockAlertManager:
    """Mock alerting system"""
    
    def __init__(self, metrics_collector: MockMetricsCollector, skip_background: bool = False):
        self.metrics_collector = metrics_collector
        self.alerts = {}
        self.alert_rules = {}
        self.subscribers = []
        self.lock = threading.Lock()
        self.logger = logging.getLogger(f"{__name__}.MockAlertManager")
        
        # Default alert thresholds
        self.default_thresholds = {
            "error_rate": {"threshold": 0.05, "operator": ">", "severity": MockAlertSeverity.WARNING},
            "response_time_p95": {"threshold": 30.0, "operator": ">", "severity": MockAlertSeverity.WARNING},
            "token_usage_rate": {"threshold": 1000, "operator": ">", "severity": MockAlertSeverity.INFO},
            "system_cpu_usage": {"threshold": 0.85, "operator": ">", "severity": MockAlertSeverity.WARNING},
            "memory_usage": {"threshold": 0.90, "operator": ">", "severity": MockAlertSeverity.CRITICAL}
        }
        
        # Set up default rules
        for metric_name, config in self.default_thresholds.items():
            self.add_alert_rule(metric_name, config["threshold"], config["operator"], config["severity"])
        
        # Start background monitoring (conditionally)
        if not skip_background:
            self.monitoring_thread = threading.Thread(target=self._background_monitoring, daemon=True)
            self.monitoring_thread.start()
        else:
            self.monitoring_thread = None
    
    def add_alert_rule(self, metric_name: str, threshold: float, operator: str, severity: MockAlertSeverity):
        """Add an alert rule"""
        rule_id = f"{metric_name}_{operator}_{threshold}"
        self.alert_rules[rule_id] = {
            "metric_name": metric_name,
            "threshold": threshold,
            "operator": operator,
            "severity": severity,
            "enabled": True
        }
        self.logger.info(f"Added alert rule: {metric_name} {operator} {threshold}")
    
    def subscribe_to_alerts(self, callback: Callable[[MockAlert], None]):
        """Subscribe to alert notifications"""
        self.subscribers.append(callback)
    
    def trigger_alert(self, severity: MockAlertSeverity, title: str, message: str, 
                     metric_name: str = None, threshold: float = None, actual_value: float = None):
        """Trigger an alert"""
        alert_id = str(uuid.uuid4())
        alert = MockAlert(
            id=alert_id,
            severity=severity,
            title=title,
            message=message,
            timestamp=datetime.now(),
            metric_name=metric_name,
            threshold=threshold,
            actual_value=actual_value
        )
        
        with self.lock:
            self.alerts[alert_id] = alert
        
        # Notify subscribers
        for callback in self.subscribers:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")
        
        self.logger.warning(f"🚨 ALERT [{severity.value.upper()}]: {title}")
        return alert_id
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        with self.lock:
            if alert_id in self.alerts:
                self.alerts[alert_id].resolved = True
                self.alerts[alert_id].resolved_at = datetime.now()
                self.logger.info(f"✅ Alert resolved: {alert_id}")
    
    def _background_monitoring(self):
        """Background thread for alert monitoring"""
        while True:
            try:
                time.sleep(10)  # Check every 10 seconds
                self._check_alert_conditions()
            except Exception as e:
                self.logger.error(f"Alert monitoring error: {e}")
    
    def _check_alert_conditions(self):
        """Check all alert conditions"""
        for rule_id, rule in self.alert_rules.items():
            if not rule["enabled"]:
                continue
                
            metric_name = rule["metric_name"]
            summary = self.metrics_collector.get_metric_summary(metric_name)
            
            if not summary:
                continue
            
            # Use last value for gauge metrics, average for others
            current_value = summary.get("last_value", summary.get("average", 0))
            threshold = rule["threshold"]
            operator = rule["operator"]
            
            # Simulate some metric values if none exist
            if current_value is None:
                current_value = self._simulate_metric_value(metric_name)
            
            condition_met = False
            if operator == ">":
                condition_met = current_value > threshold
            elif operator == "<":
                condition_met = current_value < threshold
            elif operator == ">=":
                condition_met = current_value >= threshold
            elif operator == "<=":
                condition_met = current_value <= threshold
            
            if condition_met:
                # Check if we already have an active alert for this rule
                active_alerts = [a for a in self.alerts.values() 
                               if not a.resolved and a.metric_name == metric_name]
                
                if not active_alerts:  # Only trigger if no active alert exists
                    self.trigger_alert(
                        severity=rule["severity"],
                        title=f"Threshold exceeded: {metric_name}",
                        message=f"{metric_name} is {current_value:.2f}, exceeding threshold of {threshold}",
                        metric_name=metric_name,
                        threshold=threshold,
                        actual_value=current_value
                    )
    
    def _simulate_metric_value(self, metric_name: str) -> float:
        """Simulate metric values for testing"""
        base_values = {
            "error_rate": random.uniform(0.01, 0.12),
            "response_time_p95": random.uniform(5.0, 45.0),
            "token_usage_rate": random.uniform(100, 2000),
            "system_cpu_usage": random.uniform(0.20, 0.95),
            "memory_usage": random.uniform(0.30, 0.95)
        }
        return base_values.get(metric_name, random.uniform(0, 100))
    
    def get_active_alerts(self) -> List[MockAlert]:
        """Get all active alerts"""
        with self.lock:
            return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alert_history(self, hours: int = 24) -> List[MockAlert]:
        """Get alert history"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        with self.lock:
            return [alert for alert in self.alerts.values() if alert.timestamp > cutoff_time]


class MockAuditLogger:
    """Mock audit logging system"""
    
    def __init__(self):
        self.audit_entries = {}
        self.lock = threading.Lock()
        self.logger = logging.getLogger(f"{__name__}.MockAuditLogger")
    
    def log_event(self, session_id: str, event_type: str, event_data: Dict[str, Any],
                  user: str = None, result: str = None, duration_ms: int = None, error: str = None):
        """Log an audit event"""
        entry_id = str(uuid.uuid4())
        entry = MockAuditEntry(
            id=entry_id,
            session_id=session_id,
            timestamp=datetime.now(),
            event_type=event_type,
            event_data=event_data,
            user=user,
            result=result,
            duration_ms=duration_ms,
            error=error
        )
        
        with self.lock:
            self.audit_entries[entry_id] = entry
        
        self.logger.info(f"📝 AUDIT: {event_type} for session {session_id}")
        return entry_id
    
    def get_session_events(self, session_id: str) -> List[MockAuditEntry]:
        """Get all events for a session"""
        with self.lock:
            return [entry for entry in self.audit_entries.values() if entry.session_id == session_id]
    
    def get_events_by_type(self, event_type: str, hours: int = 24) -> List[MockAuditEntry]:
        """Get events by type within time window"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        with self.lock:
            return [entry for entry in self.audit_entries.values() 
                   if entry.event_type == event_type and entry.timestamp > cutoff_time]
    
    def get_error_events(self, hours: int = 24) -> List[MockAuditEntry]:
        """Get all error events"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        with self.lock:
            return [entry for entry in self.audit_entries.values() 
                   if entry.error and entry.timestamp > cutoff_time]


class MockDashboard:
    """Mock monitoring dashboard"""
    
    def __init__(self, metrics_collector: MockMetricsCollector, alert_manager: MockAlertManager, audit_logger: MockAuditLogger):
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(f"{__name__}.MockDashboard")
    
    def generate_system_overview(self) -> Dict[str, Any]:
        """Generate system overview dashboard"""
        active_alerts = self.alert_manager.get_active_alerts()
        error_events = self.audit_logger.get_error_events(1)  # Last hour
        
        overview = {
            "timestamp": datetime.now().isoformat(),
            "system_status": {
                "overall_health": "HEALTHY" if len(active_alerts) == 0 else "DEGRADED" if len(active_alerts) < 3 else "UNHEALTHY",
                "active_alerts": len(active_alerts),
                "error_rate": len(error_events) / max(1, len(self.audit_logger.audit_entries)) * 100,
                "uptime_percentage": random.uniform(99.5, 99.99)
            },
            "performance_metrics": {
                "avg_response_time": random.uniform(2.5, 8.5),
                "requests_per_minute": random.randint(15, 45),
                "success_rate": random.uniform(95.0, 99.5),
                "token_usage": {
                    "current_rate": random.randint(500, 1500),
                    "daily_usage": random.randint(25000, 85000),
                    "cost_estimate": random.uniform(12.50, 45.75)
                }
            },
            "agent_status": {
                "learning_agent": random.choice(["ACTIVE", "IDLE", "PROCESSING"]),
                "planning_agent": random.choice(["ACTIVE", "IDLE", "PROCESSING"]),
                "execution_agent": random.choice(["ACTIVE", "IDLE", "PROCESSING"]),
                "review_agent": random.choice(["ACTIVE", "IDLE", "PROCESSING"]),
                "audit_agent": random.choice(["ACTIVE", "IDLE", "PROCESSING"]),
                "improvement_agent": random.choice(["ACTIVE", "IDLE", "PROCESSING"])
            },
            "resource_utilization": {
                "cpu_usage": random.uniform(25.0, 75.0),
                "memory_usage": random.uniform(40.0, 85.0),
                "storage_usage": random.uniform(15.0, 60.0),
                "network_io": random.uniform(5.0, 25.0)
            },
            "recent_activity": {
                "sessions_today": random.randint(8, 25),
                "evaluations_completed": random.randint(15, 40),
                "avg_session_duration": random.uniform(25.0, 65.0),
                "user_satisfaction": random.uniform(85.0, 95.0)
            }
        }
        
        return overview
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate detailed performance report"""
        metric_names = self.metrics_collector.get_metric_names()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "reporting_period": "Last 24 Hours",
            "metric_summaries": {},
            "trend_analysis": {},
            "performance_insights": {
                "top_performing_areas": [
                    "Response time consistency",
                    "Error handling effectiveness",
                    "User satisfaction scores"
                ],
                "improvement_opportunities": [
                    "Token usage optimization",
                    "Agent coordination efficiency",
                    "Resource allocation balancing"
                ],
                "recommended_actions": [
                    "Implement caching for frequent queries",
                    "Optimize prompt engineering for token efficiency",
                    "Add load balancing for peak usage periods"
                ]
            },
            "sla_compliance": {
                "availability": random.uniform(99.7, 99.99),
                "response_time": random.uniform(95.0, 99.5),
                "accuracy": random.uniform(92.0, 97.5),
                "user_satisfaction": random.uniform(87.0, 94.0)
            }
        }
        
        # Add metric summaries
        for metric_name in metric_names[:10]:  # Top 10 metrics
            summary = self.metrics_collector.get_metric_summary(metric_name)
            if summary:
                report["metric_summaries"][metric_name] = summary
        
        # Add trend analysis (simulated)
        for metric_name in metric_names[:5]:  # Top 5 for trends
            report["trend_analysis"][metric_name] = {
                "trend": random.choice(["INCREASING", "DECREASING", "STABLE"]),
                "change_percentage": random.uniform(-15.0, 15.0),
                "forecast": random.choice(["IMPROVING", "STABLE", "DEGRADING"])
            }
        
        return report
    
    def print_dashboard(self):
        """Print dashboard to console"""
        overview = self.generate_system_overview()
        
        print("\n" + "=" * 80)
        print("📊 DEEP RESEARCH SYSTEM - MONITORING DASHBOARD")
        print("=" * 80)
        
        # System Status
        print(f"\n🏥 SYSTEM HEALTH: {overview['system_status']['overall_health']}")
        print(f"   Active Alerts: {overview['system_status']['active_alerts']}")
        print(f"   Error Rate: {overview['system_status']['error_rate']:.2f}%")
        print(f"   Uptime: {overview['system_status']['uptime_percentage']:.2f}%")
        
        # Performance Metrics
        perf = overview['performance_metrics']
        print(f"\n⚡ PERFORMANCE METRICS:")
        print(f"   Avg Response Time: {perf['avg_response_time']:.2f}s")
        print(f"   Requests/Min: {perf['requests_per_minute']}")
        print(f"   Success Rate: {perf['success_rate']:.1f}%")
        print(f"   Token Usage: {perf['token_usage']['current_rate']}/min")
        print(f"   Daily Cost: ${perf['token_usage']['cost_estimate']:.2f}")
        
        # Agent Status
        print(f"\n🤖 AGENT STATUS:")
        for agent, status in overview['agent_status'].items():
            print(f"   {agent.replace('_', ' ').title()}: {status}")
        
        # Resource Utilization
        resources = overview['resource_utilization']
        print(f"\n💻 RESOURCE UTILIZATION:")
        print(f"   CPU: {resources['cpu_usage']:.1f}%")
        print(f"   Memory: {resources['memory_usage']:.1f}%")
        print(f"   Storage: {resources['storage_usage']:.1f}%")
        print(f"   Network I/O: {resources['network_io']:.1f} MB/s")
        
        # Recent Activity
        activity = overview['recent_activity']
        print(f"\n📈 RECENT ACTIVITY:")
        print(f"   Sessions Today: {activity['sessions_today']}")
        print(f"   Evaluations Completed: {activity['evaluations_completed']}")
        print(f"   Avg Session Duration: {activity['avg_session_duration']:.1f} min")
        print(f"   User Satisfaction: {activity['user_satisfaction']:.1f}/100")
        
        # Active Alerts
        alerts = self.alert_manager.get_active_alerts()
        if alerts:
            print(f"\n🚨 ACTIVE ALERTS ({len(alerts)}):")
            for alert in alerts[:5]:  # Show top 5
                print(f"   [{alert.severity.value.upper()}] {alert.title}")
        
        print("\n" + "=" * 80)


class MockResearchMonitoringSystem:
    """Complete mock monitoring system for deep research"""
    
    def __init__(self, skip_background_loops: bool = False):
        self.skip_background_loops = skip_background_loops
        self.metrics_collector = MockMetricsCollector(skip_background=skip_background_loops)
        self.alert_manager = MockAlertManager(self.metrics_collector, skip_background=skip_background_loops)
        self.audit_logger = MockAuditLogger()
        self.dashboard = MockDashboard(self.metrics_collector, self.alert_manager, self.audit_logger)
        
        self.session_id = None
        self.logger = logging.getLogger(f"{__name__}.MockResearchMonitoringSystem")
        
        # Subscribe to alerts for logging
        self.alert_manager.subscribe_to_alerts(self._handle_alert)
        
        self.logger.info("🎯 Mock Research Monitoring System initialized")
    
    def start_monitoring_session(self, session_id: str):
        """Start monitoring a research session"""
        self.session_id = session_id
        self.audit_logger.log_event(
            session_id=session_id,
            event_type="SESSION_START",
            event_data={"start_time": datetime.now().isoformat()}
        )
        self.logger.info(f"📊 Started monitoring session: {session_id}")
    
    def end_monitoring_session(self, session_id: str, result: str = "SUCCESS"):
        """End monitoring a research session"""
        self.audit_logger.log_event(
            session_id=session_id,
            event_type="SESSION_END",
            event_data={"end_time": datetime.now().isoformat()},
            result=result
        )
        self.logger.info(f"🏁 Ended monitoring session: {session_id}")
    
    def track_file_upload(self, session_id: str, filename: str, size_bytes: int, success: bool):
        """Track file upload event"""
        self.metrics_collector.record_counter("file_uploads_total", 1, {"success": str(success)})
        self.metrics_collector.record_gauge("file_size_bytes", size_bytes)
        
        self.audit_logger.log_event(
            session_id=session_id,
            event_type="FILE_UPLOAD",
            event_data={"filename": filename, "size_bytes": size_bytes},
            result="SUCCESS" if success else "FAILED"
        )
    
    def track_vector_store_creation(self, session_id: str, store_id: str, file_count: int, duration: float):
        """Track vector store creation"""
        self.metrics_collector.record_timer("vector_store_creation_duration", duration)
        self.metrics_collector.record_gauge("vector_store_file_count", file_count)
        
        self.audit_logger.log_event(
            session_id=session_id,
            event_type="VECTOR_STORE_CREATED",
            event_data={"store_id": store_id, "file_count": file_count},
            duration_ms=int(duration * 1000)
        )
    
    def track_agent_execution(self, session_id: str, agent_name: str, duration: float, 
                            success: bool, tokens_used: int = None):
        """Track agent execution"""
        self.metrics_collector.record_timer(f"agent_{agent_name}_duration", duration)
        self.metrics_collector.record_counter(f"agent_{agent_name}_executions", 1, {"success": str(success)})
        
        if tokens_used:
            self.metrics_collector.record_gauge("tokens_used", tokens_used, {"agent": agent_name})
        
        self.audit_logger.log_event(
            session_id=session_id,
            event_type="AGENT_EXECUTION",
            event_data={"agent_name": agent_name, "tokens_used": tokens_used},
            result="SUCCESS" if success else "FAILED",
            duration_ms=int(duration * 1000)
        )
    
    def track_error(self, session_id: str, error_type: str, error_message: str, component: str = None):
        """Track error event"""
        self.metrics_collector.record_counter("errors_total", 1, {"type": error_type, "component": component})
        
        self.audit_logger.log_event(
            session_id=session_id,
            event_type="ERROR",
            event_data={"error_type": error_type, "component": component},
            error=error_message
        )
    
    def _handle_alert(self, alert: MockAlert):
        """Handle alert notifications"""
        self.logger.warning(f"🚨 Alert triggered: {alert.title}")
        
        if self.session_id:
            self.audit_logger.log_event(
                session_id=self.session_id,
                event_type="ALERT_TRIGGERED",
                event_data={
                    "alert_id": alert.id,
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "metric_name": alert.metric_name
                }
            )
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session summary"""
        session_events = self.audit_logger.get_session_events(session_id)
        
        # Categorize events
        event_counts = defaultdict(int)
        for event in session_events:
            event_counts[event.event_type] += 1
        
        # Calculate durations
        durations = [event.duration_ms for event in session_events if event.duration_ms]
        
        summary = {
            "session_id": session_id,
            "total_events": len(session_events),
            "event_breakdown": dict(event_counts),
            "errors": len([e for e in session_events if e.error]),
            "average_duration_ms": sum(durations) / len(durations) if durations else 0,
            "session_duration": None,
            "success_rate": (len(session_events) - event_counts.get("ERROR", 0)) / max(1, len(session_events)) * 100
        }
        
        # Calculate session duration
        start_events = [e for e in session_events if e.event_type == "SESSION_START"]
        end_events = [e for e in session_events if e.event_type == "SESSION_END"]
        
        if start_events and end_events:
            duration = end_events[-1].timestamp - start_events[0].timestamp
            summary["session_duration"] = duration.total_seconds()
        
        return summary
    
    def simulate_realistic_metrics(self):
        """Simulate realistic system metrics for testing"""
        # Simulate various metrics
        self.metrics_collector.record_gauge("system_cpu_usage", random.uniform(0.20, 0.80))
        self.metrics_collector.record_gauge("memory_usage", random.uniform(0.40, 0.90))
        self.metrics_collector.record_timer("response_time", random.uniform(1.0, 10.0))
        self.metrics_collector.record_counter("requests_total", random.randint(1, 5))
        self.metrics_collector.record_gauge("token_usage_rate", random.uniform(100, 1500))
        
        # Occasionally trigger errors for testing
        if random.random() < 0.1:  # 10% chance
            self.metrics_collector.record_counter("errors_total", 1)


# Test the monitoring system
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🔧 Testing Mock Research Monitoring System")
    print("=" * 60)
    
    # Initialize monitoring system
    monitoring = MockResearchMonitoringSystem()
    
    # Start a test session
    test_session = "test_session_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    monitoring.start_monitoring_session(test_session)
    
    print(f"📊 Started monitoring session: {test_session}")
    
    # Simulate various events
    print("\n📁 Simulating file uploads...")
    for i in range(3):
        monitoring.track_file_upload(
            session_id=test_session,
            filename=f"document_{i+1}.pdf",
            size_bytes=random.randint(50000, 500000),
            success=random.choice([True, True, True, False])  # Mostly successful
        )
        time.sleep(0.1)
    
    print("🗄️ Simulating vector store creation...")
    monitoring.track_vector_store_creation(
        session_id=test_session,
        store_id="vs_mock_test_123",
        file_count=3,
        duration=random.uniform(5.0, 15.0)
    )
    
    print("🤖 Simulating agent executions...")
    agents = ["learning", "planning", "execution", "review", "audit", "improvement"]
    for agent in agents:
        monitoring.track_agent_execution(
            session_id=test_session,
            agent_name=agent,
            duration=random.uniform(10.0, 30.0),
            success=random.choice([True, True, True, False]),  # Mostly successful
            tokens_used=random.randint(1000, 5000)
        )
        time.sleep(0.1)
    
    # Simulate some errors
    print("⚠️ Simulating error conditions...")
    monitoring.track_error(
        session_id=test_session,
        error_type="TIMEOUT",
        error_message="Mock timeout error for testing",
        component="vector_store"
    )
    
    # Generate some realistic metrics
    print("📊 Generating realistic metrics...")
    for _ in range(20):
        monitoring.simulate_realistic_metrics()
        time.sleep(0.05)
    
    # End session
    monitoring.end_monitoring_session(test_session, "SUCCESS")
    
    print("\n" + "=" * 60)
    print("📈 GENERATING REPORTS AND DASHBOARD")
    print("=" * 60)
    
    # Show dashboard
    monitoring.dashboard.print_dashboard()
    
    # Show session summary
    print("\n📋 SESSION SUMMARY:")
    print("-" * 40)
    summary = monitoring.get_session_summary(test_session)
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Show performance report
    print("\n📊 PERFORMANCE REPORT:")
    print("-" * 40)
    report = monitoring.dashboard.generate_performance_report()
    print(f"   Reporting Period: {report['reporting_period']}")
    print(f"   Metrics Tracked: {len(report['metric_summaries'])}")
    print(f"   SLA Compliance:")
    for sla, value in report['sla_compliance'].items():
        print(f"     {sla}: {value:.2f}%")
    
    print(f"\n   Top Performing Areas:")
    for area in report['performance_insights']['top_performing_areas']:
        print(f"     • {area}")
    
    print(f"\n   Improvement Opportunities:")
    for opportunity in report['performance_insights']['improvement_opportunities']:
        print(f"     • {opportunity}")
    
    print("\n🎉 Mock monitoring system test completed!")