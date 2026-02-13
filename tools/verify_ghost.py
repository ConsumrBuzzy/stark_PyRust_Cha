from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient
import asyncio
import os

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

async def check():
    load_env()
    rpc_url = os.getenv("STARKNET_MAINNET_URL") or os.getenv("STARKNET_RPC_URL")
    if not rpc_url:
        print("Error: STARKNET_RPC_URL not found in .env")
        return

    client = FullNodeClient(node_url=rpc_url)
    # ETH Contract Address on Starknet
    eth_address = int(os.getenv("STARKNET_ETH_TOKEN_ADDRESS", "int(os.getenv("STARKNET_ETH_CONTRACT", "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"), 16)"), 16)
    # Derived Starknet equivalent of Transit EVM Wallet
    ghost_address = os.getenv("GHOST_ADDRESS", "os.getenv("STARKNET_GHOST_ADDRESS")")
    
    print(f"--- Direct Starknet RPC Query ---")
    print(f"Target: {ghost_address}")
    print(f"RPC: {rpc_url[:30]}...")

    try:
        # Use simple call for uninitialized accounts
        from starknet_py.hash.selector import get_selector_from_name
        from starknet_py.net.client_models import Call
        
        call = Call(
            to_addr=int(eth_address, 16),
            selector=get_selector_from_name("balanceOf"),
            calldata=[int(ghost_address, 16)]
        )
        res = await client.call_contract(call)
        balance = res[0]
        
        print(f"Wei Balance: {balance}")
        print(f"ETH Balance: {balance / 10**18}")
        
        if balance > 0:
            print("\n✨ SUCCESS: Funds detected on the ledger!")
        else:
            print("\n⌛ STILL PENDING: Orbiter Maker has not released funds yet.")
            
    except Exception as e:
        print(f"Error during RPC call: {e}")

if __name__ == "__main__":
    asyncio.run(check())
