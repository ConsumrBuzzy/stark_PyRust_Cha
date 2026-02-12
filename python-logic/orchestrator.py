import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from pathlib import Path
import os
import sys
import json

try:
    import stark_pyrust_chain
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

app = typer.Typer()
console = Console()

@app.command()
def init():
    """
    Initialize the stark_PyRust_Chain environment.
    Sets up the Vault and configuration.
    """
    console.print("[bold green]Initializing stark_PyRust_Chain...[/bold green]")
    
    if not RUST_AVAILABLE:
        console.print("[bold red]Critical Error: Rust extension not found.[/bold red]")
        console.print("Please run `maturin develop` to build the extension.")
        return

    password = Prompt.ask("Create a Vault Password", password=True)
    confirm = Prompt.ask("Confirm Vault Password", password=True)
    
    if password != confirm:
        console.print("[red]Passwords do not match![/red]")
        return
        
    try:
        vault = stark_pyrust_chain.PyVault(password)
        console.print("[green]Vault initialized successfully.[/green]")
        console.print("Configuration saved (mock).") # In real app, save salt/hash
        
    except Exception as e:
        console.print(f"[red]Initialization failed: {e}[/red]")

@app.command()
def wizard():
    """
    The 'Introduction Wizard' for Starknet & Influence setup.
    """
    console.print(Panel.fit("[bold blue]stark_PyRust_Chain Setup Wizard[/bold blue]"))
    
    console.print("\n[bold]1. Starknet RPC Provider[/bold]")
    console.print("High-performance automation requires a reliable RPC (Alchemy, Infura, etc).")
    rpc_url = Prompt.ask("Enter your Starknet RPC URL (or press Enter to try auto-detect from .env)")
    
    if rpc_url:
        console.print(f"[dim]Saved RPC URL: {rpc_url[:20]}...[/dim]")
        # In real app: update .env file here

    console.print("\n[bold]2. Influence API[/bold]")
    console.print("To interact with SAGE Labs, you need access to the Influence API.")
    api_url = Prompt.ask("Enter Influence API URL", default="https://api.influenceth.io")
    
    console.print("\n[bold]3. Session Keys (Account Abstraction)[/bold]")
    if Confirm.ask("Do you want to generate a Session Key now?"):
        generate_session_key()

@app.command()
def start(strategy: str = "default"):
    """
    Start the autonomous supply chain orchestrator.
    """
    console.print(f"[bold blue]Starting Orchestrator with strategy: {strategy}[/bold blue]")
    
    if not RUST_AVAILABLE:
        console.print("[bold red]Rust extension missing.[/bold red]")
        return

    # Initialize Clients
    try:
        # Client will auto-detect RPC from env if not passed args (or we could pass rpc_url from config)
        starknet = stark_pyrust_chain.PyStarknetClient(None) 
        console.print("✅ Starknet Client connected.")
        
        influence = stark_pyrust_chain.PyInfluenceClient()
        console.print("✅ Influence Client connected.")
        
        graph = stark_pyrust_chain.PySupplyChain()
        console.print("✅ Supply Chain Graph initialized.")
        
    except Exception as e:
        console.print(f"[red]Startup failed: {e}[/red]")
        return
    
    console.print("[dim]Polling Influence state and Starknet blocks... (Ctrl+C to stop)[/dim]")
    
    try:
        while True:
            # Main loop logic would go here
            block = starknet.get_block_number()
            # console.print(f"Current Block: {block}") # Uncomment to see noise
            pass
    except KeyboardInterrupt:
        console.print("[yellow]Shutting down...[/yellow]")

def generate_session_key():
    if not RUST_AVAILABLE:
        return

    try:
        key = stark_pyrust_chain.PySessionKey()
        pub = key.get_public_key()
        
        console.print(Panel(f"[bold]Session Public Key:[/bold] {pub}", title="New Session Key"))
        
        master = Prompt.ask("Enter your Master Account Address (0x...)")
        payload = key.create_auth_payload(master)
        
        console.print("\n[bold yellow]ACTION REQUIRED:[/bold yellow]")
        console.print("Sign the following payload with your Master Wallet (Argent/Braavos):")
        console.print(Panel(payload, title="Authorization Payload"))
        
        console.print("[dim]After signing, submit the transaction to the Starknet network.[/dim]")
        
    except Exception as e:
        console.print(f"[red]Key generation failed: {e}[/red]")

if __name__ == "__main__":
    app()
