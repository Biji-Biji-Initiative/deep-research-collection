#!/usr/bin/env python3
"""
API Key Setup Script for Deep Research System
Interactive script to configure API keys for the research system
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.api_config import APIConfigManager, print_api_status

def main():
    """Main setup function"""
    print("🚀 Deep Research System - API Key Setup")
    print("=" * 50)
    
    # Check current status first
    print("\n📊 Current API Configuration Status:")
    manager = APIConfigManager(interactive=False)
    status = manager.get_status()
    
    print(f"OpenAI API Key: {'✅ Found' if status['openai_configured'] else '❌ Missing'}")
    print(f"Valid Format: {'✅ Yes' if status['openai_valid'] else '❌ No' if status['openai_configured'] else 'N/A'}")
    print(f"Ready for execution: {'✅ Yes' if status['ready_for_execution'] else '❌ No'}")
    
    if status['ready_for_execution']:
        print("\n🎉 Your system is already configured and ready to go!")
        choice = input("\nWould you like to continue with setup anyway? (y/n): ").strip().lower()
        if choice not in ['y', 'yes']:
            print("Setup cancelled.")
            return
    
    print("\n🔧 Setup Options:")
    print("1. Set up API key interactively")
    print("2. Create .env file template")
    print("3. Manual setup instructions")
    print("4. Test current configuration")
    print("5. Exit")
    
    while True:
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == '1':
            setup_interactive()
            break
        elif choice == '2':
            create_env_template()
            break
        elif choice == '3':
            show_manual_instructions()
            break
        elif choice == '4':
            test_configuration()
            break
        elif choice == '5':
            print("Setup cancelled.")
            return
        else:
            print("Invalid choice. Please select 1-5.")

def setup_interactive():
    """Interactive API key setup"""
    print("\n🔑 Interactive API Key Setup")
    print("-" * 30)
    
    # Create manager with interactive mode
    manager = APIConfigManager(interactive=True)
    
    # Check if we now have a key
    if manager.config.has_openai_key:
        print("\n✅ Setup completed successfully!")
        test_configuration_with_manager(manager)
    else:
        print("\n❌ Setup was not completed. Please try manual setup.")
        show_manual_instructions()

def create_env_template():
    """Create .env file templates"""
    print("\n📄 Creating .env File Templates")
    print("-" * 35)
    
    manager = APIConfigManager(interactive=False)
    
    # Create sample .env in project directory
    sample_path = manager.create_sample_env_file()
    if sample_path:
        print(f"✅ Sample .env file created at: {sample_path}")
    
    # Create .env template in home directory
    home_env_path = Path.home() / ".env"
    if not home_env_path.exists():
        try:
            with open(home_env_path, 'w') as f:
                f.write("# Global API Configuration\n")
                f.write("# Add your API keys here\n\n")
                f.write("OPENAI_API_KEY=your-openai-api-key-here\n")
            print(f"✅ Template .env file created at: {home_env_path}")
        except Exception as e:
            print(f"❌ Failed to create template in home directory: {e}")
    else:
        print(f"ℹ️  ~/.env already exists at: {home_env_path}")
    
    print("\n📝 Next Steps:")
    print("1. Edit the .env file with your actual API key")
    print("2. Replace 'your-openai-api-key-here' with your real OpenAI API key")
    print("3. Save the file and run this setup script again to test")

def show_manual_instructions():
    """Show manual setup instructions"""
    print("\n📖 Manual Setup Instructions")
    print("-" * 32)
    
    print("\n🔧 Method 1: Environment Variable (Recommended)")
    print("Add this to your shell profile (~/.bashrc, ~/.zshrc, etc.):")
    print("   export OPENAI_API_KEY='sk-your-actual-api-key-here'")
    print("Then restart your terminal or run: source ~/.bashrc")
    
    print("\n🔧 Method 2: Global .env File")
    print("Create or edit ~/.env file and add:")
    print("   OPENAI_API_KEY=sk-your-actual-api-key-here")
    
    print("\n🔧 Method 3: Project .env File")
    project_env = project_root / ".env"
    print(f"Create {project_env} with:")
    print("   OPENAI_API_KEY=sk-your-actual-api-key-here")
    
    print("\n🔧 Method 4: Temporary for Current Session")
    print("Run this command in your terminal (temporary):")
    print("   export OPENAI_API_KEY='sk-your-actual-api-key-here'")
    
    print("\n🔑 Getting Your OpenAI API Key:")
    print("1. Go to https://platform.openai.com/account/api-keys")
    print("2. Click 'Create new secret key'")
    print("3. Copy the key (starts with 'sk-')")
    print("4. Use it with one of the methods above")
    
    print("\n⚠️  Security Note:")
    print("- Never share your API key publicly")
    print("- Don't commit .env files to version control")
    print("- Rotate your keys regularly")

def test_configuration():
    """Test the current configuration"""
    print("\n🧪 Testing Current Configuration")
    print("-" * 33)
    
    manager = APIConfigManager(interactive=False)
    test_configuration_with_manager(manager)

def test_configuration_with_manager(manager):
    """Test configuration with a given manager"""
    status = manager.get_status()
    
    print(f"OpenAI API Key: {'✅ Found' if status['openai_configured'] else '❌ Missing'}")
    
    if status['openai_configured']:
        key = manager.get_openai_api_key()
        print(f"Key Preview: {key[:8]}...{key[-4:] if len(key) > 12 else '***'}")
        print(f"Key Length: {len(key)} characters")
        print(f"Format Valid: {'✅ Yes' if status['openai_valid'] else '❌ No'}")
        
        if status['openai_valid']:
            print("\n🎯 Testing API Connection...")
            if test_openai_connection(key):
                print("✅ API connection successful!")
                print("🚀 Your system is ready for deep research execution!")
            else:
                print("❌ API connection failed. Please check your key.")
        else:
            print("⚠️  Key format appears invalid. OpenAI keys should start with 'sk-'")
    else:
        print("❌ No OpenAI API key found.")
        print("Please run setup option 1 or follow manual instructions.")

def test_openai_connection(api_key: str) -> bool:
    """Test OpenAI API connection"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key, timeout=10)
        
        # Simple test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return True
        
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import openai
        return True
    except ImportError:
        print("❌ OpenAI library not found.")
        print("Please install it with: pip install openai")
        return False

if __name__ == "__main__":
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)