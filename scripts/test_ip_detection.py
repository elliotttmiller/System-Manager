# -*- coding: utf-8 -*-
"""
Test IP Detection

Quick script to test and display detected IP addresses.
"""
import sys
from pathlib import Path

# Add the personal-ssh-cli directory to path
script_dir = Path(__file__).parent.parent  # Go up to project root
sys.path.insert(0, str(script_dir / 'personal-ssh-cli'))

from features.auto_setup import AutoSetup  # type: ignore


def main():
    """Test IP detection."""
    # Set UTF-8 encoding for Windows
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass
    
    print("="*70)
    print("IP ADDRESS DETECTION TEST")
    print("="*70)
    
    setup = AutoSetup()
    system_info = setup.detect_system_info()
    
    print(f"\nHostname: {system_info['hostname']}")
    print(f"OS: {system_info['os']}")
    print(f"Username: {system_info['username']}")
    
    print("\nDetected IP Addresses:")
    for idx, ip in enumerate(system_info['ip_addresses'], 1):
        marker = " <- Primary (will be used by default)" if idx == 1 else ""
        print(f"  {idx}. {ip}{marker}")
    
    print("\n" + "="*70)
    print("Is the primary IP correct?")
    print("If not, you can select a different one during setup,")
    print("or manually enter your IP address (e.g., 192.168.0.14)")
    print("="*70)


if __name__ == '__main__':
    main()
