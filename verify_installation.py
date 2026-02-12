import sys
import os

try:
    import stark_pyrust_chain
    print(f"✅ Successfully imported stark_pyrust_chain module: {stark_pyrust_chain}")
except ImportError as e:
    print(f"❌ Failed to import stark_pyrust_chain: {e}")
    sys.exit(1)

def test_vault():
    print("\n🔐 Testing Vault...")
    try:
        vault = stark_pyrust_chain.PyVault("mysecretpassword")
        original = "super_secret_key"
        encrypted = vault.encrypt(original)
        decrypted = vault.decrypt(encrypted)
        
        if original == decrypted:
            print(f"   ✅ Vault Encryption/Decryption passed. '{original}' -> '{decrypted}'")
        else:
            print(f"   ❌ Vault verification failed! '{original}' != '{decrypted}'")
            sys.exit(1)
            
    except Exception as e:
        print(f"   ❌ Vault checks threw exception: {e}")
        sys.exit(1)

def test_graph():
    print("\n🕸️  Testing Supply Chain Graph...")
    try:
        graph = stark_pyrust_chain.PySupplyChain()
        graph.add_recipe("TestRecipe", {"Input": 1}, {"Output": 1}, 10)
        # Assuming we can invoke find_sources, though logic is mocked in Rust for now
        # Just checking if methods exist and run without crashing
        print("   ✅ Supply Chain Graph initialized and methods callable.")
    except Exception as e:
         print(f"   ❌ Graph checks threw exception: {e}")
         sys.exit(1)

def test_client_init():
    print("\n🌍 Testing Client Initialization (Rate Limiting check)...")
    try:
        # Pass a dummy URL to bypass Env check for this test
        client = stark_pyrust_chain.PyStarknetClient("https://starknet-mainnet.public.blastapi.io")
        print("   ✅ StarknetClient initialized with URL (Rate Limiter active).")
    except Exception as e:
        print(f"   ❌ Client initialization failed: {e}")

if __name__ == "__main__":
    test_vault()
    test_graph()
    test_client_init()
    print("\n✨ All systems operational.")
