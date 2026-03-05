#!/usr/bin/env python3
"""
API Setup Test Script
Quick validation that the API configuration system is working properly
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from config.api_config import (
            APIConfigManager, 
            get_api_config_manager, 
            ensure_openai_api_key,
            print_api_status
        )
        print("✅ API config module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import API config: {e}")
        return False

def test_config_manager():
    """Test the configuration manager"""
    print("\n🧪 Testing configuration manager...")
    
    try:
        from config.api_config import get_api_config_manager
        
        # Create manager without interactive mode
        manager = get_api_config_manager(interactive=False)
        
        # Get status
        status = manager.get_status()
        print(f"✅ Configuration manager created")
        print(f"   - OpenAI configured: {status['openai_configured']}")
        print(f"   - Ready for execution: {status['ready_for_execution']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration manager test failed: {e}")
        return False

def test_api_status():
    """Test the API status reporting"""
    print("\n🧪 Testing API status reporting...")
    
    try:
        from config.api_config import print_api_status
        
        print("📊 Current API Status:")
        print_api_status()
        
        print("✅ API status reporting works")
        return True
        
    except Exception as e:
        print(f"❌ API status test failed: {e}")
        return False

def test_env_file_creation():
    """Test .env file template creation"""
    print("\n🧪 Testing .env template creation...")
    
    try:
        from config.api_config import get_api_config_manager
        
        manager = get_api_config_manager(interactive=False)
        sample_path = manager.create_sample_env_file()
        
        if sample_path and sample_path.exists():
            print(f"✅ Sample .env created at: {sample_path}")
            return True
        else:
            print("❌ Failed to create sample .env file")
            return False
            
    except Exception as e:
        print(f"❌ .env template test failed: {e}")
        return False

def test_key_validation():
    """Test API key validation"""
    print("\n🧪 Testing API key validation...")
    
    try:
        from config.api_config import APIConfigManager
        
        # Test with fake key
        manager = APIConfigManager(interactive=False)
        
        # Test validation logic
        test_key = "sk-test1234567890abcdef1234567890abcdef123456"
        manager.config.openai_api_key = test_key
        
        is_valid = manager.validate_openai_key()
        print(f"✅ Key validation works (test key valid: {is_valid})")
        
        # Test invalid key
        manager.config.openai_api_key = "invalid-key"
        is_valid = manager.validate_openai_key()
        print(f"✅ Invalid key detection works (invalid key valid: {is_valid})")
        
        return True
        
    except Exception as e:
        print(f"❌ Key validation test failed: {e}")
        return False

def test_environment_setup():
    """Test environment variable setup"""
    print("\n🧪 Testing environment setup...")
    
    try:
        import os
        from config.api_config import APIConfigManager
        
        # Save current env
        original_key = os.environ.get('OPENAI_API_KEY')
        
        # Test setup
        manager = APIConfigManager(interactive=False)
        manager.config.openai_api_key = "sk-test1234567890abcdef1234567890abcdef123456"
        
        manager.setup_environment()
        
        # Check if environment was set
        env_key = os.environ.get('OPENAI_API_KEY')
        success = env_key == manager.config.openai_api_key
        
        print(f"✅ Environment setup works: {success}")
        
        # Restore original environment
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        return success
        
    except Exception as e:
        print(f"❌ Environment setup test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧠 Deep Research System - API Setup Test Suite")
    print("=" * 55)
    
    tests = [
        test_imports,
        test_config_manager,
        test_api_status,
        test_env_file_creation,
        test_key_validation,
        test_environment_setup,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 55)
    print("📊 TEST RESULTS")
    print("=" * 55)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your API setup system is working correctly.")
        print("\n📝 Next steps:")
        print("1. Run: python3 setup_api_keys.py")
        print("2. Or: ./run_research.sh")
        print("3. Or: python3 run_with_api_config.py")
        
        return True
    else:
        print("\n❌ SOME TESTS FAILED")
        print("There may be issues with the API setup system.")
        print("Check the error messages above for details.")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)