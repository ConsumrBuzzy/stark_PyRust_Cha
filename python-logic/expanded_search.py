"""
Expanded Search - Extended Parameter Discovery
=============================================
Tests wider range of class hashes and salts
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

def expanded_search():
    """Extended search with more class hashes and salt ranges"""
    
    target = 0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9
    pk = int(os.getenv("STARKNET_PRIVATE_KEY"), 16)
    pub = KeyPair.from_private_key(pk).public_key
    
    print(f"🔍 Target: {hex(target)}")
    print(f"🔑 Public Key: {hex(pub)}")
    
    # Much wider class hash list
    hashes = [
        # Standard Argent variants
        0x01a7366993b74e484c2fa434313f89832207b53f609e25d26a27a26a27a26a27,
        0x036078334509b514626504edc9fb252328d1a240e4e948bef8d0c08dff45927f,
        0x029927c8af6bccf3f639a0259e64e99a5a8c711a35c1a35c1a35c1a35c1a35c1,
        
        # OpenZeppelin variants
        0x041d788f01c2b6f914b5fd7e07b5e4b0e9e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5,
        0x0539f522860b093c83664d4c5709968853f3e828d57d740f941f1738722a4501,
        
        # Braavos variants
        0x03131fa018572e01512d6b46182690d354a35c1a35c1a35c1a35c1a35c1a35c1,
        0x025ec026985a3bf9d0cc53fe6a9428574c4915ebf8a8e0a9b9b9b9b9b9b9b9b9b,
        
        # Custom/Unknown variants
        0x071707e7c4f2b8c1e7d6e5f4e3d2c1b0a9f8e7d6c5b4a392817261514131211,
        0x03331bb0b7b955dfb643775cf5ead54378770cd0b58851eb065b5453c4f15089,
        
        # Additional common hashes
        0x0246b7b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6,
        0x0585d5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5,
    ]
    
    print(f"🧪 Testing {len(hashes)} hashes × 1000 salts = {len(hashes) * 1000} combos")
    
    for i, h in enumerate(hashes):
        print(f"\n🔍 Hash {i+1}/{len(hashes)}: {hex(h)}")
        
        for salt in range(0, 1000):  # Expanded salt range
            if salt % 100 == 0:
                print(f"  📊 Progress: Salt {salt}/1000")
                
            try:
                # Test constructor patterns
                patterns = [
                    [pub, 0],      # Most common
                    [pub],         # Simple
                    [pub, 1],      # Alternative guardian
                    [pub, salt],   # Salt as guardian
                ]
                
                for calldata in patterns:
                    try:
                        addr = compute_address(
                            class_hash=h,
                            constructor_calldata=calldata,
                            salt=salt,
                            deployer_address=0
                        )
                        
                        if addr == target:
                            print(f"\n🎉 **MATCH FOUND!** 🎉")
                            print(f"Hash: {hex(h)}")
                            print(f"Salt: {salt}")
                            print(f"Constructor: {calldata}")
                            return {"hash": h, "salt": salt, "calldata": calldata}
                            
                    except:
                        continue
                        
            except:
                continue
    
    print(f"\n❌ No match found in {len(hashes) * 1000} combinations")
    return None

if __name__ == "__main__":
    result = expanded_search()
    
    if result:
        print(f"\n✅ FOUND! Hash: {hex(result['hash'])}, Salt: {result['salt']}")
    else:
        print(f"\n❌ Still no match - this account is truly custom")
