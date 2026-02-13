from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
phantom = '0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9'

print('💰 PHANTOM WALLET STATUS')
print('=' * 30)

try:
    # Check current balance
    balance_wei = w3.eth.get_balance(phantom)
    balance_eth = w3.from_wei(balance_wei, 'ether')
    print(f'Current Balance: {balance_eth:.6f} ETH')
    
    # Get transaction count
    nonce = w3.eth.get_transaction_count(phantom)
    print(f'Transaction Count (Nonce): {nonce}')
    
    # If nonce > 0, there were outgoing transactions
    if nonce > 0:
        print('')
        print(f'🔍 EVIDENCE: Phantom has sent {nonce} transactions!')
        print('')
        print('📋 LIKELY SCENARIO:')
        print('1. AI executed bridge transaction(s)')
        print('2. Funds left Phantom wallet')
        print('3. Bridge failed or funds stuck in transit')
        print('4. Recovery state not updated (private key issue)')
        
        # Search for the most recent transaction
        current = w3.eth.block_number
        print('')
        print(f'Searching last 1000 blocks for Phantom transactions...')
        
        for block_num in range(current, max(0, current - 1000), -1):
            try:
                block = w3.eth.get_block(block_num, full_transactions=True)
                
                for tx in block.transactions:
                    if tx['from'].lower() == phantom.lower() and tx['value'] > 0:
                        value_eth = w3.from_wei(tx['value'], 'ether')
                        print('')
                        print('🎯 FOUND AI TRANSACTION:')
                        print(f'  TX: {tx.hash.hex()}')
                        print(f'  To: {tx["to"]}')
                        print(f'  Value: {value_eth:.6f} ETH')
                        print(f'  Block: {block_num}')
                        print(f'  Explorer: https://basescan.org/tx/{tx.hash.hex()}')
                        break
                        
            except:
                continue
    else:
        print('No outgoing transactions found')
        
except Exception as e:
    print(f'Error: {e}')
