#!/usr/bin/env python3
"""Test script to verify feature loading"""

import sys
import os
import importlib

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Import the TUI engine module directly
tui_module_path = os.path.join(parent_dir, 'personal-ssh-cli', 'interface', 'tui_engine.py')
spec = importlib.util.spec_from_file_location("tui_engine", tui_module_path)
tui_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tui_module)

TUIEngine = tui_module.TUIEngine

engine = TUIEngine()

print("=" * 60)
print("LOCAL FEATURES AUDIT")
print("=" * 60)
print(f"Total local features loaded: {len(engine.local_features)}")
print()

for feature_name, feature_module in engine.local_features.items():
    has_run = hasattr(feature_module, 'run')
    status = "✓" if has_run else "✗"
    print(f"{status} {feature_name:30s} | has run(): {has_run}")

print()
print("=" * 60)
print("REMOTE FEATURES AUDIT")
print("=" * 60)
print(f"Total remote features loaded: {len(engine.remote_features)}")
print()

for feature_name, feature_module in engine.remote_features.items():
    has_run = hasattr(feature_module, 'run')
    status = "✓" if has_run else "✗"
    print(f"{status} {feature_name:30s} | has run(): {has_run}")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)

local_with_run = sum(1 for m in engine.local_features.values() if hasattr(m, 'run'))
remote_with_run = sum(1 for m in engine.remote_features.values() if hasattr(m, 'run'))

print(f"Local features with run():  {local_with_run}/{len(engine.local_features)}")
print(f"Remote features with run(): {remote_with_run}/{len(engine.remote_features)}")
print()

if local_with_run == len(engine.local_features) and remote_with_run == len(engine.remote_features):
    print("✓ ALL FEATURES PROPERLY INTEGRATED!")
else:
    print("✗ Some features missing run() function")
