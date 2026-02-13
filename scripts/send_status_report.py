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

from src.foundation.reporting import ReportingSystem

async def send_status_report():
    """Send GitHub Actions status report to Telegram"""
    reporting = ReportingSystem()
    
    if reporting.is_enabled():
        # Get environment variables from GitHub Actions
        status = os.getenv('JOB_STATUS', 'unknown')
        workflow = os.getenv('GITHUB_WORKFLOW', 'unknown')
        run_id = os.getenv('GITHUB_RUN_ID', 'unknown')
        
        message = f"""📊 GITHUB ACTIONS REPORT

🔄 Workflow: {workflow}
🆔 Run ID: {run_id}
✅ Status: {status}
⏰ Time: {asyncio.get_event_loop().time()}

🏭 Full-Auto Mining Rig Status Report"""
        
        await reporting.telegram.send_alert('GITHUB ACTIONS REPORT', message)
        print("✅ Status report sent to Telegram")
    else:
        print("❌ Telegram not configured")

if __name__ == "__main__":
    asyncio.run(send_status_report())
