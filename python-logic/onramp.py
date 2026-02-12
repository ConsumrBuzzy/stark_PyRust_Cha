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
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        
        # CDP Credentials
        self._api_key_name = os.getenv("COINBASE_CLIENT_API_KEY", "")
        self._api_private_key = os.getenv("COINBASE_API_PRIVATE_KEY", "")
        
        # Handle escaped newlines
        if self._api_private_key:
            self._api_private_key = self._api_private_key.replace("\\n", "\n")
            
        # Configuration
        self._starknet_address = os.getenv("STARKNET_WALLET_ADDRESS", "")
        self._min_bridge_amount = 5.0 # Min $5
        self._dust_floor = 1.0 # Keep $1
        
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
            free = float(asset_bal.get('free', 0.0))
            total = float(asset_bal.get('total', 0.0))
            
            console.print(f"💰 Coinbase Balance: {free:.4f} {asset} (Total: {total:.4f})")
            return free
        except Exception as e:
            console.print(f"[red]❌ Balance fetch error: {e}[/red]")
            return 0.0

    async def bridge_funds(self):
        console.print(Panel.fit("[bold blue]🌉 Coinbase -> Starknet Bridge[/bold blue]"))
        
        # 0. Validate Target
        if not self._starknet_address:
            console.print("[red]❌ Target Wallet not configured (STARKNET_WALLET_ADDRESS).[/red]")
            return

        # 1. Check ETH Balance (Primary Gas Token)
        eth_bal = await self.get_balance("ETH")
        
        # Calculate Value in USD (approx) or just use ETH amount
        # For simplicity, assuming ETH price $2600. 0.005 ETH ~ $13.
        target_amount = 0.005 # ~ $13
        
        if eth_bal < target_amount:
            console.print(f"[yellow]⚠️  Low ETH Balance ({eth_bal:.4f} < {target_amount}). Checking USDC...[/yellow]")
            # TODO: Implement USDC -> ETH swap if needed? 
            # For now, just abort if no ETH.
            console.print("[red]⛔ Insufficient ETH on Coinbase. Buy ETH first.[/red]")
            await self.close()
            return

        amount = eth_bal - 0.001 # Leave some dust for fees/floor
        if amount < 0.001: 
             console.print("[red]⛔ Available amount too small.[/red]")
             await self.close()
             return

        console.print(f"   🎯 Target: {self._starknet_address}")
        console.print(f"   💸 Bridging: {amount:.4f} ETH -> Starknet")

        if self.dry_run:
            console.print(Panel(f"Simulating Withdrawal:\nAsset: ETH\nAmount: {amount:.4f}\nNetwork: {self.ALLOWED_NETWORK}", title="[DRY RUN]"))
        else:
            # Execute
            try:
                exchange = await self._ensure_exchange()
                params = {'network': self.ALLOWED_NETWORK}
                
                console.print(f"[yellow]🚀 Sending {amount:.4f} ETH to Starknet...[/yellow]")
                
                # Check if exchange supports 'starknet' network for ETH
                # Note: Coinbase API network names can be tricky. 'starknet' is likely correct if supported.
                # If this fails, user might need to use L1 'ethereum' and bridge manually.
                
                withdrawal = await exchange.withdraw(
                    code='ETH',
                    amount=amount,
                    address=self._starknet_address,
                    params=params
                )
                
                console.print(f"[green]✅ Withdrawal Initialized! ID: {withdrawal.get('id')}[/green]")
                
            except Exception as e:
                 console.print(f"[bold red]❌ Withdrawal Failed: {e}[/bold red]")
                 console.print("[dim]Use 'ethereum' network (L1) if 'starknet' is not supported directly.[/dim]")

        await self.close()

    async def close(self):
        if self._exchange:
            await self._exchange.close()

if __name__ == "__main__":
    # Check for dry-run flag
    is_dry = "--no-dry-run" not in sys.argv
    
    driver = CoinbaseOnramp(dry_run=is_dry)
    asyncio.run(driver.bridge_funds())
