#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Manager - Main Entry Point

Simple launcher that bootstraps and runs the TUI Engine or CLI.

Usage:
    python start.py              # Launch interactive TUI
    python start.py [OPTIONS]    # Use CLI mode
    
Examples:
    python start.py
    python start.py --help
    python start.py connect my-desktop
"""

import sys
import os
from pathlib import Path
import codecs
import shutil

# Ensure UTF-8 encoding on Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
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


def clean_cache():
    """Clean the cache directory to ensure a fresh start."""
    cache_dir = project_root / 'cache'
    if cache_dir.exists() and cache_dir.is_dir():
        try:
            shutil.rmtree(cache_dir)
            print("Cache cleaned successfully.")
        except Exception as e:
            print(f"Warning: Failed to clean cache: {e}")


def check_dependencies():
    """Check if required dependencies are installed."""
    missing_deps = []
    
    required_packages = {
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
        print("\nPlease install: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Main entry point - route to TUI or CLI."""

    # Clean cache at the start
    clean_cache()

    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # If command-line arguments provided, use CLI mode
        if len(sys.argv) > 1:
            from core.cli_engine import main as cli_main
            cli_main()
        else:
            # No arguments - launch TUI Engine
            from interface.tui_engine import TUIEngine
            
            engine = TUIEngine()
            engine.run()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure dependencies installed: pip install -e .")
        print("2. Check you're in the correct directory")
        print("3. Verify 'personal-ssh-cli' directory exists")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
