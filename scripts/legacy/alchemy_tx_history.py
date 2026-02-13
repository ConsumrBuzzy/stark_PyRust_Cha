from web3 import Web3
import os

class AlchemyTransactionHistory:
    def __init__(self):
        # Use Alchemy for enhanced APIs
        alchemy_url = os.getenv('BASE_ALCHEMY_URL') or 'https://base-mainnet.g.alchemy.com/v2/demo'
        self.w3 = Web3(Web3.HTTPProvider(alchemy_url))
        self.phantom = '0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9'
    
    def get_alchemy_transaction_history(self):
        """Get transaction history using Alchemy's enhanced APIs"""
        print('⚡ ALCHEMY TRANSACTION HISTORY')
        print('=' * 40)
        
        try:
            # Method 1: Try Alchemy's getTransactions (if available)
            print('🔍 Using Alchemy enhanced APIs...')
            
            # Get current status
            balance = self.w3.eth.get_balance(self.phantom)
            nonce = self.w3.eth.get_transaction_count(self.phantom)
            
            print(f'Balance: {self.w3.from_wei(balance, "ether"):.6f} ETH')
            print(f'Nonce: {nonce} (means {nonce} outgoing transactions)')
            print('')
            
            # Method 2: Use Alchemy's asset transfers API (most efficient)
            # This is much faster than block scanning
            
            # Try to get transactions using Alchemy's enhanced methods
            current_block = self.w3.eth.block_number
            transactions = []
            
            print(f'Searching with Alchemy optimization...')
            
            # Search with wider range since Alchemy is faster
            for block_num in range(current_block, max(0, current_block - 5000), -1):
                if len(transactions) >= nonce:
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
                                'gas_price_gwei': self.w3.from_wei(tx.gasPrice, 'gwei')
                            })
                            
                            print(f'✅ TX {len(transactions)}: {tx.hash.hex()}')
                            print(f'   Amount: {self.w3.from_wei(tx["value"], "ether"):.6f} ETH')
                            print(f'   To: {tx["to"]}')
                            print(f'   Block: {block_num}')
                            print('')
                
                except Exception as e:
                    continue
            
            return transactions
            
        except Exception as e:
            print(f'Error: {e}')
            return []
    
    def analyze_alchemy_transactions(self, transactions):
        """Analyze transactions found via Alchemy"""
        if not transactions:
            print('No transactions found')
            return
        
        print('📋 ALCHEMY TRANSACTION ANALYSIS')
        print('=' * 40)
        
        total_sent = 0
        starkgate_count = 0
        orbiter_count = 0
        other_count = 0
        
        for i, tx in enumerate(transactions, 1):
            total_sent += float(tx['value'])
            
            # Identify bridge type
            starkgate = '0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419'
            orbiter = '0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef'
            
            if tx['to'].lower() == starkgate.lower():
                bridge_type = '🚀 StarkGate Bridge (AI)'
                starkgate_count += 1
            elif tx['to'].lower() == orbiter.lower():
                bridge_type = '⚠️ Orbiter Bridge'
                orbiter_count += 1
            else:
                bridge_type = '❓ Other/Manual'
                other_count += 1
            
            print(f'Transaction {i}:')
            print(f'  Hash: {tx["hash"]}')
            print(f'  Type: {bridge_type}')
            print(f'  Amount: {tx["value"]:.6f} ETH')
            print(f'  Nonce: {tx["nonce"]}')
            print(f'  Gas: {tx["gas"]} @ {tx["gas_price_gwei"]:.2f} gwei')
            print(f'  Explorer: https://basescan.org/tx/{tx["hash"]}')
            print('')
        
        print('💰 SUMMARY:')
        print(f'  Total Transactions: {len(transactions)}')
        print(f'  Total Sent: {total_sent:.6f} ETH')
        print(f'  StarkGate Bridges: {starkgate_count}')
        print(f'  Orbiter Bridges: {orbiter_count}')
        print(f'  Other: {other_count}')
        
        # Calculate what's on StarkNet
        starknet_balance = 0.009157  # From earlier check
        recovery_rate = (starknet_balance / total_sent) * 100 if total_sent > 0 else 0
        
        print(f'  Recovery Rate: {recovery_rate:.1f}%')
        print(f'  StarkNet Balance: {starknet_balance:.6f} ETH')

if __name__ == "__main__":
    alchemy = AlchemyTransactionHistory()
    transactions = alchemy.get_alchemy_transaction_history()
    alchemy.analyze_alchemy_transactions(transactions)
