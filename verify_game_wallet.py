import requests
import json
import os
from rich.console import Console

console = Console()

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

def get_balance():
    load_env()
    rpc_url = os.getenv("STARKNET_MAINNET_URL")
    target_addr = os.getenv("STARKNET_WALLET_ADDRESS")
    eth_token_addr = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"

    # balanceOf selector (keccak256("balanceOf(address)")) 
    # But in Starknet it's the sn_keccak of 'balanceOf'
    selector = "0x2e4263af84355325621406e7a6f73a2b0ce49dd33f0d59633c64c7185078505"
    
    payload = {
        "jsonrpc": "2.0",
        "method": "starknet_call",
        "params": {
            "request": {
                "contract_address": eth_token_addr,
                "entry_point_selector": selector,
                "calldata": [str(int(target_addr, 16))]
            },
            "block_id": "latest"
        },
        "id": 1
    }

    console.print(f"--- [bold]Starknet Game Wallet Query (Raw RPC)[/bold] ---")
    console.print(f"Target: [dim]{target_addr}[/dim]")
    
    try:
        response = requests.post(rpc_url, json=payload)
        res_json = response.json()
        
        if "error" in res_json:
            console.print(f"[red]RPC Error: {res_json['error']['message']}[/red]")
            return

        result = res_json["result"]
        low = int(result[0], 16)
        high = int(result[1], 16)
        wei_balance = (high << 128) + low
        eth_balance = wei_balance / 10**18
        
        console.print(f"💰 [bold green]Balance: {eth_balance:.6f} ETH[/bold green]")
        
        if eth_balance > 0.005:
            console.print("🚀 [bold blue]FUNDS READY FOR MISSION START![/bold blue]")
        else:
            console.print("⌛ Still awaiting Rhino.fi settlement (~60s)...")
            
    except Exception as e:
        console.print(f"[red]Connection Error: {e}[/red]")

if __name__ == "__main__":
    get_balance()
