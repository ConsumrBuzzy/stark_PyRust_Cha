#!/usr/bin/env python3
"""
Real-time Starknet Balance Auditor
Checks Ghost address and main wallet without mock data
"""

import asyncio
import sys
from pathlib import Path

from loguru import logger

# Ensure repo root on path for `src` imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ops.audit_ops import run_audit, display_results


async def main():
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
    )

    result = await run_audit()
    display_results(result)
    print("\n📄 Audit complete")


if __name__ == "__main__":
    asyncio.run(main())
