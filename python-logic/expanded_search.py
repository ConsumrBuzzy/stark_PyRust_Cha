"""
Expanded Search - Extended Parameter Discovery
Tests wider range of class hashes and salts using core search engine.
"""

import os
import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from foundation.legacy_env import load_env_manual
    from engines.search import AddressSearchEngine, _default_hashes
except Exception as e:
    print(f"❌ Failed to import core modules: {e}")
    raise


def expanded_search():
    load_env_manual()
    engine = AddressSearchEngine()
    return engine.expanded_search(hashes=_default_hashes(), salt_range=1000)


if __name__ == "__main__":
    result = expanded_search()
    if result.get("success"):
        print(f"\n✅ FOUND! Hash: {result['hash']}, Salt: {result['salt']}")
    else:
        print(f"\n❌ Still no match - this account is truly custom")
