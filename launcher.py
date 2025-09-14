#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        app_path = os.path.join(base_path, 'streamlit_app.py')
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(base_path, 'streamlit_app.py')
    
    os.chdir(base_path)
    
    print("Starting YPF Dashboard...")
    print("Once started, open your browser and go to: http://localhost:8079")
    print("-" * 50)
    
    cmd = [sys.executable, '-m', 'streamlit', 'run', app_path, '--server.port', '8079']
    subprocess.run(cmd)

if __name__ == "__main__":
    main()