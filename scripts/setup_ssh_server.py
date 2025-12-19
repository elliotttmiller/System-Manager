#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Setup Script for SSH Server Configuration

Run this on your DESKTOP/SERVER to automatically configure it for remote access.
The generated profile can then be imported on your LAPTOP/CLIENT.

Usage:
    python setup_ssh_server.py
"""

import sys
from pathlib import Path

# Add the personal-ssh-cli directory to path
script_dir = Path(__file__).parent.parent  # Go up to project root
sys.path.insert(0, str(script_dir / 'personal-ssh-cli'))

from features.auto_setup import AutoSetup  # type: ignore


def main():
    """Run automated SSH server setup."""
    # Set console to UTF-8 to handle special characters
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    
    print("""
========================================================================
                 SSH SERVER AUTO-CONFIGURATION                        
========================================================================

  This script will:
  - Detect your system information (IP, hostname, OS)
  - Configure SSH server (if needed)
  - Generate SSH keys (optional)
  - Create a profile configuration file

  Run this on the REMOTE device (desktop/server)
========================================================================
    """)
    
    input("Press ENTER to continue...")
    
    setup = AutoSetup()
    
    try:
        success = setup.run_interactive_setup()
        
        if success:
            print("\n** Setup completed successfully! **")
            print("\nTo use this device from your laptop:")
            print("   1. Copy the generated JSON file to your laptop")
            print("   2. Run: pssh import-profile <filename>.json")
            print("   3. Connect: pssh connect <profile-name>")
        else:
            print("\nSetup incomplete. Please review the errors above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nSetup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\nSetup failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
