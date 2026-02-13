#!/usr/bin/env python3
"""
GitHub Actions helper script for recovery state checking
"""

import sys
import os
sys.path.insert(0, 'src')

from src.foundation.state import StateRegistry
import asyncio

async def check_state():
    state_registry = StateRegistry()
    recovery_state = await state_registry.load_state()
    if recovery_state:
        print(f'has_state=true')
        print(f'current_phase={recovery_state.current_phase}')
        print(f'total_bridged={recovery_state.total_bridged}')
        if recovery_state.mission_active:
            print(f'mission_active=true')
        else:
            print(f'mission_active=false')
    else:
        print(f'has_state=false')
        print(f'current_phase=none')
        print(f'total_bridged=0')
        print(f'mission_active=false')

if __name__ == "__main__":
    asyncio.run(check_state())
