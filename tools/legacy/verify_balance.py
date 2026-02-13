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

def test_balance():
    console.print(Panel.fit("[bold blue]💰 Starknet Wallet Health Check[/bold blue]"))
    load_env_manual()
    
    wallet = os.getenv("STARKNET_WALLET_ADDRESS")
    if not wallet:
        # Use a random Starknet address (e.g. from block explorer) for testing read capability
        console.print("[yellow]⚠️  STARKNET_WALLET_ADDRESS not in .env. Using a test address (Argent X deployer).[/yellow]")
        wallet = "0x0258550d4d3c3365851214fa64687d65f57357497217961b7b7528e5d66666"
    else:
        console.print(f"[green]✅ Using Wallet from .env: {wallet[:10]}...[/green]") 
    
    try:
        # Auto-detect RPC
        client = stark_pyrust_chain.PyStarknetClient(None)
        
        console.print(f"   🔎 Checking Balance for: {wallet[:10]}...")
        
        balance_wei = client.get_eth_balance(wallet)
        balance_eth = balance_wei / 1e18
        balance_usd = balance_eth * 2500.0 # Approx Feb 2026 price? Or $3000? Let's say $2500 conservative.
        
        console.print(f"   ✅ Balance: [bold green]{balance_eth:.6f} ETH[/bold green]")
        console.print(f"   💵 Value: [dim]~${balance_usd:.2f} USD[/dim]")
        
        if balance_eth > 0.001:
             console.print("[green]✨ Gas Buffer Satisfied (> 0.001 ETH)[/green]")
        else:
             console.print("[red]⚠️  Low Balance. Gas Buffer Risk.[/red]")

    except Exception as e:
        console.print(f"[bold red]❌ Failed:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_balance()
