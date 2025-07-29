#!/usr/bin/env python3
"""
Simple runner script for the influencer research application.
Run this from the project root directory.
"""

import sys
import os

# Add src directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

# Change to src directory
os.chdir(src_dir)

# Import and run the enhanced main
try:
    from enhanced_main import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all files are in the correct directories and dependencies are installed.")
    sys.exit(1)