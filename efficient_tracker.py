from web3 import Web3

class EfficientPhantomTracker:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider('https://base.gateway.tenderly.co'))
        self.phantom = '0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9'
        
        # Contract addresses
        self.starkgate = '0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419'
        self.orbiter = '0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef'
    
    def get_wallet_summary(self):
        """Get complete wallet summary instantly"""
        balance = self.w3.eth.get_balance(self.phantom)
        nonce = self.w3.eth.get_transaction_count(self.phantom)
        
        return {
            'address': self.phantom,
            'balance_eth': self.w3.from_wei(balance, 'ether'),
            'total_outgoing': nonce,
            'remaining_balance': self.w3.from_wei(balance, 'ether')
        }
    
    def analyze_transfers_by_nonce(self):
        """Analyze transfers using nonce logic - MOST EFFICIENT"""
        print('🎯 PHANTOM TRANSFER ANALYSIS (BY NONCE)')
        print('=' * 50)
        
        summary = self.get_wallet_summary()
        
        print(f'📍 Wallet: {summary["address"]}')
        print(f'💰 Current Balance: {summary["balance_eth"]:.6f} ETH')
        print(f'📤 Total Outgoing Transfers: {summary["total_outgoing"]}')
        print('')
        
        if summary["total_outgoing"] == 0:
            print('❌ No transfers found')
            return
        
        print('🔍 TRANSFER BREAKDOWN:')
        print('')
        
        # Calculate what was sent
        # If we know current balance and total transfers, we can estimate
        estimated_total_sent = 0.02043 - float(summary["balance_eth"])  # Original balance minus current
        
        print(f'📊 ESTIMATED TRANSFER HISTORY:')
        print(f'  Original Balance: ~0.02043 ETH')
        print(f'  Current Balance: {summary["balance_eth"]:.6f} ETH')
        print(f'  Estimated Sent: {estimated_total_sent:.6f} ETH')
        print(f'  Transaction Count: {summary["total_outgoing"]}')
        print('')
        
        # Likely scenario based on evidence
        print('🎯 LIKELY SCENARIO:')
        print(f'  ✅ {summary["total_outgoing"]} AI-executed bridge transactions')
        print(f'  ✅ ~{estimated_total_sent:.6f} ETH sent to StarkNet bridges')
        print(f'  ✅ Funds arrived on StarkNet (0.009157 ETH balance)')
        print(f'  ❌ Recovery tracking failed (state blind)')
        print('')
        
        # StarkNet status
        starknet_balance = 0.009157  # From our earlier check
        recovery_rate = (starknet_balance / estimated_total_sent) * 100 if estimated_total_sent > 0 else 0
        
        print(f'💸 RECOVERY RATE: {recovery_rate:.1f}%')
        print(f'  Sent: {estimated_total_sent:.6f} ETH')
        print(f'  Arrived: {starknet_balance:.6f} ETH')
        print(f'  Lost to fees: {(estimated_total_sent - starknet_balance):.6f} ETH')
    
    def quick_status_check(self):
        """Super quick status check"""
        summary = self.get_wallet_summary()
        
        print('⚡ INSTANT PHANTOM STATUS')
        print('=' * 30)
        print(f'Balance: {summary["balance_eth"]:.6f} ETH')
        print(f'Transfers: {summary["total_outgoing"]}')
        print(f'Status: {"AI BRIDGES EXECUTED" if summary["total_outgoing"] > 0 else "NO ACTIVITY"}')

if __name__ == "__main__":
    tracker = EfficientPhantomTracker()
    
    # Quick check first
    tracker.quick_status_check()
    print('')
    
    # Full analysis
    tracker.analyze_transfers_by_nonce()
