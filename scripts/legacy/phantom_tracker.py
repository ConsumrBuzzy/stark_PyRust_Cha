from web3 import Web3
import time

class PhantomTransferTracker:
    def __init__(self):
        # Use multiple RPC endpoints for speed
        self.w3 = Web3(Web3.HTTPProvider('https://base.gateway.tenderly.co'))
        self.phantom = '0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9'
        
        # Known contracts
        self.starkgate = '0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419'
        self.orbiter = '0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef'
        
    def get_current_status(self):
        """Get current wallet status instantly"""
        balance = self.w3.eth.get_balance(self.phantom)
        nonce = self.w3.eth.get_transaction_count(self.phantom)
        
        return {
            'balance': self.w3.from_wei(balance, 'ether'),
            'nonce': nonce,
            'total_sent': nonce  # Each nonce = 1 outgoing transaction
        }
    
    def find_recent_transfers(self, limit=5):
        """Find only your recent outgoing transfers - FAST"""
        print(f'🔍 Finding last {limit} transfers from Phantom...')
        
        current_block = self.w3.eth.block_number
        transfers = []
        
        # Search recent blocks efficiently
        for block_num in range(current_block, max(0, current_block - 200), -1):
            if len(transfers) >= limit:
                break
                
            try:
                block = self.w3.eth.get_block(block_num, full_transactions=True)
                
                for tx in block.transactions:
                    if (tx['from'].lower() == self.phantom.lower() and 
                        tx['value'] > 0):
                        
                        transfers.append({
                            'hash': tx.hash.hex(),
                            'to': tx['to'],
                            'value': self.w3.from_wei(tx['value'], 'ether'),
                            'block': block_num,
                            'nonce': tx.nonce,
                            'gas_price': self.w3.from_wei(tx.gasPrice, 'gwei')
                        })
                        
            except Exception as e:
                continue
        
        return transfers
    
    def identify_transfer_type(self, to_address):
        """Identify what type of transfer this was"""
        if to_address.lower() == self.starkgate.lower():
            return "🚀 StarkGate Bridge (AI)"
        elif to_address.lower() == self.orbiter.lower():
            return "⚠️ Orbiter Bridge"
        else:
            return "❓ Other/Manual"
    
    def track_transfers(self):
        """Main tracking function"""
        print('⚡ PHANTOM TRANSFER TRACKER')
        print('=' * 40)
        
        # Get current status
        status = self.get_current_status()
        print(f'Current Balance: {status["balance"]:.6f} ETH')
        print(f'Total Transfers: {status["total_sent"]}')
        print('')
        
        # Find recent transfers
        transfers = self.find_recent_transfers()
        
        if not transfers:
            print('No recent transfers found')
            return
        
        print(f'📋 RECENT TRANSFERS:')
        total_sent = 0
        
        for i, tx in enumerate(transfers, 1):
            transfer_type = self.identify_transfer_type(tx['to'])
            total_sent += float(tx['value'])
            
            print(f''
                  f'Transfer {i}:')
            print(f'  Type: {transfer_type}')
            print(f'  Amount: {tx["value"]:.6f} ETH')
            print(f'  To: {tx["to"]}')
            print(f'  Block: {tx["block"]}')
            print(f'  Hash: {tx["hash"]}')
            print(f'  Explorer: https://basescan.org/tx/{tx["hash"]}')
        
        print('')
        print(f'💰 SUMMARY:')
        print(f'  Recent Total Sent: {total_sent:.6f} ETH')
        print(f'  Current Balance: {status["balance"]:.6f} ETH')
        print(f'  Lifetime Transfers: {status["total_sent"]}')

if __name__ == "__main__":
    tracker = PhantomTransferTracker()
    tracker.track_transfers()
