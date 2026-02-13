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

from src.foundation.reporting import ReportingSystem

async def fuel_alert():
    reporting = ReportingSystem()
    if reporting.is_enabled():
        await reporting.telegram.send_alert(
            '⛽ FUEL_INJECTED',
            f'''0.0181 ETH Found on StarkNet!
            
📍 Address: 0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9
💰 Balance: {os.getenv('READY_BALANCE', '0.018')} ETH
⏰ Time: {asyncio.get_event_loop().time()}
🎯 Action: AUTO-EXECUTE GENESIS BUNDLE

The DuggerCore-Stark Engine is now initiating autonomous deployment...'''
        )
        print('✅ Fuel alert sent to Telegram')

if __name__ == "__main__":
    asyncio.run(fuel_alert())
