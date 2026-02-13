#!/usr/bin/env python3
"""
Step B: Messenger - Send Fuel Alert
"""

import asyncio
import sys
import os
from pathlib import Path

# Load .env for local testing (GitHub Actions uses secrets)
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ops.reporting_ops import send_fuel_alert
from src.ops.env import build_config

async def fuel_alert():
    config = build_config()
    sent = await send_fuel_alert(
        starknet_address=config.starknet_address,
        balance_display=os.getenv('READY_BALANCE', '0.018'),
        event_time=asyncio.get_event_loop().time(),
    )
    if sent:
        print('✅ Fuel alert sent to Telegram')
    
if __name__ == "__main__":
    asyncio.run(fuel_alert())
