import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from pathlib import Path
import os
import sys
import json
import time

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

load_env_manual()

try:
    import stark_pyrust_chain
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

# Import Strategies
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from strategy_module import RefiningStrategy
except ImportError:
    RefiningStrategy = None

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
        console.print("Configuration saved (mock).") 
        
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

    console.print("\n[bold]2. Influence API[/bold]")
    console.print("To interact with SAGE Labs, you need access to the Influence API.")
    api_url = Prompt.ask("Enter Influence API URL", default="https://api.influenceth.io")
    
    console.print("\n[bold]3. Session Keys (Account Abstraction)[/bold]")
    if Confirm.ask("Do you want to generate a Session Key now?"):
        generate_session_key()

@app.command()
def start(strategy: str = "refine", dry_run: bool = True):
    """
    Start the autonomous supply chain orchestrator.
    Defaults to 'refine' strategy in DRY RUN mode.
    """
    console.print(f"[bold blue]Starting Orchestrator with strategy: {strategy} (Dry Run: {dry_run})[/bold blue]")
    
    if not RUST_AVAILABLE:
        console.print("[bold red]Rust extension missing.[/bold red]")
        return

    active_strategy = None
    
    if strategy == "refine":
        if RefiningStrategy:
            active_strategy = RefiningStrategy(dry_run=dry_run)
            console.print("✅ RefiningStrategy Initialized.")
        else:
            console.print("[red]RefiningStrategy module not found.[/red]")
            return
    else:
        console.print(f"[red]Unknown strategy: {strategy}[/red]")
        return
    
    console.print("[dim]Starting Loop... (Ctrl+C to stop)[/dim]")
    
    try:
        while True:
            console.print(f"\n[bold]--- Tick {time.strftime('%H:%M:%S')} ---[/bold]")
            active_strategy.tick()
            
            console.print("[dim]Sleeping for 60s...[/dim]")
            time.sleep(60)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")

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
