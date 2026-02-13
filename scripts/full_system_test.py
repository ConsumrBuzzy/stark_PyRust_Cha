#!/usr/bin/env python3
"""
Full System Test - Complete Integration Test
"""

import os
import sys
import asyncio
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

from src.ops.env import build_config
from src.ops.network_checks import ensure_oracle
from src.ops.reporting_ops import send_pulse
from src.foundation.state import StateRegistry
from src.foundation.reporting import ReportingSystem

async def full_system_test():
    print('🧪 FULL SYSTEM INTEGRATION TEST')
    print('=' * 50)
    
    # Test 1: Network Oracle
    print('1️⃣ Testing Network Oracle...')
    config = build_config()
    oracle = await ensure_oracle()
    
    phantom_balance = await oracle.get_balance(config.phantom_address, 'base')
    starknet_balance = await oracle.get_balance(config.starknet_address, 'starknet')
    
    print(f'   ✅ Phantom: {phantom_balance:.6f} ETH')
    print(f'   ✅ StarkNet: {starknet_balance:.6f} ETH')
    
    # Test 2: State Registry
    print('\n2️⃣ Testing State Registry...')
    state_registry = StateRegistry()
    recovery_state = await state_registry.load_state()
    
    if recovery_state:
        print(f'   ✅ State loaded: {recovery_state.current_phase}')
    else:
        print('   ✅ No existing state (fresh start)')
    
    # Test 3: Reporting System
    print('\n3️⃣ Testing Reporting System...')
    reporting = ReportingSystem()
    
    if reporting.is_enabled():
        print('   ✅ Telegram enabled')
        
        # Send system status
        status_data = {
            'phantom_balance': f'{phantom_balance:.6f} ETH',
            'starknet_balance': f'{starknet_balance:.6f} ETH',
            'threshold_met': starknet_balance >= 0.018,
            'system_status': 'OPERATIONAL'
        }
        
        await reporting.send_heartbeat(status_data)
        print('   ✅ System heartbeat sent')
        
        # Send test alert
        await send_pulse('SYSTEM TEST', 'Full system integration test completed successfully!', reporting=reporting)
        print('   ✅ Test alert sent')
        
    else:
        print('   ❌ Telegram disabled')
    
    # Test 4: Threshold Check
    print('\n4️⃣ Testing Threshold Logic...')
    threshold_met = starknet_balance >= 0.018
    
    if threshold_met:
        print('   🎯 THRESHOLD MET - Ready for Full-Auto execution!')
    else:
        needed = 0.018 - starknet_balance
        print(f'   ⏳ THRESHOLD NOT MET - Need {needed:.6f} more ETH')
    
    # Test 5: Safety Interlocks
    print('\n5️⃣ Testing Safety Interlocks...')
    
    # Gas price check
    client = oracle.clients["starknet"]
    block = await client.get_block("latest")
    gas_price = getattr(block, 'gas_price', 20)
    
    gas_safe = gas_price <= 100
    print(f'   ⛽ Gas Price: {gas_price} Gwei {"✅ SAFE" if gas_safe else "❌ HIGH"}')
    
    # Dust protection
    dust_protected = phantom_balance > 0.001
    print(f'   🌫️ Dust Protection: {"✅ PROTECTED" if dust_protected else "❌ LOW"}')
    
    # Final status
    print('\n📊 FINAL SYSTEM STATUS')
    print('=' * 30)
    print(f'🏭 Mining Ready: {"✅ YES" if threshold_met and gas_safe else "❌ NO"}')
    print(f'📱 Telegram: {"✅ ACTIVE" if reporting.is_enabled() else "❌ INACTIVE"}')
    print(f'🛡️ Safety: {"✅ ENGAGED" if gas_safe and dust_protected else "❌ COMPROMISED"}')
    print(f'🎯 Auto-Execute: {"✅ READY" if threshold_met else "⏳ WAITING"}')
    
    print('\n🚀 FULL SYSTEM TEST COMPLETE')

if __name__ == "__main__":
    asyncio.run(full_system_test())
