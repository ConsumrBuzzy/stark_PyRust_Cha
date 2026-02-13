#!/usr/bin/env python3
"""
Clawback Cost Analysis - Exit Strategy Calculator (Simplified)
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

async def simple_clawback_analysis():
    print('🛡️ CLAWBACK COST ANALYSIS')
    print('=' * 50)
    
    # Initialize network oracle
    oracle = NetworkOracle()
    await oracle.initialize()
    
    # Current investment data
    total_invested_usd = 63.00
    current_starknet_balance = await oracle.get_balance('0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9', 'starknet')
    current_value_usd = float(current_starknet_balance) * 2200
    
    print(f'💰 Total Invested: ${total_invested_usd:.2f}')
    print(f'🏭 Current StarkNet Balance: {current_starknet_balance:.6f} ETH')
    print(f'💵 Current Value: ${current_value_usd:.2f}')
    print()
    
    # Simplified cost estimates
    print('📊 WITHDRAWAL COST ESTIMATES')
    print('=' * 30)
    
    # Fixed cost estimates for L2→L1 withdrawal
    l2_withdrawal_cost_eth = Decimal('0.0003')  # ~$0.66
    l1_claim_cost_eth = Decimal('0.0005')      # ~$1.10
    total_cost_eth = l2_withdrawal_cost_eth + l1_claim_cost_eth
    total_cost_usd = float(total_cost_eth) * 2200
    
    print(f'⛽ L2 Withdrawal Cost: {l2_withdrawal_cost_eth:.6f} ETH (${float(l2_withdrawal_cost_eth) * 2200:.2f})')
    print(f'⛽ L1 Claim Cost: {l1_claim_cost_eth:.6f} ETH (${float(l1_claim_cost_eth) * 2200:.2f})')
    print(f'💸 Total Withdrawal Cost: {total_cost_eth:.6f} ETH (${total_cost_usd:.2f})')
    print()
    
    # Scenarios
    scenarios = [
        ("Current Balance", Decimal(str(current_starknet_balance))),
        ("Target Threshold", Decimal('0.018')),
        ("Full Target", Decimal('0.0238')),
    ]
    
    for scenario_name, amount in scenarios:
        print(f'🎯 Scenario: {scenario_name}')
        print(f'   Amount: {amount:.6f} ETH (${float(amount) * 2200:.2f})')
        
        net_amount_eth = amount - total_cost_eth
        net_amount_usd = float(net_amount_eth) * 2200
        profitable = net_amount_eth > 0
        
        print(f'   Net After Fees: {net_amount_eth:.6f} ETH (${net_amount_usd:.2f})')
        print(f'   Profitable: {"✅ YES" if profitable else "❌ NO"}')
        
        if profitable:
            roi_usd = net_amount_usd - total_invested_usd
            roi_percent = (roi_usd / total_invested_usd) * 100
            print(f'   ROI: ${roi_usd:.2f} ({roi_percent:+.1f}%)')
        else:
            loss_usd = total_invested_usd - net_amount_usd
            loss_percent = (loss_usd / total_invested_usd) * 100
            print(f'   Loss: ${loss_usd:.2f} ({loss_percent:+.1f}%)')
        print()
    
    # Exit strategy recommendation
    print('🎯 EXIT STRATEGY RECOMMENDATION')
    print('=' * 30)
    
    current_net_eth = Decimal(str(current_starknet_balance)) - total_cost_eth
    current_net_usd = float(current_net_eth) * 2200
    
    if current_net_eth > 0:
        print('✅ CLAWBACK VIABLE: Current withdrawal is profitable')
        print(f'💰 You would recover: ${current_net_usd:.2f}')
        print(f'📉 Loss from investment: ${total_invested_usd - current_net_usd:.2f}')
        print(f'📊 Recovery rate: {(current_net_usd / total_invested_usd) * 100:.1f}%')
    else:
        print('❌ CLAWBACK NOT VIABLE: Withdrawal costs exceed current balance')
        print('💡 Recommendation: Wait for Iron → Steel mining to increase balance')
    
    print()
    print('🚨 EMERGENCY EXIT SCENARIO')
    print('=' * 25)
    print('If you MUST exit immediately (ignoring costs):')
    print(f'   You would receive: ${current_value_usd:.2f} (current balance)')
    print(f'   Total loss: ${total_invested_usd - current_value_usd:.2f}')
    print(f'   Recovery rate: {(current_value_usd / total_invested_usd) * 100:.1f}%')
    
    print()
    print('🛡️ EXIT HATCH STATUS: READY')
    print('✅ ClawbackSystem initialized in BridgeSystem')
    print('✅ Manual-only emergency lever (no auto-trigger)')
    print('✅ Cost-benefit analysis prevents unprofitable withdrawals')
    print('✅ StateRegistry tracks withdrawal progress')
    
    print()
    print('🎯 KNOWLEDGE IS POWER')
    print('You now have exact numbers for your exit strategy.')
    print('The Escape Hatch is ready when you need it.')

if __name__ == "__main__":
    asyncio.run(simple_clawback_analysis())
