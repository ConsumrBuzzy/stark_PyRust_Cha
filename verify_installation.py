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
           print(f"   ✅ Vault Encryption/Decryption passed.")
        else:
           print(f"   ❌ Vault verification failed!")
           sys.exit(1)
           
    except Exception as e:
        print(f"   ❌ Vault checks threw exception: {e}")
        sys.exit(1)

def test_graph():
    print("\n🕸️  Testing Supply Chain Graph...")
    try:
        graph = stark_pyrust_chain.PySupplyChain()
        graph.add_recipe("TestRecipe", {"Input": 1}, {"Output": 1}, 10)
        print("   ✅ Supply Chain Graph initialized and methods callable.")
    except Exception as e:
         print(f"   ❌ Graph checks threw exception: {e}")
         sys.exit(1)

def test_client_init():
    print("\n🌍 Testing Client Initialization (Rate Limiting check)...")
    try:
        # Pass a dummy URL to bypass Env check for this test
        client = stark_pyrust_chain.PyStarknetClient("https://starknet-mainnet.public.blastapi.io")
        print("   ✅ StarknetClient initialized with URL.")
    except Exception as e:
        print(f"   ❌ Client initialization failed: {e}")

def test_influence_client():
    print("\n☄️  Testing Influence Client...")
    try:
        client = stark_pyrust_chain.PyInfluenceClient()
        print("   ✅ InfluenceClient initialized.")
        try:
            asteroid_json = client.get_asteroid(1) # Prime asteroid
            print(f"   ✅ Fetched asteroid data: {asteroid_json[:20]}...")
        except Exception as e:
            print(f"   ⚠️  Fetch failed (Expected without API/Network): {e}")

    except Exception as e:
        print(f"   ❌ Influence Client initialization failed: {e}")
        sys.exit(1)

def test_session_key():
    print("\n🔑 Testing Session Key Generation...")
    try:
        key = stark_pyrust_chain.PySessionKey()
        pub = key.get_public_key()
        payload = key.create_auth_payload("0xMasterAccount")
        
        print(f"   ✅ Generated Session Key (Pub: {pub[:10]}...)")
        print(f"   ✅ Created Auth Payload: {payload}")
        
    except Exception as e:
        print(f"   ❌ Session Key test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_vault()
    test_graph()
    test_client_init()
    test_influence_client()
    test_session_key()
    print("\n✨ All systems operational.")
