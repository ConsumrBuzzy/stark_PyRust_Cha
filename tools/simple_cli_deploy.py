#!/usr/bin/env python3
"""
Simple CLI StarkNet Account Deployment
"""

import asyncio
import os
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def deploy_account():
    """Deploy account using CLI"""
    print("🚀 Simple CLI StarkNet Account Deployment")
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
        
        # Import starknet components
        from starknet_py.net.full_node_client import FullNodeClient
        from starknet_py.net.signer.key_pair import KeyPair
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
            "https://starknet-mainnet.g.alchemy.com/v2/demo",
        ]
        
        client = None
        for rpc_url in rpc_urls:
            try:
                client = FullNodeClient(node_url=rpc_url)
                # Test connection
                await client.get_block_number()
                print(f"✅ Connected to: {rpc_url}")
                break
            except Exception as e:
                print(f"❌ Failed: {rpc_url} - {str(e)[:50]}")
                continue
        
        if not client:
            print("❌ All RPCs failed")
            return False
        
        # Check balance
        address_int = int(wallet_address, 16)
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
        
        print("✅ Sufficient balance for deployment")
        
        # Create deployment transaction
        from starknet_py.net.models import DeployAccountV1
        
        class_hash = int("0x06d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b", 16)
        private_key_int = int(private_key, 16)
        key_pair = KeyPair.from_private_key(private_key_int)
        
        # Create deployment transaction without signature first
        deploy_tx = DeployAccountV1(
            class_hash=class_hash,
            contract_address_salt=0,
            constructor_calldata=[key_pair.public_key, 0],
            max_fee=int(0.01e18),
            version=1,
            nonce=0,
            signature=[],
        )
        
        # Sign transaction using private key directly
        from starknet_py.hash.transaction import compute_deploy_account_transaction_hash
        from starknet_py.hash.utils import message_signature
        
        # Compute transaction hash
        tx_hash = compute_deploy_account_transaction_hash(
            contract_address=address_int,
            class_hash=class_hash,
            salt=0,
            constructor_calldata=[key_pair.public_key, 0],
            max_fee=int(0.01e18),
            version=1,
            nonce=0,
            chain_id=0x534e5f4d41494e4e4554,  # SN_MAINNET
        )
        
        # Sign with private key
        signature = message_signature(tx_hash, key_pair.private_key)
        
        deploy_tx = DeployAccountV1(
            class_hash=class_hash,
            contract_address_salt=0,
            constructor_calldata=[key_pair.public_key, 0],
            max_fee=int(0.01e18),
            version=1,
            nonce=0,
            signature=signature,
        )
        
        print("🔥 Deploying account...")
        
        # Send deployment transaction
        response = await client.deploy_account(deploy_tx)
        tx_hash = response.transaction_hash
        
        print(f"✅ Transaction: {hex(tx_hash)}")
        print("⏳ Waiting for confirmation...")
        
        # Wait for confirmation
        from starknet_py.net.client_models import TransactionStatus
        
        for i in range(60):  # Wait up to 60 seconds
            try:
                receipt = await client.get_transaction_receipt(tx_hash)
                if receipt.execution_status == TransactionStatus.SUCCEEDED:
                    print("🎉 ACCOUNT DEPLOYED SUCCESSFULLY!")
                    print(f"🔗 Transaction: {hex(tx_hash)}")
                    print("💼 Ready for Influence game!")
                    return True
                elif receipt.execution_status == TransactionStatus.REJECTED:
                    print(f"❌ Transaction rejected")
                    return False
            except Exception as e:
                pass
            await asyncio.sleep(1)
        
        print("⏳ Transaction submitted, check later...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(deploy_account())
