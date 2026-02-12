"""
Coinbase Onramp Driver (PhantomArbiter Port)
============================================
Adapted for stark_PyRust_Chain.
Uses CCXT + CDP Authentication to bridge funds to Starknet.
"""

import os
import time
import asyncio
import sys
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel

try:
    import ccxt.async_support as ccxt
except ImportError:
    print("Error: ccxt not installed. Run 'pip install ccxt'")
    sys.exit(1)

console = Console()

# Robust Env Loader (Shared utility)
def load_env_manual():
    env_path = ".env"
    if not os.path.exists(env_path): return
    try:
        lines = []
        try:
            with open(env_path, "r", encoding="utf-8") as f: lines = f.readlines()
        except UnicodeDecodeError:
            with open(env_path, "r", encoding="latin-1") as f: lines = f.readlines()
        for line in lines:
            if line.strip() and not line.strip().startswith("#") and "=" in line:
                key, val = line.strip().split("=", 1)
                # Cleanup inline comments if any
                if " #" in val: val = val.split(" #", 1)[0]
                if key.strip() not in os.environ: os.environ[key.strip()] = val.strip()
                
        # Aliases for keys
        if "COINBASE_API_KEY" in os.environ and "COINBASE_CLIENT_API_KEY" not in os.environ:
             os.environ["COINBASE_CLIENT_API_KEY"] = os.environ["COINBASE_API_KEY"]
        if "COINBASE_API_SECRET" in os.environ and "COINBASE_API_PRIVATE_KEY" not in os.environ:
             os.environ["COINBASE_API_PRIVATE_KEY"] = os.environ["COINBASE_API_SECRET"]
             
    except: pass

load_env_manual()

class CoinbaseOnramp:
    """
    CCXT-based driver for Coinbase Advanced Trade.
    Ported from PhantomArbiter for Starknet.
    """
    
    ALLOWED_NETWORK = "starknet" # Target Network
    
    MAX_WAIT_SECONDS = 300 # 5 minutes for funds to arrive

    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        
        # CDP Credentials
        self._api_key_name = os.getenv("COINBASE_CLIENT_API_KEY", "")
        self._api_private_key = os.getenv("COINBASE_API_PRIVATE_KEY", "")
        
        if self._api_private_key:
            self._api_private_key = self._api_private_key.replace("\\n", "\n")
            
        # Configuration for ADR-047 (Base Transit)
        self._transit_address = os.getenv("TRANSIT_EVM_ADDRESS", "")
        
        self._exchange = None
        self._initialized = False

    async def _ensure_exchange(self):
        if self._exchange is None:
            if not self._api_key_name or not self._api_private_key:
                console.print("[red]❌ Coinbase CDP credentials not configured.[/red]")
                return None
            
            self._exchange = ccxt.coinbase({
                'apiKey': self._api_key_name,
                'secret': self._api_private_key,
                'verbose': False, 
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                    'brokerId': 'CCXT',
                }
            })
            self._initialized = True
        return self._exchange

    async def get_balance(self, asset="ETH") -> float:
        try:
            exchange = await self._ensure_exchange()
            if not exchange: return 0.0
            
            balance = await exchange.fetch_balance()
            asset_bal = balance.get(asset, {})
            return float(asset_bal.get('free', 0.0))
        except Exception as e:
            console.print(f"[red]❌ Balance fetch error: {e}[/red]")
            return 0.0

    async def bridge_funds(self):
        console.print(Panel.fit("[bold blue]🌉 Coinbase -> Base (Transit)[/bold blue]"))
        
        # 0. Validate Target (EVM Transit Wallet)
        if not self._transit_address:
            console.print("[red]❌ TRANSIT_EVM_ADDRESS not configured. Run 'generate_transit_wallet.py' first.[/red]")
            return

        # 1. Check ETH Balance
        eth_bal = await self.get_balance("ETH")
        # Base needs minor gas, but mostly we are moving to Orbiter
        target_amount = 0.005 
        
        if eth_bal < target_amount:
            console.print(f"[yellow]⚠️  Low ETH Balance ({eth_bal:.4f}).[/yellow]")
            console.print("[red]⛔ Insufficient ETH on Coinbase.[/red]")
            return

        amount = eth_bal - 0.0005 # Leave dust
        
        console.print(f"   🎯 Transit: {self._transit_address} (Base L2)")
        console.print(f"   💸 Withdrawing: {amount:.4f} ETH -> Base")

        if self.dry_run:
            console.print(Panel(f"Simulating Withdrawal:\nAsset: ETH\nAmount: {amount:.4f}\nNetwork: base\nTarget: {self._transit_address}", title="[DRY RUN]"))
        else:
            try:
                exchange = await self._ensure_exchange()
                # 'base' is the ID for Base Mainnet on Coinbase
                params = {'network': 'base'} 
                
                console.print(f"[yellow]🚀 Sending {amount:.4f} ETH to Base...[/yellow]")
                
                withdrawal = await exchange.withdraw(
                    code='ETH',
                    amount=amount,
                    address=self._transit_address,
                    params=params
                )
                
                console.print(f"[green]✅ Withdrawal to Base Initialized! ID: {withdrawal.get('id')}[/green]")
                console.print("[dim]Next Step: Run 'python python-logic/bridge_logic.py' once funds arrive.[/dim]")
                
            except Exception as e:
                 console.print(f"[bold red]❌ Withdrawal Failed: {e}[/bold red]")
        
        await self.close()

    async def close(self):
        if self._exchange:
            await self._exchange.close()

if __name__ == "__main__":
    # Check for dry-run flag
    is_dry = "--no-dry-run" not in sys.argv
    
    driver = CoinbaseOnramp(dry_run=is_dry)
    asyncio.run(driver.bridge_funds())
