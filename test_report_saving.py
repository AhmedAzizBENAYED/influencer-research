#!/usr/bin/env python3
"""Test script to verify report saving functionality."""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

from variables.tools.research_tools import save_markdown_report
from src.config.settings import settings

def test_report_saving():
    """Test the report saving functionality."""
    print("🧪 Testing report saving functionality...")
    
    # Create test content
    test_content = """# AI Influencer Research Report

## Executive Summary
This is a test report to verify the saving functionality.

## Test Influencers
1. **Test Influencer 1**
   - Platform: YouTube
   - Followers: 100K+
   - Niche: AI/Tech

2. **Test Influencer 2**
   - Platform: LinkedIn
   - Followers: 50K+
   - Niche: Machine Learning

## Conclusion
This test report demonstrates that the saving mechanism works correctly.
"""
    
    try:
        # Test saving with default path
        print(f"📁 Output directory: {settings.OUTPUT_DIR}")
        saved_path = save_markdown_report(test_content)
        print(f"✅ Report saved successfully to: {saved_path}")
        
        # Verify file exists
        if os.path.exists(saved_path):
            print("✅ File exists and is accessible")
            with open(saved_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"📄 File size: {len(content)} characters")
        else:
            print("❌ File was not created")
            
    except Exception as e:
        print(f"❌ Error saving report: {e}")

if __name__ == "__main__":
    test_report_saving()