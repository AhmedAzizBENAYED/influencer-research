#!/usr/bin/env python3
"""Simple test to isolate the recursion issue."""

import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import settings
from variables.agents.research_agents import ResearchAgents

def test_simple_agent():
    """Test creating agents without workflow."""
    try:
        print("Testing agent creation...")
        agents = ResearchAgents()
        print("✅ ResearchAgents created successfully")
        
        print("Testing research agent creation...")
        research_agent = agents.create_research_agent()
        print("✅ Research agent created successfully")
        
        print("Testing simple invoke...")
        result = research_agent.invoke({
            "messages": [("user", "Hello, this is a test message")]
        })
        print("✅ Simple invoke successful")
        print(f"Result type: {type(result)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    settings.validate()
    test_simple_agent()