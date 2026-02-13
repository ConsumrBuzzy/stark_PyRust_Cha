#!/usr/bin/env python3
"""
Phantom Sweep - Zero-Waste Capital Consolidation
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ops.env import build_config
from src.ops.network_checks import phantom_sweep_recommendation

async def phantom_sweep():
    """Capital sweep recommendation using shared ops helpers."""

    config = build_config()
    result = await phantom_sweep_recommendation(config=config)

    phantom_balance = result["phantom_balance"]
    starknet_balance = result["starknet_balance"]
    sweep_amount = result["sweep_amount"]
    needed = result["needed"]

    print('💰 PHANTOM-SWEEP CAPITAL AUDIT')
    print('=' * 50)
    print(f'👻 Phantom Balance: {phantom_balance:.6f} ETH (${float(phantom_balance) * 2200:.2f})')
    print(f'🏭 StarkNet Balance: {starknet_balance:.6f} ETH (${float(starknet_balance) * 2200:.2f})')
    print(f'⛽ Gas Reserve: {config.gas_reserve_eth:.6f} ETH')
    print(f'🧹 Sweep Amount: {float(sweep_amount):.6f} ETH (${float(sweep_amount) * 2200:.2f})')

    if result["sweep_recommended"]:
        print('🎯 SWEEP RECOMMENDED:')
        print(f'   Current StarkNet: {starknet_balance:.6f} ETH')
        print(f'   Target Threshold: {config.threshold_eth:.3f} ETH')
        print(f'   Needed: {needed:.6f} ETH')
        print(f'   Available: {float(sweep_amount):.6f} ETH')

        if result["sweep_sufficient"]:
            print('✅ SWEEP SUFFICIENT - Will reach threshold')
        else:
            print('⚠️ SWEEP INSUFFICIENT - Will still be short')
        return True

    print('❌ NO SWEEP NEEDED')
    if starknet_balance >= config.threshold_eth:
        print('   StarkNet already above threshold')
    elif sweep_amount <= 0:
        print('   Insufficient Phantom funds for sweep')
    return False

if __name__ == "__main__":
    result = asyncio.run(phantom_sweep())
    print('')
    print('📊 TOTAL CAPITAL INVESTED: $63.00')
    print(f'🎯 SWEEP RECOMMENDED: {"YES" if result else "NO"}')
