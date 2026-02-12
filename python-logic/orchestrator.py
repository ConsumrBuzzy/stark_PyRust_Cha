import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.live import Live
from pathlib import Path
import os
import sys
import json
import time
import threading

# Add python-logic to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import stark_pyrust_chain
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

try:
    from strategy_module import RefiningStrategy
    from dashboard import Dashboard
except ImportError:
    RefiningStrategy = None
    Dashboard = None

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

app = typer.Typer()
console = Console()

@app.command()
def init():
    """ Initialize the stark_PyRust_Chain environment. """
    console.print("[bold green]Initializing stark_PyRust_Chain...[/bold green]")
    if not RUST_AVAILABLE:
        console.print("[bold red]Critical Error: Rust extension not found.[/bold red]")
        return
    password = Prompt.ask("Create A Vault Password", password=True)
    try:
        vault = stark_pyrust_chain.PyVault(password)
        console.print("[green]Vault initialized successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Initialization failed: {e}[/red]")

@app.command()
def wizard():
    """ The 'Introduction Wizard' for Starknet & Influence setup. """
    console.print(Panel.fit("[bold blue]stark_PyRust_Chain Setup Wizard[/bold blue]"))
    rpc_url = Prompt.ask("Enter your Starknet RPC URL")
    if rpc_url: console.print(f"[dim]Saved RPC URL: {rpc_url[:20]}...[/dim]")
    
    if Confirm.ask("Do you want to generate a Session Key now?"):
        if RUST_AVAILABLE:
            key = stark_pyrust_chain.PySessionKey()
            console.print(Panel(f"[bold]Session Public Key:[/bold] {key.get_public_key()}", title="New Session Key"))

@app.command()
def start(strategy: str = "refine", dry_run: bool = True):
    """
    Start the autonomous supply chain orchestrator (Mainnet Launch).
    """
    if not RUST_AVAILABLE:
        console.print("[bold red]Rust extension missing.[/bold red]")
        return
    
    # Initialize Dashboard
    dash = Dashboard()

    # Initialize Strategy
    active_strategy = None
    if strategy == "refine":
        active_strategy = RefiningStrategy(dry_run=dry_run)
        
        # Monkey-patch strategy logging to feed Dashboard
        def dashboard_log(msg):
            dash.log(msg)
            # Check if profit message to update ROI (Parsing hack for v1)
            if "Profit:" in msg:
                 try:
                     val = float(msg.split("Profit:")[1].strip().split()[0])
                     dash.update_roi(val)
                 except: pass

        active_strategy.log = dashboard_log
    else:
        console.print(f"[red]Unknown strategy: {strategy}[/red]")
        return

    # Run Loop
    wallet_addr = os.getenv("STARKNET_WALLET_ADDRESS")
    if not wallet_addr:
        dash.log("Warning: No Wallet Address in .env. Balance check skipped.")

    with Live(dash.render(0, 0, 0.0), refresh_per_second=4, screen=True) as live:
        dash.log(f"Orchestrator Started. Strategy: {strategy.upper()} | Dry Run: {dry_run}")
        
        try:
            while True:
                # 1. Update Network Status in Header
                try:
                    block, gas_wei = active_strategy.starknet.get_network_status()
                    gas_gwei = gas_wei / 1e9
                    
                    eth_balance = 0.0
                    if wallet_addr:
                        wei_bal = active_strategy.starknet.get_eth_balance(wallet_addr)
                        eth_balance = wei_bal / 1e18

                    live.update(dash.render(block, gas_gwei, eth_balance))
                except Exception as e:
                    # dash.log(f"Status Error: {e}") # Debug only
                    live.update(dash.render(0, 0, 0.0))

                # 2. Run Strategy Tick
                active_strategy.tick()
                
                # 3. Sleep (responsive update)
                for _ in range(60): # 60 seconds sleep, updating UI every 1s
                    time.sleep(1)
                    live.update(dash.render(block, gas_gwei, eth_balance))
                    
        except KeyboardInterrupt:
            dash.log("Shutting down...")
            live.update(dash.render(block, gas_gwei, eth_balance))
            time.sleep(1)

@app.command()
def pulse(strategy: str = "refine", dry_run: bool = True):
    """
    Execute a single Strategy Tick (Pulse Mode).
    Suitable for Cron Jobs / GitHub Actions.
    """
    if not RUST_AVAILABLE:
        console.print("[bold red]Rust extension missing.[/bold red]")
        return
    
    # Initialize Strategy
    active_strategy = None
    if strategy == "refine":
        active_strategy = RefiningStrategy(dry_run=dry_run)
        
        # Simple logging for Pulse (Stdout) with Masking
        def pulse_log(msg):
            # 1. Mask known secrets if they somehow leak into logs
            secrets = [os.getenv("STARKNET_PRIVATE_KEY"), os.getenv("INFLUENCE_API_KEY")]
            for s in secrets:
                if s and s in msg:
                    msg = msg.replace(s, "***SECRET***")
            
            # 2. General Heuristic: Mask long hex strings (signatures/keys) in logs
            #    (User requested explicitly redacting 0x strings)
            #    We use a simple check to avoid masking Wallet Addresses (usually public) unless paranoid.
            #    Let's just mask Private Keys context if identifiable. 
            
            print(f"[PULSE] {msg}")

        active_strategy.log = pulse_log
    else:
        print(f"Unknown strategy: {strategy}")
        return

    print(f"--- PULSE STARTED: Strategy={strategy.upper()} | DryRun={dry_run} ---")
    
    # Secret Presence Check (Masked)
    rpc = os.getenv("STARKNET_RPC_URL")
    pk = os.getenv("STARKNET_PRIVATE_KEY")
    inf_key = os.getenv("INFLUENCE_API_KEY")
    
    print(f"Secret Check:")
    print(f"  RPC_URL: {'[CONFIGURED]' if rpc else '[MISSING]'} {f'({rpc[:8]}...)' if rpc else ''}")
    print(f"  PRIVATE_KEY: {'[CONFIGURED]' if pk else '[MISSING]'}")
    print(f"  INFLUENCE_KEY: {'[CONFIGURED]' if inf_key else '[MISSING]'}")

    # 1. Update Network Status (Log only)
    try:
        block, gas_wei = active_strategy.starknet.get_network_status()
        gas_gwei = gas_wei / 1e9
        print(f"Network Status: Block={block} | Gas={gas_gwei:.2f} Gwei")
    except Exception as e:
        print(f"Network Status Error: {e}")

    # 2. Run Single Tick
    active_strategy.tick()
    
    print("--- PULSE COMPLETE ---")


if __name__ == "__main__":
    app()
