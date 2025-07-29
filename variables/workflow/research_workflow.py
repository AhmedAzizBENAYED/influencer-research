"""Main workflow for influencer research."""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functools import partial
from langgraph.graph import StateGraph, START, END, MessagesState



from variables.agents.research_agents import ResearchAgents, research_node, verify_node, report_node
from src.config.settings import settings


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
        
        # Add edges
        workflow.add_edge(START, "researcher")
        
        return workflow.compile()
    
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
        
        for event in events:
            step_count += 1
            
            if 'researcher' in event:
                content = event['researcher']['messages'][-1].content
                print(f"🔍 Research Step {step_count}: {len(content)} characters generated")
                
                # Show progress indicators
                if "FINAL ANSWER" in content:
                    print("✅ Research phase completed!")
                else:
                    print("⏳ Continuing research...")
                    
                final_result = content
                
            elif 'verifier_agent' in event:
                content = event['verifier_agent']['messages'][-1].content
                print(f"🔍 Verification Step {step_count}: Checking data quality...")
                
                if "FINAL ANSWER" in content:
                    print("✅ Verification completed - data approved!")
                else:
                    print("🔄 Requesting additional research...")
                    
            elif 'reporter' in event:
                print(f"📄 Report Generation Step {step_count}: Creating final document...")
                final_result = event['reporter']['messages'][-1].content
        
        return final_result or "No results generated"
    
    def visualize_workflow(self):
        """Generate workflow visualization if possible."""
        try:
            from IPython.display import Image, display
            display(Image(self.graph.get_graph().draw_mermaid_png()))
        except Exception as e:
            print(f"Could not generate workflow visualization: {e}")
            print("Install IPython and graphviz for visualization support")