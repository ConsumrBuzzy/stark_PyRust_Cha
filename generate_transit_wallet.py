import secrets
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
    
    # 3. Output
    console.print(Panel.fit(
        f"[bold yellow]🔑 NEW TRANSIT WALLET GENERATED[/bold yellow]\n\n"
        f"[bold]Address:[/bold] [green]{address}[/green]\n"
        f"[bold]Private Key:[/bold] [red]{private_key}[/red]\n\n"
        f"[dim]Action Required: Add the following to your .env file:[/dim]\n"
        f"TRANSIT_EVM_PRIVATE_KEY={private_key}\n"
        f"TRANSIT_EVM_ADDRESS={address}",
        title="ADR-047 Security"
    ))

if __name__ == "__main__":
    generate_transit_wallet()
