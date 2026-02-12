import os

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

load_env()

print("=== Coinbase Configuration ===")
print(f"CDP_API_KEY_NAME: {os.getenv('CDP_API_KEY_NAME', 'NOT SET')}")
print(f"COINBASE_CLIENT_API_KEY: {'SET' if os.getenv('COINBASE_CLIENT_API_KEY') else 'NOT SET'}")
print(f"COINBASE_API_PRIVATE_KEY: {'SET' if os.getenv('COINBASE_API_PRIVATE_KEY') else 'NOT SET'}")

# Check for any Starknet-related Coinbase addresses
print("\n=== Starknet Addresses ===")
print(f"STARKNET_WALLET_ADDRESS: {os.getenv('STARKNET_WALLET_ADDRESS', 'NOT SET')}")
print(f"TRANSIT_EVM_ADDRESS: {os.getenv('TRANSIT_EVM_ADDRESS', 'NOT SET')}")

# Look for any Coinbase Starknet deposit addresses
print("\n=== Looking for Coinbase Starknet Addresses ===")
for key, value in os.environ.items():
    if 'COINBASE' in key and 'STARKNET' in key:
        print(f"{key}: {value}")
    if 'STARKNET' in key and 'COINBASE' in key:
        print(f"{key}: {value}")
