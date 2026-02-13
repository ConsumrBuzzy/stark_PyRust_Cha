from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
phantom = '0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9'
starkgate = '0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419'

print('🚀 FAST PHANTOM → STARKGATE BRIDGE SEARCH')
print('=' * 50)

try:
    # Get current block
    current = w3.eth.block_number
    start = max(0, current - 10000)  # Last ~10k blocks
    
    print(f'Searching StarkGate events from block {start} to {current}...')
    
    # Filter for Transfer events from Phantom to StarkGate
    events = w3.eth.get_logs({
        'address': starkgate,
        'fromBlock': start,
        'toBlock': current
    })
    
    print(f'Found {len(events)} events')
    
    for event in events:
        # Decode the event to check if it's from Phantom
        try:
            # Check if transaction is from Phantom
            tx = w3.eth.get_transaction(event.transactionHash)
            if tx['from'].lower() == phantom.lower() and tx['value'] > 0:
                value_eth = w3.from_wei(tx['value'], 'ether')
                print('')
                print('🎯 FOUND AI BRIDGE TRANSACTION:')
                print(f'  TX: {event.transactionHash.hex()}')
                print(f'  Block: {event.blockNumber}')
                print(f'  From: {tx["from"]}')
                print(f'  To: {tx["to"]}')
                print(f'  Value: {value_eth:.6f} ETH')
                print(f'  Gas: {tx.gas} @ {w3.from_wei(tx.gasPrice, "gwei")} gwei')
                print(f'  Explorer: https://basescan.org/tx/{event.transactionHash.hex()}')
                
        except Exception as e:
            continue
    
    print('')
    print('✅ Search complete!')

except Exception as e:
    print(f'❌ Error: {e}')
