import os
import requests
import sys
from rich.console import Console
from rich.panel import Panel

console = Console()

def get_swap_quote(amount_eth=0.002):
    # AVNU API Endpoint for Starknet Mainnet
    url = "https://starknet.api.avnu.fi/swap/v1/quotes"
    
    # Token Addresses
    ETH_ADDRESS = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
    STRK_ADDRESS = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
    
    amount_decimal = str(int(amount_eth * 10**18))
    
    params = {
        "sellTokenAddress": ETH_ADDRESS,
        "buyTokenAddress": STRK_ADDRESS,
        "sellAmount": amount_decimal,
        "size": 1 # Just get the best quote
    }
    
    console.print(f"[blue]🔍 Fetching AVNU quote: {amount_eth} ETH -> STRK...[/blue]")
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            quotes = response.json()
            if quotes:
                quote = quotes[0]
                buy_amount = int(quote['buyAmount']) / 10**18
                sell_amount = int(quote['sellAmount']) / 10**18
                
                console.print(Panel.fit(
                    f"[bold green]✅ Quote Received[/bold green]\n\n"
                    f"Sell: [yellow]{sell_amount:.6f} ETH[/yellow]\n"
                    f"Buy: [bold green]{buy_amount:.6f} STRK[/bold green]\n"
                    f"Quote ID: [dim]{quote['quoteId']}[/dim]",
                    title="AVNU Swap Quote"
                ))
                return quote
            else:
                console.print("[yellow]⚠ No quotes found for this pair.[/yellow]")
        else:
            console.print(f"[red]❌ AVNU API Error: {response.status_code} - {response.text}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Connection Error: {e}[/red]")
    return None

if __name__ == "__main__":
    get_swap_quote()
