#!/usr/bin/env python3
"""
Launch script for the Streamlit Influencer Research App
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    required_packages = ['streamlit', 'plotly', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        
        print("\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Main launch function."""
    print("🎯 AI Influencer Research Assistant - Streamlit Launcher")
    print("=" * 60)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    app_file = current_dir / "streamlit_app.py"
    
    if not app_file.exists():
        print("❌ streamlit_app.py not found in current directory")
        print(f"   Current directory: {current_dir}")
        print("   Please run this script from the project root directory")
        return
    
    # Check requirements
    print("🔍 Checking requirements...")
    if not check_requirements():
        return
    
    print("✅ All requirements satisfied")
    
    # Launch Streamlit
    print("🚀 Launching Streamlit app...")
    print("   App will open in your default browser")
    print("   Press Ctrl+C to stop the server")
    print()
    
    try:
        # Launch streamlit with custom configuration
        cmd = [
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.headless", "false",
            "--server.fileWatcherType", "auto",
            "--browser.gatherUsageStats", "false"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped by user")
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")

if __name__ == "__main__":
    main()