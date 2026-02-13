from web3 import Web3
import os

# Connect to Base
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# Known transaction hash from our analysis
tx_hash = '0x2dec7c24a1b11c731a25fd8c7c2e681488e0c58730ba82f9d20d46032a263407'

print('🔍 BASE TO ORBITER TRADE ANALYSIS')
print('=' * 50)
print(f'Transaction Hash: {tx_hash}')

try:
    # Get transaction details
    tx = w3.eth.get_transaction(tx_hash)
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    
    print('')
    print('📋 TRANSACTION DETAILS:')
    print(f'From: {tx["from"]}')
    print(f'To: {tx["to"]}')
    print(f'Value: {w3.from_wei(tx["value"], "ether")} ETH')
    print(f'Gas Used: {receipt.gasUsed}')
    print(f'Block: {tx.blockNumber}')
    print(f'Status: {"SUCCESS" if receipt.status == 1 else "FAILED"}')
    
    # Check if it's to Orbiter contract
    orbiter_contract = '0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef'
    if tx['to'].lower() == orbiter_contract.lower():
        print('')
        print('✅ CONFIRMED: This is an Orbiter Finance transaction')
        print(f'Orbiter Contract: {orbiter_contract}')
    else:
        print('')
        print(f'⚠️  Unexpected recipient: {tx["to"]}')
    
    # Check input data for bridge parameters
    if tx['input']:
        print('')
        print(f'📝 INPUT DATA: {tx["input"][:100]}...')
        
        # Try to decode if it's standard Orbiter format
        if len(tx['input']) > 10:
            # Orbiter typically uses first 4 bytes for function selector
            selector = tx['input'][:10]
            data = tx['input'][10:]
            print(f'Function Selector: {selector}')
            print(f'Data Length: {len(data)} characters')
            
            # Try to extract amount and target chain
            try:
                # Remove 0x prefix
                clean_data = data[2:] if data.startswith('0x') else data
                if len(clean_data) >= 64:
                    # First 32 bytes might contain amount
                    amount_hex = clean_data[:64]
                    amount = int(amount_hex, 16)
                    amount_eth = amount / 1e18
                    print(f'Extracted Amount: {amount_eth:.6f} ETH')
            except:
                print('Could not decode amount from input data')
    
    print('')
    print('🔗 EXPLORER LINKS:')
    print(f'Basescan: https://basescan.org/tx/{tx_hash}')
    print(f'Orbiter: https://orbiter.finance/history')
    
except Exception as e:
    print(f'❌ Error fetching transaction: {e}')
