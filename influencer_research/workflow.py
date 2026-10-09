"""LangGraph orchestration of the researcher -> verifier -> reporter loop."""

import os
from datetime import datetime
from functools import partial

from langgraph.graph import START, MessagesState, StateGraph

from influencer_research.agents import ResearchAgents, report_node, research_node, verify_node
from influencer_research.config import settings


class InfluencerResearchWorkflow:
    """Main workflow orchestrator for influencer research."""
    
    def __init__(self):
        self.agents = ResearchAgents()
        self.research_agent = self.agents.create_research_agent()
        self.verifier_agent = self.agents.create_verifier_agent()
        self.reporter_agent = self.agents.create_reporter_agent()
        self.graph = self._build_workflow()
    
    def _build_workflow(self):
        """Build the workflow graph."""
        workflow = StateGraph(MessagesState)
        
        # Add nodes with partial functions to inject agents
        workflow.add_node(
            "researcher", 
            partial(research_node, research_agent=self.research_agent)
        )
        workflow.add_node(
            "verifier_agent", 
            partial(verify_node, verifier_agent=self.verifier_agent)
        )
        workflow.add_node(
            "reporter", 
            partial(report_node, reporter_agent=self.reporter_agent)
        )
        
        # Only the entry edge is static: each node routes itself via Command(goto=...)
        workflow.add_edge(START, "researcher")
        
        return workflow.compile()
    
    def _save_report_safely(self, content: str, query: str, is_partial: bool = False) -> str:
        """Save the report under a timestamped name, falling back to the working directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

            filename = f"influencer_report_{timestamp}.md"
            report_file_path = os.path.join(settings.OUTPUT_DIR, filename)
            
            # Prepare content with metadata
            if is_partial:
                header = f"""# Influencer Research Report (Partial Results)
## Query: {query}
## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
## Status: Workflow interrupted - saving available results

---

"""
            else:
                header = f"""# Influencer Research Report
## Query: {query}
## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
            
            final_content = header + content.strip()
            
            # Write to file
            with open(report_file_path, "w", encoding="utf-8") as f:
                f.write(final_content + "\n")
            
            # Also save as the default filename for backwards compatibility
            default_path = os.path.join(settings.OUTPUT_DIR, "influencer_report.md")
            with open(default_path, "w", encoding="utf-8") as f:
                f.write(final_content + "\n")
            
            saved_path = os.path.abspath(report_file_path)
            print(f"💾 Report saved to: {saved_path}")
            print(f"💾 Also saved as: {os.path.abspath(default_path)}")
            
            return saved_path
            
        except Exception as e:
            print(f"⚠️ Error saving report: {e}")
            # Try to save to current directory as fallback
            try:
                fallback_path = f"influencer_report_fallback_{timestamp}.md"
                with open(fallback_path, "w", encoding="utf-8") as f:
                    f.write(content.strip() + "\n")
                print(f"💾 Fallback: Report saved to current directory: {os.path.abspath(fallback_path)}")
                return os.path.abspath(fallback_path)
            except Exception as e2:
                print(f"❌ Critical: Could not save report anywhere: {e2}")
                return ""
    
    def run_research(self, query: str) -> str:
        """Run the complete research workflow with enhanced progress tracking."""
        print("🔄 Starting multi-agent research workflow...")
        print("   👤 Researcher: Analyzing query and gathering data...")
        print("   🔍 Verifier: Will validate findings...")
        print("   📄 Reporter: Will generate final report...")
        print()
        
        events = self.graph.stream(
            {
                "messages": [
                    ("user", f"""
Research Query: {query}

Please conduct a comprehensive influencer research based on this query.
Follow your systematic research strategy:
1. Analyze the query to understand requirements
2. Develop a multi-phase search approach
3. Use all available tools to gather data
4. Provide detailed profiles with verified information
5. Include industry insights and recommendations

Remember to aim for 15-20 high-quality influencer profiles with verified contact information.
                """)
                ],
            },
            {"recursion_limit": settings.RECURSION_LIMIT},
        )
        
        final_result = None
        step_count = 0
        all_research_content = []  # Collect all research content
        reporter_executed = False
        
        try:
            for event in events:
                step_count += 1
                
                if 'researcher' in event:
                    content = event['researcher']['messages'][-1].content
                    print(f"🔍 Research Step {step_count}: {len(content)} characters generated")
                    
                    # Collect all research content
                    all_research_content.append(f"=== RESEARCH STEP {step_count} ===\n{content}\n")
                    
                    # Show progress indicators
                    if "FINAL ANSWER" in content:
                        print("✅ Research phase completed!")
                    else:
                        print("⏳ Continuing research...")
                        
                    final_result = content
                    
                elif 'verifier_agent' in event:
                    content = event['verifier_agent']['messages'][-1].content
                    print(f"🔍 Verification Step {step_count}: Checking data quality...")
                    
                    # Collect verification content too
                    all_research_content.append(f"=== VERIFICATION STEP {step_count} ===\n{content}\n")
                    
                    if "FINAL ANSWER" in content:
                        print("✅ Verification completed - data approved!")
                    else:
                        print("🔄 Requesting additional research...")
                        
                elif 'reporter' in event:
                    print(f"📄 Report Generation Step {step_count}: Creating final document...")
                    final_result = event['reporter']['messages'][-1].content
                    reporter_executed = True
                    
                    # Save the final report
                    self._save_report_safely(final_result, query, is_partial=False)
        
        except StopIteration:
            print("🔄 Workflow completed - generator finished")
        except RuntimeError as e:
            if "generator raised StopIteration" in str(e):
                print("🔄 Workflow completed - generator finished")
            else:
                raise
        except Exception as e:
            print(f"❌ Workflow error: {e}")
            print("🔄 Attempting to save partial results...")
        
        # Always persist something, even if the workflow failed midway
        if not reporter_executed:
            # Create a comprehensive report from all collected content
            if all_research_content:
                combined_content = "\n".join(all_research_content)
                self._save_report_safely(combined_content, query, is_partial=True)
            elif final_result:
                self._save_report_safely(final_result, query, is_partial=True)
            else:
                # Save an error report
                error_content = f"""# Influencer Research Report - Error
## Query: {query}
## Status: Workflow failed - No results generated

The research workflow encountered an error and could not generate results.
Please check your API keys and try again.

**Possible issues:**
- API rate limits exceeded
- Network connectivity problems
- Invalid API credentials
- Search query too complex

**Recommendations:**
1. Check your .env file for correct API keys
2. Try a simpler, more specific query
3. Wait a few minutes and try again
4. Check your internet connection
"""
                self._save_report_safely(error_content, query, is_partial=True)

        return final_result or "No results generated"
    
    def visualize_workflow(self):
        """Generate workflow visualization if possible."""
        try:
            from IPython.display import Image, display
            display(Image(self.graph.get_graph().draw_mermaid_png()))
        except Exception as e:
            print(f"Could not generate workflow visualization: {e}")
            print("Install IPython and graphviz for visualization support")
