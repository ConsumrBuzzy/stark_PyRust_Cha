#!/usr/bin/env python3
"""
GitHub Actions helper script for threshold checking
"""

import sys
import os
from pathlib import Path

# Add src to path for both local and GitHub Actions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.foundation.network import NetworkOracle
import asyncio

async def check_threshold():
    oracle = NetworkOracle()
    await oracle.initialize()
    balance = await oracle.get_balance('0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9', 'starknet')
    print(f'balance={balance}')
    if balance >= 0.018:
        print('ready=true')
        print('ready_for_mining=true')
    else:
        print('ready=false')
        print('ready_for_mining=false')

if __name__ == "__main__":
    asyncio.run(check_threshold())
