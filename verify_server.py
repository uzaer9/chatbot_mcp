#!/usr/bin/env python3
"""
Quick verification script to check if your soccer server is working
Run this before starting the main application
"""

import subprocess
import os
import sys
import time
import json
from app.config import config
from dotenv import load_dotenv
import os
import soccerdata as sd
print(sd.FBref.available_leagues())


# import google.generativeai as genai
load_dotenv()

# genai.configure(api_key=os.environ['GEMINI_API_KEY'])

# model = genai.GenerativeModel(model_name='gemini-1.5-flash')
# response = model.generate_content('Teach me about how an LLM works')

# print(response.text)
def check_dependencies():
    print("\n📦 Checking dependencies...")

    # Map your package names to correct import names here
    packages = {
        'soccerdata': 'soccerdata',
        'mcp': 'mcp',
        'fastapi': 'fastapi',
        'google-generativeai': 'google.generativeai'  # correct import path
    }

    missing_packages = []

    for package, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")

    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True



def check_server_file():
    """Check if the server file exists"""
    server_path = config.MCP_SERVER_PATH
    print(f"🔍 Checking server file: {server_path}")
    
    if os.path.exists(server_path):
        print(f"✅ Server file found!")
        
        # Check if it's executable
        if os.access(server_path, os.R_OK):
            print("✅ Server file is readable")
        else:
            print("❌ Server file is not readable")
            return False
            
        return True
    else:
        print(f"❌ Server file not found!")
        print("\n💡 Options:")
        print(f"1. Copy your server.py to: {server_path}")
        print(f"2. Update MCP_SERVER_PATH in .env file")
        return False

def test_server_startup():
    """Test if the server can start"""
    print(f"\n🚀 Testing server startup...")
    
    try:
        # Try to start the server process
        process = subprocess.Popen(
            ["python", config.MCP_SERVER_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully!")
            
            # Terminate the test process
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ Server failed to start!")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Python interpreter not found or server file missing")
        return False
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

def check_server_tools():
    """Check if server has the expected tools"""
    print(f"\n🛠️ Checking server tools...")
    
    try:
        # Read the server file to check for tools
        with open(config.MCP_SERVER_PATH, 'r') as f:
            content = f.read()
        
        # Look for common tool decorators
        expected_tools = [
            '@mcp.tool()',
            'available_leagues',
            'read_team_season_stats',
            'read_schedule',
            'soccerdata'
        ]
        
        found_tools = []
        missing_tools = []
        
        for tool in expected_tools:
            if tool in content:
                found_tools.append(tool)
                print(f"✅ Found: {tool}")
            else:
                missing_tools.append(tool)
                print(f"⚠️ Missing: {tool}")
        
        if len(found_tools) >= 3:  # At least some core tools
            print(f"\n✅ Server appears to have soccer tools ({len(found_tools)} indicators found)")
            return True
        else:
            print(f"\n❌ Server may be missing soccer tools")
            return False
            
    except Exception as e:
        print(f"❌ Could not analyze server file: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print(f"\n📦 Checking dependencies...")
    
    required_packages = [
        'soccerdata',
        'mcp',
        'fastapi',
        'google-generativeai'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True

def main():
    """Main verification function"""
    print("⚽ Soccer Analytics Chatbot - Server Verification")
    print("=" * 55)
    
    # Check environment
    try:
        config.validate()
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Run all checks
    checks = [
        ("Server File", check_server_file),
        ("Dependencies", check_dependencies), 
        ("Server Startup", test_server_startup),
        ("Server Tools", check_server_tools)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        result = check_func()
        results.append((check_name, result))
    
    # Summary
    print(f"\n{'='*55}")
    print("📋 VERIFICATION SUMMARY")
    print(f"{'='*55}")
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:20} {status}")
        if not result:
            all_passed = False
    
    print(f"\n{'='*55}")
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("You're ready to start the soccer analytics chatbot!")
        print("\nNext steps:")
        print("1. uvicorn app.main:app --reload --port 8000")
        print("2. streamlit run frontend/streamlit_app.py --server.port 8501")
    else:
        print("⚠️ SOME CHECKS FAILED!")
        print("Please fix the issues above before starting the application.")
    
    print(f"{'='*55}")

if __name__ == "__main__":
    main()