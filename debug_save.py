#!/usr/bin/env python3
"""Debug script to test report saving."""

import os
import sys

# Add paths
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

def test_basic_save():
    """Test basic file saving without imports."""
    print("🧪 Testing basic file saving...")
    
    # Test 1: Basic file creation
    try:
        os.makedirs("outputs", exist_ok=True)
        test_file = os.path.join("outputs", "test_report.md")
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("# Test Report\nThis is a test.")
        
        print(f"✅ Basic file created: {test_file}")
        
        # Check if file exists
        if os.path.exists(test_file):
            print("✅ File exists")
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"📄 Content: {content[:50]}...")
        else:
            print("❌ File does not exist")
            
    except Exception as e:
        print(f"❌ Basic save failed: {e}")
    
    # Test 2: Test with settings import
    try:
        from src.config.settings import settings
        print(f"📁 Settings OUTPUT_DIR: {settings.OUTPUT_DIR}")
        print(f"📁 Current working directory: {os.getcwd()}")
        
        # Create directory using settings
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        settings_file = os.path.join(settings.OUTPUT_DIR, "settings_test.md")
        
        with open(settings_file, "w", encoding="utf-8") as f:
            f.write("# Settings Test\nUsing settings.OUTPUT_DIR")
        
        print(f"✅ Settings-based file created: {settings_file}")
        
    except Exception as e:
        print(f"❌ Settings-based save failed: {e}")
    
    # Test 3: Test the actual save function
    try:
        from variables.tools.research_tools import save_markdown_report
        
        test_content = "# Function Test\nTesting save_markdown_report function"
        saved_path = save_markdown_report(test_content)
        print(f"✅ Function save completed: {saved_path}")
        
        if os.path.exists(saved_path):
            print("✅ Function-saved file exists")
        else:
            print("❌ Function-saved file does not exist")
            
    except Exception as e:
        print(f"❌ Function save failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_save()