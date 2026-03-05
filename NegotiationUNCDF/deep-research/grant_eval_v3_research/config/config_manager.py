#!/usr/bin/env python3
"""
Configuration Manager for Agentic Deep Research System
Handles loading, validation, and management of system configuration
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

@dataclass
class SystemConfig:
    """System configuration settings"""
    version: str = "1.0.0"
    name: str = "Grant Eval v3 Agentic Research"
    workspace_root: str = "/Users/agent-g/Downloads/NegotiationUNCDF"
    research_root: str = "deep_research/grant_eval_v3_research"
    max_concurrent_agents: int = 3
    self_improvement_enabled: bool = True
    performance_tracking: bool = True

@dataclass
class OpenAIConfig:
    """OpenAI API configuration"""
    model: str = "o4-mini-deep-research"
    timeout: int = 3600
    max_retries: int = 3
    retry_delay: int = 5
    background_execution: bool = True
    tools: Dict[str, bool] = field(default_factory=lambda: {
        "file_search": True,
        "code_interpreter": True
    })

@dataclass
class AgentConfig:
    """Individual agent configuration"""
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SelfImprovementConfig:
    """Self-improvement loop configuration"""
    cycle_frequency: str = "after_each_run"
    learning_sources: List[str] = field(default_factory=lambda: [
        "performance_metrics", "user_feedback", "error_patterns", "execution_logs"
    ])
    improvement_strategies: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class MonitoringConfig:
    """Monitoring system configuration"""
    dashboard_enabled: bool = True
    real_time_alerts: bool = True
    metrics_collection: str = "comprehensive"
    retention_period: int = 30
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    dashboards: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ResearchConfig:
    """Research-specific configuration"""
    vector_store: Dict[str, Any] = field(default_factory=dict)
    analysis_depth: str = "comprehensive"
    focus_areas: List[str] = field(default_factory=list)
    output_format: Dict[str, bool] = field(default_factory=dict)

@dataclass
class MemoryConfig:
    """Memory and learning configuration"""
    persistent_storage: bool = True
    storage_type: str = "json"
    memory_types: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    caching: Dict[str, Any] = field(default_factory=dict)
    batching: Dict[str, Any] = field(default_factory=dict)
    parallel_processing: Dict[str, Any] = field(default_factory=dict)
    resource_limits: Dict[str, int] = field(default_factory=dict)

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers: List[Dict[str, Any]] = field(default_factory=list)

class ConfigManager:
    """Configuration manager for the agentic research system"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config_data = {}
        self.parsed_config = {}
        
        # Load configuration
        self.load_config()
        self.validate_config()
        self.parse_config()
        
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
                
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f)
                
            self.logger.info(f"Configuration loaded from: {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
            
    def validate_config(self):
        """Validate configuration structure and values"""
        required_sections = [
            'system', 'openai', 'agents', 'self_improvement', 
            'monitoring', 'research', 'memory', 'performance', 'logging'
        ]
        
        for section in required_sections:
            if section not in self.config_data:
                raise ValueError(f"Missing required configuration section: {section}")
                
        # Validate OpenAI configuration
        openai_config = self.config_data.get('openai', {})
        if not openai_config.get('model'):
            raise ValueError("OpenAI model must be specified")
            
        # Validate agent configuration
        agents_config = self.config_data.get('agents', {})
        if not agents_config:
            raise ValueError("At least one agent must be configured")
            
        # Validate paths
        system_config = self.config_data.get('system', {})
        workspace_root = system_config.get('workspace_root')
        if workspace_root and not Path(workspace_root).exists():
            self.logger.warning(f"Workspace root does not exist: {workspace_root}")
            
        self.logger.info("Configuration validation passed")
        
    def parse_config(self):
        """Parse configuration into structured objects"""
        try:
            # Parse system configuration
            self.parsed_config['system'] = SystemConfig(
                **self.config_data.get('system', {})
            )
            
            # Parse OpenAI configuration
            self.parsed_config['openai'] = OpenAIConfig(
                **self.config_data.get('openai', {})
            )
            
            # Parse agent configurations
            self.parsed_config['agents'] = {}
            agents_data = self.config_data.get('agents', {})
            for agent_name, agent_config in agents_data.items():
                self.parsed_config['agents'][agent_name] = AgentConfig(
                    enabled=agent_config.get('enabled', True),
                    config=agent_config
                )
                
            # Parse other configurations
            self.parsed_config['self_improvement'] = SelfImprovementConfig(
                **self.config_data.get('self_improvement', {})
            )
            
            self.parsed_config['monitoring'] = MonitoringConfig(
                **self.config_data.get('monitoring', {})
            )
            
            self.parsed_config['research'] = ResearchConfig(
                **self.config_data.get('research', {})
            )
            
            self.parsed_config['memory'] = MemoryConfig(
                **self.config_data.get('memory', {})
            )
            
            self.parsed_config['performance'] = PerformanceConfig(
                **self.config_data.get('performance', {})
            )
            
            self.parsed_config['logging'] = LoggingConfig(
                **self.config_data.get('logging', {})
            )
            
            self.logger.info("Configuration parsing completed")
            
        except Exception as e:
            self.logger.error(f"Failed to parse configuration: {e}")
            raise
            
    def get_system_config(self) -> SystemConfig:
        """Get system configuration"""
        return self.parsed_config['system']
        
    def get_openai_config(self) -> OpenAIConfig:
        """Get OpenAI configuration"""
        return self.parsed_config['openai']
        
    def get_agent_config(self, agent_name: str) -> Optional[AgentConfig]:
        """Get configuration for a specific agent"""
        return self.parsed_config['agents'].get(agent_name)
        
    def get_all_agent_configs(self) -> Dict[str, AgentConfig]:
        """Get all agent configurations"""
        return self.parsed_config['agents']
        
    def get_enabled_agents(self) -> List[str]:
        """Get list of enabled agent names"""
        return [
            name for name, config in self.parsed_config['agents'].items()
            if config.enabled
        ]
        
    def get_self_improvement_config(self) -> SelfImprovementConfig:
        """Get self-improvement configuration"""
        return self.parsed_config['self_improvement']
        
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration"""
        return self.parsed_config['monitoring']
        
    def get_research_config(self) -> ResearchConfig:
        """Get research configuration"""
        return self.parsed_config['research']
        
    def get_memory_config(self) -> MemoryConfig:
        """Get memory configuration"""
        return self.parsed_config['memory']
        
    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration"""
        return self.parsed_config['performance']
        
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration"""
        return self.parsed_config['logging']
        
    def get_raw_config(self) -> Dict[str, Any]:
        """Get raw configuration data"""
        return self.config_data.copy()
        
    def get_config_value(self, path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation path"""
        try:
            keys = path.split('.')
            value = self.config_data
            
            for key in keys:
                value = value[key]
                
            return value
            
        except (KeyError, TypeError):
            return default
            
    def update_config_value(self, path: str, value: Any):
        """Update configuration value using dot notation path"""
        try:
            keys = path.split('.')
            config_ref = self.config_data
            
            # Navigate to parent
            for key in keys[:-1]:
                if key not in config_ref:
                    config_ref[key] = {}
                config_ref = config_ref[key]
                
            # Set value
            config_ref[keys[-1]] = value
            
            # Re-parse configuration
            self.validate_config()
            self.parse_config()
            
            self.logger.info(f"Updated configuration: {path} = {value}")
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            raise
            
    def save_config(self, backup: bool = True):
        """Save configuration to file"""
        try:
            if backup:
                backup_path = self.config_path.with_suffix(
                    f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
                )
                with open(backup_path, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
                    
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
                
            self.logger.info(f"Configuration saved to: {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise
            
    def export_config(self, format: str = "json") -> str:
        """Export configuration in specified format"""
        if format.lower() == "json":
            return json.dumps(self.config_data, indent=2, default=str)
        elif format.lower() == "yaml":
            return yaml.dump(self.config_data, default_flow_style=False, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
    def get_environment_overrides(self) -> Dict[str, Any]:
        """Get configuration overrides from environment variables"""
        overrides = {}
        prefix = "AGENTIC_RESEARCH_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower().replace('_', '.')
                
                # Try to parse as JSON, fall back to string
                try:
                    parsed_value = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    parsed_value = value
                    
                overrides[config_key] = parsed_value
                
        return overrides
        
    def apply_environment_overrides(self):
        """Apply environment variable overrides to configuration"""
        overrides = self.get_environment_overrides()
        
        for path, value in overrides.items():
            try:
                self.update_config_value(path, value)
                self.logger.info(f"Applied environment override: {path} = {value}")
            except Exception as e:
                self.logger.warning(f"Failed to apply environment override {path}: {e}")
                
    def validate_agent_config(self, agent_name: str) -> bool:
        """Validate configuration for a specific agent"""
        agent_config = self.get_agent_config(agent_name)
        if not agent_config:
            return False
            
        # Agent-specific validation logic
        if agent_name == "learning_agent":
            required_keys = ["learning_rate", "pattern_threshold", "memory_window"]
        elif agent_name == "planning_agent":
            required_keys = ["strategy_types", "optimization_targets", "planning_horizon"]
        elif agent_name == "improvement_agent":
            required_keys = ["optimization_types", "improvement_threshold"]
        elif agent_name == "execution_agent":
            required_keys = ["monitoring_level", "checkpoint_interval"]
        elif agent_name == "audit_agent":
            required_keys = ["compliance_checks", "audit_level", "retention_days"]
        elif agent_name == "review_agent":
            required_keys = ["quality_metrics", "review_criteria", "iteration_threshold"]
        else:
            return True  # Unknown agent, skip validation
            
        for key in required_keys:
            if key not in agent_config.config:
                self.logger.error(f"Missing required configuration for {agent_name}: {key}")
                return False
                
        return True
        
    def get_workspace_paths(self) -> Dict[str, Path]:
        """Get important workspace paths"""
        system_config = self.get_system_config()
        workspace_root = Path(system_config.workspace_root)
        research_root = workspace_root / system_config.research_root
        
        return {
            "workspace_root": workspace_root,
            "research_root": research_root,
            "config_dir": research_root / "config",
            "scripts_dir": research_root / "scripts",
            "logs_dir": research_root / "logs",
            "results_dir": research_root / "results",
            "memory_dir": research_root / "memory",
            "agents_dir": research_root / "agents"
        }
        
    def ensure_directories(self):
        """Ensure all required directories exist"""
        paths = self.get_workspace_paths()
        
        for name, path in paths.items():
            try:
                path.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Ensured directory exists: {name} -> {path}")
            except Exception as e:
                self.logger.error(f"Failed to create directory {name}: {e}")
                
    def get_status(self) -> Dict[str, Any]:
        """Get configuration manager status"""
        return {
            "config_loaded": bool(self.config_data),
            "config_path": str(self.config_path),
            "config_valid": self._is_config_valid(),
            "enabled_agents": self.get_enabled_agents(),
            "last_modified": self._get_config_last_modified(),
            "workspace_paths": {
                name: str(path) for name, path in self.get_workspace_paths().items()
            }
        }
        
    def _is_config_valid(self) -> bool:
        """Check if configuration is valid"""
        try:
            self.validate_config()
            return True
        except Exception:
            return False
            
    def _get_config_last_modified(self) -> Optional[str]:
        """Get configuration file last modified time"""
        try:
            if self.config_path.exists():
                return datetime.fromtimestamp(
                    self.config_path.stat().st_mtime
                ).isoformat()
        except Exception:
            pass
        return None

# Global configuration manager instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def reload_config():
    """Reload configuration from file"""
    global _config_manager
    _config_manager = None
    return get_config_manager()

# Example usage and testing
if __name__ == "__main__":
    # Test configuration manager
    config_manager = ConfigManager()
    
    print("=== Configuration Manager Test ===")
    print(f"Config loaded: {config_manager.get_status()['config_loaded']}")
    print(f"Enabled agents: {config_manager.get_enabled_agents()}")
    
    # Test getting specific configurations
    system_config = config_manager.get_system_config()
    print(f"System version: {system_config.version}")
    
    openai_config = config_manager.get_openai_config()
    print(f"OpenAI model: {openai_config.model}")
    
    # Test getting agent configurations
    learning_agent = config_manager.get_agent_config("learning_agent")
    if learning_agent:
        print(f"Learning agent enabled: {learning_agent.enabled}")
        print(f"Learning rate: {learning_agent.config.get('learning_rate')}")
    
    # Test configuration value access
    print(f"Max concurrent agents: {config_manager.get_config_value('system.max_concurrent_agents')}")
    
    # Test workspace paths
    paths = config_manager.get_workspace_paths()
    print(f"Research root: {paths['research_root']}")
    
    # Ensure directories
    config_manager.ensure_directories()
    
    print("Configuration manager test completed!")