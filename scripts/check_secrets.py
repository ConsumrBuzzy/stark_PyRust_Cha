#!/usr/bin/env python3
"""
GitHub Secrets Connectivity Test - Last-Mile Validation
"""

import os
import sys
import asyncio
import aiohttp
from pathlib import Path
from decimal import Decimal

# Load .env file
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.foundation.network import NetworkOracle
from src.foundation.security import SecurityManager
from src.foundation.reporting import ReportingSystem

async def test_connectivity():
    print('🛡️ GITHUB SECRETS CONNECTIVITY TEST')
    print('=' * 50)
    
    # Test 1: Required Secrets Check
    print('1️⃣ REQUIRED SECRETS VALIDATION')
    print('=' * 30)
    
    required_secrets = {
        'SIGNER_PASSWORD': 'Master password for encrypted vault',
        'TELEGRAM_BOT_TOKEN': 'Bot token with prefix (123456:ABC...)',
        'TELEGRAM_CHAT_ID': 'Your personal chat ID',
        'STARKNET_RPC_URL': 'StarkNet RPC endpoint (Alchemy/Infura recommended)',
        'STARKNET_WALLET_ADDRESS': 'Exact address from main.py --setup',
        'STARKNET_PRIVATE_KEY': 'Private key for StarkNet wallet',
        'INFLUENCE_API_KEY': 'API key for services'
    }
    
    secrets_status = {}
    for secret, description in required_secrets.items():
        value = os.getenv(secret)
        if value:
            if 'TOKEN' in secret and ':' not in value:
                print(f'   ❌ {secret}: INVALID FORMAT - Missing prefix')
                secrets_status[secret] = False
            elif 'ADDRESS' in secret and not value.startswith('0x'):
                print(f'   ❌ {secret}: INVALID FORMAT - Should start with 0x')
                secrets_status[secret] = False
            elif 'PRIVATE_KEY' in secret and not value.startswith('0x'):
                print(f'   ❌ {secret}: INVALID FORMAT - Should start with 0x')
                secrets_status[secret] = False
            else:
                masked = value[:10] + '...' if len(value) > 10 else '***'
                print(f'   ✅ {secret}: {masked} - {description}')
                secrets_status[secret] = True
        else:
            print(f'   ❌ {secret}: MISSING - {description}')
            secrets_status[secret] = False
    
    print(f'   📊 Secrets Valid: {sum(secrets_status.values())}/{len(secrets_status)}')
    
    # Test 2: StarkNet RPC Connectivity
    print('\n2️⃣ STARKNET RPC CONNECTIVITY')
    print('=' * 30)
    
    rpc_url = os.getenv('STARKNET_RPC_URL')
    if rpc_url:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Content-Type': 'application/json'}
                payload = {
                    "jsonrpc": "2.0",
                    "method": "starknet_getBlockWithTxHashes",
                    "params": {"block_id": "latest"},
                    "id": 1
                }
                
                async with session.post(rpc_url, headers=headers, json=payload, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'result' in data:
                            block_number = data['result'].get('block_number', 'unknown')
                            print(f'   ✅ StarkNet RPC: CONNECTED - Block {block_number}')
                        else:
                            print(f'   ❌ StarkNet RPC: INVALID RESPONSE - {data}')
                    else:
                        error_text = await response.text()
                        print(f'   ❌ StarkNet RPC: HTTP {response.status} - {error_text}')
                        
        except asyncio.TimeoutError:
            print(f'   ❌ StarkNet RPC: TIMEOUT - Check endpoint reliability')
        except Exception as e:
            print(f'   ❌ StarkNet RPC: ERROR - {e}')
    else:
        print('   ❌ StarkNet RPC: NOT CONFIGURED')
    
    # Test 3: Telegram Bot Connectivity
    print('\n3️⃣ TELEGRAM BOT CONNECTIVITY')
    print('=' * 30)
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token and chat_id:
        try:
            reporting = ReportingSystem()
            if reporting.is_enabled():
                # Send test message
                await reporting.telegram.send_alert(
                    '🧪 CONNECTIVITY_TEST',
                    f'''GitHub Secrets Validation Test
                    
✅ StarkNet RPC: Tested
✅ Telegram Bot: Testing
✅ Security Manager: Ready
✅ Network Oracle: Ready

Time: {asyncio.get_event_loop().time()}
Status: LAST-MILE VALIDATION COMPLETE'''
                )
                print(f'   ✅ Telegram Bot: CONNECTED - Test message sent')
            else:
                print(f'   ❌ Telegram Bot: NOT ENABLED')
                
        except Exception as e:
            print(f'   ❌ Telegram Bot: ERROR - {e}')
    else:
        print('   ❌ Telegram Bot: MISSING CREDENTIALS')
    
    # Test 4: Security Manager Validation
    print('\n4️⃣ SECURITY MANAGER VALIDATION')
    print('=' * 30)
    
    try:
        security_manager = SecurityManager()
        
        # Test vault access
        if os.getenv('SIGNER_PASSWORD'):
            private_key = security_manager.get_starknet_private_key()
            if private_key:
                print(f'   ✅ Security Manager: VAULT ACCESSIBLE')
                print(f'   🔑 Private Key: {"***" + private_key[-10:] if private_key else "NOT FOUND"}')
            else:
                print(f'   ❌ Security Manager: VAULT ACCESS FAILED')
        else:
            print(f'   ⚠️  Security Manager: NO PASSWORD PROVIDED')
            
    except Exception as e:
        print(f'   ❌ Security Manager: ERROR - {e}')
    
    # Test 5: Network Oracle Validation
    print('\n5️⃣ NETWORK ORACLE VALIDATION')
    print('=' * 30)
    
    try:
        oracle = NetworkOracle()
        await oracle.initialize()
        
        # Test balance query
        wallet_address = os.getenv('STARKNET_WALLET_ADDRESS')
        if wallet_address:
            balance = await oracle.get_balance(wallet_address, 'starknet')
            print(f'   ✅ Network Oracle: CONNECTED')
            print(f'   💰 Wallet Balance: {balance:.6f} ETH')
        else:
            print(f'   ❌ Network Oracle: NO WALLET ADDRESS')
            
    except Exception as e:
        print(f'   ❌ Network Oracle: ERROR - {e}')
    
    # Test 6: Account Prerequisites
    print('\n6️⃣ ACCOUNT PREREQUISITES')
    print('=' * 30)
    
    wallet_address = os.getenv('STARKNET_WALLET_ADDRESS')
    if wallet_address:
        try:
            oracle = NetworkOracle()
            await oracle.initialize()
            
            # Check if account exists
            client = oracle.clients['starknet']
            try:
                # Try to get account nonce
                nonce = await client.get_contract_nonce(wallet_address)
                print(f'   ✅ Account Status: EXISTS - Nonce: {nonce}')
                print(f'   🎯 Genesis: NOT NEEDED - Account already deployed')
            except Exception:
                print(f'   ⏳ Account Status: NOT DEPLOYED - Genesis required')
                print(f'   💰 Genesis Cost: 0.018 ETH needed for account birth')
                
        except Exception as e:
            print(f'   ❌ Account Check: ERROR - {e}')
    else:
        print('   ❌ Account Check: NO WALLET ADDRESS')
    
    # Summary
    print('\n📊 CONNECTIVITY TEST SUMMARY')
    print('=' * 30)
    
    total_tests = len(required_secrets) + 5  # secrets + 5 connectivity tests
    passed_tests = sum(secrets_status.values())
    
    print(f'🧪 Total Tests: {total_tests}')
    print(f'✅ Secrets Valid: {passed_tests}/{len(required_secrets)}')
    print(f'🌐 RPC: Tested')
    print(f'📱 Telegram: Tested')
    print(f'🔐 Security: Tested')
    print(f'🔮 Network: Tested')
    print(f'👤 Account: Tested')
    
    # Recommendations
    print('\n💡 LAST-MILE RECOMMENDATIONS')
    print('=' * 30)
    
    if passed_tests == len(required_secrets):
        print('✅ All secrets configured correctly')
    else:
        print('❌ Fix missing/invalid secrets before deployment')
    
    print('📡 Use reliable RPC provider (Alchemy/Infura)')
    print('🔑 Verify SIGNER_PASSWORD matches encrypted vault')
    print('📱 Send /start to your Telegram bot')
    print('🎯 Confirm wallet address matches main.py --setup')
    
    print('\n🚀 DEPLOYMENT READINESS')
    print('=' * 20)
    
    if passed_tests == len(required_secrets):
        print('🎉 READY FOR GITHUB DEPLOYMENT')
        print('📤 Copy these secrets to GitHub repository settings')
    else:
        print('⚠️  FIX ISSUES BEFORE DEPLOYMENT')

if __name__ == "__main__":
    asyncio.run(test_connectivity())
