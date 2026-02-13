"""
Ultimate Search - Final Parameter Discovery
Tests all possible combinations using core search engine.
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


def ultimate_search():
    load_env_manual()
    engine = AddressSearchEngine()
    # Slightly narrower salt range for performance; can be adjusted
    return engine.expanded_search(hashes=_default_hashes(), salt_range=101, constructor_patterns=None)


if __name__ == "__main__":
    result = ultimate_search()

    print(f"\n{'='*60}")
    print(f"🏁 ULTIMATE SEARCH RESULT")
    print(f"{'='*60}")
    
    if result.get("success"):
        print(f"✅ SUCCESS")
        print(f"🔧 Class Hash: {result['hash']}")
        print(f"🧂 Salt: {result['salt']}")
        print(f"📋 Constructor: {result['calldata']}")
        print(f"\n🚀 DEPLOYMENT READY!")
    else:
        print(f"❌ FAILED")
        print(f"💡 {result.get('error')}")
        print(f"\n🌐 FINAL OPTION: portfolio.argent.xyz")
