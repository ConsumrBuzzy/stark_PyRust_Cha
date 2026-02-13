#!/usr/bin/env python3
"""
Phantom Sweep - Zero-Waste Capital Consolidation
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.foundation.network import NetworkOracle

async def phantom_sweep():
    oracle = NetworkOracle()
    await oracle.initialize()
    
    phantom_address = '0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9'
    starknet_address = '0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9'
    
    print('💰 PHANTOM-SWEEP CAPITAL AUDIT')
    print('=' * 50)
    
    # Check Phantom balance
    phantom_balance = await oracle.get_balance(phantom_address, 'base')
    print(f'👻 Phantom Balance: {phantom_balance:.6f} ETH (${phantom_balance * 2200:.2f})')
    
    # Check StarkNet balance
    starknet_balance = await oracle.get_balance(starknet_address, 'starknet')
    print(f'🏭 StarkNet Balance: {starknet_balance:.6f} ETH (${starknet_balance * 2200:.2f})')
    
    # Calculate sweep amount
    gas_reserve = 0.001
    sweep_amount = max(0, float(phantom_balance) - gas_reserve)
    
    print(f'⛽ Gas Reserve: {gas_reserve:.6f} ETH')
    print(f'🧹 Sweep Amount: {sweep_amount:.6f} ETH (${sweep_amount * 2200:.2f})')
    
    # Check if sweep is needed
    if float(starknet_balance) < 0.018 and sweep_amount > 0:
        print(f'🎯 SWEEP RECOMMENDED:')
        print(f'   Current StarkNet: {starknet_balance:.6f} ETH')
        print(f'   Target Threshold: 0.018 ETH')
        print(f'   Needed: {0.018 - float(starknet_balance):.6f} ETH')
        print(f'   Available: {sweep_amount:.6f} ETH')
        
        if sweep_amount >= (0.018 - float(starknet_balance)):
            print(f'✅ SWEEP SUFFICIENT - Will reach threshold')
        else:
            print(f'⚠️ SWEEP INSUFFICIENT - Will still be short')
        
        return True
    else:
        print(f'❌ NO SWEEP NEEDED')
        if float(starknet_balance) >= 0.018:
            print(f'   StarkNet already above threshold')
        elif sweep_amount <= 0:
            print(f'   Insufficient Phantom funds for sweep')
        return False

if __name__ == "__main__":
    result = asyncio.run(phantom_sweep())
    print('')
    print('📊 TOTAL CAPITAL INVESTED: $63.00')
    print(f'🎯 SWEEP RECOMMENDED: {"YES" if result else "NO"}')
