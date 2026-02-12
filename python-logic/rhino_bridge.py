"""
ADR-060: Rhino Bridge Helper
============================
Fetches a bridge quote from Rhino.fi for Base -> Starknet
and prepares the transaction payload for manual or script signing.
"""

import requests
import json
import os
from rich.console import Console

console = Console()

def get_rhino_quote(amount_usd=15.0):
    # Rhino.fi API v1
    # Note: For Intent-based bridging, we usually query the bridge/quote endpoint.
    url = "https://api.rhino.fi/bridge/quote"
    
    params = {
        "fromChain": "BASE",
        "toChain": "STARKNET",
        "fromToken": "USDC",  # Since chaser sent USDC
        "toToken": "ETH",    # Destination on Starknet usually ETH for gas
        "amount": str(amount_usd)
    }
    
    console.print(f"[blue]🔍 Fetching Rhino.fi quote for {amount_usd} USDC (Base -> Starknet ETH)...[/blue]")
    
    try:
        response = requests.get(url, params=params)
        if response.status_status == 200:
            quote = response.json()
            console.print("[green]✅ Quote Received![/green]")
            return quote
        else:
            console.print(f"[red]❌ Rhino API Error: {response.text}[/red]")
            return None
    except Exception as e:
        console.print(f"[red]❌ Connection Error: {e}[/red]")
        return None

def display_payload(quote):
    if not quote: return
    
    # In a real scenario, the quote contains 'receiverAddress', 'bridgeAddress', 'calldata', etc.
    console.print("\n[bold]--- Rhino.fi Bridge Payload ---[/bold]")
    console.print(f"Receiver on Starknet: [dim]{quote.get('receiver', 'Not specified')}[/dim]")
    console.print(f"Contract to Call (Base): [yellow]{quote.get('contractAddress', '0x...')}[/yellow]")
    console.print(f"Value/Amount: [bold]{quote.get('amountToBridge', '0')}[/bold]")
    
    console.print("\n[yellow]💡 ACTION: Copy the 'contractAddress' and 'data' into your Phantom Custom Transaction or use the Rhino UI with these values.[/yellow]")

if __name__ == "__main__":
    q = get_rhino_quote()
    if q:
        display_payload(q)
    else:
        # Fallback explanation if API is restricted
        console.print("[dim]Note: If the public API is restricted, use https://app.rhino.fi/bridge in the Phantom browser.[/dim]")
