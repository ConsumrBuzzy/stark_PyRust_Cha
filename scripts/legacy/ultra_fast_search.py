from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
phantom = '0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9'

print('⚡ ULTRA FAST PHANTOM TX SEARCH')
print('=' * 40)

try:
    # Get latest transactions directly from Phantom
    current = w3.eth.block_number
    
    # Check last 50 blocks for any Phantom transactions
    found_txs = []
    
    for block_num in range(current, max(0, current - 50), -1):
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            
            for tx in block.transactions:
                if tx['from'].lower() == phantom.lower() and tx['value'] > 0:
                    value_eth = w3.from_wei(tx['value'], 'ether')
                    found_txs.append({
                        'hash': tx.hash.hex(),
                        'to': tx['to'],
                        'value': value_eth,
                        'block': block_num
                    })
                    
        except:
            continue
    
    print(f'Found {len(found_txs)} outgoing transactions from Phantom:')
    
    for tx in found_txs:
        print('')
        print(f'TX: {tx["hash"]}')
        print(f'  To: {tx["to"]}')
        print(f'  Value: {tx["value"]:.6f} ETH')
        print(f'  Block: {tx["block"]}')
        
        # Check if it's StarkGate
        starkgate = '0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419'
        if tx['to'].lower() == starkgate.lower():
            print('  Type: ✅ STARKGATE BRIDGE (AI EXECUTED)')
        else:
            print('  Type: Unknown contract')
            
        print(f'  Explorer: https://basescan.org/tx/{tx["hash"]}')

except Exception as e:
    print(f'Error: {e}')
