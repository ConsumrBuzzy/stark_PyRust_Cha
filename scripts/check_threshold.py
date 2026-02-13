#!/usr/bin/env python3
"""
GitHub Actions helper script for threshold checking
"""

import sys
import os
from pathlib import Path

# Add src to path for both local and GitHub Actions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio

from src.ops.env import build_config
from src.ops.network_checks import check_threshold as check_threshold_ops

async def check_threshold():
    """Threshold check using shared ops helpers to preserve behavior."""

    config = build_config()
    ready, balance = await check_threshold_ops(config=config)
    print(f'balance={balance}')
    if ready:
        print('ready=true')
        print('ready_for_mining=true')
    else:
        print('ready=false')
        print('ready_for_mining=false')

if __name__ == "__main__":
    asyncio.run(check_threshold())
