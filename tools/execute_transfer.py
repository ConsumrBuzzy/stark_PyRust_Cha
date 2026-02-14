#!/usr/bin/env python3
"""
Execute the transfer to Phantom wallet programmatically
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.ops.audit_ops import run_audit
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.address import compute_address
from starknet_py.hash.transaction import compute_invoke_transaction_hash
from starknet_py.net.client_models import InvokeTransactionV1
from starknet_py.hash.utils import message_signature

async def execute_transfer():
    """Execute the transfer to Phantom wallet"""
    print("🚀 Executing Transfer to Phantom")
    print("=" * 40)
    
    # Load environment
    env_path = Path(__file__).parent.parent / ".env"
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key.strip()] = value.strip()
    
    starknet_address = os.getenv("STARKNET_WALLET_ADDRESS")
    private_key = os.getenv("STARKNET_PRIVATE_KEY")
    phantom_address = "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
    
    print(f"📍 From: {starknet_address}")
    print(f"📍 To: {phantom_address}")
    
    # Get balance
    try:
        result = await run_audit(
            ghost_address="0x000000000000000000000000ff01e0776369ce51debb16dfb70f23c16d875463",
            main_address=starknet_address
        )
        
        balance_eth = float(result.main_balance_eth)
        print(f"💰 Current Balance: {balance_eth:.6f} ETH")
        
        if balance_eth < 0.001:
            print("❌ Balance too low for transfer")
            return False
        
        # Calculate transfer amount
        transfer_amount_wei = int((balance_eth - 0.001) * 1e18)
        transfer_eth = (balance_eth - 0.001)
        print(f"💸 Transfer Amount: {transfer_eth:.6f} ETH")
        
        # Connect to RPC
        client = FullNodeClient(node_url="https://starknet.drpc.org")
        
        # Create account
        private_key_int = int(private_key, 16)
        key_pair = KeyPair.from_private_key(private_key_int)
        address_int = int(starknet_address, 16)
        
        from starknet_py.net.models import StarknetChainId
        
        account = Account(
            address=address_int,
            client=client,
            key_pair=key_pair,
            chain=StarknetChainId.MAINNET,
        )
        
        # Get nonce
        nonce = await account.get_nonce()
        print(f"🔢 Nonce: {nonce}")
        
        # Create transfer call
        eth_contract = int("0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7", 16)
        transfer_selector = get_selector_from_name("transfer")
        
        call = Call(
            to_addr=eth_contract,
            selector=transfer_selector,
            calldata=[
                int(phantom_address, 16),  # recipient
                transfer_amount_wei,        # amount
                0x0                      # padding
            ]
        )
        
        # Execute transfer
        print(f"🔥 Executing transfer...")
        
        try:
            # Calculate transaction hash
            tx_hash = compute_invoke_transaction_hash(
                version=1,
                sender_address=address_int,
                calldata=call.calldata,
                nonce=nonce,
                max_fee=int(0.01e18),
                signature=[],
                account_deployment=0,
                calldata_len=len(call.calldata)
            )
            
            # Sign transaction
            signature = message_signature(tx_hash, key_pair.private_key)
            
            # Create invoke transaction
            invoke_tx = InvokeTransactionV1(
                version=1,
                sender_address=starknet_address,
                calldata=call.calldata,
                max_fee=int(0.01e18),
                signature=signature,
                nonce=nonce,
                nonce_data_availability_mode="L1",
                fee_data_availability_mode="L1"
            )
            
            # Send transaction
            response = await client.send_transaction(invoke_tx)
            tx_hash = response.transaction_hash
            
            print(f"✅ Transaction sent!")
            print(f"🔗 Transaction Hash: {hex(tx_hash)}")
            print(f"💸 Amount: {transfer_eth:.6f} ETH")
            print(f"🎯 To: {phantom_address}")
            
            # Wait for confirmation
            print("⏳ Waiting for confirmation...")
            
            # Wait for transaction to be processed
            for i in range(30):  # Wait up to 30 seconds
                try:
                    receipt = await client.get_transaction_receipt(tx_hash)
                    if receipt.execution_status.value == 1:  # ACCEPTED_ON_L2
                        print(f"✅ Transaction confirmed!")
                        print(f"🎉 Transfer completed!")
                        return True
                    elif receipt.execution_status.value == 3:  # REJECTED
                        print(f"❌ Transaction rejected")
                        return False
                except:
                    pass
                await asyncio.sleep(1)
            
            print("⏰ Transaction submitted, check status later")
            return True
            
        except Exception as e:
            print(f"❌ Transfer error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(execute_transfer())
