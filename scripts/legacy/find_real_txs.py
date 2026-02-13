from web3 import Web3
import time

class PhantomTransactionFinder:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider('https://base.gateway.tenderly.co'))
        self.phantom = '0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9'
        
        # Contract addresses
        self.starkgate = '0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419'
        self.orbiter = '0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef'
    
    def get_all_phantom_transactions(self, max_results=9):
        """Get actual transaction hashes and details"""
        print('🔍 FINDING REAL TRANSACTION HASHES')
        print('=' * 50)
        
        current_block = self.w3.eth.block_number
        transactions = []
        
        print(f'Searching from block {current_block} backwards...')
        print(f'Target: Find {max_results} transactions from Phantom')
        print('')
        
        # Search wider range to find all transactions
        for block_num in range(current_block, max(0, current_block - 10000), -1):
            if len(transactions) >= max_results:
                break
                
            try:
                block = self.w3.eth.get_block(block_num, full_transactions=True)
                
                for tx in block.transactions:
                    if (tx['from'].lower() == self.phantom.lower() and 
                        tx['value'] > 0):
                        
                        transactions.append({
                            'hash': tx.hash.hex(),
                            'to': tx['to'],
                            'value': self.w3.from_wei(tx['value'], 'ether'),
                            'block': block_num,
                            'nonce': tx.nonce,
                            'gas': tx.gas,
                            'gas_price': self.w3.from_wei(tx.gasPrice, 'gwei'),
                            'input': tx['input'][:10] if tx['input'] else '0x'
                        })
                        
                        print(f'Found TX {len(transactions)}: {tx.hash.hex()}')
                        print(f'  Amount: {self.w3.from_wei(tx["value"], "ether"):.6f} ETH')
                        print(f'  To: {tx["to"]}')
                        print(f'  Block: {block_num}')
                        print('')
                        
            except Exception as e:
                continue
        
        return transactions
    
    def analyze_transactions(self, transactions):
        """Analyze the found transactions"""
        if not transactions:
            print('❌ No transactions found')
            return
        
        print('📋 TRANSACTION ANALYSIS')
        print('=' * 30)
        
        total_sent = 0
        bridge_types = {}
        
        for i, tx in enumerate(transactions, 1):
            total_sent += float(tx['value'])
            
            # Identify bridge type
            if tx['to'].lower() == self.starkgate.lower():
                bridge_type = '🚀 StarkGate (AI)'
            elif tx['to'].lower() == self.orbiter.lower():
                bridge_type = '⚠️ Orbiter'
            else:
                bridge_type = '❓ Other'
            
            bridge_types[bridge_type] = bridge_types.get(bridge_type, 0) + 1
            
            print(f'TX {i}: {tx["hash"]}')
            print(f'  Type: {bridge_type}')
            print(f'  Amount: {tx["value"]:.6f} ETH')
            print(f'  Nonce: {tx["nonce"]}')
            print(f'  Gas: {tx["gas"]} @ {tx["gas_price"]:.2f} gwei')
            print(f'  Input: {tx["input"]}')
            print(f'  Explorer: https://basescan.org/tx/{tx["hash"]}')
            print('')
        
        print('💰 SUMMARY:')
        print(f'  Total Transactions: {len(transactions)}')
        print(f'  Total Sent: {total_sent:.6f} ETH')
        print(f'  Bridge Types: {bridge_types}')
        
        return transactions

if __name__ == "__main__":
    finder = PhantomTransactionFinder()
    transactions = finder.get_all_phantom_transactions(9)
    finder.analyze_transactions(transactions)
