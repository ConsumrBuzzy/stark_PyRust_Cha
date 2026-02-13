#!/usr/bin/env python3
"""
Account Activation - Self-Funded Proxy Deploy
Activates undeployed StarkNet account using internal ETH balance
"""

import asyncio
import os
import sys
from pathlib import Path

# Add core to path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.models import StarknetChainId
from rich.console import Console

class AccountActivator:
    """Activates undeployed StarkNet accounts"""
    
    def __init__(self):
        self.console = Console()
        self.load_env()
        
        # Account configuration
        self.wallet_address = os.getenv("STARKNET_WALLET_ADDRESS")
        self.private_key = os.getenv("STARKNET_PRIVATE_KEY")
        self.rpc_url = os.getenv("STARKNET_MAINNET_URL")  # Alchemy
        
        # Argent proxy class hash (standard for most accounts)
        self.argent_proxy_hash = 0x06d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b
        
        if not all([self.wallet_address, self.private_key, self.rpc_url]):
            raise ValueError("Missing required environment variables")
    
    def load_env(self):
        """Load environment variables"""
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key.strip()] = value.strip()
    
    async def activate_account(self, dry_run: bool = False):
        """Activate the undeployed account"""
        
        self.console.print("🚀 Account Activation - Self-Funded Proxy Deploy", style="bold blue")
        
        try:
            # Initialize client
            client = FullNodeClient(node_url=self.rpc_url)
            
            # Create key pair
            private_key_int = int(self.private_key, 16)
            key_pair = KeyPair.from_private_key(private_key_int)
            
            # Convert address to int
            address_int = int(self.wallet_address, 16)
            
            self.console.print(f"📍 Target Address: {self.wallet_address}")
            self.console.print(f"🔑 Key Pair: {key_pair.public_key:064x}")
            self.console.print(f"📡 RPC: {self.rpc_url[:50]}...")
            
            if dry_run:
                self.console.print("🔍 DRY RUN MODE - Connectivity Check Only")
                
                # Test basic connectivity
                from starknet_py.net.client_models import Call
                from starknet_py.hash.selector import get_selector_from_name
                
                # Simple block number check
                block_number = await client.get_block_number()
                self.console.print(f"✅ RPC Connectivity: Block {block_number}")
                
                # Test ETH contract call
                eth_contract = 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7
                call = Call(
                    to_addr=eth_contract,
                    selector=get_selector_from_name("balanceOf"),
                    calldata=[address_int]
                )
                
                result = await client.call_contract(call)
                balance_eth = result[0] / 1e18
                self.console.print(f"💰 Account Balance: {balance_eth:.6f} ETH")
                
                if balance_eth >= 0.01:
                    self.console.print("✅ Sufficient balance for activation")
                    self.console.print(f"💡 Estimated activation cost: ~0.01-0.02 ETH")
                else:
                    self.console.print("⚠️ Low balance - activation may fail")
                
                return True
            
            # Real activation
            self.console.print("🔥 Attempting account activation...")
            
            # Fix API compatibility - remove chain parameter
            deploy_result = await Account.deploy_account_v3(
                address=address_int,
                class_hash=self.argent_proxy_hash,
                salt=0,  # Standard salt
                key_pair=key_pair,
                client=client,
                constructor_calldata=[key_pair.public_key, 0],
                max_fee=int(0.01e18),  # 0.01 ETH max fee
            )
            
            self.console.print(f"✅ Activation Broadcast: {hex(deploy_result.hash)}")
            self.console.print("⏳ Waiting for transaction acceptance...")
            
            # Wait for acceptance
            await deploy_result.wait_for_acceptance()
            
            self.console.print("🎉 ACCOUNT IS NOW LIVE!", style="bold green")
            self.console.print(f"🔗 Transaction: {deploy_result.hash}")
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Activation Failed: {e}", style="bold red")
            
            # Provide troubleshooting tips
            if "insufficient balance" in str(e).lower():
                self.console.print("💡 Tip: Ensure account has at least 0.01 ETH for activation fees")
            elif "already deployed" in str(e).lower():
                self.console.print("💡 Tip: Account appears to already be deployed")
            elif "invalid signature" in str(e).lower():
                self.console.print("💡 Tip: Check private key matches the account address")
            
            return False

async def main():
    """Main execution"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="StarkNet Account Activation")
    parser.add_argument("--dry-run", action="store_true", help="Connectivity check only")
    args = parser.parse_args()
    
    try:
        activator = AccountActivator()
        success = await activator.activate_account(dry_run=args.dry_run)
        
        if args.dry_run:
            print("\n✅ Dry run completed - Connectivity verified")
        elif success:
            print("\n✅ Account activation completed successfully!")
            print("💼 The account is now ready for transactions")
        else:
            print("\n❌ Account activation failed")
            print("🔧 Check the error message above and retry")
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
