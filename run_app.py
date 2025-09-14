#!/usr/bin/env python3
"""
Simple wrapper to run the Streamlit app
"""
import streamlit.web.cli as stcli
import sys
import os

def main():
    # Handle PyInstaller paths
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        os.chdir(base_path)
        app_path = 'streamlit_app.py'  # File should be in the same directory
    else:
        app_path = 'streamlit_app.py'
    
    # Make sure the file exists
    if not os.path.exists(app_path):
        print(f"Error: Cannot find {app_path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')}")
        input("Press Enter to exit...")
        return
    
    # Run streamlit directly
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.port=8079",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false"  # This fixes the port conflict
    ]
    
    print(f"Starting Streamlit app: {app_path}")
    print("Open your browser to: http://localhost:8079")
    
    stcli.main()

if __name__ == "__main__":
    main()