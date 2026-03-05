#!/usr/bin/env python3
"""
Monitoring and Audit System for Grant Eval V3 Deep Research
Provides comprehensive tracking, metrics, and observability
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from enum import Enum

# Configuration
METRICS_RETENTION_DAYS = 30
ALERT_THRESHOLDS = {
    "error_rate": 0.1,  # 10% error rate triggers alert
    "token_usage": 100000,  # 100K tokens triggers alert
    "latency_p95": 300,  # 5 minutes P95 latency triggers alert
    "cost_per_run": 15.0,  # $15 per run triggers alert
}

class MetricType(Enum):
    """Types of metrics we track"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Metric:
    """Individual metric data point"""
    name: str
    type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """Alert notification"""
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime
    metric_name: Optional[str] = None
    threshold: Optional[float] = None
    actual_value: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class AuditEntry:
    """Audit log entry"""
    session_id: str
    timestamp: datetime
    event_type: str
    event_data: Dict[str, Any]
    user: Optional[str] = None
    result: Optional[str] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None

class MetricsCollector:
    """Collects and aggregates metrics"""
    
    def __init__(self, buffer_size: int = 1000):
        self.metrics_buffer = deque(maxlen=buffer_size)
        self.aggregated_metrics = defaultdict(list)
        self.lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def record_metric(self, metric: Metric):
        """Record a single metric"""
        with self.lock:
            self.metrics_buffer.append(metric)
            self.aggregated_metrics[metric.name].append(metric)
            
    def record_counter(self, name: str, value: float = 1, tags: Dict[str, str] = None):
        """Record a counter metric"""
        metric = Metric(
            name=name,
            type=MetricType.COUNTER,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        self.record_metric(metric)
        
    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a gauge metric"""
        metric = Metric(
            name=name,
            type=MetricType.GAUGE,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        self.record_metric(metric)
        
    def record_timer(self, name: str, duration_ms: float, tags: Dict[str, str] = None):
        """Record a timer metric"""
        metric = Metric(
            name=name,
            type=MetricType.TIMER,
            value=duration_ms,
            timestamp=datetime.now(),
            tags=tags or {},
            metadata={"unit": "milliseconds"}
        )
        self.record_metric(metric)
        
    def get_metrics_summary(self, metric_name: str = None, 
                           time_window: timedelta = None) -> Dict[str, Any]:
        """Get summary statistics for metrics"""
        with self.lock:
            if metric_name:
                metrics = self.aggregated_metrics.get(metric_name, [])
            else:
                metrics = list(self.metrics_buffer)
                
            if time_window:
                cutoff = datetime.now() - time_window
                metrics = [m for m in metrics if m.timestamp >= cutoff]
                
            if not metrics:
                return {}
                
            values = [m.value for m in metrics]
            return {
                "count": len(values),
                "sum": sum(values),
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "p50": self._percentile(values, 50),
                "p95": self._percentile(values, 95),
                "p99": self._percentile(values, 99),
            }
            
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.alerts = deque(maxlen=1000)
        self.alert_handlers = []
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def check_thresholds(self):
        """Check metrics against thresholds and trigger alerts"""
        alerts_triggered = []
        
        # Check error rate
        error_summary = self.metrics_collector.get_metrics_summary(
            "research.errors", 
            time_window=timedelta(minutes=5)
        )
        if error_summary and error_summary.get("mean", 0) > ALERT_THRESHOLDS["error_rate"]:
            alert = Alert(
                severity=AlertSeverity.WARNING,
                title="High Error Rate",
                message=f"Error rate {error_summary['mean']:.2%} exceeds threshold",
                timestamp=datetime.now(),
                metric_name="research.errors",
                threshold=ALERT_THRESHOLDS["error_rate"],
                actual_value=error_summary["mean"]
            )
            alerts_triggered.append(alert)
            
        # Check token usage
        token_summary = self.metrics_collector.get_metrics_summary(
            "api.tokens.total",
            time_window=timedelta(hours=1)
        )
        if token_summary and token_summary.get("sum", 0) > ALERT_THRESHOLDS["token_usage"]:
            alert = Alert(
                severity=AlertSeverity.WARNING,
                title="High Token Usage",
                message=f"Token usage {token_summary['sum']:,.0f} exceeds threshold",
                timestamp=datetime.now(),
                metric_name="api.tokens.total",
                threshold=ALERT_THRESHOLDS["token_usage"],
                actual_value=token_summary["sum"]
            )
            alerts_triggered.append(alert)
            
        # Check latency
        latency_summary = self.metrics_collector.get_metrics_summary(
            "research.latency",
            time_window=timedelta(minutes=15)
        )
        if latency_summary and latency_summary.get("p95", 0) > ALERT_THRESHOLDS["latency_p95"]:
            alert = Alert(
                severity=AlertSeverity.WARNING,
                title="High Latency",
                message=f"P95 latency {latency_summary['p95']:.1f}s exceeds threshold",
                timestamp=datetime.now(),
                metric_name="research.latency",
                threshold=ALERT_THRESHOLDS["latency_p95"],
                actual_value=latency_summary["p95"]
            )
            alerts_triggered.append(alert)
            
        # Process alerts
        for alert in alerts_triggered:
            self.trigger_alert(alert)
            
        return alerts_triggered
        
    def trigger_alert(self, alert: Alert):
        """Trigger an alert and notify handlers"""
        self.alerts.append(alert)
        self.logger.log(
            self._severity_to_log_level(alert.severity),
            f"Alert: {alert.title} - {alert.message}"
        )
        
        # Notify all registered handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {e}")
                
    def _severity_to_log_level(self, severity: AlertSeverity) -> int:
        """Convert alert severity to logging level"""
        mapping = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL,
        }
        return mapping.get(severity, logging.INFO)
        
    def register_handler(self, handler):
        """Register an alert handler function"""
        self.alert_handlers.append(handler)

class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = None
        self.audit_entries = []
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def start_session(self, session_id: str, metadata: Dict[str, Any] = None):
        """Start a new audit session"""
        self.current_session = session_id
        entry = AuditEntry(
            session_id=session_id,
            timestamp=datetime.now(),
            event_type="session_start",
            event_data=metadata or {}
        )
        self.log_entry(entry)
        
    def end_session(self, result: str = "success", metadata: Dict[str, Any] = None):
        """End the current audit session"""
        if not self.current_session:
            return
            
        entry = AuditEntry(
            session_id=self.current_session,
            timestamp=datetime.now(),
            event_type="session_end",
            event_data=metadata or {},
            result=result
        )
        self.log_entry(entry)
        self.current_session = None
        
    def log_event(self, event_type: str, event_data: Dict[str, Any], 
                  result: str = None, duration_ms: int = None, error: str = None):
        """Log an audit event"""
        entry = AuditEntry(
            session_id=self.current_session or "unknown",
            timestamp=datetime.now(),
            event_type=event_type,
            event_data=event_data,
            result=result,
            duration_ms=duration_ms,
            error=error
        )
        self.log_entry(entry)
        
    def log_entry(self, entry: AuditEntry):
        """Write audit entry to log"""
        self.audit_entries.append(entry)
        
        # Write to file
        log_file = self.log_dir / f"audit_{entry.timestamp.strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(asdict(entry), default=str) + '\n')
            
    def get_session_audit_trail(self, session_id: str) -> List[AuditEntry]:
        """Get complete audit trail for a session"""
        return [e for e in self.audit_entries if e.session_id == session_id]
        
    def generate_audit_report(self, session_id: str = None, 
                            start_time: datetime = None,
                            end_time: datetime = None) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        entries = self.audit_entries
        
        if session_id:
            entries = [e for e in entries if e.session_id == session_id]
        if start_time:
            entries = [e for e in entries if e.timestamp >= start_time]
        if end_time:
            entries = [e for e in entries if e.timestamp <= end_time]
            
        if not entries:
            return {}
            
        # Analyze entries
        event_counts = defaultdict(int)
        error_counts = defaultdict(int)
        total_duration = 0
        successful_events = 0
        failed_events = 0
        
        for entry in entries:
            event_counts[entry.event_type] += 1
            if entry.error:
                error_counts[entry.event_type] += 1
                failed_events += 1
            elif entry.result == "success":
                successful_events += 1
            if entry.duration_ms:
                total_duration += entry.duration_ms
                
        return {
            "total_events": len(entries),
            "successful_events": successful_events,
            "failed_events": failed_events,
            "error_rate": failed_events / len(entries) if entries else 0,
            "event_counts": dict(event_counts),
            "error_counts": dict(error_counts),
            "total_duration_ms": total_duration,
            "average_duration_ms": total_duration / len(entries) if entries else 0,
            "time_range": {
                "start": min(e.timestamp for e in entries),
                "end": max(e.timestamp for e in entries),
            }
        }

class MonitoringDashboard:
    """Real-time monitoring dashboard"""
    
    def __init__(self, metrics_collector: MetricsCollector, 
                 alert_manager: AlertManager,
                 audit_logger: AuditLogger):
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "health_status": self._calculate_health_status(),
            "metrics": self._get_key_metrics(),
            "recent_alerts": self._get_recent_alerts(),
            "session_stats": self._get_session_stats(),
            "performance": self._get_performance_metrics(),
        }
        
    def _calculate_health_status(self) -> str:
        """Calculate overall system health"""
        recent_alerts = list(self.alert_manager.alerts)[-10:]
        if any(a.severity == AlertSeverity.CRITICAL for a in recent_alerts):
            return "critical"
        elif any(a.severity == AlertSeverity.ERROR for a in recent_alerts):
            return "degraded"
        elif any(a.severity == AlertSeverity.WARNING for a in recent_alerts):
            return "warning"
        return "healthy"
        
    def _get_key_metrics(self) -> Dict[str, Any]:
        """Get key metrics for display"""
        return {
            "api_calls": self.metrics_collector.get_metrics_summary("api.calls"),
            "tokens": self.metrics_collector.get_metrics_summary("api.tokens.total"),
            "errors": self.metrics_collector.get_metrics_summary("research.errors"),
            "latency": self.metrics_collector.get_metrics_summary("research.latency"),
        }
        
    def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent alerts for display"""
        recent = list(self.alert_manager.alerts)[-5:]
        return [asdict(alert) for alert in recent]
        
    def _get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        report = self.audit_logger.generate_audit_report(
            start_time=datetime.now() - timedelta(hours=24)
        )
        return {
            "sessions_24h": report.get("total_events", 0),
            "success_rate": 1 - report.get("error_rate", 0),
            "avg_duration": report.get("average_duration_ms", 0),
        }
        
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "token_efficiency": self._calculate_token_efficiency(),
            "cost_per_research": self._calculate_average_cost(),
            "throughput": self._calculate_throughput(),
        }
        
    def _calculate_token_efficiency(self) -> float:
        """Calculate tokens per insight ratio"""
        token_summary = self.metrics_collector.get_metrics_summary("api.tokens.total")
        insight_summary = self.metrics_collector.get_metrics_summary("research.insights")
        
        if token_summary and insight_summary:
            total_tokens = token_summary.get("sum", 0)
            total_insights = insight_summary.get("sum", 0)
            if total_insights > 0:
                return total_tokens / total_insights
        return 0
        
    def _calculate_average_cost(self) -> float:
        """Calculate average cost per research"""
        # Assuming $0.01 per 1K tokens for input, $0.03 per 1K tokens for output
        token_summary = self.metrics_collector.get_metrics_summary("api.tokens.total")
        if token_summary:
            total_tokens = token_summary.get("sum", 0)
            estimated_cost = (total_tokens / 1000) * 0.02  # Average of input/output
            research_count = token_summary.get("count", 1)
            return estimated_cost / research_count
        return 0
        
    def _calculate_throughput(self) -> float:
        """Calculate research completions per hour"""
        report = self.audit_logger.generate_audit_report(
            start_time=datetime.now() - timedelta(hours=1)
        )
        return report.get("successful_events", 0)
        
    def display(self):
        """Display dashboard (console version)"""
        data = self.get_dashboard_data()
        
        print("\n" + "="*60)
        print("GRANT EVAL V3 - MONITORING DASHBOARD")
        print("="*60)
        print(f"Timestamp: {data['timestamp']}")
        print(f"Health Status: {data['health_status'].upper()}")
        print("\n--- Key Metrics ---")
        
        metrics = data['metrics']
        for metric_name, summary in metrics.items():
            if summary:
                print(f"{metric_name}:")
                print(f"  Count: {summary.get('count', 0)}")
                print(f"  Mean: {summary.get('mean', 0):.2f}")
                print(f"  P95: {summary.get('p95', 0):.2f}")
                
        print("\n--- Session Stats (24h) ---")
        stats = data['session_stats']
        print(f"Sessions: {stats['sessions_24h']}")
        print(f"Success Rate: {stats['success_rate']:.1%}")
        print(f"Avg Duration: {stats['avg_duration']:.0f}ms")
        
        print("\n--- Performance ---")
        perf = data['performance']
        print(f"Token Efficiency: {perf['token_efficiency']:.0f} tokens/insight")
        print(f"Cost per Research: ${perf['cost_per_research']:.2f}")
        print(f"Throughput: {perf['throughput']:.0f} researches/hour")
        
        if data['recent_alerts']:
            print("\n--- Recent Alerts ---")
            for alert in data['recent_alerts']:
                print(f"[{alert['severity']}] {alert['title']}")
                
        print("="*60 + "\n")

class ResearchMonitoringSystem:
    """Complete monitoring and audit system for research"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.log_dir = workspace_root / "monitoring_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.metrics = MetricsCollector()
        self.alerts = AlertManager(self.metrics)
        self.audit = AuditLogger(self.log_dir)
        self.dashboard = MonitoringDashboard(self.metrics, self.alerts, self.audit)
        
        # Start background monitoring
        self._start_monitoring_thread()
        
    def _start_monitoring_thread(self):
        """Start background monitoring thread"""
        def monitor_loop():
            while True:
                try:
                    # Check thresholds every minute
                    self.alerts.check_thresholds()
                    time.sleep(60)
                except Exception as e:
                    logging.error(f"Monitoring loop error: {e}")
                    
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        
    def track_research_execution(self, session_id: str):
        """Context manager for tracking research execution"""
        class ExecutionTracker:
            def __init__(self, monitoring_system):
                self.monitoring = monitoring_system
                self.session_id = session_id
                self.start_time = None
                
            def __enter__(self):
                self.start_time = time.time()
                self.monitoring.audit.start_session(self.session_id)
                self.monitoring.metrics.record_counter("research.started")
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = (time.time() - self.start_time) * 1000
                self.monitoring.metrics.record_timer("research.duration", duration)
                
                if exc_type:
                    self.monitoring.metrics.record_counter("research.errors")
                    self.monitoring.audit.end_session("error", {"error": str(exc_val)})
                else:
                    self.monitoring.metrics.record_counter("research.completed")
                    self.monitoring.audit.end_session("success")
                    
        return ExecutionTracker(self)
        
    def track_api_call(self, operation: str, tokens: int = 0, error: str = None):
        """Track an API call"""
        self.metrics.record_counter("api.calls", tags={"operation": operation})
        if tokens:
            self.metrics.record_gauge("api.tokens.total", tokens)
        if error:
            self.metrics.record_counter("api.errors", tags={"operation": operation})
            
    def track_insight(self, insight_type: str, confidence: float):
        """Track an extracted insight"""
        self.metrics.record_counter("research.insights", tags={"type": insight_type})
        self.metrics.record_gauge("research.confidence", confidence)
        
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return self.dashboard.get_dashboard_data()
        
    def show_dashboard(self):
        """Display the monitoring dashboard"""
        self.dashboard.display()

# Example usage
if __name__ == "__main__":
    # Initialize monitoring system
    monitoring = ResearchMonitoringSystem(Path("/tmp/research_monitoring"))
    
    # Simulate research execution
    with monitoring.track_research_execution("test_session_001") as tracker:
        # Track some metrics
        monitoring.track_api_call("vector_store_create", tokens=1500)
        time.sleep(0.1)
        
        monitoring.track_api_call("deep_research_create", tokens=5000)
        time.sleep(0.2)
        
        monitoring.track_insight("implementation_gap", confidence=0.85)
        monitoring.track_insight("performance_issue", confidence=0.72)
        
        monitoring.track_api_call("results_retrieval", tokens=500)
        
    # Show dashboard
    monitoring.show_dashboard()
    
    # Get audit report
    report = monitoring.audit.generate_audit_report("test_session_001")
    print("Audit Report:", json.dumps(report, indent=2, default=str))