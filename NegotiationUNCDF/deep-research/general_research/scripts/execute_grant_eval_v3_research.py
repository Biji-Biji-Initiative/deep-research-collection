#!/usr/bin/env python3
"""
Execute Deep Research Analysis for Grant Evaluation v3 System
Uses OpenAI's o3-deep-research model for comprehensive system analysis
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List
from openai import OpenAI
from datetime import datetime

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WORKSPACE_ROOT = "/Users/agent-g/Downloads/NegotiationUNCDF"

class GrantEvalV3DeepResearch:
    def __init__(self, api_key: str):
        """Initialize the deep research analyzer with OpenAI API key"""
        self.client = OpenAI(api_key=api_key, timeout=3600)
        self.research_results = {}
        
    def create_vector_store(self, files: List[Path]) -> str:
        """Create a vector store for the grant evaluation v3 system files"""
        try:
            # Create vector store for analysis
            response = self.client.vector_stores.create(
                name="grant_eval_v3_analysis",
                metadata={
                    "purpose": "Grant Evaluation v3 system analysis",
                    "created_at": datetime.now().isoformat()
                }
            )
            vector_store_id = response.id
            print(f"✅ Created vector store: {vector_store_id}")
            
            # Add files to vector store
            for file_path in files:
                if file_path.exists() and file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Add file to vector store
                        self.client.vector_stores.files.create(
                            vector_store_id=vector_store_id,
                            file_id=self._upload_file(file_path, content)
                        )
                        print(f"   📄 Added: {file_path.name}")
                    except Exception as e:
                        print(f"   ⚠️  Skipped {file_path.name}: {e}")
                        continue
            
            return vector_store_id
            
        except Exception as e:
            print(f"❌ Error creating vector store: {e}")
            return None
    
    def _upload_file(self, file_path: Path, content: str) -> str:
        """Upload a file to OpenAI for vector store inclusion"""
        try:
            # Create a temporary file for upload
            temp_file = Path(f"/tmp/{file_path.name}")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Upload file to OpenAI
            with open(temp_file, 'rb') as f:
                response = self.client.files.create(
                    file=f,
                    purpose="assistants"
                )
            
            # Clean up temp file
            temp_file.unlink()
            
            return response.id
            
        except Exception as e:
            print(f"❌ Error uploading file {file_path.name}: {e}")
            return None
    
    def execute_deep_research(self, vector_store_id: str) -> Dict[str, Any]:
        """Execute deep research analysis using o3-deep-research model"""
        
        # Load the comprehensive research prompt
        prompt_file = Path(__file__).parent / "grant_eval_v3_deep_research_prompt.md"
        with open(prompt_file, 'r', encoding='utf-8') as f:
            research_prompt = f.read()
        
        # Create the research input
        research_input = f"""
{research_prompt}

## 🔍 EXECUTION INSTRUCTIONS

Please analyze the Grant Evaluation v3 system using the files provided in the vector store. 
Focus on the specific analysis requirements outlined above and provide structured findings.

Use the file search capabilities to examine:
1. Current implementation code in grant_eval_v3/evaluation/
2. Historical implementations in evaluation_agent/ and evaluation_agent_v2/
3. Supporting infrastructure and documentation
4. Implementation plans and specifications

Provide your analysis in the exact format specified in the research output format section.
"""
        
        try:
            print("🚀 Starting deep research analysis with o3-deep-research...")
            print("📋 Research prompt loaded and configured")
            print("🔍 This will take 10-30 minutes for comprehensive analysis...")
            
            # Execute deep research using o3-deep-research model
            response = self.client.responses.create(
                model="o3-deep-research",
                input=research_input,
                background=True,
                tools=[
                    {
                        "type": "file_search",
                        "vector_store_ids": [vector_store_id]
                    },
                    {
                        "type": "code_interpreter",
                        "container": {"type": "auto"}
                    }
                ]
            )
            
            print(f"✅ Deep research started successfully!")
            print(f"🆔 Response ID: {response.id}")
            print(f"📊 Status: {response.status}")
            
            return {
                "response_id": response.id,
                "status": response.status,
                "started_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error starting deep research: {e}")
            return {"error": str(e)}
    
    def monitor_research_progress(self, response_id: str, max_wait_time: int = 3600) -> Dict[str, Any]:
        """Monitor the progress of the deep research analysis"""
        print(f"\n⏳ Monitoring research progress (max wait: {max_wait_time}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # Check response status
                response = self.client.responses.retrieve(response_id)
                
                print(f"   📊 Status: {response.status}")
                
                if response.status == "completed":
                    print("   ✅ Research completed successfully!")
                    return {
                        "status": "completed",
                        "response_id": response_id,
                        "completed_at": datetime.now().isoformat()
                    }
                elif response.status == "failed":
                    print(f"   ❌ Research failed: {getattr(response, 'error', 'Unknown error')}")
                    return {
                        "status": "failed",
                        "response_id": response_id,
                        "error": getattr(response, 'error', 'Unknown error')
                    }
                elif response.status == "in_progress":
                    print("   🔄 Research in progress...")
                else:
                    print(f"   ⏳ Status: {response.status}")
                
                # Wait before next check
                print("   🔄 Waiting 60 seconds before next check...")
                time.sleep(60)
                
            except Exception as e:
                print(f"   ⚠️  Error checking status: {e}")
                time.sleep(60)
        
        print(f"   ⏰ Timeout reached. Research may still be in progress.")
        return {
            "status": "timeout",
            "response_id": response_id,
            "message": "Research timeout reached"
        }
    
    def retrieve_research_results(self, response_id: str) -> Dict[str, Any]:
        """Retrieve the completed research results"""
        try:
            print(f"\n📊 Retrieving research results...")
            
            # Get the response
            response = self.client.responses.retrieve(response_id)
            
            if response.status == "completed":
                # Get the results
                results = self.client.responses.retrieve_results(response_id)
                
                print("   ✅ Results retrieved successfully!")
                
                return {
                    "status": "completed",
                    "response_id": response_id,
                    "results": results,
                    "completed_at": datetime.now().isoformat()
                }
            else:
                print(f"   ⚠️  Research not complete: {response.status}")
                return {
                    "status": response.status,
                    "response_id": response_id,
                    "message": "Research not complete"
                }
                
        except Exception as e:
            print(f"   ❌ Error retrieving results: {e}")
            return {"error": str(e)}
    
    def save_results(self, results: Dict[str, Any], output_dir: str = "research_results"):
        """Save research results to files"""
        if not results:
            print("❌ No results to save")
            return
            
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n💾 Saving research results to {output_dir}/...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%HMM%S")
        
        # Save detailed results
        results_file = os.path.join(output_dir, f"grant_eval_v3_analysis_{timestamp}.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"   📄 Detailed results: {results_file}")
        
        # Save summary report
        summary_file = os.path.join(output_dir, f"grant_eval_v3_summary_{timestamp}.md")
        self._generate_summary_report(results, summary_file)
        print(f"   📋 Summary report: {summary_file}")
        
        # Save configuration for reference
        config_file = os.path.join(output_dir, f"research_config_{timestamp}.json")
        with open(config_file, 'w') as f:
            config = {
                "workspace_root": WORKSPACE_ROOT,
                "research_executed_at": timestamp,
                "model_used": "o3-deep-research",
                "files_analyzed": self._get_analyzed_files()
            }
            json.dump(config, f, indent=2, default=str)
        print(f"   ⚙️  Configuration: {config_file}")
    
    def _generate_summary_report(self, results: Dict[str, Any], output_file: str):
        """Generate a markdown summary report"""
        with open(output_file, 'w') as f:
            f.write("# Grant Evaluation v3 Deep Research Analysis Summary\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Research Execution\n\n")
            f.write(f"**Model Used**: o3-deep-research\n")
            f.write(f"**Response ID**: {results.get('response_id', 'Unknown')}\n")
            f.write(f"**Status**: {results.get('status', 'Unknown')}\n")
            f.write(f"**Completed**: {results.get('completed_at', 'Unknown')}\n\n")
            
            if results.get("results"):
                f.write("## Analysis Results\n\n")
                f.write("Deep research analysis completed successfully.\n")
                f.write("Check the detailed JSON results for comprehensive findings.\n\n")
            else:
                f.write("## Analysis Status\n\n")
                f.write(f"Research status: {results.get('status', 'Unknown')}\n")
                if results.get("error"):
                    f.write(f"Error: {results['error']}\n")
                if results.get("message"):
                    f.write(f"Message: {results['message']}\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. Review the detailed analysis results\n")
            f.write("2. Update the implementation tracker based on findings\n")
            f.write("3. Begin critical path implementation work\n")
            f.write("4. Schedule regular progress reviews\n")
    
    def _get_analyzed_files(self) -> List[str]:
        """Get list of files that were analyzed"""
        analyzed_files = []
        
        # Core v3 system files
        v3_files = [
            "grant_eval_v3/evaluation/skills/rubric_mining/",
            "grant_eval_v3/evaluation/agents/",
            "grant_eval_v3/evaluation/skills/retrieval/",
            "grant_eval_v3/evaluation/skills/scoring/",
            "grant_eval_v3/evaluation/infra/",
            "grant_eval_v3/docs/"
        ]
        
        # Historical implementation files
        historical_files = [
            "evaluation_agent/",
            "evaluation_agent_v2/"
        ]
        
        # Supporting infrastructure
        infrastructure_files = [
            "deep_research/",
            "evaluation_framework/",
            "conversion_engine/"
        ]
        
        analyzed_files.extend(v3_files)
        analyzed_files.extend(historical_files)
        analyzed_files.extend(infrastructure_files)
        
        return analyzed_files
    
    def run_complete_analysis(self, max_wait_time: int = 3600):
        """Run the complete deep research analysis workflow"""
        print("🎯 Starting Grant Evaluation v3 Deep Research Analysis")
        print("=" * 70)
        
        # Step 1: Identify files to analyze
        print("\n📁 Identifying files for analysis...")
        files_to_analyze = self._identify_analysis_files()
        
        if not files_to_analyze:
            print("❌ No files found for analysis")
            return False
        
        print(f"✅ Found {len(files_to_analyze)} files for analysis")
        
        # Step 2: Create vector store
        print("\n🔧 Creating vector store for analysis...")
        vector_store_id = self.create_vector_store(files_to_analyze)
        
        if not vector_store_id:
            print("❌ Failed to create vector store")
            return False
        
        # Step 3: Execute deep research
        print("\n🚀 Executing deep research analysis...")
        research_start = self.execute_deep_research(vector_store_id)
        
        if "error" in research_start:
            print(f"❌ Failed to start research: {research_start['error']}")
            return False
        
        # Step 4: Monitor progress
        print("\n⏳ Monitoring research progress...")
        progress = self.monitor_research_progress(
            research_start["response_id"], 
            max_wait_time
        )
        
        # Step 5: Retrieve results
        if progress.get("status") == "completed":
            print("\n📊 Retrieving research results...")
            results = self.retrieve_research_results(progress["response_id"])
            
            # Step 6: Save results
            self.save_results(results)
            
            print("\n🎉 Deep Research Analysis Complete!")
            print("📁 Check the 'research_results' directory for outputs")
            return True
        else:
            print(f"\n⚠️  Research did not complete: {progress.get('status', 'Unknown')}")
            if progress.get("error"):
                print(f"   Error: {progress['error']}")
            return False
    
    def _identify_analysis_files(self) -> List[Path]:
        """Identify files and directories to analyze"""
        files_to_analyze = []
        workspace_path = Path(WORKSPACE_ROOT)
        
        # Core v3 system files
        v3_paths = [
            "grant_eval_v3/evaluation/skills/rubric_mining/",
            "grant_eval_v3/evaluation/agents/",
            "grant_eval_v3/evaluation/skills/retrieval/",
            "grant_eval_v3/evaluation/skills/scoring/",
            "grant_eval_v3/evaluation/infra/",
            "grant_eval_v3/docs/",
            "grant_eval_v3/projects/",
            "grant_eval_v3/runs/"
        ]
        
        # Historical implementation files
        historical_paths = [
            "evaluation_agent/",
            "evaluation_agent_v2/"
        ]
        
        # Supporting infrastructure
        infrastructure_paths = [
            "deep_research/",
            "evaluation_framework/",
            "conversion_engine/"
        ]
        
        # Add all paths
        all_paths = v3_paths + historical_paths + infrastructure_paths
        
        for path_str in all_paths:
            path = workspace_path / path_str
            if path.exists():
                if path.is_dir():
                    # For directories, find all Python, Markdown, and text files
                    for file_path in path.rglob("*"):
                        if file_path.is_file() and file_path.suffix.lower() in ['.py', '.md', '.txt', '.csv', '.json', '.yaml', '.yml']:
                            files_to_analyze.append(file_path)
                else:
                    # For individual files, add them directly
                    files_to_analyze.append(path)
                print(f"   📂 {path_str}")
        
        return files_to_analyze

def main():
    """Main execution function"""
    print("🔍 Grant Evaluation v3 Deep Research Analysis")
    print("=" * 50)
    
    # Check API key
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY is not set. Export it in your environment before running.")
        print("   For example: export OPENAI_API_KEY=...\n")
        return
    
    # Initialize analyzer
    analyzer = GrantEvalV3DeepResearch(OPENAI_API_KEY)
    
    # Run complete analysis
    success = analyzer.run_complete_analysis()
    
    if success:
        print("\n✅ Analysis completed successfully!")
        print("📁 Check the 'research_results' directory for outputs")
        print("\nNext steps:")
        print("1. Review the analysis results")
        print("2. Update implementation tracker based on findings")
        print("3. Begin critical path implementation work")
    else:
        print("\n❌ Analysis failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
