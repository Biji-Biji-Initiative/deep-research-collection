#!/bin/bash

# Enhanced Deep Research System Runner
# Provides comprehensive API key management and execution options

set -e  # Exit on any error

echo "🧠 Deep Research System - Enhanced Runner"
echo "=========================================="
echo

# Check if we're in the right directory
if [ ! -f "setup_api_keys.py" ]; then
    echo "❌ Error: Please run this script from the deep research directory"
    echo "Expected files: setup_api_keys.py, run_with_api_config.py"
    exit 1
fi

# Function to check if API key is set
check_api_key() {
    if [ ! -z "$OPENAI_API_KEY" ]; then
        echo "✅ OPENAI_API_KEY is set in environment"
        return 0
    fi
    
    # Check ~/.env file
    if [ -f "$HOME/.env" ] && grep -q "OPENAI_API_KEY=" "$HOME/.env"; then
        echo "✅ OPENAI_API_KEY found in ~/.env"
        return 0
    fi
    
    # Check local .env file
    if [ -f ".env" ] && grep -q "OPENAI_API_KEY=" ".env"; then
        echo "✅ OPENAI_API_KEY found in local .env"
        return 0
    fi
    
    echo "❌ OPENAI_API_KEY not found"
    return 1
}

# Function to show menu
show_menu() {
    echo "🔧 Available Options:"
    echo "1. Setup API keys (interactive)"
    echo "2. Check API configuration status"
    echo "3. Run deep research (with auto API setup)"
    echo "4. Run deep research (expert mode - assumes API key ready)"
    echo "5. Create .env template"
    echo "6. Exit"
    echo
}

# Function to setup API keys
setup_api_keys() {
    echo "🔑 Setting up API keys..."
    python3 setup_api_keys.py
}

# Function to check API status
check_api_status() {
    echo "📊 Checking API configuration status..."
    python3 -c "
import sys
sys.path.insert(0, '.')
from config.api_config import print_api_status
print_api_status()
"
}

# Function to run research with auto setup
run_research_auto() {
    echo "🚀 Running deep research with automatic API setup..."
    python3 run_with_api_config.py
}

# Function to run research expert mode
run_research_expert() {
    if ! check_api_key; then
        echo "❌ API key not configured. Please run option 1 first."
        return 1
    fi
    
    echo "🚀 Running deep research in expert mode..."
    python3 run_with_api_config.py
}

# Function to create .env template
create_env_template() {
    echo "📄 Creating .env template..."
    python3 -c "
import sys
sys.path.insert(0, '.')
from config.api_config import get_api_config_manager
manager = get_api_config_manager()
manager.create_sample_env_file()
print('✅ Template created. Edit the .env files with your actual API keys.')
"
}

# Main execution
main() {
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not found"
        exit 1
    fi
    
    # Show initial status
    echo "🔍 Initial API Key Status:"
    if check_api_key; then
        echo
        echo "✅ API key is configured. You can proceed with option 3 or 4."
    else
        echo
        echo "❌ API key needs setup. Please use option 1 first."
    fi
    echo
    
    # Interactive menu
    while true; do
        show_menu
        read -p "Select an option (1-6): " choice
        echo
        
        case $choice in
            1)
                setup_api_keys
                echo
                ;;
            2)
                check_api_status
                echo
                ;;
            3)
                run_research_auto
                break
                ;;
            4)
                run_research_expert
                break
                ;;
            5)
                create_env_template
                echo
                ;;
            6)
                echo "👋 Goodbye!"
                exit 0
                ;;
            *)
                echo "❌ Invalid option. Please select 1-6."
                echo
                ;;
        esac
    done
}

# Handle command line arguments
if [ $# -eq 0 ]; then
    # Interactive mode
    main
else
    case "$1" in
        "setup")
            setup_api_keys
            ;;
        "status")
            check_api_status
            ;;
        "run")
            run_research_auto
            ;;
        "expert")
            run_research_expert
            ;;
        "template")
            create_env_template
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [option]"
            echo
            echo "Options:"
            echo "  setup     - Setup API keys interactively"
            echo "  status    - Check API configuration status"
            echo "  run       - Run deep research with auto setup"
            echo "  expert    - Run in expert mode (assumes key ready)"
            echo "  template  - Create .env template"
            echo "  help      - Show this help message"
            echo
            echo "If no option is provided, runs in interactive mode."
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "Use '$0 help' for usage information."
            exit 1
            ;;
    esac
fi