import sys
import os
from rich.console import Console

try:
    import stark_pyrust_chain
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

console = Console()

# Robust Env Loader for Windows/UTF-8 issues
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

def test_gas_fetch():
    console.print("\n[bold blue]⛽ Verifying Gas Price Fetch...[/bold blue]")
    load_env_manual()
    
    try:
        # Auto-detect RPC
        client = stark_pyrust_chain.PyStarknetClient(None)
        console.print("   ✅ Client Initialized.")
        
        # Call new method
        console.print("   ⏳ Fetching Network Status...")
        block, gas_wei = client.get_network_status()
        
        gas_gwei = gas_wei / 1e9
        
        console.print(f"   ✅ Block: [bold green]{block}[/bold green]")
        console.print(f"   ✅ Gas Price: [bold yellow]{gas_wei} Wei ({gas_gwei:.2f} Gwei)[/bold yellow]")
        
        if block > 0 and gas_wei > 0:
            console.print("   ✨ Verification SUCCESS.")
        else:
            console.print("   ⚠️  Values seem explicit zero? (Could be pending block or minimal gas)")

    except Exception as e:
        console.print(f"   ❌ Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_gas_fetch()
