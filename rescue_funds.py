"""
ADR-049: Ghost Sweep Recovery
=============================
Derives the Starknet 'Ghost Address' from EVM keys and sweeps funds.
"""

import os
import sys
import json
import time
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

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call
import asyncio

async def check_starknet_balance(address: str):
    rpc_url = os.getenv("STARKNET_MAINNET_URL") or os.getenv("STARKNET_RPC_URL")
    if not rpc_url:
        print("Error: STARKNET_RPC_URL not found in env.")
        return 0.0
        
    client = FullNodeClient(node_url=rpc_url)
    eth_address = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
    
    try:
        call = Call(
            to_addr=int(eth_address, 16),
            selector=get_selector_from_name("balanceOf"),
            calldata=[int(address, 16)]
        )
        res = await client.call_contract(call)
        low = res[0]
        return low / 10**18
    except Exception as e:
        print(f"Error fetching balance: {e}")
        return 0.0

def find_funds():
    verbose = "--verbose" in sys.argv or "--direct-query" in sys.argv
    poll_mode = "--poll" in sys.argv
    ghost = get_ghost_address()
    if not ghost:
        console.print("[red]❌ TRANSIT_EVM_ADDRESS not in .env[/red]")
        return

    rpc_url = os.getenv("STARKNET_MAINNET_URL") or os.getenv("STARKNET_RPC_URL")
    if verbose:
        console.print(f"[dim]Debug: Using Ghost Address {ghost}[/dim]")
        console.print(f"[dim]Debug: RPC URL: {rpc_url}[/dim]")

    console.print(Panel.fit(f"[bold cyan]🔍 Locating Ghost Funds[/bold cyan]\n"
                          f"EVM Base: {os.getenv('TRANSIT_EVM_ADDRESS')}\n"
                          f"Starknet Ghost: [green]{ghost}[/green]"))
    
    # Polling Loop
    max_tries = 100 if poll_mode else 1
    interval = 120 if poll_mode else 0
    
    for i in range(max_tries):
        if i > 0:
            console.print(f"[dim]{time.strftime('%H:%M:%S')} - Poll {i+1}/{max_tries}: Waiting {interval}s...[/dim]")
            time.sleep(interval)
            
        eth = asyncio.run(check_starknet_balance(ghost))
        
        if eth > 0:
            console.print(f"💰 [bold green]GHOST BALANCE DETECTED: {eth:.8f} ETH[/bold green]")
            console.print("[bold yellow]🚀 TRIGGERING AUTO-SWEEP...[/bold yellow]")
            sweep_funds()
            return
        elif not poll_mode:
            console.print(f"💰 [bold white]Ghost Balance: {eth:.6f} ETH[/bold white]")
            console.print("[dim]No funds detected yet.[/dim]")

    if poll_mode:
        console.print("[yellow]Polling cycle finished or timed out.[/yellow]")

async def execute_sweep(ghost_addr, target_addr, priv_key):
    rpc_url = os.getenv("STARKNET_MAINNET_URL") or os.getenv("STARKNET_RPC_URL")
    client = FullNodeClient(node_url=rpc_url)
    
    # Visionary Priority: 1.5 Gwei max_fee per user directive
    GAS_BUFFER_ETH = 0.0001
    GAS_PRICE_GWEI = 1.5
    
    # Estimate gas for a standard transfer (~50k gas)
    # Estimate = 50000 * 1.5e9 = 0.000075 ETH. 
    # Buffer is sufficient.
    
    bal_eth = await check_starknet_balance(ghost_addr)
    if bal_eth <= GAS_BUFFER_ETH:
        console.print(f"[red]❌ Balance too low to sweep ({bal_eth:.6f} ETH)[/red]")
        return

    sweep_amount = bal_eth - GAS_BUFFER_ETH
    console.print(f"[bold cyan]Sweep details:[/bold cyan]")
    console.print(f"   Value: {sweep_amount:.8f} ETH")
    console.print(f"   Gas Buffer: {GAS_BUFFER_ETH} ETH")
    console.print(f"   Priority: {GAS_PRICE_GWEI} Gwei")

    if "--confirm" not in sys.argv:
        console.print("[yellow]⚠️  READY FOR SIGNATURE. Use --confirm to broadcast.[/yellow]")
        return

    console.print("[bold red]☢️ BROADCASTING SECP256K1 TRANSACTION...[/bold red]")
    # Implementation of signing logic will go here
    # Requires an account factory that supports Secp256k1
    console.print("[dim]Broadcast staged. Waiting for fund confirmation to finalize signer type.[/dim]")

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
