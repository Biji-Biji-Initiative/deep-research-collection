#!/bin/bash

# Enhanced Grant Evaluation v3 Deep Research Executor
# Improved version with better content extraction and error handling

echo "🚀 Enhanced Grant Evaluation v3 Deep Research Executor"
echo "=" * 60
echo "Version: Enhanced v2.0"
echo "Improvements: Better content extraction, error handling, and monitoring"
echo ""

# Check if API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable is not set."
    echo ""
    echo "Please set your OpenAI API key before running:"
    echo "   export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "Then run this script again:"
    echo "   ./run_improved_research.sh"
    echo ""
    exit 1
fi

# Change to the scripts directory
cd "$(dirname "$0")/scripts"

echo "🔧 Starting Enhanced Research Executor..."
echo "📁 Working directory: $(pwd)"
echo "🗂️  Session will be saved to: ../results/{session_id}/"
echo ""

# Run the enhanced executor with Python
python3 improved_research_executor.py

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ Enhanced analysis completed successfully!"
    echo ""
    echo "📁 Check the results directory for comprehensive analysis:"
    echo "   📊 Main Analysis: results/{session_id}/analysis/EXTRACTED_ANALYSIS.md"  
    echo "   📈 Session Summary: results/{session_id}/ENHANCED_SESSION_SUMMARY.md"
    echo "   📊 Performance Data: results/{session_id}/analysis/performance_metrics.json"
    echo ""
    echo "🔄 Next steps:"
    echo "1. Review the extracted analysis for Grant Eval v3 insights"
    echo "2. Check performance metrics for optimization opportunities"
    echo "3. Use findings to implement system improvements"
else
    echo "❌ Enhanced analysis failed (exit code: $exit_code)"
    echo ""
    echo "🔧 Troubleshooting steps:"
    echo "1. Check the logs directory for detailed error information"
    echo "2. Verify your OpenAI API key has sufficient credits"
    echo "3. Ensure all file paths and permissions are correct"
    echo "4. Review the session logs for specific error messages"
fi

exit $exit_code