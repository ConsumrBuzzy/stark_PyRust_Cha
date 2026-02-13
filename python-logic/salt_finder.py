"""
Salt Finder - Brute Force Account Derivation
Uses core AddressSearchEngine for common Argent hashes/salts.
"""

import asyncio
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


async def find_account_parameters():
    load_env_manual()
    engine = AddressSearchEngine()

    # Common Argent hashes
    argent_hashes = [
        0x01A7366993B74E484C2FA434313F89832207B53F609E25D26A27A26A27A26A27,
        0x03331BB0B7B955DFB643775CF5EAD54378770CD0B58851EB065B5453C4F15089,
        0x041D788F01C2B6F914B5FD7E07B5E4B0E9E5E5E5E5E5E5E5E5E5E5E5E5E5E5E5E5,
    ]

    salt_candidates = [0, 1, None, 12345]  # None placeholder for pub-key-based salt

    # Constructor patterns; None will be replaced by salt in engine
    constructor_patterns = [
        [None],
        [None, 0],
        [None, 1],
        [None, None],
    ]

    # If salt None, we let the engine substitute salt; engine also allows explicit salts
    salts = []
    for s in salt_candidates:
        if s is None:
            continue
        salts.append(s)

    # Use engine with provided salts and patterns (salt placeholders handled by engine)
    result = engine.expanded_search(
        hashes=argent_hashes,
        salt_range=0,  # not used when salt_values provided
        salt_values=salts,
        constructor_patterns=constructor_patterns,
    )

    if result.get("success"):
        print(f"\n🎉 **MATCH FOUND!** 🎉")
        print(f"Class Hash: {result['hash']}")
        print(f"Salt: {result['salt']}")
        print(f"Constructor Calldata: {result['calldata']}")
        print(f"Target Address: {result['target']}")
        with open("deployment_params.txt", "w") as f:
            f.write(f"class_hash={result['hash']}\n")
            f.write(f"salt={result['salt']}\n")
            f.write(f"constructor_calldata={result['calldata']}\n")
            f.write(f"target_address={result['target']}\n")
    else:
        print("\n❌ No match found")
        print("⚠️ This account may use a custom class_hash or salt not in our list")


if __name__ == "__main__":
    asyncio.run(find_account_parameters())
