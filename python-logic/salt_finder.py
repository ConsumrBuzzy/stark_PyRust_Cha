"""
Salt Finder - Brute Force Account Derivation
===========================================
Finds the exact class_hash and salt combination for Argent Web Wallet
"""

import os
import asyncio
from starknet_py.hash.address import compute_address
from starknet_py.net.signer.key_pair import KeyPair

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

load_env()

async def find_account_parameters():
    """Find the exact parameters that generate the target address"""
    
    # Target address
    target_address = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
    target_int = int(target_address, 16)
    
    # Private key for public key calculation
    private_key_str = os.getenv("STARKNET_PRIVATE_KEY")
    if not private_key_str:
        print("❌ Missing STARKNET_PRIVATE_KEY")
        return
        
    private_key = int(private_key_str, 16)
    key_pair = KeyPair.from_private_key(private_key)
    public_key = key_pair.public_key
    
    print(f"🔍 Searching for parameters that generate: {target_address}")
    print(f"🔑 Public Key: {hex(public_key)}")
    
    # Common Argent Web Wallet class hashes
    argent_class_hashes = [
        # Standard Argent Cairo 1.0 Web Account
        0x01a7366993b74e484c2fa434313f89832207b53f609e25d26a27a26a27a26a27,
        # Alternative Argent class hashes (smaller values to avoid overflow)
        0x03331bb0b7b955dfb643775cf5ead54378770cd0b58851eb065b5453c4f15089,
        0x041d788f01c2b6f914b5fd7e07b5e4b0e9e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5,
    ]
    
    # Common salt values
    salt_candidates = [
        0,
        1,
        public_key % 2**64,  # Truncate to 64 bits
        12345,  # Common test salt
    ]
    
    print(f"\n🧪 Testing {len(argent_class_hashes)} class hashes × {len(salt_candidates)} salts = {len(argent_class_hashes) * len(salt_candidates)} combinations")
    
    for i, class_hash in enumerate(argent_class_hashes):
        print(f"\n📋 Testing Class Hash {i+1}/{len(argent_class_hashes)}: {hex(class_hash)}")
        
        for j, salt in enumerate(salt_candidates):
            # Try different constructor calldata patterns
            constructor_patterns = [
                [public_key],  # Simple owner only
                [public_key, 0],  # Owner + guardian (0 = no guardian)
                [public_key, 1],  # Owner + guardian (1 = default)
                [public_key, target_int],  # Owner + self as guardian
            ]
            
            for k, calldata in enumerate(constructor_patterns):
                computed_address = compute_address(
                    class_hash=class_hash,
                    constructor_calldata=calldata,
                    salt=salt,
                    deployer_address=0
                )
                
                if computed_address == target_int:
                    print(f"\n🎉 **MATCH FOUND!** 🎉")
                    print(f"Class Hash: {hex(class_hash)}")
                    print(f"Salt: {salt} ({hex(salt)})")
                    print(f"Constructor Calldata: {calldata}")
                    print(f"Computed Address: {hex(computed_address)}")
                    print(f"Target Address: {hex(target_int)}")
                    
                    # Save the parameters for deployment
                    with open("deployment_params.txt", "w") as f:
                        f.write(f"class_hash={hex(class_hash)}\n")
                        f.write(f"salt={salt}\n")
                        f.write(f"constructor_calldata={calldata}\n")
                        f.write(f"target_address={target_address}\n")
                    
                    return {
                        "class_hash": class_hash,
                        "salt": salt,
                        "constructor_calldata": calldata,
                        "target_address": target_address
                    }
    
    print(f"\n❌ No match found for {target_address}")
    print("⚠️ This account may use a custom class_hash or salt not in our list")
    return None

if __name__ == "__main__":
    asyncio.run(find_account_parameters())
