import sys
import os
from rich.console import Console
from rich.panel import Panel

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

def verify_logistics():
    console.print(Panel.fit("[bold blue]🚚 Logistics & Nonce Guardrail (ADR-040)[/bold blue]"))
    load_env_manual()
    
    try:
        client = stark_pyrust_chain.PyStarknetClient(None)
        
        # 1. Nonce Check
        wallet = os.getenv("STARKNET_WALLET_ADDRESS") or "0x0258550d4d3c3365851214fa64687d65f57357497217961b7b7528e5d66666"
        console.print(f"   🔎 Fetching Nonce for: {wallet[:10]}...")
        
        try:
            nonce = client.get_nonce(wallet)
            console.print(f"   ✅ Nonce: [bold green]{nonce}[/bold green] (Verified from Mainnet)")
        except Exception as e:
            if "ContractNotFound" in str(e) or "not found" in str(e).lower():
                 console.print(f"   ⚠️  Nonce Fetch: [yellow]Account not deployed (ContractNotFound)[/yellow]. Defaulting to 0.")
            else:
                 console.print(f"   ❌ Nonce Fetch Error: {e}")
        
        # 2. Logistics Check (Mock)
        # In real app: fetch asteroid locations of Source Storage vs Destination Building
        source_loc = "Adalia Prime: Lot 42"
        dest_loc = "Adalia Prime: Lot 42"
        
        console.print(f"   🏭 Source: {source_loc}")
        console.print(f"   🏭 Dest:   {dest_loc}")
        
        if source_loc == dest_loc:
            console.print("[green]✅ Logistics Optimized: Co-located (0 Fuel Cost)[/green]")
        else:
             console.print("[yellow]⚠️  Distance Detected! Logistics Penalty applied in pre_check.py[/yellow]")

    except Exception as e:
        console.print(f"[bold red]❌ Failed:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_logistics()
