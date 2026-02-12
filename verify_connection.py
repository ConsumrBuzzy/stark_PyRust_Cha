import sys
import os
from rich.console import Console

try:
    import stark_pyrust_chain
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

console = Console()

def load_env_manual():
    env_path = ".env"
    if not os.path.exists(env_path):
        return {}
    
    config = {}
    with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                config[key.strip()] = val.strip()
    return config

def test_mainnet_connection():
    console.print("\n[bold blue]🌍 Verifying Mainnet Connection (Manual Env Load)...[/bold blue]")
    
    config = load_env_manual()
    rpc_url = config.get("STARKNET_MAINNET_URL")
    
    if not rpc_url:
        # Fallback to other keys
        rpc_url = config.get("STARKNET_RPC_URL")
    
    if not rpc_url:
        console.print("[red]❌ Could not find STARKNET_MAINNET_URL in .env[/red]")
        sys.exit(1)

    console.print(f"   🔑 Found RPC URL: {rpc_url[:20]}... (Masked)")

    try:
        # 1. Initialize Client with Explicit URL
        client = stark_pyrust_chain.PyStarknetClient(rpc_url)
        console.print("   ✅ Client Initialized (Explicit URL).")
        
        # 2. Fetch Block Number
        console.print("   ⏳ Fetching latest block number...")
        block = client.get_block_number()
        console.print(f"   ✅ Connected! Current Block: [bold green]{block}[/bold green]")
        
    except Exception as e:
        console.print(f"   ❌ Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_mainnet_connection()
