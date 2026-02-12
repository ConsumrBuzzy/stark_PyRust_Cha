import os
import requests
import sys
import asyncio
from rich.console import Console
from rich.panel import Panel
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.net.client_models import Call

console = Console()

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

def get_swap_quote(amount_eth=0.002):
    url = "https://starknet.api.avnu.fi/swap/v1/quotes"
    ETH_ADDRESS = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
    STRK_ADDRESS = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
    amount_hex = hex(int(amount_eth * 10**18))
    
    params = {
        "sellTokenAddress": ETH_ADDRESS,
        "buyTokenAddress": STRK_ADDRESS,
        "sellAmount": amount_hex,
        "size": 1
    }
    
    console.print(f"[blue]🔍 Fetching AVNU quote: {amount_eth} ETH -> STRK...[/blue]")
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            quotes = response.json()
            if quotes:
                quote = quotes[0]
                buy_amount = int(quote['buyAmount'], 16) / 10**18
                sell_amount = int(quote['sellAmount'], 16) / 10**18
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

async def execute_swap(quote):
    load_env()
    wallet_addr = os.getenv("STARKNET_WALLET_ADDRESS")
    priv_key = os.getenv("STARKNET_PRIVATE_KEY")
    rpc_url = os.getenv("STARKNET_MAINNET_URL") or os.getenv("STARKNET_RPC_URL")
    
    if not all([wallet_addr, priv_key, rpc_url]):
        console.print("[red]❌ Missing credentials or RPC URL in .env[/red]")
        return

    # 1. Build Transaction
    build_url = "https://starknet.api.avnu.fi/swap/v1/build"
    payload = {
        "quoteId": quote['quoteId'],
        "takerAddress": wallet_addr,
        "slippage": 0.01 # 1% slippage
    }
    
    console.print("[blue]🛠 Building swap transaction...[/blue]")
    res = requests.post(build_url, json=payload)
    if res.status_code != 200:
        console.print(f"[red]❌ Build Error: {res.text}[/red]")
        return

    build_data = res.json()
    
    # 2. Setup Starknet Client & Account
    client = FullNodeClient(node_url=rpc_url)
    key_pair = KeyPair.from_private_key(priv_key)
    account = Account(
        address=wallet_addr,
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.MAINNET
    )

    # 3. Parse Calls
    calls = []
    for call in build_data['calls']:
        calls.append(Call(
            to_addr=int(call['contractAddress'], 16),
            selector=int(call['entrypoint'], 16) if isinstance(call['entrypoint'], str) and call['entrypoint'].startswith("0x") else call['entrypoint'],
            calldata=[int(x, 16) for x in call['calldata']]
        ))
    
    # Fix entrypoint if it's a string name (AVNU usually gives selectors)
    from starknet_py.hash.selector import get_selector_from_name
    for i, call in enumerate(calls):
        if isinstance(build_data['calls'][i]['entrypoint'], str) and not build_data['calls'][i]['entrypoint'].startswith("0x"):
             calls[i] = Call(
                 to_addr=call.to_addr,
                 selector=get_selector_from_name(build_data['calls'][i]['entrypoint']),
                 calldata=call.calldata
             )

    # 4. Sign and Broadcast
    console.print("[yellow]🚀 Signing and broadcasting swap...[/yellow]")
    if "--confirm" not in sys.argv:
        console.print("[yellow]⚠ Simulation only. Run with --confirm to execute.[/yellow]")
        return

    try:
        invoke_tx = await account.execute(calls=calls, max_fee=int(1e15)) # 0.001 ETH max fee safety
        console.print(f"[bold green]✨ Swap Broadcasted![/bold green]")
        console.print(f"Transaction Hash: [cyan]{hex(invoke_tx.transaction_hash)}[/cyan]")
        console.print("[dim]Waiting for inclusion...[/dim]")
    except Exception as e:
        console.print(f"[red]❌ Transaction Failed: {e}[/red]")

if __name__ == "__main__":
    quote = get_swap_quote()
    if quote:
        asyncio.run(execute_swap(quote))
