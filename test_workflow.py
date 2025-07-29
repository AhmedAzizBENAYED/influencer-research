#!/usr/bin/env python3
"""Test simplified workflow to isolate recursion issue."""

import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END, MessagesState

def simple_node(state: MessagesState):
    """Simple node that just returns a message."""
    return {
        "messages": [("assistant", "This is a simple test response")]
    }

def test_simple_workflow():
    """Test a minimal workflow."""
    try:
        print("Creating simple workflow...")
        
        # Create workflow
        workflow = StateGraph(MessagesState)
        workflow.add_node("simple", simple_node)
        workflow.add_edge(START, "simple")
        workflow.add_edge("simple", END)
        
        graph = workflow.compile()
        print("✅ Workflow compiled successfully")
        
        print("Testing workflow execution...")
        result = graph.invoke({
            "messages": [("user", "Hello test")]
        })
        print("✅ Workflow executed successfully")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    settings.validate()
    test_simple_workflow()