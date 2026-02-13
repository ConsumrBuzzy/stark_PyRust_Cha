#!/usr/bin/env python3
"""
Telegram Pulse Helper - GitHub Actions Communication Bridge
"""

import asyncio
import sys
import os
from pathlib import Path

# Load .env file
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ops.reporting_ops import send_pulse

async def main():
    if len(sys.argv) < 3:
        print("Usage: python telegram_pulse.py <pulse_type> <message>")
        sys.exit(1)

    pulse_type = sys.argv[1]
    message = sys.argv[2]

    await send_pulse(pulse_type, message)


if __name__ == "__main__":
    asyncio.run(main())
