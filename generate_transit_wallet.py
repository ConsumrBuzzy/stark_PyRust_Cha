import secrets
import os
from web3 import Web3
from rich.console import Console
from rich.panel import Panel

console = Console()

def generate_transit_wallet():
    # 1. Generate Entropy
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    
    # 2. Derive Address
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)
    address = account.address
    
    # 3. Output & Save
    console.print(Panel.fit(
        f"[bold yellow]🔑 NEW TRANSIT WALLET GENERATED[/bold yellow]\n\n"
        f"[bold]Address:[/bold] [green]{address}[/green]\n"
        f"[bold]Private Key:[/bold] [red]{private_key}[/red]",
        title="ADR-047 Security"
    ))
    
    # Auto-save to .env
    env_path = ".env"
    try:
        current_content = ""
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                current_content = f.read()
        
        if "TRANSIT_EVM_PRIVATE_KEY" not in current_content:
            with open(env_path, "a", encoding="utf-8") as f:
                f.write(f"\n# ADR-047 Transit Wallet\n")
                f.write(f"TRANSIT_EVM_PRIVATE_KEY={private_key}\n")
                f.write(f"TRANSIT_EVM_ADDRESS={address}\n")
            console.print("[green]✅ Credentials automatically appended to .env[/green]")
        else:
            console.print("[yellow]⚠️  Transit Wallet already present in .env. Skipping save.[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Failed to write to .env: {e}[/red]")

if __name__ == "__main__":
    generate_transit_wallet()
