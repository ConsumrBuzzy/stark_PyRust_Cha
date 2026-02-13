#!/usr/bin/env python3
"""
Quick test for StarkGate L1 deposit check
"""

import asyncio
import sys
from pathlib import Path

# Add core to path
sys.path.append(str(Path(__file__).parent))

from tools.starkgate_watch import StarkGateWatcher

async def test_l1_check():
    """Test L1 deposit check"""
    
    watcher = StarkGateWatcher()
    result = await watcher.check_l1_deposit()
    
    print(f"L1 Deposit Check Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_l1_check())
