#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Manager - Main Entry Point

This is the primary launcher for the Personal SSH/SCP CLI System Manager.
Run this script to start the CLI interface.

Usage:
    python start.py [COMMAND] [OPTIONS]
    
Examples:
    python start.py --help
    python start.py setup
    python start.py setup-server
    python start.py connect my-desktop
    python start.py list-profiles
"""

import sys
import os
from pathlib import Path

# Ensure UTF-8 encoding on Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add the personal-ssh-cli directory to Python path
project_root = Path(__file__).parent
personal_ssh_cli_dir = project_root / 'personal-ssh-cli'

if personal_ssh_cli_dir.exists():
    sys.path.insert(0, str(personal_ssh_cli_dir))
else:
    print(f"Error: Could not find 'personal-ssh-cli' directory at {personal_ssh_cli_dir}")
    print("Please ensure you're running this script from the project root directory.")
    sys.exit(1)


def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                  PERSONAL SSH/SCP SYSTEM MANAGER                     ║
║                         Version 1.0.0                                ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    # Use simple ASCII if Unicode fails
    try:
        print(banner)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print("="*70)
        print("      PERSONAL SSH/SCP SYSTEM MANAGER - Version 1.0.0")
        print("="*70)


def check_dependencies():
    """Check if required dependencies are installed."""
    missing_deps = []
    
    # Map of package import names to pip package names
    required_packages = {
        'click': 'click',
        'rich': 'rich',
        'paramiko': 'paramiko',
        'scp': 'scp',
        'prompt_toolkit': 'prompt_toolkit',
        'yaml': 'pyyaml',
        'cryptography': 'cryptography',
    }
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_deps.append(package_name)
    
    if missing_deps:
        print("\n⚠️  Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nPlease install missing dependencies:")
        print("   pip install -r requirements.txt")
        print("   OR")
        print("   pip install -e .")
        return False
    
    return True


def main():
    """Main entry point."""
    # Show banner only if no arguments or --help
    if len(sys.argv) == 1 or '--help' in sys.argv:
        print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Import and run the CLI engine
        from core.cli_engine import main as cli_main
        
        # Run the CLI
        cli_main()
        
    except ImportError as e:
        print(f"\n❌ Error: Failed to import CLI engine: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -e .")
        print("2. Check that you're in the correct directory")
        print("3. Verify the 'personal-ssh-cli' directory exists")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
