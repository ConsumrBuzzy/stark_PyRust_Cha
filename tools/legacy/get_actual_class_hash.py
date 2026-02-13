import os
import asyncio
from starknet_py.net.full_node_client import FullNodeClient

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

load_env()

async def get_class_hash():
    client = FullNodeClient(node_url=os.getenv('STARKNET_MAINNET_URL'))
    address = 'os.getenv("STARKNET_WALLET_ADDRESS")'
    
    try:
        class_hash = await client.get_class_hash_at(contract_address=int(address, 16))
        print(f'✅ Account Class Hash: {hex(class_hash)}')
        return class_hash
    except Exception as e:
        print(f'❌ Error: {e}')
        return None

if __name__ == "__main__":
    asyncio.run(get_class_hash())
