#!/usr/bin/env python3
"""
GitHub Actions Test Script - Simulate Workflow Execution
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ops.ga_checks import test_github_actions_locally

if __name__ == "__main__":
    test_github_actions_locally()
