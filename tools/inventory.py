#!/usr/bin/env python3
"""
Multi-chain Asset Inventory & Monitoring System (delegates to ops.portfolio).
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.ops.portfolio import run_portfolio


if __name__ == "__main__":
    run_portfolio()
