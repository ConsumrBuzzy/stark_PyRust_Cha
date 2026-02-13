#!/usr/bin/env python3
"""
GitHub Actions Quick Test - Essential Components Only
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ops.ga_checks import quick_github_actions_test

if __name__ == "__main__":
    quick_github_actions_test()
