#!/usr/bin/env python3
"""
Account Activation - Self-Funded Proxy Deploy
Activates undeployed StarkNet account using internal ETH balance
"""

import sys
from pathlib import Path
import asyncio

# Add core to path
sys.path.append(str(Path(__file__).parent.parent))

from src.ops.activation import main


if __name__ == "__main__":
    main()
