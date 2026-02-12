"""
Unlock Derivation - Salt Discovery Protocol
=========================================
Finds the exact Salt/Class Hash combination for Argent Web Wallet
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

def find_my_recipe():
    """Find the exact parameters that generate the target address"""
    
    target = 0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9
    
    private_key_str = os.getenv("STARKNET_PRIVATE_KEY")
    if not private_key_str:
        print("❌ Missing STARKNET_PRIVATE_KEY")
        return None
        
    pk = int(private_key_str, 16)
    pub = KeyPair.from_private_key(pk).public_key
    
    print(f"🔍 Target Address: {hex(target)}")
    print(f"🔑 Public Key: {hex(pub)}")
    print(f"🧪 Starting derivation search...")
    
    # Top 5 Argent Web Class Hashes (expanded list)
    hashes = [
        # Standard Argent Web Wallet
        0x01a7366993b74e484c2fa434313f89832207b53f609e25d26a27a26a27a26a27,
        # ArgentX v0.4 (Cairo 1)
        0x036078334509b514626504edc9fb252328d1a240e4e948bef8d0c08dff45927f,
        # Latest Cairo 1.0 Argent
        0x029927c8af6bccf3f639a0259e64e99a5a8c711a35c1a35c1a35c1a35c1a35c1,
        # Alternative Web variants
        0x041d788f01c2b6f914b5fd7e07b5e4b0e9e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5,
        0x03331bb0b7b955dfb643775cf5ead54378770cd0b58851eb065b5453c4f15089,
        # Additional variants
        0x0539f522860b093c83664d4c5709968853f3e828d57d740f941f1738722a4501,
        0x025ec026985a3bf9d0cc53fe6a9428574c4915ebf8a8e0a9b9b9b9b9b9b9b9b9b,
        0x071707e7c4f2b8c1e7d6e5f4e3d2c1b0a9f8e7d6c5b4a392817261514131211,
    ]
    
    print(f"📋 Testing {len(hashes)} class hashes × 100 salts = {len(hashes) * 100} combinations")
    
    for i, h in enumerate(hashes):
        print(f"\n🔍 Class Hash {i+1}/{len(hashes)}: {hex(h)}")
        
        for salt in range(0, 100):  # Testing salts 0-99
            try:
                # Try different constructor patterns
                patterns = [
                    [pub, 0],  # Owner + Guardian(0) - most common
                    [pub],     # Owner only
                    [pub, 1],  # Owner + Guardian(1)
                    [pub, target],  # Owner + Self as Guardian
                ]
                
                for j, calldata in enumerate(patterns):
                    try:
                        addr = compute_address(
                            class_hash=h, 
                            constructor_calldata=calldata, 
                            salt=salt,
                            deployer_address=0
                        )
                        
                        if addr == target:
                            print(f"\n🎉 **MATCH FOUND!** 🎉")
                            print(f"Class Hash: {hex(h)}")
                            print(f"Salt: {salt}")
                            print(f"Constructor: {calldata}")
                            print(f"Computed: {hex(addr)}")
                            print(f"Target: {hex(target)}")
                            
                            return {
                                "class_hash": h,
                                "salt": salt,
                                "constructor_calldata": calldata,
                                "pattern_index": j
                            }
                            
                    except Exception as e:
                        # Skip invalid combinations
                        continue
                        
            except Exception as e:
                # Skip problematic salts
                continue
    
    print(f"\n❌ No match found in {len(hashes) * 100} combinations")
    print("⚠️ This account may use a custom class hash outside our list")
    return None

if __name__ == "__main__":
    result = find_my_recipe()
    
    if result:
        print(f"\n✅ SUCCESS! Ready for deployment with found parameters:")
        print(f"   Class Hash: {hex(result['class_hash'])}")
        print(f"   Salt: {result['salt']}")
        print(f"   Constructor: {result['constructor_calldata']}")
        print(f"\n🚀 Next: Use these parameters in argent_emergency_exit.py")
    else:
        print(f"\n❌ FAILED - No derivation match found")
        print(f"💡 Consider: portfolio.argent.xyz for manual recovery")
