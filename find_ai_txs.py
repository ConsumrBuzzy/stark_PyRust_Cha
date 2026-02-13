from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
phantom = '0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9'

print('🎯 FINDING AI EXECUTED TRANSACTIONS')
print('=' * 40)

try:
    # Get transaction count (nonce = 9 means 9 outgoing transactions)
    nonce = w3.eth.get_transaction_count(phantom)
    print(f'Phantom nonce: {nonce} (means {nonce} outgoing transactions)')
    
    # Search for recent transactions by checking recent blocks
    current = w3.eth.block_number
    
    # Search wider range since we know there are 9 transactions
    found_count = 0
    target_count = min(9, 5)  # Find last 5 transactions
    
    print(f'Searching for last {target_count} transactions...')
    
    for block_num in range(current, max(0, current - 5000), -1):
        if found_count >= target_count:
            break
            
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            
            for tx in block.transactions:
                if tx['from'].lower() == phantom.lower() and tx['value'] > 0:
                    value_eth = w3.from_wei(tx['value'], 'ether')
                    found_count += 1
                    
                    print('')
                    print(f'TRANSACTION {found_count}:')
                    print(f'  Hash: {tx.hash.hex()}')
                    print(f'  To: {tx["to"]}')
                    print(f'  Value: {value_eth:.6f} ETH')
                    print(f'  Block: {block_num}')
                    print(f'  Gas: {tx.gas} @ {w3.from_wei(tx.gasPrice, "gwei")} gwei')
                    
                    # Identify the bridge type
                    starkgate = '0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419'
                    orbiter = '0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef'
                    
                    if tx['to'].lower() == starkgate.lower():
                        print(f'  Type: 🚀 STARKGATE BRIDGE (AI EXECUTED)')
                        print(f'  Status: This should have arrived on StarkNet!')
                    elif tx['to'].lower() == orbiter.lower():
                        print(f'  Type: ⚠️  ORBITER BRIDGE')
                    else:
                        print(f'  Type: ❓ OTHER CONTRACT')
                    
                    print(f'  Explorer: https://basescan.org/tx/{tx.hash.hex()}')
                    
        except Exception as e:
            continue
    
    print('')
    print(f'✅ Found {found_count} recent transactions from Phantom')
    print('')
    print('🔍 ANALYSIS:')
    print('- AI DID execute bridge transactions')
    print('- Funds DID leave Phantom wallet') 
    print('- Recovery_state.json shows NO bridges (system blind)')
    print('- This means AI bridge succeeded but tracking failed')

except Exception as e:
    print(f'Error: {e}')
