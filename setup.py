#!/usr/bin/env python3
"""
Setup script for MSSQL MCP Server
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def check_env_file():
    """Check if .env file exists and prompt user to configure it"""
    if not os.path.exists(".env"):
        print("⚠️  .env file not found!")
        print("Please configure your database settings in .env file")
        return False
    
    print("✅ .env file found")
    return True

def main():
    print("🚀 Setting up MSSQL MCP Server...")
    
    try:
        install_requirements()
        check_env_file()
        
        print("\n✅ Setup complete!")
        print("\nNext steps:")
        print("1. Configure your database settings in .env file")
        print("2. Run: python src/mcp/server/server.py")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()