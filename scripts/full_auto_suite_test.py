#!/usr/bin/env python3
"""
Full-Auto Suite Test - Complete Integration Verification
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
from src.foundation.reporting import ReportingSystem

async def full_auto_suite_test():
    print('🚀 FULL-AUTO SUITE INTEGRATION TEST')
    print('=' * 50)
    
    # Test 1: Network Connectivity
    print('1️⃣ Testing Network Oracle...')
    try:
        config = build_config()
        oracle = await ensure_oracle()
        
        starknet_balance = await oracle.get_balance(config.starknet_address, 'starknet')
        print(f'   ✅ StarkNet Balance: {starknet_balance:.6f} ETH')
        
        threshold_met = starknet_balance >= 0.018
        print(f'   🎯 Threshold Met: {"YES" if threshold_met else "NO"}')
        
    except Exception as e:
        print(f'   ❌ Network Error: {e}')
        return False
    
    # Test 2: Telegram Configuration
    print('\n2️⃣ Testing Telegram Configuration...')
    reporting = ReportingSystem()
    
    if reporting.is_enabled():
        print('   ✅ Telegram credentials loaded')
        print(f'   🔑 Bot Token: {os.getenv("TELEGRAM_BOT_TOKEN", "NOT SET")[:20]}...')
        print(f'   🆔 Chat ID: {os.getenv("TELEGRAM_CHAT_ID", "NOT SET")}')
        
        # Test local connectivity (may fail due to network)
        try:
            await reporting.telegram.send_alert('SUITE_TEST', 'Full-Auto Suite Integration Test')
            print('   ✅ Telegram connectivity: WORKING')
        except Exception as e:
            print(f'   ⚠️  Telegram connectivity: ISSUE ({e})')
            print('   📝 Note: This may be a local network issue, GitHub Actions will have different connectivity')
    else:
        print('   ❌ Telegram not configured')
        return False
    
    # Test 3: Environment Parity
    print('\n3️⃣ Testing Environment Parity...')
    print(f'   🐍 Python Version: {sys.version}')
    print(f'   📁 Working Directory: {os.getcwd()}')
    print(f'   🛤️  Python Path: {sys.path[:3]}...')
    
    # Check required modules
    required_modules = ['src.foundation.network', 'src.foundation.reporting', 'src.engines.recovery_kernel']
    for module in required_modules:
        try:
            __import__(module)
            print(f'   ✅ {module}: IMPORT SUCCESS')
        except ImportError as e:
            print(f'   ❌ {module}: IMPORT FAILED - {e}')
            return False
    
    # Test 4: Secrets Verification
    print('\n4️⃣ Testing Required Secrets...')
    required_secrets = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
        'STARKNET_RPC_URL',
        'STARKNET_WALLET_ADDRESS',
        'STARKNET_PRIVATE_KEY',
        'SIGNER_PASSWORD'
    ]
    
    for secret in required_secrets:
        value = os.getenv(secret)
        if value:
            masked = value[:10] + '...' if len(value) > 10 else '***'
            print(f'   ✅ {secret}: {masked}')
        else:
            print(f'   ❌ {secret}: MISSING')
    
    # Test 5: Workflow Logic Simulation
    print('\n5️⃣ Testing Workflow Logic...')
    
    # Simulate threshold check
    if starknet_balance >= 0.018:
        print('   🎯 STEP A (Sentry): THRESHOLD MET - Would proceed to Step B')
        print('   📱 STEP B (Messenger): Would send FUEL_INJECTED alert')
        print('   ⚛️ STEP C (Forge): Would execute Genesis Bundle')
        print('   ⛏️ STEP D (Loop): Would launch Iron → Steel refining')
        print('   📊 STEP E (Yield): Would report Steel production')
    else:
        needed = 0.018 - starknet_balance
        print(f'   ⏳ STEP A (Sentry): THRESHOLD NOT MET - Need {needed:.6f} more ETH')
        print('   🔄 Would continue monitoring every 5 minutes')
    
    # Final Status
    print('\n📊 FULL-AUTO SUITE STATUS')
    print('=' * 30)
    print(f'🏭 Ready for Deployment: {"✅ YES" if all([os.getenv(s) for s in required_secrets]) else "❌ NO"}')
    print(f'📱 Telegram: {"✅ CONFIGURED" if reporting.is_enabled() else "❌ NOT CONFIGURED"}')
    print(f'🌐 Network: {"✅ CONNECTED" if "oracle" in locals() else "❌ NOT CONNECTED"}')
    print(f'🎯 Auto-Execute: {"✅ READY" if threshold_met else "⏳ WAITING"}')
    
    print('\n🚀 FULL-AUTO SUITE TEST COMPLETE')
    return True

if __name__ == "__main__":
    asyncio.run(full_auto_suite_test())
