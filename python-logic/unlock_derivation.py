"""
Unlock Derivation - Salt Discovery Protocol
Uses core AddressSearchEngine to find class hash/salt combos.
"""

import os
import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from foundation.legacy_env import load_env_manual
    from engines.search import AddressSearchEngine
except Exception as e:
    print(f"❌ Failed to import core modules: {e}")
    raise


def find_my_recipe():
    """Find the exact parameters that generate the target address"""
    load_env_manual()
    engine = AddressSearchEngine()

    hashes = [
        0x01A7366993B74E484C2FA434313F89832207B53F609E25D26A27A26A27A26A27,
        0x036078334509B514626504EDC9FB252328D1A240E4E948BEF8D0C08DFF45927F,
        0x029927C8AF6BCCF3F639A0259E64E99A5A8C711A35C1A35C1A35C1A35C1A35C1,
        0x041D788F01C2B6F914B5FD7E07B5E4B0E9E5E5E5E5E5E5E5E5E5E5E5E5E5E5E5E5,
        0x03331BB0B7B955DFB643775CF5EAD54378770CD0B58851EB065B5453C4F15089,
        0x0539F522860B093C83664D4C5709968853F3E828D57D740F941F1738722A4501,
        0x025EC026985A3BF9D0CC53FE6A9428574C4915EBF8A8E0A9B9B9B9B9B9B9B9B9B,
        0x071707E7C4F2B8C1E7D6E5F4E3D2C1B0A9F8E7D6C5B4A392817261514131211,
    ]

    constructor_patterns = [[None, 0], [None], [None, 1], [None, None]]

    result = engine.expanded_search(
        hashes=hashes,
        salt_range=100,
        constructor_patterns=constructor_patterns,
    )

    if result.get("success"):
        print(f"\n🎉 **MATCH FOUND!** 🎉")
        print(f"Class Hash: {result['hash']}")
        print(f"Salt: {result['salt']}")
        print(f"Constructor: {result['calldata']}")
        print(f"Target: {result['target']}")
        print(f"\n🚀 Next: Use these parameters in argent_emergency_exit.py")
    else:
        print(f"\n❌ FAILED - No derivation match found")
        print(f"💡 Consider: portfolio.argent.xyz for manual recovery")

    return result


if __name__ == "__main__":
    result = find_my_recipe()
    if result.get("success"):
        print(f"\n✅ SUCCESS! Ready for deployment with found parameters!")
    else:
        print(f"\n⚠️ May need custom class hash or salt")
