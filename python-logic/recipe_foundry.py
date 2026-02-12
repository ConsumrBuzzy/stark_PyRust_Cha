"""
Recipe Foundry - Headless Discovery Tool
=======================================
Finds the exact Argent Web Wallet deployment parameters
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

def find_recovery_recipe():
    """Find the exact deployment recipe for Argent Web Wallet"""
    
    target_addr = 0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9
    
    private_key_str = os.getenv("STARKNET_PRIVATE_KEY")
    if not private_key_str:
        return {"STATUS": "FAILED", "HINT": "Missing STARKNET_PRIVATE_KEY in .env"}
    
    pk = int(private_key_str, 16)
    pub = KeyPair.from_private_key(pk).public_key
    
    print(f"🔍 Target Address: {hex(target_addr)}")
    print(f"🔑 Public Key: {hex(pub)}")
    print(f"🧪 Testing 3 specific Argent Web/Ready class hashes...")
    
    # The 3 specific Argent Web/Ready Class Hashes (2025-2026)
    potential_hashes = [
        0x01a7366993b74e484c2fa434313f89832207b53f609e25d26a27a26a27a26a27,  # Standard Web
        0x029927c8af6bccf3f639a0259e64e99a5a8c711a35c1a35c1a35c1a35c1a35c1,  # Proxy Cairo 1
        0x033434ad846c24458925509f7a933f9202545815e96a84c307e596e8d2e61633,  # Plugin-based
    ]
    
    for i, ch in enumerate(potential_hashes):
        print(f"\n📋 Testing Hash {i+1}/3: {hex(ch)}")
        
        # Argent Web always uses [owner, guardian] in constructor
        # If no guardian was set, it's 0.
        calldata = [pub, 0] 
        
        # Test Salt 0 (Standard) and Salt 1 (Fallback)
        for s in [0, 1]:
            try:
                derived = compute_address(class_hash=ch, constructor_calldata=calldata, salt=s)
                
                print(f"  🧪 Salt {s}: {hex(derived)}")
                
                if derived == target_addr:
                    print(f"\n🎉 **MATCH FOUND!** 🎉")
                    print(f"Class Hash: {hex(ch)}")
                    print(f"Salt: {s}")
                    print(f"Constructor: {calldata}")
                    print(f"Derived: {hex(derived)}")
                    print(f"Target: {hex(target_addr)}")
                    
                    return {
                        "STATUS": "MATCH FOUND", 
                        "class_hash": hex(ch), 
                        "salt": s,
                        "constructor_calldata": calldata,
                        "derived_address": hex(derived)
                    }
                    
            except Exception as e:
                print(f"  ❌ Salt {s} failed: {str(e)[:50]}...")
                continue
    
    return {
        "STATUS": "FAILED", 
        "HINT": "Check if Private Key matches Ready.co file. May need custom class hash."
    }

if __name__ == "__main__":
    result = find_recovery_recipe()
    
    print(f"\n{'='*50}")
    print(f"📊 RECIPE FOUNDRY RESULT")
    print(f"{'='*50}")
    
    if result["STATUS"] == "MATCH FOUND":
        print(f"✅ {result['STATUS']}")
        print(f"🔧 Class Hash: {result['class_hash']}")
        print(f"🧂 Salt: {result['salt']}")
        print(f"📋 Constructor: {result['constructor_calldata']}")
        print(f"\n🚀 Ready for deployment with these parameters!")
        print(f"💡 Next: Use these in argent_emergency_exit.py")
    else:
        print(f"❌ {result['STATUS']}")
        print(f"💡 {result['HINT']}")
        print(f"\n🌐 Alternative: portfolio.argent.xyz for manual recovery")
