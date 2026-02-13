#!/usr/bin/env python3
"""
GitHub Actions Status Report Script
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

from src.ops.reporting_ops import send_status_report as send_status_report_op

async def send_status_report():
    """Send GitHub Actions status report to Telegram"""

    status = os.getenv('JOB_STATUS', 'unknown')
    workflow = os.getenv('GITHUB_WORKFLOW', 'unknown')
    run_id = os.getenv('GITHUB_RUN_ID', 'unknown')

    await send_status_report_op(
        status=status,
        workflow=workflow,
        run_id=run_id,
        event_time=asyncio.get_event_loop().time(),
    )

if __name__ == "__main__":
    asyncio.run(send_status_report())
