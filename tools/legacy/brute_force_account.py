import asyncio
import os
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

async def brute_force():
    load_env()
    target_addr = os.getenv("STARKNET_WALLET_ADDRESS").lower()
    pk = os.getenv("STARKNET_PRIVATE_KEY")
    
    key_pair = KeyPair.from_private_key(int(pk, 16))
    pub_key = key_pair.public_key
    
    # Class Hashes to test
    hashes = {
        "OZ 0.7.0": 0x048dd51ef690f584af33dbfe2ea2cc2a4f3169147d310112444101100000000,
        "OZ 0.8.0": 0x061efe27dba2c442a6663364f93bdadd83cb51850e1d00061fa693158c23f80,
        "Argent v0.4.0": 0x033434ad846c2d239b64bb9c65f0cb27320d1dd408d66050b1df9a0f7e44923e,
        "Argent v0.5.0": 0x01a736cb7361405e6088e89abcce497702d76537a80e93b0f4270219d365d6b0,
        "Argent Proxy": 0x025ec026985a3bf6d08b14771408d2de02d76537a80e93b0f4270219d365d6b0,
        "Braavos Base": 0x05aa23d5bb0948726559a835a21e4c020117a298910041695493019808f9720b,
        "Argent X (some versions)": 0x036078334509b514626504edc9fb252328d1a240e4e948bef8d0c08dff45927f
    }

    salts = [0, pub_key, 1]
    
    # Common constructor calldatas
    calldatas = [
        [pub_key],           # OZ, Braavos
        [pub_key, 0],        # Argent
        [0, pub_key, 1],     # Argent v0.4.0 official
        [hashes["Argent v0.5.0"], 0x2dd76537a80e93b0f4270219d365d6b0, pub_key, 0] # Argent Proxy
    ]

    for h_name, h_val in hashes.items():
        for salt in salts:
            for cd in calldatas:
                try:
                    addr = compute_address(class_hash=h_val, salt=salt, constructor_calldata=cd, deployer_address=0)
                    if hex(addr) == target_addr:
                        console.print(f"🎯 [bold green]FOUND MATCH![/bold green]")
                        console.print(f"   Name: {h_name}")
                        console.print(f"   Hash: {hex(h_val)}")
                        console.print(f"   Salt: {hex(salt)}")
                        console.print(f"   Calldata: {[hex(x) for x in cd]}")
                        return
                except:
                    continue

    console.print("[red]❌ No standard matches. Requesting help from user/further research.[/red]")

if __name__ == "__main__":
    asyncio.run(brute_force())
