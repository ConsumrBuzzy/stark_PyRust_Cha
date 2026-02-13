import os
from dotenv import load_dotenv

print("🔍 Debugging .env file...")

# Explicitly load from current directory
env_path = os.path.join(os.getcwd(), '.env')
print(f"   Target path: {env_path}")

if os.path.exists(env_path):
    print("   ✅ .env file exists.")
else:
    print("   ❌ .env file NOT found.")

# Load env
loaded = load_dotenv(env_path)
print(f"   Input loaded: {loaded}")

# Check for specific key
key = "STARKNET_MAINNET_URL"
val = os.getenv(key)

if val:
    print(f"   ✅ Found {key}: {val[:10]}... (Masked)")
else:
    print(f"   ❌ {key} NOT found in environment.")

# Check valid keys
print("   Available Env Keys:", [k for k in os.environ.keys() if "STARKNET" in k or "RPC" in k])
