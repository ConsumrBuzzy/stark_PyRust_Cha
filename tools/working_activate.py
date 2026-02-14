#!/usr/bin/env python3
"""
Working StarkNet Account Activation
Based on latest starknet.py API documentation
"""

import asyncio
import os
from pathlib import Path

from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.hash.address import compute_address
from starknet_py.net.client_models import Call
from starknet_py.hash.selector import get_selector_from_name

# Load environment
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key.strip()] = value.strip()

async def activate_account():
    """Activate StarkNet account using correct API"""
    print("🚀 StarkNet Account Activation")
    print("=" * 40)
    
    # Configuration
    wallet_address = os.getenv("STARKNET_WALLET_ADDRESS")
    private_key = os.getenv("STARKNET_PRIVATE_KEY")
    rpc_url = "https://starknet-mainnet.g.alchemy.com/starknet/version/rpc/v0_10/demo"
    
    if not all([wallet_address, private_key]):
        print("❌ Missing environment variables")
        return False
    
    # Convert addresses to integers
    address_int = int(wallet_address, 16)
    private_key_int = int(private_key, 16)
    
    # Create key pair
    key_pair = KeyPair.from_private_key(private_key_int)
    
    # Create client
    client = FullNodeClient(node_url=rpc_url)
    
    print(f"📍 Address: {wallet_address}")
    print(f"🔑 Public Key: {key_pair.public_key:064x}")
    print(f"📡 RPC: {rpc_url}")
    
    # Check balance
    try:
        eth_contract = int(
            os.getenv(
                "STARKNET_ETH_CONTRACT",
                "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
            ),
            16,
        )
        
        call = Call(
            to_addr=eth_contract,
            selector=get_selector_from_name("balanceOf"),
            calldata=[address_int],
        )
        
        result = await client.call_contract(call)
        balance_eth = result[0] / 1e18
        
        print(f"💰 Balance: {balance_eth:.6f} ETH")
        
        if balance_eth < 0.01:
            print("❌ Insufficient balance for activation")
            return False
        
        print("✅ Sufficient balance for activation")
        
    except Exception as e:
        print(f"❌ Balance check failed: {e}")
        return False
    
    # Get class hash
    class_hash = int(
        os.getenv(
            "STARKNET_ARGENT_PROXY_HASH",
            "0x06d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b",
        ),
        16,
    )
    
    print(f"🏗️  Class Hash: {hex(class_hash)}")
    
    try:
        # Create account instance for deployment
        account = Account(
            address=address_int,
            client=client,
            key_pair=key_pair,
            chain=StarknetChainId.MAINNET,
        )
        
        # Sign deploy transaction
        deploy_invoke_tx = await account.sign_deploy_transaction(
            class_hash=class_hash,
            contract_address_salt=0,
            constructor_calldata=[key_pair.public_key, 0],
            max_fee=int(0.01e18),
        )
        
        print("🔥 Deploying account...")
        
        # Send transaction
        response = await client.send_transaction(deploy_invoke_tx)
        tx_hash = response.transaction_hash
        
        print(f"✅ Transaction sent: {hex(tx_hash)}")
        print("⏳ Waiting for acceptance...")
        
        # Wait for acceptance
        from starknet_py.net.client_models import TransactionStatus
        
        while True:
            receipt = await client.get_transaction_receipt(tx_hash)
            if receipt.execution_status == TransactionStatus.SUCCEEDED:
                break
            elif receipt.execution_status == TransactionStatus.REJECTED:
                print(f"❌ Transaction rejected: {receipt.revert_reason}")
                return False
            await asyncio.sleep(2)
        
        print("🎉 ACCOUNT ACTIVATED SUCCESSFULLY!")
        print(f"🔗 Transaction: {hex(tx_hash)}")
        return True
        
    except Exception as e:
        print(f"❌ Activation failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(activate_account())
