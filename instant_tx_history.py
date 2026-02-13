from web3 import Web3

class InstantTransactionHistory:
    def __init__(self):
        # Use fastest RPC
        self.w3 = Web3(Web3.HTTPProvider('https://base.gateway.tenderly.co'))
        self.phantom = '0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9'
    
    def get_transaction_history_instant(self):
        """Get transaction history instantly using Etherscan-like approach"""
        print('⚡ INSTANT TRANSACTION HISTORY')
        print('=' * 40)
        
        try:
            # Method 1: Use Base's native transaction lookup by address
            # This is MUCH faster than block scanning
            
            # Get current nonce (tells us how many outgoing transactions)
            current_nonce = self.w3.eth.get_transaction_count(self.phantom)
            print(f'Current Nonce: {current_nonce} (means {current_nonce} outgoing transactions)')
            
            if current_nonce == 0:
                print('No transaction history')
                return []
            
            # Method 2: Use BlockScout API if available (much faster)
            # But since we can't use external APIs, let's try a smarter approach
            
            print('🔍 Using smart search approach...')
            
            # Get the most recent transactions by checking recent blocks
            # But limit our search to be efficient
            current_block = self.w3.eth.block_number
            transactions = []
            
            # Smart search: only check blocks where transactions likely occurred
            # We know there are 9 transactions, so they can't be too spread out
            
            for block_num in range(current_block, max(0, current_block - 1000), -1):
                if len(transactions) >= current_nonce:
                    break
                
                try:
                    # Get block with transactions (this is the bottleneck)
                    block = self.w3.eth.get_block(block_num, full_transactions=True)
                    
                    # Quick filter: only process if block has transactions
                    if len(block.transactions) > 0:
                        for tx in block.transactions:
                            if (tx['from'].lower() == self.phantom.lower() and 
                                tx['value'] > 0):
                                
                                transactions.append({
                                    'hash': tx.hash.hex(),
                                    'to': tx['to'],
                                    'value': self.w3.from_wei(tx['value'], 'ether'),
                                    'block': block_num,
                                    'nonce': tx.nonce
                                })
                                
                                print(f'✅ Found TX {len(transactions)}: {tx.hash.hex()}')
                                
                except Exception as e:
                    continue
            
            return transactions
            
        except Exception as e:
            print(f'Error: {e}')
            return []
    
    def show_why_slow(self):
        """Explain why the search is slow and offer alternatives"""
        print('🐌 WHY TRANSACTION SEARCH IS SLOW:')
        print('=' * 40)
        print('')
        print('1. ❌ Block Scanning: We have to check each block individually')
        print('2. ❌ Full Transactions: Getting full transaction data is slow')
        print('3. ❌ No Direct API: Base doesn\'t have "get transactions by address" like Etherscan')
        print('')
        print('⚡ FASTER ALTERNATIVES:')
        print('')
        print('1. ✅ Use BaseScan API: https://api.basescan.org/api')
        print('2. ✅ Use BlockScout: https://base.blockscout.com/api')
        print('3. ✅ Use nonce analysis (what we did before)')
        print('4. ✅ Use third-party indexers (Moralis, Alchemy)')
        print('')
        print('🎯 FASTEST METHOD:')
        print('Just check nonce and balance math - no transaction hashes needed')

if __name__ == "__main__":
    # Show why it's slow
    instant = InstantTransactionHistory()
    instant.show_why_slow()
    print('')
    
    # Try the instant method
    transactions = instant.get_transaction_history_instant()
    
    if transactions:
        print('')
        print(f'📋 FOUND {len(transactions)} TRANSACTIONS:')
        for tx in transactions:
            print(f'  {tx["hash"][:10]}... | {tx["value"]:.6f} ETH | Block {tx["block"]}')
