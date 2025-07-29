#!/usr/bin/env python3
"""Debug script to isolate the recursion issue."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from variables.workflow.research_workflow import InfluencerResearchWorkflow

def test_workflow():
    """Test the workflow with minimal input."""
    try:
        print("Creating workflow...")
        workflow = InfluencerResearchWorkflow()
        print("Workflow created successfully!")
        
        print("Testing simple query...")
        result = workflow.run_research("test query")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow()