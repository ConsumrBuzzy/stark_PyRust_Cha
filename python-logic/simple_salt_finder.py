"""
Simple Salt Finder - Direct Parameter Matching
Uses core AddressSearchEngine for common Argent class hashes and salts.
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


def find_parameters():
    load_env_manual()
    engine = AddressSearchEngine()

    class_hashes = [
        0x01A7366993B74E484C2FA434313F89832207B53F609E25D26A27A26A27A26A27,
        0x03331BB0B7B955DFB643775CF5EAD54378770CD0B58851EB065B5453C4F15089,
        0x041D788F01C2B6F914B5FD7E07B5E4B0E9E5E5E5E5E5E5E5E5E5E5E5E5E5E5E5E5,
    ]

    salts = [0, 1, 12345]
    constructor_patterns = [[None], [None, 0], [None, 1]]

    result = engine.expanded_search(
        hashes=class_hashes,
        salt_range=0,
        salt_values=salts,
        constructor_patterns=constructor_patterns,
    )

    if result.get("success"):
        print(f"\n🎉 **MATCH FOUND!** 🎉")
        print(f"Class Hash: {result['hash']}")
        print(f"Salt: {result['salt']}")
        print(f"Constructor: {result['calldata']}")
        return result

    print(f"\n❌ No match found")
    return None


if __name__ == "__main__":
    result = find_parameters()
    if result:
        print(f"\n✅ Ready for deployment with found parameters!")
    else:
        print(f"\n⚠️ May need custom class hash or salt")
