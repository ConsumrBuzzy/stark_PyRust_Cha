from web3 import Web3

# Connect to Base to find ALL outgoing transactions from Phantom
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
phantom_address = '0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9'

print('🔍 PHANTOM WALLET - ALL OUTGOING TRANSACTIONS')
print('=' * 60)
print(f'Phantom: {phantom_address}')

try:
    current_block = w3.eth.block_number
    start_block = max(0, current_block - 2000)  # Search wider range
    
    print(f'Searching blocks {start_block} to {current_block}...')
    
    outgoing_txs = []
    
    for block_num in range(current_block, start_block, -1):
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            
            for tx in block.transactions:
                if tx['from'].lower() == phantom_address.lower() and tx['value'] > 0:
                    value_eth = w3.from_wei(tx['value'], 'ether')
                    outgoing_txs.append({
                        'hash': tx.hash.hex(),
                        'to': tx['to'],
                        'value': value_eth,
                        'block': block_num,
                        'gas': tx.gas,
                        'gasPrice': tx.gasPrice
                    })
                    
        except:
            continue
            
        if len(outgoing_txs) >= 10:  # Limit results
            break
    
    print('')
    print(f'📋 FOUND {len(outgoing_txs)} OUTGOING TRANSACTIONS:')
    
    for i, tx in enumerate(outgoing_txs, 1):
        print('')
        print(f'TX {i}: {tx["hash"]}')
        print(f'  To: {tx["to"]}')
        print(f'  Value: {tx["value"]:.6f} ETH')
        print(f'  Block: {tx["block"]}')
        print(f'  Gas: {tx["gas"]} @ {w3.from_wei(tx["gasPrice"], "gwei")} gwei')
        
        # Identify bridge type
        starkgate = '0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419'
        orbiter = '0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef'
        
        if tx['to'].lower() == starkgate.lower():
            print(f'  Type: StarkGate Bridge')
        elif tx['to'].lower() == orbiter.lower():
            print(f'  Type: Orbiter Bridge')
        else:
            print(f'  Type: UNKNOWN - Possibly Rhino/Manual')
            
        print(f'  Explorer: https://basescan.org/tx/{tx["hash"]}')

except Exception as e:
    print(f'Error: {e}')
