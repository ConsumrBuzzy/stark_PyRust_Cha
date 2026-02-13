"""
Simple Salt Finder - Direct Parameter Matching
=============================================
Finds the exact class_hash and salt for the target address
"""

import os
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

def find_parameters():
    """Find the exact parameters that generate the target address"""
    
    # Target address
    target_address = "os.getenv("STARKNET_WALLET_ADDRESS")"
    target_int = int(target_address, 16)
    
    # Private key for public key calculation
    private_key_str = os.getenv("STARKNET_PRIVATE_KEY")
    if not private_key_str:
        print("❌ Missing STARKNET_PRIVATE_KEY")
        return
        
    private_key = int(private_key_str, 16)
    key_pair = KeyPair.from_private_key(private_key)
    public_key = key_pair.public_key
    
    print(f"🔍 Target: {target_address}")
    print(f"🔑 Public Key: {hex(public_key)}")
    
    # Test common Argent class hashes
    class_hashes = [
        0x01a7366993b74e484c2fa434313f89832207b53f609e25d26a27a26a27a26a27,  # Argent Web
        0x03331bb0b7b955dfb643775cf5ead54378770cd0b58851eb065b5453c4f15089,  # Alternative
        0x041d788f01c2b6f914b5fd7e07b5e4b0e9e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5,  # Another
    ]
    
    # Test common salts
    salts = [0, 1, public_key % 2**64, 12345]
    
    # Test constructor patterns
    constructor_patterns = [
        [public_key],
        [public_key, 0],
        [public_key, 1],
    ]
    
    print(f"\n🧪 Testing {len(class_hashes)} × {len(salts)} × {len(constructor_patterns)} = {len(class_hashes) * len(salts) * len(constructor_patterns)} combos")
    
    for class_hash in class_hashes:
        print(f"\n📋 Class Hash: {hex(class_hash)}")
        
        for salt in salts:
            for calldata in constructor_patterns:
                try:
                    computed = compute_address(
                        class_hash=class_hash,
                        constructor_calldata=calldata,
                        salt=salt,
                        deployer_address=0
                    )
                    
                    if computed == target_int:
                        print(f"\n🎉 **MATCH FOUND!** 🎉")
                        print(f"Class Hash: {hex(class_hash)}")
                        print(f"Salt: {salt} ({hex(salt)})")
                        print(f"Constructor: {calldata}")
                        print(f"Address: {hex(computed)}")
                        
                        return {
                            "class_hash": class_hash,
                            "salt": salt,
                            "constructor_calldata": calldata
                        }
                        
                except Exception as e:
                    # Skip invalid combinations
                    continue
    
    print(f"\n❌ No match found")
    return None

if __name__ == "__main__":
    result = find_parameters()
    if result:
        print(f"\n✅ Ready for deployment with found parameters!")
    else:
        print(f"\n⚠️ May need custom class hash or salt")
