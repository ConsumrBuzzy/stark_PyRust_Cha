import os
import sys
import asyncio
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

def get_keys():
    pk = os.getenv("STARKNET_PRIVATE_KEY")
    if not pk:
        # Fallback to SOLANA_PRIVATE_KEY as per orchestrator.py
        pk_base58 = os.getenv("SOLANA_PRIVATE_KEY")
        if pk_base58:
            import base58
            pk_bytes = base58.b58decode(pk_base58)
            # Use first 32 bytes or similar
            pk = hex(int.from_bytes(pk_bytes[:32], 'big'))
    
    if pk:
        if pk.startswith("0x"):
            key_pair = KeyPair.from_private_key(int(pk, 16))
        else:
            # Handle possible base10 or other formats
            try:
                key_pair = KeyPair.from_private_key(int(pk))
            except ValueError:
                key_pair = None
        return key_pair
    return None

def debug():
    load_env()
    target_addr = os.getenv("STARKNET_WALLET_ADDRESS")
    if not target_addr:
        console.print("[red]❌ STARKNET_WALLET_ADDRESS not found in .env[/red]")
        return

    key_pair = get_keys()
    if not key_pair:
        console.print("[red]❌ Could not derive KeyPair. Check STARKNET_PRIVATE_KEY or SOLANA_PRIVATE_KEY.[/red]")
        return

    pub_key = key_pair.public_key
    console.print(f"Pub Key: {hex(pub_key)}")
    console.print(f"Target Addr: {target_addr.lower()}")

    # Common Class Hashes
    # OpenZeppelin v0.8.0/0.8.1
    OZ_CLASS_HASH = 0x061efe27dba2c442a6663364f93bdadd83cb51850e1d00061fa693158c23f80 
    # Argent X v0.2.3+ Proxy
    ARGENT_PROXY_HASH = 0x025ec026985a3bf6d08b14771408d2de02d76537a80e93b0f4270219d365d6b0
    # Argent X v0.3.0+ Implementation
    ARGENT_IMPL_HASH = 0x01a736cb7361405e6088e89abcce497702d76537a80e93b0f4270219d365d6b0

    classes = [
        ("OpenZeppelin (salt=pub_key)", OZ_CLASS_HASH, pub_key, [pub_key]),
        ("OpenZeppelin (salt=0)", OZ_CLASS_HASH, 0, [pub_key]),
        ("Argent (salt=pub_key)", ARGENT_IMPL_HASH, pub_key, [pub_key, 0]),
        ("Argent (salt=0)", ARGENT_IMPL_HASH, 0, [pub_key, 0]),
    ]

    found = False
    for name, class_hash, salt, calldata in classes:
        addr = compute_address(
            class_hash=class_hash,
            salt=salt,
            constructor_calldata=calldata,
            deployer_address=0
        )
        if hex(addr) == target_addr.lower():
            console.print(f"[bold green]✨ MATCH FOUND: {name}[/bold green]")
            console.print(f"   Class Hash: {hex(class_hash)}")
            console.print(f"   Salt: {hex(salt)}")
            console.print(f"   Calldata: {[hex(x) for x in calldata]}")
            found = True
            break
        else:
            console.print(f"[dim]No match for {name}: {hex(addr)}[/dim]")

    if not found:
        console.print("[yellow]⚠ No standard matches found. Is this a Braavos or Argent X Proxy account?[/yellow]")

if __name__ == "__main__":
    debug()
