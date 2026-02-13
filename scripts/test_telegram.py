#!/usr/bin/env python3
"""
Test Telegram Integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Load .env file with proper encoding
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ops.reporting_ops import test_telegram_connection

async def test_telegram():
    print('🧪 TESTING TELEGRAM INTEGRATION')
    print('=' * 40)
    
    # Show environment variables
    print(f'🔑 BOT_TOKEN: {os.getenv("TELEGRAM_BOT_TOKEN", "NOT FOUND")[:20]}...')
    print(f'🆔 CHAT_ID: {os.getenv("TELEGRAM_CHAT_ID", "NOT FOUND")}')
    
    await test_telegram_connection()

if __name__ == "__main__":
    asyncio.run(test_telegram())
