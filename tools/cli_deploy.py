#!/usr/bin/env python3
"""
CLI StarkNet Account Deployment
Works when web explorers are down
"""

import asyncio
import os
import json
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def deploy_account_cli():
    """Deploy account using CLI when web is down"""
    print("🚀 CLI StarkNet Account Deployment")
    print("=" * 40)
    
    try:
        # Load environment
        env_path = Path(__file__).parent.parent / ".env"
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key.strip()] = value.strip()
        
        # Configuration
        wallet_address = os.getenv("STARKNET_WALLET_ADDRESS")
        private_key = os.getenv("STARKNET_PRIVATE_KEY")
        
        print(f"📍 Address: {wallet_address}")
        print(f"🔑 Key: {private_key[:10]}...")
        
        # Use starknet-js style deployment
        from starknet_py.net.full_node_client import FullNodeClient
        from starknet_py.net.signer.key_pair import KeyPair
        from starknet_py.hash.address import compute_address
        from starknet_py.net.account.account import Account
        from starknet_py.net.client_models import Call
        from starknet_py.hash.selector import get_selector_from_name
        
        # Try multiple RPCs
        rpc_urls = [
            "https://starknet-mainnet.public.blastapi.io",
            "https://starknet-mainnet.g.alchemy.com/starknet/version/rpc/v0_10/demo",
            "https://starknet.rpc.lava.build",
            "https://starknet.api.onfinality.io/public",
            "https://1rpc.io/starknet",
            "https://rpc.starknet.lava.build:443",
            "https://starknet-mainnet.public.blastapi.io/rpc/v0_6",
            "https://starknet-goerli.public.blastapi.io",
            "https://starknet-mainnet.g.alchemy.com/v2/demo",
            "https://starknet-mainnet.infura.io/v3/demo",
        ]
        
        client = None
        for rpc_url in rpc_urls:
            try:
                client = FullNodeClient(node_url=rpc_url)
                # Test connection
                await client.get_block_number()
                print(f"✅ Connected to: {rpc_url}")
                break
            except:
                print(f"❌ Failed: {rpc_url}")
                continue
        
        if not client:
            print("❌ All RPCs failed")
            return False
        
        # Create account
        address_int = int(wallet_address, 16)
        private_key_int = int(private_key, 16)
        key_pair = KeyPair.from_private_key(private_key_int)
        
        # Check balance
        from starknet_py.net.models import Call
        from starknet_py.hash.selector import get_selector_from_name
        
        eth_contract = int("0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7", 16)
        
        call = Call(
            to_addr=eth_contract,
            selector=get_selector_from_name("balanceOf"),
            calldata=[address_int],
        )
        
        result = await client.call_contract(call)
        balance_eth = result[0] / 1e18
        print(f"💰 Balance: {balance_eth:.6f} ETH")
        
        if balance_eth < 0.01:
            print("❌ Insufficient balance")
            return False
        
        # Deploy using raw transaction
        class_hash = int("0x06d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b", 16)
        
        # Create deploy account transaction
        from starknet_py.net.models import DeclareV2, DeployAccount
        
        deploy_tx = DeployAccount(
            class_hash=class_hash,
            contract_address_salt=0,
            constructor_calldata=[key_pair.public_key, 0],
            max_fee=int(0.01e18),
            version=1,
            nonce=0,
        )
        
        # Sign transaction
        signature = key_pair.sign_transaction(deploy_tx)
        deploy_tx.signature = signature
        
        print("🔥 Deploying account...")
        
        # Send transaction
        response = await client.send_transaction(deploy_tx)
        tx_hash = response.transaction_hash
        
        print(f"✅ Transaction: {hex(tx_hash)}")
        print("⏳ Waiting for confirmation...")
        
        # Wait for confirmation
        from starknet_py.net.client_models import TransactionStatus
        
        for i in range(30):  # Wait up to 30 seconds
            try:
                receipt = await client.get_transaction_receipt(tx_hash)
                if receipt.execution_status == TransactionStatus.SUCCEEDED:
                    print("🎉 ACCOUNT DEPLOYED SUCCESSFULLY!")
                    print(f"🔗 Transaction: {hex(tx_hash)}")
                    return True
                elif receipt.execution_status == TransactionStatus.REJECTED:
                    print(f"❌ Transaction rejected")
                    return False
            except:
                pass
            await asyncio.sleep(1)
        
        print("⏳ Transaction submitted, check later...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(deploy_account_cli())
