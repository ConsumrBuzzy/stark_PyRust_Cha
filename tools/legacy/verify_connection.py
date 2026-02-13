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
        return
    try:
        with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = val.strip()
    except Exception as e:
        print(f"Warning: Failed to load .env manually: {e}")

def test_round_robin():
    console.print("\n[bold blue]🌍 Verifying Round-Robin RPC Rotation (Deep Debug)...[/bold blue]")
    
    load_env_manual()
    
    keys = ["STARKNET_MAINNET_URL", "STARKNET_LAVA_URL", "STARKNET_1RPC_URL"]
    
    console.print("   Current Env Values (repr):")
    for k in keys:
        val = os.environ.get(k, "MISSING")
        # Print repr() to see hidden chars/quotes
        console.print(f"   - {k}: {repr(val)}")

    try:
        # Initialize Client
        client = stark_pyrust_chain.PyStarknetClient(None)
        console.print("   ✅ Client Initialized.")
        
        for i in range(1, 4): 
            console.print(f"   ⏳ Request #{i}: Fetching block...")
            block = client.get_block_number()
            console.print(f"      ✅ Block: [bold green]{block}[/bold green]")

    except Exception as e:
        console.print(f"   ❌ Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_round_robin()
