#!/usr/bin/env python3
"""
Deep Research Execution Script for UNCDF Document Analysis
This script orchestrates the complete deep research workflow
"""

import json
import time
import os
from datetime import datetime
from deep_research.deep_research_setup import DeepResearchAnalyzer

class DeepResearchExecutor:
    def __init__(self, config_file: str = "deep_research_config.json"):
        """Initialize the executor with configuration"""
        self.config_file = config_file
        self.config = self.load_config()
        self.analyzer = None
        self.research_runs = {}
        
    def load_config(self) -> dict:
        """Load the research configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {self.config_file}")
            print("Please run the setup script first: python -m deep_research.deep_research_setup")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing configuration: {e}")
            return None
    
    def initialize_analyzer(self, api_key: str):
        """Initialize the OpenAI analyzer"""
        try:
            self.analyzer = DeepResearchAnalyzer(api_key)
            print("✅ OpenAI analyzer initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing analyzer: {e}")
            return False
    
    def discover_and_categorize_documents(self) -> dict:
        """Discover and categorize all available markdown documents"""
        print("\n📁 Discovering and categorizing documents...")
        
        document_categories = {
            "technical_proposals": [],
            "cv_documents": [],
            "organizational_docs": [],
            "gedsi_strategies": [],
            "references": [],
            "certificates": []
        }
        
        workspace_root = self.config["workspace_root"]
        
        # Search for documents in all project directories
        for project_dir in os.listdir(workspace_root):
            project_path = os.path.join(workspace_root, project_dir)
            if not os.path.isdir(project_path):
                continue
                
            print(f"   📂 Scanning {project_dir}...")
            
            # Look for markdown files in various subdirectories
            search_paths = [
                os.path.join(project_path, "Requirement Attachments", "Documents to be submitted"),
                os.path.join(project_path, "Requirement Attachments", "Technical evaluation"),
                os.path.join(project_path, "output", "md", "clean"),
                os.path.join(project_path, "output", "md", "raw")
            ]
            
            for search_path in search_paths:
                if os.path.exists(search_path):
                    for file in os.listdir(search_path):
                        if file.endswith('.md'):
                            file_path = os.path.join(search_path, file)
                            
                            # Categorize based on filename and content
                            category = self.categorize_document(file, file_path)
                            if category:
                                document_categories[category].append({
                                    "path": file_path,
                                    "project": project_dir,
                                    "filename": file,
                                    "size": os.path.getsize(file_path)
                                })
        
        # Print summary
        total_docs = sum(len(docs) for docs in document_categories.values())
        print(f"\n📊 Document Discovery Summary:")
        print(f"   Total documents found: {total_docs}")
        for category, docs in document_categories.items():
            if docs:
                print(f"   {category.replace('_', ' ').title()}: {len(docs)} documents")
        
        return document_categories
    
    def categorize_document(self, filename: str, filepath: str) -> str:
        """Categorize a document based on filename and content analysis"""
        filename_lower = filename.lower()
        
        # CV and personnel documents
        if any(keyword in filename_lower for keyword in ['cv', 'resume', 'personnel', 'team']):
            return "cv_documents"
        
        # GEDSI strategies
        if any(keyword in filename_lower for keyword in ['gedsi', 'gender', 'inclusion', 'equality']):
            return "gedsi_strategies"
        
        # Technical proposals
        if any(keyword in filename_lower for keyword in ['technical', 'proposal', 'strategy', 'approach']):
            return "technical_proposals"
        
        # References and past performance
        if any(keyword in filename_lower for keyword in ['reference', 'performance', 'project', 'completion']):
            return "references"
        
        # Certificates and registrations
        if any(keyword in filename_lower for keyword in ['certificate', 'registration', 'approval', 'statement']):
            return "certificates"
        
        # Organizational documents
        if any(keyword in filename_lower for keyword in ['policy', 'financial', 'organizational', 'company']):
            return "organizational_docs"
        
        # Default to technical proposals if uncertain
        return "technical_proposals"
    
    def setup_research_sessions(self) -> bool:
        """Set up all configured research sessions"""
        if not self.analyzer:
            print("❌ Analyzer not initialized")
            return False
            
        print("\n🚀 Setting up research sessions...")
        
        for session_key, session_config in self.config["research_sessions"].items():
            print(f"   📋 Setting up: {session_config['name']}")
            
            session_id = self.analyzer.setup_research_session(
                session_config["name"],
                session_config["description"]
            )
            
            if session_id:
                self.config["research_sessions"][session_key]["session_id"] = session_id
                print(f"      ✅ Session ID: {session_id}")
            else:
                print(f"      ❌ Failed to create session")
                return False
        
        return True
    
    def add_documents_to_sessions(self, document_categories: dict) -> bool:
        """Add documents to appropriate research sessions"""
        if not self.analyzer:
            print("❌ Analyzer not initialized")
            return False
            
        print("\n📚 Adding documents to research sessions...")
        
        # Map document categories to research sessions
        session_mapping = {
            "technical_proposals": "technical_evaluation",
            "cv_documents": "technical_evaluation",
            "organizational_docs": "organizational_assessment",
            "gedsi_strategies": "gedsi_strategy_analysis",
            "references": "organizational_assessment",
            "certificates": "organizational_assessment"
        }
        
        for category, docs in document_categories.items():
            if not docs:
                continue
                
            target_session = session_mapping.get(category, "technical_evaluation")
            print(f"   📁 Adding {len(docs)} {category} documents to {target_session}")
            
            # Get document paths
            doc_paths = [doc["path"] for doc in docs]
            
            # Add documents to session
            success = self.analyzer.add_documents_to_session(target_session, doc_paths)
            if not success:
                print(f"      ❌ Failed to add documents to {target_session}")
                return False
        
        return True
    
    def execute_research_analysis(self) -> dict:
        """Execute the research analysis for all sessions"""
        if not self.analyzer:
            print("❌ Analyzer not initialized")
            return {}
            
        print("\n🔍 Executing research analysis...")
        
        for session_key, session_config in self.config["research_sessions"].items():
            if "session_id" not in session_config:
                print(f"   ⚠️  Skipping {session_key} - no session ID")
                continue
                
            print(f"   🚀 Starting analysis for: {session_config['name']}")
            
            # Get the appropriate research question
            question_key = "comprehensive_evaluation"  # Default question
            if "gedsi" in session_key:
                question_key = "comprehensive_evaluation"
            elif "organizational" in session_key:
                question_key = "comprehensive_evaluation"
            
            research_question = self.config["analysis_questions"][question_key]
            
            # Start research
            run_id = self.analyzer.start_research(session_key, research_question)
            if run_id:
                self.research_runs[session_key] = {
                    "run_id": run_id,
                    "started_at": datetime.now().isoformat(),
                    "status": "started"
                }
                print(f"      ✅ Research started: {run_id}")
            else:
                print(f"      ❌ Failed to start research")
        
        return self.research_runs
    
    def monitor_research_progress(self, max_wait_time: int = 3600) -> dict:
        """Monitor the progress of research runs"""
        if not self.research_runs:
            print("❌ No research runs to monitor")
            return {}
            
        print(f"\n⏳ Monitoring research progress (max wait: {max_wait_time}s)...")
        
        start_time = time.time()
        completed_runs = {}
        
        while time.time() - start_time < max_wait_time:
            all_completed = True
            
            for session_key, run_info in self.research_runs.items():
                if run_info["status"] == "completed":
                    continue
                    
                all_completed = False
                status = self.analyzer.get_research_status(session_key, run_info["run_id"])
                
                if status.get("status") == "completed":
                    run_info["status"] = "completed"
                    run_info["completed_at"] = datetime.now().isoformat()
                    completed_runs[session_key] = run_info
                    print(f"   ✅ {session_key}: Research completed!")
                elif status.get("status") == "failed":
                    run_info["status"] = "failed"
                    run_info["error"] = status.get("error", "Unknown error")
                    print(f"   ❌ {session_key}: Research failed - {run_info['error']}")
                else:
                    print(f"   ⏳ {session_key}: {status.get('status', 'Unknown status')}")
            
            if all_completed:
                break
                
            print("   🔄 Waiting 30 seconds before next check...")
            time.sleep(30)
        
        if not all_completed:
            print(f"   ⏰ Timeout reached. Some research runs may still be in progress.")
        
        return completed_runs
    
    def retrieve_research_results(self, completed_runs: dict) -> dict:
        """Retrieve results from completed research runs"""
        if not completed_runs:
            print("❌ No completed research runs to retrieve results from")
            return {}
            
        print("\n📊 Retrieving research results...")
        
        results = {}
        for session_key, run_info in completed_runs.items():
            if run_info["status"] != "completed":
                continue
                
            print(f"   📋 Retrieving results for: {session_key}")
            
            try:
                result_data = self.analyzer.get_research_results(session_key, run_info["run_id"])
                results[session_key] = result_data
                
                if result_data.get("status") == "completed":
                    print(f"      ✅ Results retrieved successfully")
                else:
                    print(f"      ⚠️  Results not ready: {result_data.get('message', 'Unknown')}")
                    
            except Exception as e:
                print(f"      ❌ Error retrieving results: {e}")
                results[session_key] = {"error": str(e)}
        
        return results
    
    def save_results(self, results: dict, output_dir: str = "research_results"):
        """Save research results to files"""
        if not results:
            print("❌ No results to save")
            return
            
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n💾 Saving research results to {output_dir}/...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = os.path.join(output_dir, f"deep_research_results_{timestamp}.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"   📄 Detailed results: {results_file}")
        
        # Save summary report
        summary_file = os.path.join(output_dir, f"research_summary_{timestamp}.md")
        self.generate_summary_report(results, summary_file)
        print(f"   📋 Summary report: {summary_file}")
        
        # Save configuration for reference
        config_file = os.path.join(output_dir, f"research_config_{timestamp}.json")
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)
        print(f"   ⚙️  Configuration: {config_file}")
    
    def generate_summary_report(self, results: dict, output_file: str):
        """Generate a markdown summary report"""
        with open(output_file, 'w') as f:
            f.write("# Deep Research Analysis Summary Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Research Sessions\n\n")
            for session_key, session_config in self.config["research_sessions"].items():
                f.write(f"### {session_config['name']}\n")
                f.write(f"{session_config['description']}\n\n")
                
                if session_key in results:
                    result = results[session_key]
                    if result.get("status") == "completed":
                        f.write("✅ **Status**: Completed\n")
                        f.write(f"📅 **Completed**: {result.get('completed_at', 'Unknown')}\n")
                    else:
                        f.write(f"⚠️ **Status**: {result.get('status', 'Unknown')}\n")
                        if result.get("error"):
                            f.write(f"❌ **Error**: {result['error']}\n")
                else:
                    f.write("⏳ **Status**: Not started\n")
                
                f.write("\n**Focus Areas**:\n")
                for area in session_config["focus_areas"]:
                    f.write(f"- {area}\n")
                f.write("\n---\n\n")
            
            f.write("## Analysis Questions\n\n")
            for question_key, question in self.config["analysis_questions"].items():
                f.write(f"### {question_key.replace('_', ' ').title()}\n")
                f.write(f"{question.strip()}\n\n")
    
    def run_complete_workflow(self, api_key: str, max_wait_time: int = 3600):
        """Run the complete deep research workflow"""
        print("🎯 Starting Complete Deep Research Workflow")
        print("=" * 60)
        
        # Step 1: Initialize
        if not self.initialize_analyzer(api_key):
            return False
        
        # Step 2: Discover documents
        document_categories = self.discover_and_categorize_documents()
        if not document_categories:
            print("❌ No documents found for analysis")
            return False
        
        # Step 3: Setup sessions
        if not self.setup_research_sessions():
            return False
        
        # Step 4: Add documents
        if not self.add_documents_to_sessions(document_categories):
            return False
        
        # Step 5: Execute research
        research_runs = self.execute_research_analysis()
        if not research_runs:
            print("❌ No research runs started")
            return False
        
        # Step 6: Monitor progress
        completed_runs = self.monitor_research_progress(max_wait_time)
        
        # Step 7: Retrieve results
        results = self.retrieve_research_results(completed_runs)
        
        # Step 8: Save results
        self.save_results(results)
        
        print("\n🎉 Deep Research Workflow Complete!")
        return True

def main():
    """Main execution function"""
    # Get API key from user
    api_key = input("Enter your OpenAI API key: ").strip()
    if not api_key:
        print("❌ API key is required")
        return
    
    # Initialize executor
    executor = DeepResearchExecutor()
    if not executor.config:
        return
    
    # Run the complete workflow
    success = executor.run_complete_workflow(api_key)
    
    if success:
        print("\n✅ Workflow completed successfully!")
        print("📁 Check the 'research_results' directory for outputs")
    else:
        print("\n❌ Workflow failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
