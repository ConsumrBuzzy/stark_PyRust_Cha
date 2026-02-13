from web3 import Web3
import os

# Connect to Base to find Phantom transactions
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# Phantom wallet address
phantom_address = '0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9'

print('🔍 PHANTOM WALLET TO STARKNET TRANSFER SEARCH')
print('=' * 60)
print(f'Phantom Address: {phantom_address}')

try:
    # Get recent transactions from Phantom wallet
    current_block = w3.eth.block_number
    print(f'Current Block: {current_block}')
    
    # Look for outgoing transactions (last 1000 blocks)
    start_block = max(0, current_block - 1000)
    
    print('')
    print('🔍 SEARCHING FOR OUTGOING TRANSACTIONS...')
    
    found_transactions = []
    
    for block_num in range(current_block, start_block, -1):
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            
            for tx in block.transactions:
                if tx['from'].lower() == phantom_address.lower() and tx['value'] > 0:
                    # Found outgoing transaction
                    value_eth = w3.from_wei(tx['value'], 'ether')
                    found_transactions.append({
                        'hash': tx.hash.hex(),
                        'to': tx['to'],
                        'value': value_eth,
                        'block': block_num,
                        'input': tx['input']
                    })
                    
                    print(f'Found: {value_eth:.6f} ETH to {tx["to"]} in block {block_num}')
                    
                    # Stop if we find the expected amount
                    if abs(value_eth - 0.01471479) < 0.001:
                        print('🎯 FOUND EXPECTED TRANSFER AMOUNT!')
                        break
                        
        except Exception as e:
            continue  # Skip problematic blocks
            
        if len(found_transactions) >= 5:  # Limit search
            break
    
    print('')
    print(f'📋 PHANTOM TRANSACTIONS FOUND: {len(found_transactions)}')
    
    for i, tx in enumerate(found_transactions, 1):
        print('')
        print(f'Transaction {i}:')
        print(f'  Hash: {tx["hash"]}')
        print(f'  To: {tx["to"]}')
        print(f'  Value: {tx["value"]:.6f} ETH')
        print(f'  Block: {tx["block"]}')
        
        # Check if it's a known bridge
        starkgate_contract = '0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419'
        orbiter_contract = '0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef'
        
        if tx['to'].lower() == starkgate_contract.lower():
            print(f'  Type: ✅ StarkGate Bridge')
        elif tx['to'].lower() == orbiter_contract.lower():
            print(f'  Type: ⚠️  Orbiter Bridge')
        else:
            print(f'  Type: ❓ Unknown Contract')
            
        print(f'  Basescan: https://basescan.org/tx/{tx["hash"]}')
    
except Exception as e:
    print(f'❌ Error searching transactions: {e}')
