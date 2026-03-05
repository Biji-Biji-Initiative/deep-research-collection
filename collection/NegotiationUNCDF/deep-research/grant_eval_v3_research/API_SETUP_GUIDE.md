# API Key Setup Guide

## Deep Research System - API Key Management

This system provides comprehensive API key management with multiple fallback options to ensure your OpenAI API key is properly configured for the deep research system.

## 🚀 Quick Start

### Option 1: Interactive Setup (Recommended)
```bash
python3 setup_api_keys.py
```

### Option 2: Shell Script (Easiest)
```bash
./run_research.sh
```

### Option 3: Direct Execution
```bash
python3 run_with_api_config.py
```

## 🔑 API Key Configuration Methods

The system checks for your OpenAI API key in the following priority order:

### 1. Environment Variable (Highest Priority)
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

Add to your shell profile for persistence:
```bash
echo 'export OPENAI_API_KEY="sk-your-actual-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Local .env File
Create `.env` in the project directory:
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Global .env File
Create `~/.env` in your home directory:
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 4. Interactive Prompt
If no key is found, the system can prompt you interactively and optionally save it to `~/.env`.

## 🛠️ Setup Tools

### setup_api_keys.py
Interactive setup script with the following options:

1. **Interactive API Key Setup** - Prompts for your key and optionally saves it
2. **Create .env Template** - Creates template files you can edit
3. **Manual Setup Instructions** - Shows all configuration methods
4. **Test Configuration** - Validates your current setup

```bash
python3 setup_api_keys.py
```

### run_research.sh
Comprehensive shell script with menu options:

```bash
./run_research.sh              # Interactive menu
./run_research.sh setup        # Setup API keys
./run_research.sh status       # Check configuration
./run_research.sh run          # Run research with auto-setup
./run_research.sh expert       # Run assuming key is ready
./run_research.sh template     # Create .env template
```

## 📊 Configuration Status

Check your current API configuration:

```bash
python3 -c "from config.api_config import print_api_status; print_api_status()"
```

Output example:
```
🔧 API Configuration Status
========================================
OpenAI API Key: ✅ Configured
  Validation: ✅ Valid format
Gemini API Key: ❌ Not found
Anthropic API Key: ❌ Not found

Ready for execution: ✅ Yes
```

## 🔍 Getting Your OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Log in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Use it with any of the configuration methods above

## 🔧 API Configuration Manager

The system uses a sophisticated configuration manager that:

- **Multi-source loading**: Checks environment variables, multiple .env files, and config files
- **Format validation**: Ensures your API key format is correct
- **Interactive prompts**: Can ask for keys when missing
- **Automatic setup**: Sets environment variables for child processes
- **Comprehensive status**: Shows detailed configuration information

### Programmatic Usage

```python
from config.api_config import get_api_config_manager, ensure_openai_api_key

# Get API key (with automatic discovery)
api_key = ensure_openai_api_key(interactive=True)

# Check configuration status
manager = get_api_config_manager()
status = manager.get_status()
print(f"Ready: {status['ready_for_execution']}")
```

## 📁 File Structure

```
config/
├── api_config.py          # Core API configuration manager
└── config.yaml           # System configuration

setup_api_keys.py          # Interactive setup script
run_with_api_config.py     # Enhanced execution script
run_research.sh            # Shell script runner
API_SETUP_GUIDE.md        # This guide
```

## 🛡️ Security Best Practices

### DO:
- Store your API key in environment variables or .env files
- Add `.env` files to `.gitignore`
- Use different keys for development and production
- Rotate your API keys regularly
- Monitor your API usage on the OpenAI platform

### DON'T:
- Commit API keys to version control
- Share API keys in chat or email
- Use production keys in development
- Hardcode keys in source code

## 🔍 Troubleshooting

### "No OpenAI API key found"
1. Run `python3 setup_api_keys.py` for interactive setup
2. Or check that your key is properly set with `echo $OPENAI_API_KEY`
3. Verify your key format (should start with `sk-` and be 40+ characters)

### "API connection failed"
1. Verify your key is correct on the OpenAI platform
2. Check your internet connection
3. Ensure you have credits/billing set up in OpenAI
4. Try the key in a simple test script

### "Invalid key format"
1. OpenAI keys should start with `sk-`
2. Keys are typically 48-51 characters long
3. Make sure there are no extra spaces or quotes

### "Permission denied: ./run_research.sh"
```bash
chmod +x run_research.sh
```

## 🚀 Quick Test

Test your setup with a simple validation:

```bash
python3 -c "
from config.api_config import ensure_openai_api_key
try:
    key = ensure_openai_api_key(interactive=False)
    print('✅ API key configured successfully!')
except Exception as e:
    print(f'❌ Setup needed: {e}')
"
```

## 📝 Example Workflow

1. **First Time Setup:**
   ```bash
   python3 setup_api_keys.py
   # Follow interactive prompts to enter your key
   ```

2. **Run Research:**
   ```bash
   python3 run_with_api_config.py
   # System automatically uses your configured key
   ```

3. **Check Status Anytime:**
   ```bash
   ./run_research.sh status
   ```

## 🆘 Support

If you encounter issues:

1. Check this guide first
2. Run the interactive setup: `python3 setup_api_keys.py`
3. Test with: `./run_research.sh status`
4. Verify your API key on the OpenAI platform
5. Check the error logs in the `logs/` directory

The system is designed to be robust and helpful - it will guide you through resolving any configuration issues you encounter.