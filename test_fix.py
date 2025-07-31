#!/usr/bin/env python3
"""Simple test to verify the StopIteration fix."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_stopiteration_fix():
    """Test that the StopIteration fix works."""
    try:
        print("Testing StopIteration fix...")
        
        # Import the workflow
        from variables.workflow.research_workflow import InfluencerResearchWorkflow
        
        print("✅ Workflow import successful")
        
        # Create workflow instance
        workflow = InfluencerResearchWorkflow()
        print("✅ Workflow instance created successfully")
        
        # Test with a simple query that should complete quickly
        print("🔍 Testing with simple query...")
        result = workflow.run_research("test simple query")
        
        print("✅ Test completed successfully!")
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(str(result))} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_stopiteration_fix()
    if success:
        print("\n🎉 StopIteration fix verified successfully!")
        sys.exit(0)
    else:
        print("\n❌ StopIteration fix test failed!")
        sys.exit(1)