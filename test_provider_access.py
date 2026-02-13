#!/usr/bin/env python3
"""
Test script to verify provider configuration and client access
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from core.factory import get_provider_factory

async def test_provider_access():
    """Test different ways to access provider clients"""
    
    print("🧪 Testing Provider Configuration Access")
    print("=" * 50)
    
    # Initialize provider factory
    factory = get_provider_factory()
    await factory.check_all_providers()
    
    print(f"📋 Available providers: {list(factory.providers.keys())}")
    
    # Test 1: get_best_provider()
    print("\n🔍 Test 1: get_best_provider()")
    try:
        name, client = factory.get_best_provider()
        print(f"✅ Best provider: {name}")
        print(f"✅ Client type: {type(client)}")
        print(f"✅ Client methods: {[m for m in dir(client) if not m.startswith('_')][:5]}...")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 2: Direct provider access
    print("\n🔍 Test 2: Direct provider config access")
    try:
        for name, config in factory.providers.items():
            print(f"📋 Provider: {name}")
            print(f"   Type: {type(config)}")
            print(f"   Attributes: {[attr for attr in dir(config) if not attr.startswith('_')]}")
            
            if hasattr(config, 'url'):
                print(f"   URL: {config.url}")
                
                # Test creating client
                try:
                    from starknet_py.net.full_node_client import FullNodeClient
                    client = FullNodeClient(node_url=config.url)
                    print(f"   ✅ Client created: {type(client)}")
                    
                    # Test balance call
                    try:
                        from starknet_py.hash.selector import get_selector_from_name
                        from starknet_py.net.client_models import Call
                        
                        call = Call(
                            to_addr=int("0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7", 16),
                            selector=get_selector_from_name("balanceOf"),
                            calldata=[int("0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9", 16)]
                        )
                        
                        result = await client.call_contract(call)
                        balance = result[0] / 1e18
                        print(f"   ✅ Balance check successful: {balance:.6f} ETH")
                        
                    except Exception as e:
                        print(f"   ❌ Balance check failed: {e}")
                        
                except Exception as e:
                    print(f"   ❌ Client creation failed: {e}")
                    
            print()
            
    except Exception as e:
        print(f"❌ Provider access failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_provider_access())
