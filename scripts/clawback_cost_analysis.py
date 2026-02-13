#!/usr/bin/env python3
"""
Clawback Cost Analysis - Exit Strategy Calculator
"""

import asyncio
import sys
import os
from pathlib import Path
from decimal import Decimal

# Load .env file
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.foundation.network import NetworkOracle
from src.foundation.security import SecurityManager
from src.engines.bridge_system import ClawbackSystem

async def clawback_cost_analysis():
    print('🛡️ CLAWBACK COST ANALYSIS')
    print('=' * 50)
    
    # Initialize systems
    oracle = NetworkOracle()
    await oracle.initialize()
    
    security_manager = SecurityManager()
    clawback_system = ClawbackSystem(oracle, security_manager)
    
    # Current investment
    total_invested_usd = 63.00
    current_starknet_balance = await oracle.get_balance('0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9', 'starknet')
    
    print(f'💰 Total Invested: ${total_invested_usd:.2f}')
    print(f'🏭 Current StarkNet Balance: {current_starknet_balance:.6f} ETH')
    print(f'💵 Current Value: ${float(current_starknet_balance) * 2200:.2f}')
    print()
    
    # Calculate withdrawal costs for different scenarios
    scenarios = [
        ("Current Balance", Decimal(str(current_starknet_balance))),
        ("Target Threshold", Decimal('0.018')),
        ("Full Target", Decimal('0.0238')),
    ]
    
    print('📊 WITHDRAWAL COST ANALYSIS')
    print('=' * 30)
    
    for scenario_name, amount in scenarios:
        print(f'\n🎯 Scenario: {scenario_name}')
        print(f'   Amount: {amount:.6f} ETH (${float(amount) * 2200:.2f})')
        
        cost_analysis = await clawback_system.calculate_withdrawal_cost(amount)
        
        if 'error' in cost_analysis:
            print(f'   ❌ Error: {cost_analysis["error"]}')
            continue
        
        print(f'   L2 Withdrawal Cost: {cost_analysis["l2_cost_eth"]:.6f} ETH (${cost_analysis["l2_cost_usd"]:.2f})')
        print(f'   L1 Claim Cost: {cost_analysis["l1_cost_eth"]:.6f} ETH (${cost_analysis["l1_cost_usd"]:.2f})')
        print(f'   Total Cost: {cost_analysis["total_cost_eth"]:.6f} ETH (${cost_analysis["total_cost_usd"]:.2f})')
        print(f'   Net Amount: {cost_analysis["net_amount_eth"]:.6f} ETH (${cost_analysis["net_amount_usd"]:.2f})')
        print(f'   Profitable: {"✅ YES" if cost_analysis["profitable"] else "❌ NO"}')
        
        # ROI calculation
        if cost_analysis["profitable"]:
            roi_usd = cost_analysis["net_amount_usd"] - total_invested_usd
            roi_percent = (roi_usd / total_invested_usd) * 100
            print(f'   ROI: ${roi_usd:.2f} ({roi_percent:+.1f}%)')
        else:
            loss_usd = total_invested_usd - cost_analysis["net_amount_usd"]
            loss_percent = (loss_usd / total_invested_usd) * 100
            print(f'   Loss: ${loss_usd:.2f} ({loss_percent:+.1f}%)')
    
    # Gas price analysis
    print(f'\n⛽ CURRENT GAS PRICES')
    print('=' * 20)
    print(f'   Base Gas Price: {cost_analysis.get("base_gas_price", "N/A")} Gwei')
    print(f'   StarkNet Gas Price: {cost_analysis.get("starknet_gas_price", "N/A")} Gwei')
    
    # Exit strategy recommendation
    print(f'\n🎯 EXIT STRATEGY RECOMMENDATION')
    print('=' * 30)
    
    if cost_analysis["profitable"]:
        print('✅ CLAWBACK VIABLE: Withdrawal is profitable')
        print('💡 Recommendation: Consider withdrawal if ROI targets not met')
    else:
        print('❌ CLAWBACK NOT VIABLE: Withdrawal costs exceed benefits')
        print('💡 Recommendation: Continue Iron → Steel mining operations')
    
    # Emergency exit calculation
    print(f'\n🚨 EMERGENCY EXIT SCENARIO')
    print('=' * 25)
    print('If you MUST exit immediately (ignoring profitability):')
    
    # Use the last successful cost analysis
    if cost_analysis.get("profitable", False) and "net_amount_usd" in cost_analysis:
        print(f'   You would receive: ${cost_analysis["net_amount_usd"]:.2f}')
        print(f'   Total loss: ${total_invested_usd - cost_analysis["net_amount_usd"]:.2f}')
        print(f'   Recovery rate: {(cost_analysis["net_amount_usd"] / total_invested_usd) * 100:.1f}%')
    else:
        # Simple calculation based on current balance
        current_value_usd = float(current_starknet_balance) * 2200
        print(f'   You would receive: ${current_value_usd:.2f} (estimated)')
        print(f'   Total loss: ${total_invested_usd - current_value_usd:.2f}')
        print(f'   Recovery rate: {(current_value_usd / total_invested_usd) * 100:.1f}%')
    
    print(f'\n🛡️ EXIT HATCH STATUS: READY')
    print('The Escape Hatch is bolted on and ready for manual activation.')

if __name__ == "__main__":
    asyncio.run(clawback_cost_analysis())
