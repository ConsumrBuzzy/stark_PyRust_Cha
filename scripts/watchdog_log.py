#!/usr/bin/env python3
"""
Watchdog Log - Real-time Full-Auto Telemetry
"""

import asyncio
import sys
import os
import time
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ops.env import build_config
from src.ops.network_checks import ensure_oracle, get_gas_price_gwei
from src.foundation.state import StateRegistry
from src.foundation.reporting import ReportingSystem

async def watchdog_log():
    config = build_config()
    oracle = await ensure_oracle()
    
    state_registry = StateRegistry()
    reporting_system = ReportingSystem()
    
    print('🐕 FULL-AUTO WATCHDOG LOG')
    print('=' * 60)
    print('🔒 SAFE-EXECUTION MODE ACTIVE')
    print('🛡️ SAFETY INTERLOCKS: Gas Ceiling | Dust Protection | State-Lock')
    if reporting_system.is_enabled():
        print('📱 TELEGRAM NOTIFICATIONS: ENABLED')
    else:
        print('📱 TELEGRAM NOTIFICATIONS: DISABLED')
    print('=' * 60)
    
    while True:
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Get balances
            phantom_balance = await oracle.get_balance(config.phantom_address, 'base')
            starknet_balance = await oracle.get_balance(config.starknet_address, 'starknet')
            
            # Get state
            recovery_state = await state_registry.load_state()
            
            # Check gas price
            gas_price_value = await get_gas_price_gwei(oracle=oracle)
            
            # Safety checks
            gas_safe = gas_price_value <= config.gas_ceiling_gwei
            threshold_met = float(starknet_balance) >= float(config.threshold_eth)
            
            print(f'⏰ {timestamp} | 💰 StarkNet: {starknet_balance:.6f} ETH | 👻 Phantom: {phantom_balance:.6f} ETH | ⛽ Gas: {gas_price_value} Gwei {"🟢" if gas_safe else "🔴"} | 🎯 {"READY" if threshold_met else "WAITING"}')
            
            # State status
            if recovery_state:
                print(f'   📂 State: {recovery_state.current_phase} | Mission: {"ACTIVE" if recovery_state.mission_active else "INACTIVE"}')
            
            # Safety alerts
            if not gas_safe:
                print(f'   ⚠️  GAS ALERT: Price exceeds {config.gas_ceiling_gwei} Gwei ceiling!')
                if reporting_system.is_enabled():
                    await reporting_system.gas_spike_alert(gas_price_value, config.gas_ceiling_gwei)
            
            if threshold_met:
                print(f'   🎯 THRESHOLD REACHED: Full-Auto will execute Genesis Bundle!')
                break
            
            # Send heartbeat to Telegram every 5 minutes (300 seconds)
            if int(time.time()) % 300 == 0:  # Every 5 minutes
                if reporting_system.is_enabled():
                    status_data = {
                        'status': 'WAITING' if not threshold_met else 'READY',
                        'starknet_balance': f'{starknet_balance:.6f} ETH',
                        'phantom_balance': f'{phantom_balance:.6f} ETH',
                        'gas_price': f'{gas_price} Gwei',
                        'threshold_met': threshold_met
                    }
                    await reporting_system.send_heartbeat(status_data)
            
            # Check for errors
            if recovery_state and recovery_state.current_phase == "mission_failed":
                print(f'   ❌ MISSION FAILED: Manual review required!')
                if reporting_system.is_enabled():
                    await reporting_system.mission_failed("Unknown error", recovery_state.current_phase)
                break
            
            print('-' * 60)
            await asyncio.sleep(60)  # 60-second heartbeat
            
        except Exception as e:
            print(f'❌ Watchdog Error: {e}')
            await asyncio.sleep(30)

if __name__ == "__main__":
    print('🐕 Starting Watchdog Log - Press Ctrl+C to stop')
    try:
        asyncio.run(watchdog_log())
    except KeyboardInterrupt:
        print('\n🛑 Watchdog stopped by user')
