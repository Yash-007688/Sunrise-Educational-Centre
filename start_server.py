#!/usr/bin/env python3
"""
Sunrise Educational Centre - Server Startup Script
Simple script to start the educational platform server
"""

import os
import sys
import subprocess
import time
import signal

def check_requirements():
    """Check if required packages are installed"""
    try:
        import flask
        import flask_socketio
        import sqlite3
        print("All required packages are available")
        return True
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def start_server():
    """Start the server with proper error handling and auto-restart"""
    if not check_requirements():
        return
    
    print("Starting Sunrise Educational Centre Server...")
    print("Current directory:", os.getcwd())
    print("Auto-restart enabled - server will restart if it crashes")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    restart_count = 0
    max_restarts = 10
    
    while restart_count < max_restarts:
        try:
            if restart_count > 0:
                print(f"Restarting server (attempt {restart_count + 1}/{max_restarts})...")
                time.sleep(2)
            
            # Run the main app
            process = subprocess.Popen([sys.executable, "app.py"])
            process.wait()
            
            # If we get here, the process ended
            if process.returncode == 0:
                print("✅ Server shut down normally")
                break
            else:
                print(f"Server exited with code {process.returncode}")
                restart_count += 1
                
        except KeyboardInterrupt:
            print("\nServer stopped by user")
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
            break
        except FileNotFoundError:
            print("app.py not found. Make sure you're in the correct directory.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            restart_count += 1
            time.sleep(5)
    
    if restart_count >= max_restarts:
        print(f"Server failed to start after {max_restarts} attempts")
        print("Check the server.log file for detailed error information")

if __name__ == "__main__":
    start_server()