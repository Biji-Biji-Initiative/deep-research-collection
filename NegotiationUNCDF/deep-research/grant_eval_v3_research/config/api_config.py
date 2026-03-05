#!/usr/bin/env python3
"""
API Configuration Manager for Deep Research System
Handles API key loading from multiple sources with proper fallback mechanisms
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

@dataclass
class APIConfig:
    """API configuration container"""
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.strip())
    
    @property
    def has_any_key(self) -> bool:
        return self.has_openai_key or bool(self.gemini_api_key) or bool(self.anthropic_api_key)

class APIConfigManager:
    """
    Comprehensive API key management system
    
    Priority order for API key loading:
    1. Environment variables
    2. Local .env file (in project directory)
    3. Global .env file (in home directory)
    4. Config file in project
    5. Interactive prompt (if enabled)
    """
    
    def __init__(self, project_root: Optional[Path] = None, interactive: bool = False):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.interactive = interactive
        
        if project_root is None:
            project_root = Path(__file__).parent.parent
        self.project_root = Path(project_root)
        
        self.config = APIConfig()
        self.load_api_keys()
    
    def load_api_keys(self):
        """Load API keys from all available sources"""
        # 1. Environment variables (highest priority)
        self._load_from_environment()
        
        # 2. Local .env file in project
        self._load_from_local_env()
        
        # 3. Global .env file in home directory
        self._load_from_global_env()
        
        # 4. Project config file
        self._load_from_config_file()
        
        # 5. Interactive prompt (if enabled and still no key)
        if self.interactive and not self.config.has_openai_key:
            self._prompt_for_api_key()
        
        self._log_config_status()
    
    def _load_from_environment(self):
        """Load API keys from environment variables"""
        if not self.config.has_openai_key:
            self.config.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.config.gemini_api_key:
            self.config.gemini_api_key = os.getenv("GEMINI_API_KEY")
            
        if not self.config.anthropic_api_key:
            self.config.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if self.config.has_openai_key:
            self.logger.info("✅ OpenAI API key loaded from environment variable")
    
    def _load_from_local_env(self):
        """Load API keys from local .env file"""
        local_env_path = self.project_root / ".env"
        if local_env_path.exists() and not self.config.has_openai_key:
            self._load_env_file(local_env_path, "local .env file")
    
    def _load_from_global_env(self):
        """Load API keys from global .env file"""
        global_env_path = Path.home() / ".env"
        if global_env_path.exists() and not self.config.has_openai_key:
            self._load_env_file(global_env_path, "global .env file")
    
    def _load_env_file(self, env_path: Path, source_name: str):
        """Load API keys from a .env file"""
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            
                            if key == "OPENAI_API_KEY" and not self.config.has_openai_key:
                                self.config.openai_api_key = value
                                self.logger.info(f"✅ OpenAI API key loaded from {source_name}")
                            elif key == "GEMINI_API_KEY" and not self.config.gemini_api_key:
                                self.config.gemini_api_key = value
                            elif key == "ANTHROPIC_API_KEY" and not self.config.anthropic_api_key:
                                self.config.anthropic_api_key = value
        except Exception as e:
            self.logger.warning(f"Failed to load {source_name}: {e}")
    
    def _load_from_config_file(self):
        """Load API keys from project config file"""
        config_path = self.project_root / "config" / "api_keys.json"
        if config_path.exists() and not self.config.has_openai_key:
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    
                if not self.config.has_openai_key:
                    self.config.openai_api_key = config_data.get("openai_api_key")
                if not self.config.gemini_api_key:
                    self.config.gemini_api_key = config_data.get("gemini_api_key")
                if not self.config.anthropic_api_key:
                    self.config.anthropic_api_key = config_data.get("anthropic_api_key")
                
                if self.config.has_openai_key:
                    self.logger.info("✅ OpenAI API key loaded from config file")
            except Exception as e:
                self.logger.warning(f"Failed to load config file: {e}")
    
    def _prompt_for_api_key(self):
        """Interactively prompt for API key"""
        try:
            print("\n🔑 OpenAI API Key Required")
            print("No OpenAI API key found in environment or config files.")
            print("Please enter your OpenAI API key to continue:")
            
            api_key = input("OpenAI API Key: ").strip()
            if api_key:
                self.config.openai_api_key = api_key
                
                # Offer to save it
                save_choice = input("\nWould you like to save this key to ~/.env? (y/n): ").strip().lower()
                if save_choice in ['y', 'yes']:
                    self._save_to_global_env(api_key)
                    
                self.logger.info("✅ OpenAI API key provided interactively")
        except KeyboardInterrupt:
            print("\n❌ API key input cancelled")
        except Exception as e:
            self.logger.error(f"Failed to get API key interactively: {e}")
    
    def _save_to_global_env(self, api_key: str):
        """Save API key to global .env file"""
        try:
            env_path = Path.home() / ".env"
            
            # Read existing content
            existing_lines = []
            if env_path.exists():
                with open(env_path, 'r') as f:
                    existing_lines = f.readlines()
            
            # Check if OPENAI_API_KEY already exists
            has_openai_line = any(line.strip().startswith('OPENAI_API_KEY=') for line in existing_lines)
            
            if not has_openai_line:
                with open(env_path, 'a') as f:
                    if existing_lines and not existing_lines[-1].endswith('\n'):
                        f.write('\n')
                    f.write(f'OPENAI_API_KEY={api_key}\n')
                    
                self.logger.info(f"✅ API key saved to {env_path}")
            else:
                self.logger.info("API key line already exists in ~/.env")
                
        except Exception as e:
            self.logger.error(f"Failed to save API key to ~/.env: {e}")
    
    def _log_config_status(self):
        """Log the current configuration status"""
        if self.config.has_openai_key:
            key_preview = f"{self.config.openai_api_key[:8]}..." if len(self.config.openai_api_key) > 8 else "***"
            self.logger.info(f"✅ OpenAI API key configured: {key_preview}")
        else:
            self.logger.warning("❌ No OpenAI API key found")
            
        if self.config.gemini_api_key:
            self.logger.info("✅ Gemini API key available")
            
        if self.config.anthropic_api_key:
            self.logger.info("✅ Anthropic API key available")
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get the OpenAI API key"""
        return self.config.openai_api_key
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider"""
        provider_lower = provider.lower()
        if provider_lower in ['openai', 'gpt']:
            return self.config.openai_api_key
        elif provider_lower in ['gemini', 'google']:
            return self.config.gemini_api_key
        elif provider_lower in ['anthropic', 'claude']:
            return self.config.anthropic_api_key
        return None
    
    def has_required_keys(self, providers: list = None) -> bool:
        """Check if required API keys are available"""
        if providers is None:
            providers = ['openai']
        
        for provider in providers:
            if not self.get_api_key(provider):
                return False
        return True
    
    def validate_openai_key(self) -> bool:
        """Validate OpenAI API key format"""
        if not self.config.has_openai_key:
            return False
        
        key = self.config.openai_api_key
        # OpenAI keys typically start with 'sk-' and are around 48-51 characters
        return key.startswith('sk-') and len(key) >= 40
    
    def setup_environment(self):
        """Set up environment variables for the current process"""
        if self.config.openai_api_key:
            os.environ['OPENAI_API_KEY'] = self.config.openai_api_key
            
        if self.config.gemini_api_key:
            os.environ['GEMINI_API_KEY'] = self.config.gemini_api_key
            
        if self.config.anthropic_api_key:
            os.environ['ANTHROPIC_API_KEY'] = self.config.anthropic_api_key
    
    def create_sample_env_file(self):
        """Create a sample .env file in the project directory"""
        sample_env_path = self.project_root / ".env.sample"
        
        sample_content = """# API Configuration for Deep Research System
# Copy this file to .env and add your actual API keys

# OpenAI API Key (required for GPT models)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Google Gemini API Key (optional, for Gemini models)
GEMINI_API_KEY=your-gemini-api-key-here

# Anthropic API Key (optional, for Claude models)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Additional configuration
DEBUG=false
VERBOSE=true
"""
        
        try:
            with open(sample_env_path, 'w') as f:
                f.write(sample_content)
            self.logger.info(f"✅ Sample .env file created at {sample_env_path}")
            return sample_env_path
        except Exception as e:
            self.logger.error(f"Failed to create sample .env file: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of API configuration"""
        return {
            "openai_configured": self.config.has_openai_key,
            "openai_valid": self.validate_openai_key(),
            "gemini_configured": bool(self.config.gemini_api_key),
            "anthropic_configured": bool(self.config.anthropic_api_key),
            "sources_checked": [
                "environment_variables",
                "local_env_file",
                "global_env_file", 
                "config_file"
            ],
            "ready_for_execution": self.config.has_openai_key and self.validate_openai_key()
        }

# Global instance
_api_config_manager = None

def get_api_config_manager(interactive: bool = False) -> APIConfigManager:
    """Get global API configuration manager instance"""
    global _api_config_manager
    if _api_config_manager is None:
        _api_config_manager = APIConfigManager(interactive=interactive)
    return _api_config_manager

def get_openai_api_key() -> Optional[str]:
    """Quick function to get OpenAI API key"""
    return get_api_config_manager().get_openai_api_key()

def ensure_openai_api_key(interactive: bool = True) -> str:
    """Ensure OpenAI API key is available, prompt if necessary"""
    manager = get_api_config_manager(interactive=interactive)
    api_key = manager.get_openai_api_key()
    
    if not api_key:
        raise RuntimeError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or run with interactive mode.")
    
    if not manager.validate_openai_key():
        raise RuntimeError("OpenAI API key format appears invalid. Please check your key.")
    
    # Set environment variable for child processes
    manager.setup_environment()
    
    return api_key

# Command-line utility functions
def print_api_status():
    """Print comprehensive API configuration status"""
    manager = get_api_config_manager()
    status = manager.get_status()
    
    print("\n🔧 API Configuration Status")
    print("=" * 40)
    
    print(f"OpenAI API Key: {'✅ Configured' if status['openai_configured'] else '❌ Not found'}")
    if status['openai_configured']:
        print(f"  Validation: {'✅ Valid format' if status['openai_valid'] else '⚠️ Invalid format'}")
    
    print(f"Gemini API Key: {'✅ Configured' if status['gemini_configured'] else '❌ Not found'}")
    print(f"Anthropic API Key: {'✅ Configured' if status['anthropic_configured'] else '❌ Not found'}")
    
    print(f"\nReady for execution: {'✅ Yes' if status['ready_for_execution'] else '❌ No'}")
    
    if not status['ready_for_execution']:
        print("\n📝 To fix this:")
        print("1. Set environment variable: export OPENAI_API_KEY=your_key_here")
        print("2. Or create ~/.env file with: OPENAI_API_KEY=your_key_here")
        print("3. Or run with interactive mode to be prompted")

if __name__ == "__main__":
    # Test the API configuration system
    print("Testing API Configuration Manager...")
    
    # Test with interactive mode disabled
    manager = APIConfigManager(interactive=False)
    status = manager.get_status()
    
    print(f"OpenAI Key Configured: {status['openai_configured']}")
    print(f"Ready for execution: {status['ready_for_execution']}")
    
    # Create sample .env file
    sample_path = manager.create_sample_env_file()
    if sample_path:
        print(f"Sample .env created at: {sample_path}")
    
    # Print status
    print_api_status()