#!/usr/bin/env python3
"""
Quick Setup Script for Banking Integration Demo
This script helps set up a minimal demo environment
"""

import os
import sys
import subprocess
import shutil

def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def check_prerequisites():
    """Check if required tools are installed."""
    print("Checking prerequisites...")

    tools = ['python', 'pip']  # Removed node, npm for demo
    for tool in tools:
        if not run_command(f"{tool} --version"):
            print(f"❌ {tool} is not installed. Please install it first.")
            return False

    print("✅ All prerequisites are installed.")
    return True

def setup_minimal_frappe():
    """Set up a minimal environment for demo."""
    print("Setting up demo environment...")

    # Install basic dependencies we need
    requirements = [
        "lxml",
        "cryptography",
        "requests"
    ]

    print("Installing dependencies...")
    for req in requirements:
        if not run_command(f"pip install {req}"):
            print(f"Failed to install {req}")
            return False

    print("✅ Demo environment ready!")
    return True

def create_demo_site():
    """Create a demo site configuration."""
    print("Creating demo site configuration...")

    site_config = """{
    "db_name": "demo_banking",
    "db_password": "demo_password",
    "db_type": "mariadb",
    "encryption_key": "demo_key_32_bytes_for_testing_123456789012"
}"""

    with open("demo_env/site_config.json", "w") as f:
        f.write(site_config)

    print("✅ Demo site configuration created.")

def run_demo():
    """Run the banking integration demo."""
    print("Running Banking Integration Demo...")

    # Set up Python path
    sys.path.insert(0, os.path.join(os.getcwd(), "apps", "banking_integration"))

    # Run the demo
    try:
        subprocess.run([sys.executable, "demo.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Demo failed to run.")
        return False

    return True

def main():
    """Main setup function."""
    print("🚀 Banking Integration App - Quick Setup")
    print("=" * 50)

    if not check_prerequisites():
        return

    if not setup_minimal_frappe():
        return

    # create_demo_site()  # Commented out since not needed

    print("\n" + "=" * 50)
    print("🎯 Setup Complete! Running Demo...")
    print("=" * 50)

    if run_demo():
        print("\n" + "=" * 50)
        print("🎉 SUCCESS! Banking Integration App is working!")
        print("=" * 50)
        print("\n📖 See RUNNING_GUIDE.md for full production setup instructions")
        print("\n🔗 Key files created:")
        print("   - demo.py (demonstration script)")
        print("   - RUNNING_GUIDE.md (complete setup guide)")
        print("   - apps/banking_integration/ (complete Frappe app)")
    else:
        print("❌ Setup failed. Check the errors above.")

if __name__ == "__main__":
    main()