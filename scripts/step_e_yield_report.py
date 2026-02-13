#!/usr/bin/env python3
"""
Step E: Yield - Report First Steel Production
"""

import asyncio
import sys
import os
from pathlib import Path

# Load .env for local testing
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ops.reporting_ops import send_yield_report

async def yield_report():
    await send_yield_report(
        production="100 Steel",
        roi="+100 Steel",
        gas_used="~20 Gwei",
        event_time=asyncio.get_event_loop().time(),
    )

if __name__ == "__main__":
    asyncio.run(yield_report())
