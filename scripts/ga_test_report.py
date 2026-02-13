#!/usr/bin/env python3
"""
GitHub Actions Test Report - Complete Validation
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ops.ga_checks import generate_test_report

if __name__ == "__main__":
    generate_test_report()
