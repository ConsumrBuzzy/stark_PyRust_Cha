"""
ADR-049: Ghost Sweep Recovery
=============================
Derives the Starknet 'Ghost Address' from EVM keys and sweeps funds.
"""

import os
import sys
import json
from rich.console import Console
from rich.panel import Panel

# Add python-logic to path
sys.path.append(os.path.join(os.getcwd(), 'python-logic'))

from strategy_module import RefiningStrategy

console = Console()

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

def get_ghost_address():
    evm_addr = os.getenv("TRANSIT_EVM_ADDRESS")
    if not evm_addr:
        return None
    
    # Strip 0x
    clean = evm_addr.lower().replace("0x", "")
    # Pad to 64 chars (32 bytes)
    ghost = "0x" + clean.zfill(64)
    return ghost

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
import asyncio

async def check_starknet_balance(address: str):
    rpc_url = os.getenv("STARKNET_MAINNET_URL") or os.getenv("STARKNET_RPC_URL")
    if not rpc_url:
        print("Error: STARKNET_RPC_URL not found in env.")
        return 0.0
        
    client = FullNodeClient(node_url=rpc_url)
    
    # ETH token address on Starknet
    eth_address = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
    
    try:
        # balanceOf call
        from starknet_py.hash.selector import get_selector_from_name
        from starknet_py.net.client_models import Call
        
        call = Call(
            to_addr=int(eth_address, 16),
            selector=get_selector_from_name("balanceOf"),
            calldata=[int(address, 16)]
        )
        res = await client.call_contract(call)
        low = res[0]
        # eth is low / 10**18
        eth = low / 10**18
        return eth
    except Exception as e:
        print(f"Error fetching balance via starknet-py: {e}")
        return 0.0

def find_funds():
    verbose = "--verbose" in sys.argv
    ghost = get_ghost_address()
    if not ghost:
        console.print("[red]❌ TRANSIT_EVM_ADDRESS not in .env[/red]")
        return

    if verbose:
        rpc_url = os.getenv("STARKNET_MAINNET_URL") or os.getenv("STARKNET_RPC_URL")
        console.print(f"[dim]Debug: Using Ghost Address {ghost}[/dim]")
        console.print(f"[dim]Debug: RPC URL: {rpc_url}[/dim]")

    console.print(Panel.fit(f"[bold cyan]🔍 Locating Ghost Funds[/bold cyan]\n"
                          f"EVM Base: {os.getenv('TRANSIT_EVM_ADDRESS')}\n"
                          f"Starknet Ghost: [green]{ghost}[/green]"))
    
    eth = asyncio.run(check_starknet_balance(ghost))
    console.print(f"💰 [bold]Ghost Balance:[/bold] [green]{eth:.6f} ETH[/green]")
    
    if eth > 0.001:
        console.print("[yellow]✨ FUNDS LANDED! You can now run --sweep[/yellow]")
    else:
        console.print("[dim]No funds detected yet. Bridge may be pending...[/dim]")

async def execute_sweep(ghost_addr, target_addr, priv_key):
    # ADR-049 Visionary Caviat: Leave 0.0001 ETH for gas buffer
    GAS_BUFFER = 0.0001
    
    console.print(f"[dim]Calculating sweep amount with {GAS_BUFFER} ETH buffer...[/dim]")
    bal = await check_starknet_balance(ghost_addr)
    
    if bal <= GAS_BUFFER:
        console.print(f"[red]❌ Balance ({bal:.6f}) is too low to sweep (Buffer: {GAS_BUFFER})[/red]")
        return

    sweep_amount = bal - GAS_BUFFER
    console.print(f"🚀 [bold green]Sweeping {sweep_amount:.6f} ETH to {target_addr}[/bold green]")
    
    # Sweep implementation via starknet-py goes here
    # Requires Account and Signer setup.
    console.print("[yellow]Ready to sign. Type 'Go' or run with --confirm to execute.[/yellow]")

def sweep_funds():
    ghost = get_ghost_address()
    target = os.getenv("STARKNET_WALLET_ADDRESS")
    priv_key = os.getenv("TRANSIT_EVM_PRIVATE_KEY")
    
    if not ghost or not target or not priv_key:
        console.print("[red]❌ Missing required env variables[/red]")
        return

    console.print(Panel.fit(f"[bold red]🧹 INITIATING GHOST SWEEP[/bold red]\n"
                          f"From: {ghost}\n"
                          f"To: {target}"))
    
    asyncio.run(execute_sweep(ghost, target, priv_key))

if __name__ == "__main__":
    load_env()
    if "--find" in sys.argv:
        find_funds()
    elif "--sweep" in sys.argv:
        sweep_funds()
    else:
        find_funds()
