#!/usr/bin/env python3
"""
Deep Research Setup for UNCDF Negotiation Documents Analysis
Uses OpenAI's Deep Research API to analyze converted markdown files
"""

import os
import json
import glob
from pathlib import Path
from typing import List, Dict, Any
import openai
from datetime import datetime

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WORKSPACE_ROOT = "/Users/agent-g/Downloads/NegotiationUNCDF"

class DeepResearchAnalyzer:
    def __init__(self, api_key: str):
        """Initialize the deep research analyzer with OpenAI API key"""
        self.client = openai.OpenAI(api_key=api_key)
        self.research_sessions = {}
        
    def setup_research_session(self, session_name: str, description: str) -> str:
        """Create a new research session for document analysis"""
        try:
            response = self.client.beta.research.create(
                name=session_name,
                description=description,
                instructions=f"""
                You are an expert document analyst specializing in:
                - Technical proposal evaluation
                - CV and personnel assessment
                - Project reference analysis
                - Organizational capacity evaluation
                - GEDSI (Gender Equality, Disability, and Social Inclusion) strategy review
                
                Analyze the provided documents thoroughly and provide:
                1. Executive summary of key findings
                2. Strengths and weaknesses assessment
                3. Risk factors and mitigation strategies
                4. Recommendations for evaluation
                5. Comparative analysis across documents
                """
            )
            session_id = response.id
            self.research_sessions[session_name] = session_id
            print(f"✅ Created research session: {session_name} (ID: {session_id})")
            return session_id
        except Exception as e:
            print(f"❌ Error creating research session: {e}")
            return None
    
    def add_documents_to_session(self, session_name: str, document_paths: List[str]) -> bool:
        """Add documents to a research session for analysis"""
        if session_name not in self.research_sessions:
            print(f"❌ Research session '{session_name}' not found")
            return False
            
        session_id = self.research_sessions[session_name]
        
        try:
            for doc_path in document_paths:
                if os.path.exists(doc_path):
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create document in the research session
                    response = self.client.beta.research.documents.create(
                        research_id=session_id,
                        content=content,
                        metadata={
                            "filename": os.path.basename(doc_path),
                            "filepath": doc_path,
                            "file_size": len(content),
                            "added_at": datetime.now().isoformat()
                        }
                    )
                    print(f"✅ Added document: {os.path.basename(doc_path)}")
                else:
                    print(f"⚠️  Document not found: {doc_path}")
                    
            return True
            
        except Exception as e:
            print(f"❌ Error adding documents to session: {e}")
            return False
    
    def start_research(self, session_name: str, research_question: str) -> str:
        """Start the research process with a specific question"""
        if session_name not in self.research_sessions:
            print(f"❌ Research session '{session_name}' not found")
            return None
            
        session_id = self.research_sessions[session_name]
        
        try:
            response = self.client.beta.research.run(
                research_id=session_id,
                question=research_question
            )
            run_id = response.id
            print(f"🚀 Started research run: {run_id}")
            print(f"📋 Research question: {research_question}")
            return run_id
            
        except Exception as e:
            print(f"❌ Error starting research: {e}")
            return None
    
    def get_research_status(self, session_name: str, run_id: str) -> Dict[str, Any]:
        """Check the status of a research run"""
        if session_name not in self.research_sessions:
            return {"error": "Session not found"}
            
        session_id = self.research_sessions[session_name]
        
        try:
            response = self.client.beta.research.runs.retrieve(
                research_id=session_id,
                run_id=run_id
            )
            return {
                "status": response.status,
                "created_at": response.created_at,
                "completed_at": response.completed_at,
                "error": getattr(response, 'error', None)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_research_results(self, session_name: str, run_id: str) -> Dict[str, Any]:
        """Retrieve the results of a completed research run"""
        if session_name not in self.research_sessions:
            return {"error": "Session not found"}
            
        session_id = self.research_sessions[session_name]
        
        try:
            response = self.client.beta.research.runs.retrieve(
                research_id=session_id,
                run_id=run_id
            )
            
            if response.status == "completed":
                # Get the research results
                results = self.client.beta.research.runs.retrieve_results(
                    research_id=session_id,
                    run_id=run_id
                )
                return {
                    "status": "completed",
                    "results": results,
                    "completed_at": response.completed_at
                }
            else:
                return {
                    "status": response.status,
                    "message": "Research is still in progress"
                }
                
        except Exception as e:
            return {"error": str(e)}

def discover_markdown_files(workspace_root: str) -> Dict[str, List[str]]:
    """Discover all markdown files in the workspace and categorize them"""
    markdown_files = {}
    
    # Search for markdown files in all project directories
    for project_dir in glob.glob(os.path.join(workspace_root, "*/")):
        project_name = os.path.basename(os.path.dirname(project_dir))
        
        # Look for markdown files in various subdirectories
        md_patterns = [
            "**/*.md",
            "**/Documents to be submitted/*.md",
            "**/Technical evaluation/*.md",
            "**/output/md/clean/*.md",
            "**/output/md/raw/*.md"
        ]
        
        project_md_files = []
        for pattern in md_patterns:
            files = glob.glob(os.path.join(project_dir, pattern), recursive=True)
            project_md_files.extend(files)
        
        if project_md_files:
            markdown_files[project_name] = project_md_files
    
    return markdown_files

def create_research_configuration(workspace_root: str) -> Dict[str, Any]:
    """Create a comprehensive research configuration"""
    config = {
        "workspace_root": workspace_root,
        "research_sessions": {
            "technical_evaluation": {
                "name": "Technical Proposal Evaluation Analysis",
                "description": "Deep analysis of technical proposals, CVs, and organizational capacity documents",
                "focus_areas": [
                    "Technical approach and methodology",
                    "Team qualifications and experience",
                    "Organizational capacity and track record",
                    "GEDSI strategy and implementation",
                    "Risk assessment and mitigation"
                ]
            },
            "organizational_assessment": {
                "name": "Organizational Capacity Assessment",
                "description": "Comprehensive evaluation of organizational structure, policies, and performance",
                "focus_areas": [
                    "Organizational structure and governance",
                    "Financial capacity and stability",
                    "Human resources and expertise",
                    "Quality management systems",
                    "Past performance and references"
                ]
            },
            "gedsi_strategy_analysis": {
                "name": "GEDSI Strategy Deep Dive",
                "description": "Specialized analysis of Gender Equality, Disability, and Social Inclusion strategies",
                "focus_areas": [
                    "GEDSI policy framework",
                    "Implementation strategies",
                    "Monitoring and evaluation approaches",
                    "Stakeholder engagement",
                    "Impact measurement"
                ]
            }
        },
        "analysis_questions": {
            "comprehensive_evaluation": """
            Based on the provided documents, provide a comprehensive evaluation that addresses:
            
            1. **Technical Competence**: Assess the technical approach, methodology, and innovation
            2. **Team Capability**: Evaluate the qualifications, experience, and expertise of proposed team members
            3. **Organizational Strength**: Analyze organizational capacity, structure, and track record
            4. **Risk Assessment**: Identify potential risks and proposed mitigation strategies
            5. **GEDSI Integration**: Evaluate the depth and quality of gender equality and social inclusion approaches
            6. **Value for Money**: Assess cost-effectiveness and efficiency of proposed solutions
            7. **Sustainability**: Evaluate long-term impact and sustainability considerations
            
            Provide specific examples from the documents to support your analysis.
            """,
            
            "comparative_analysis": """
            Conduct a comparative analysis across the different documents and organizations:
            
            1. **Strengths Comparison**: Identify and rank the strongest aspects of each proposal
            2. **Weaknesses Analysis**: Highlight areas of concern and improvement needs
            3. **Risk Profiling**: Compare risk levels and mitigation approaches
            4. **Innovation Assessment**: Evaluate innovative approaches and methodologies
            5. **Capacity Benchmarking**: Compare organizational and technical capacities
            6. **Best Practices**: Identify exemplary practices that could be replicated
            
            Provide a scoring matrix and detailed justification for each assessment.
            """,
            
            "recommendations": """
            Based on your analysis, provide actionable recommendations:
            
            1. **Selection Criteria**: Recommend key criteria for final selection
            2. **Due Diligence**: Suggest areas requiring additional investigation
            3. **Risk Mitigation**: Propose strategies to address identified risks
            4. **Capacity Building**: Recommend areas where organizations could improve
            5. **Monitoring Framework**: Suggest approaches for ongoing evaluation
            6. **Success Factors**: Identify key factors for successful implementation
            
            Prioritize recommendations by impact and feasibility.
            """
        }
    }
    
    return config

def main():
    """Main function to set up deep research analysis"""
    print("🔍 Setting up Deep Research Analysis for UNCDF Negotiation Documents")
    print("=" * 70)
    
    # Initialize the analyzer
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY is not set. Export it in your environment before running.")
        print("   For example: export OPENAI_API_KEY=...\n")
        return
    analyzer = DeepResearchAnalyzer(OPENAI_API_KEY)
    
    # Discover markdown files
    print("\n📁 Discovering markdown files...")
    md_files = discover_markdown_files(WORKSPACE_ROOT)
    
    if not md_files:
        print("❌ No markdown files found in the workspace")
        return
    
    print(f"✅ Found markdown files in {len(md_files)} project directories:")
    for project, files in md_files.items():
        print(f"   📂 {project}: {len(files)} files")
    
    # Create research configuration
    config = create_research_configuration(WORKSPACE_ROOT)
    
    # Set up research sessions
    print("\n🚀 Setting up research sessions...")
    for session_key, session_config in config["research_sessions"].items():
        session_id = analyzer.setup_research_session(
            session_config["name"],
            session_config["description"]
        )
        if session_id:
            config["research_sessions"][session_key]["session_id"] = session_id
    
    # Save configuration
    config_file = os.path.join(WORKSPACE_ROOT, "deep_research_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2, default=str)
    
    print(f"\n💾 Configuration saved to: {config_file}")
    
    # Create analysis script
    analysis_script = os.path.join(WORKSPACE_ROOT, "run_deep_research.py")
    with open(analysis_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""
Deep Research Execution Script
Run this script to execute the configured research sessions
"""

import json
import time
from deep_research.deep_research_setup import DeepResearchAnalyzer

def run_research_analysis():
    # Load configuration
    with open("deep_research_config.json", "r") as f:
        config = json.load(f)
    
    # Initialize analyzer
    analyzer = DeepResearchAnalyzer("YOUR_API_KEY_HERE")  # Replace with your actual API key
    
    # Run comprehensive evaluation
    print("🔍 Starting comprehensive evaluation...")
    run_id = analyzer.start_research(
        "technical_evaluation",
        config["analysis_questions"]["comprehensive_evaluation"]
    )
    
    if run_id:
        print(f"⏳ Research started with ID: {run_id}")
        print("📊 Monitor progress and retrieve results when complete")
    
    return run_id

if __name__ == "__main__":
    run_research_analysis()
''')
    
    print(f"📝 Analysis script created: {analysis_script}")
    
    print("\n🎯 Deep Research Setup Complete!")
    print("\nNext steps:")
    print("1. Review the configuration in 'deep_research_config.json'")
    print("2. Update the API key in 'run_deep_research.py'")
    print("3. Run 'python run_deep_research.py' to start analysis")
    print("4. Monitor progress and retrieve results")
    
    print(f"\n📊 Available research sessions:")
    for session_key, session_config in config["research_sessions"].items():
        print(f"   • {session_config['name']}")
        print(f"     Focus: {', '.join(session_config['focus_areas'])}")

if __name__ == "__main__":
    main()
