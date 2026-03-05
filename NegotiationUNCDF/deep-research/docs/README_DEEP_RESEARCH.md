# Deep Research Setup for UNCDF Document Analysis

This setup provides a comprehensive deep research analysis system using OpenAI's Deep Research API to analyze your converted markdown documents.

## 🎯 Overview

The system is designed to:
- Automatically discover and categorize your converted markdown files
- Set up specialized research sessions for different types of analysis
- Execute deep research on technical proposals, organizational capacity, and GEDSI strategies
- Generate comprehensive evaluation reports and recommendations

## 📁 Files Created

1. **`deep_research_setup.py`** - Main setup script that creates research sessions
2. **`execute_deep_research.py`** - Complete workflow execution script
3. **`deep_research_config.json`** - Configuration file (generated during setup)
4. **`research_results/`** - Output directory for analysis results

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r tools/requirements.txt
```

### 2. Run the Setup

```bash
python -m deep_research.deep_research_setup
```

This will:
- Discover all markdown files in your workspace
- Create research sessions in OpenAI
- Generate configuration files
- Set up the analysis framework

### 3. Execute Deep Research

```bash
python -m deep_research.execute_deep_research
```

This will:
- Run the complete analysis workflow
- Monitor progress in real-time
- Save results to the `research_results/` directory

## 🔧 Configuration

### Research Sessions

The system creates three specialized research sessions:

1. **Technical Proposal Evaluation Analysis**
   - Focus: Technical approach, team qualifications, methodology
   - Documents: Technical proposals, CVs, project strategies

2. **Organizational Capacity Assessment**
   - Focus: Organizational structure, policies, performance
   - Documents: Company profiles, financial statements, policies

3. **GEDSI Strategy Deep Dive**
   - Focus: Gender equality, disability, social inclusion
   - Documents: GEDSI strategies, inclusion policies

### Analysis Questions

Each session uses specialized analysis questions:

- **Comprehensive Evaluation**: Technical competence, team capability, risk assessment
- **Comparative Analysis**: Strengths comparison, risk profiling, capacity benchmarking
- **Recommendations**: Selection criteria, due diligence, monitoring frameworks

## 📊 Document Discovery

The system automatically discovers and categorizes documents:

- **Technical Proposals**: Technical strategies, methodologies, approaches
- **CV Documents**: Personnel qualifications, team experience
- **Organizational Docs**: Company policies, financial statements, structures
- **GEDSI Strategies**: Gender equality, inclusion, social impact
- **References**: Past performance, project completion certificates
- **Certificates**: Approvals, registrations, statements

## 🔍 How It Works

### Phase 1: Setup
1. Initialize OpenAI client with your API key
2. Create research sessions with specialized instructions
3. Discover and categorize all markdown documents
4. Map documents to appropriate research sessions

### Phase 2: Analysis
1. Add documents to research sessions
2. Execute research with specific analysis questions
3. Monitor progress in real-time
4. Retrieve completed results

### Phase 3: Output
1. Generate detailed JSON results
2. Create markdown summary reports
3. Save configuration for reference
4. Organize outputs by timestamp

## 📋 Output Structure

```
research_results/
├── deep_research_results_YYYYMMDD_HHMMSS.json
├── research_summary_YYYYMMDD_HHMMSS.md
└── research_config_YYYYMMDD_HHMMSS.json
```

### Results Format

- **Detailed Results**: Complete OpenAI API responses with analysis
- **Summary Report**: Human-readable markdown with session status and focus areas
- **Configuration**: Reference copy of the research setup

## ⚙️ Customization

### Modify Analysis Questions

Edit the `create_research_configuration()` function in `deep_research_setup.py` to customize:

- Research session descriptions
- Focus areas for each session
- Analysis questions and evaluation criteria

### Add New Document Categories

Modify the `categorize_document()` function in `execute_deep_research.py` to:

- Add new document types
- Customize categorization logic
- Map categories to research sessions

### Adjust Research Instructions

Modify the `setup_research_session()` method to customize:

- Expert role descriptions
- Analysis requirements
- Output format specifications

## 🔒 Security Notes

- Your OpenAI API key is stored in the setup script
- Consider using environment variables for production use
- Results are saved locally in the `research_results/` directory
- No sensitive data is transmitted beyond OpenAI's API

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify your OpenAI API key is correct
   - Ensure you have access to the Deep Research beta
   - Check your OpenAI account billing status

2. **Document Discovery Issues**
   - Verify markdown files exist in expected directories
   - Check file permissions and encoding
   - Ensure files have `.md` extensions

3. **Research Session Failures**
   - Check OpenAI API rate limits
   - Verify session creation permissions
   - Review API error messages for specific issues

### Debug Mode

Add debug logging by modifying the scripts:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Considerations

- **Document Size**: Large markdown files may take longer to process
- **API Limits**: Monitor OpenAI API usage and rate limits
- **Parallel Processing**: Research sessions run concurrently for efficiency
- **Timeout Settings**: Adjust `max_wait_time` in the execution script

## 🔄 Workflow Integration

This system integrates with your existing PDF-to-markdown conversion pipeline:

1. Convert PDFs to markdown using your existing tools
2. Run the deep research setup to analyze converted documents
3. Use results to inform evaluation decisions
4. Iterate on analysis questions based on findings

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review OpenAI's Deep Research documentation
3. Verify your API key and permissions
4. Check the generated logs and error messages

## 🎉 Next Steps

After running the analysis:

1. **Review Results**: Examine the generated reports and insights
2. **Refine Questions**: Modify analysis questions based on initial findings
3. **Iterate**: Run additional research sessions with refined criteria
4. **Integrate**: Use insights to inform your evaluation process
5. **Automate**: Schedule regular analysis runs as new documents are converted

---

**Note**: This system requires access to OpenAI's Deep Research beta. Ensure you have the necessary permissions before running the analysis.
