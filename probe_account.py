import asyncio
import os
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.hash.address import compute_address
from rich.console import Console

console = Console()

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

async def probe():
    load_env()
    rpc_url = os.getenv("STARKNET_MAINNET_URL")
    target_addr = os.getenv("STARKNET_WALLET_ADDRESS")
    pk = os.getenv("STARKNET_PRIVATE_KEY")
    
    if not all([rpc_url, target_addr, pk]):
        console.print("[red]❌ Missing data in .env[/red]")
        return

    client = FullNodeClient(node_url=rpc_url)
    key_pair = KeyPair.from_private_key(int(pk, 16))
    pub_key = key_pair.public_key
    
    console.print(f"Target: {target_addr}")
    console.print(f"Pub Key: {hex(pub_key)}")

    # 1. Try to get class hash from chain (if it ever was deployed)
    try:
        class_hash = await client.get_class_hash_at(int(target_addr, 16))
        console.print(f"✅ On-chain Class Hash found: {hex(class_hash)}")
    except Exception as e:
        console.print(f"⌛ Not found on-chain (as expected if undeployed): {e}")

    # 2. Brute-force common salts if it's a known Argent pattern
    # Ready Web Wallet usually uses Argent implementation.
    ARGENT_H = 0x01a736cb7361405e6088e89abcce497702d76537a80e93b0f4270219d365d6b0
    
    # Try common salts
    for salt in [0, pub_key, 1]:
        # Try both ARGENT and OZ patterns
        for name, ch, calldata in [
            ("OZ", 0x061efe27dba2c442a6663364f93bdadd83cb51850e1d00061fa693158c23f80, [pub_key]),
            ("Argent", ARGENT_H, [pub_key, 0]),
            ("Argent (no zero)", ARGENT_H, [pub_key]),
        ]:
            addr = compute_address(class_hash=ch, salt=salt, constructor_calldata=calldata, deployer_address=0)
            if hex(addr) == target_addr.lower():
                console.print(f"✨ [bold green]MATCH:[/bold green] {name} with salt={hex(salt)}")
                return

    console.print("[yellow]⚠ Still no match. This might be a legacy Argent account or a custom Proxy.[/yellow]")

if __name__ == "__main__":
    asyncio.run(probe())
