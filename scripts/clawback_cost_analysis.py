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

from src.ops.env import build_config
from src.ops.clawback import analyze_current_positions

async def clawback_cost_analysis():
    print('🛡️ CLAWBACK COST ANALYSIS')
    print('=' * 50)
    
    # Config & analysis
    config = build_config()
    total_invested_usd = 63.00
    analysis = await analyze_current_positions(config=config)

    current_starknet_balance = analysis["current_balance"]

    print(f'💰 Total Invested: ${total_invested_usd:.2f}')
    print(f'🏭 Current StarkNet Balance: {current_starknet_balance:.6f} ETH')
    print(f'💵 Current Value: ${float(current_starknet_balance) * 2200:.2f}')
    print()
    
    print('📊 WITHDRAWAL COST ANALYSIS')
    print('=' * 30)

    last_cost = None
    for scenario_name, cost_analysis in analysis["scenarios"].items():
        amount = cost_analysis.get("amount_eth") or cost_analysis.get("net_amount_eth", Decimal("0")) + cost_analysis.get("total_cost_eth", Decimal("0"))
        print(f'\n🎯 Scenario: {scenario_name}')
        print(f'   Amount: {amount:.6f} ETH (${float(amount) * 2200:.2f})')

        if 'error' in cost_analysis:
            print(f'   ❌ Error: {cost_analysis["error"]}')
            continue

        print(f'   L2 Withdrawal Cost: {cost_analysis["l2_cost_eth"]:.6f} ETH (${cost_analysis["l2_cost_usd"]:.2f})')
        print(f'   L1 Claim Cost: {cost_analysis["l1_cost_eth"]:.6f} ETH (${cost_analysis["l1_cost_usd"]:.2f})')
        print(f'   Total Cost: {cost_analysis["total_cost_eth"]:.6f} ETH (${cost_analysis["total_cost_usd"]:.2f})')
        print(f'   Net Amount: {cost_analysis["net_amount_eth"]:.6f} ETH (${cost_analysis["net_amount_usd"]:.2f})')
        print(f'   Profitable: {"✅ YES" if cost_analysis["profitable"] else "❌ NO"}')

        if cost_analysis["profitable"]:
            roi_usd = cost_analysis["net_amount_usd"] - total_invested_usd
            roi_percent = (roi_usd / total_invested_usd) * 100
            print(f'   ROI: ${roi_usd:.2f} ({roi_percent:+.1f}%)')
        else:
            loss_usd = total_invested_usd - cost_analysis["net_amount_usd"]
            loss_percent = (loss_usd / total_invested_usd) * 100
            print(f'   Loss: ${loss_usd:.2f} ({loss_percent:+.1f}%)')

        last_cost = cost_analysis
    
    # Gas price analysis
    if last_cost:
        print(f'\n⛽ CURRENT GAS PRICES')
        print('=' * 20)
        print(f'   Base Gas Price: {last_cost.get("base_gas_price", "N/A")} Gwei')
        print(f'   StarkNet Gas Price: {last_cost.get("starknet_gas_price", "N/A")} Gwei')
    
    # Exit strategy recommendation
    print(f'\n🎯 EXIT STRATEGY RECOMMENDATION')
    print('=' * 30)

    if last_cost and last_cost.get("profitable", False):
        print('✅ CLAWBACK VIABLE: Withdrawal is profitable')
        print('💡 Recommendation: Consider withdrawal if ROI targets not met')
    else:
        print('❌ CLAWBACK NOT VIABLE: Withdrawal costs exceed benefits')
        print('💡 Recommendation: Continue Iron → Steel mining operations')
    
    # Emergency exit calculation
    print(f'\n🚨 EMERGENCY EXIT SCENARIO')
    print('=' * 25)
    print('If you MUST exit immediately (ignoring profitability):')
    
    if last_cost and last_cost.get("profitable", False) and "net_amount_usd" in last_cost:
        print(f'   You would receive: ${last_cost["net_amount_usd"]:.2f}')
        print(f'   Total loss: ${total_invested_usd - last_cost["net_amount_usd"]:.2f}')
        print(f'   Recovery rate: {(last_cost["net_amount_usd"] / total_invested_usd) * 100:.1f}%')
    else:
        current_value_usd = float(current_starknet_balance) * 2200
        print(f'   You would receive: ${current_value_usd:.2f} (estimated)')
        print(f'   Total loss: ${total_invested_usd - current_value_usd:.2f}')
        print(f'   Recovery rate: {(current_value_usd / total_invested_usd) * 100:.1f}%')
    
    print(f'\n🛡️ EXIT HATCH STATUS: READY')
    print('The Escape Hatch is bolted on and ready for manual activation.')

if __name__ == "__main__":
    asyncio.run(clawback_cost_analysis())
