"""
Orbiter Bridge Logic (Base -> Starknet)
=======================================
Implements ADR-047: Hybrid Bridge.
Moves ETH from Base (L2) to Starknet via Orbiter Finance.
"""

import os
import sys
import json
from decimal import Decimal
from rich.console import Console
from rich.panel import Panel

try:
    from web3 import Web3
except ImportError:
    print("Error: web3 not installed. Run 'pip install web3'")
    sys.exit(1)

console = Console()

# Orbiter Makers (Check https://github.com/Orbiter-Finance/Orbiter-Bridge-Contracts)
# Base (Chain 8453) -> Starknet (9004)
# Maker Address usually stable, but verify if fails.
ORBITER_MAKER_BASE = "0xe530d28960d48708ccf3e62aa7b42a80bc427aef" 
STARKNET_CODE = 9004

class OrbiterBridge:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
        
        # Load Transit Key
        self.private_key = os.getenv("TRANSIT_EVM_PRIVATE_KEY")
        if not self.private_key:
            console.print("[red]❌ TRANSIT_EVM_PRIVATE_KEY not found in .env[/red]")
            self.account = None
            return

        try:
            self.account = self.w3.eth.account.from_key(self.private_key)
            console.print(f"[green]✅ Transit Wallet Loaded:[/green] {self.account.address}")
        except Exception as e:
            console.print(f"[red]❌ Invalid EVM Key:[/red] {e}")
            self.account = None

    def get_balance(self):
        if not self.account: return 0.0
        wei = self.w3.eth.get_balance(self.account.address)
        eth = self.w3.from_wei(wei, 'ether')
        return float(eth)

    def bridge_to_starknet(self, amount_eth):
        """
        Sends ETH to Orbiter Maker with the 9004 code.
        """
        if not self.account: return

        console.print(Panel.fit("[bold blue]🌉 Base -> Starknet (via Orbiter)[/bold blue]"))
        
        balance = self.get_balance()
        console.print(f"   💰 Transit Balance (Base): {balance:.4f} ETH")

        if balance < amount_eth:
            console.print(f"[red]⛔ Insufficient Balance on Base. Need {amount_eth} ETH.[/red]")
            return

        # Encoding Logic (Orbiter Specific)
        # Keeps first 4 decimal places, replaces last 4 digits with Destination Code (9004)
        # However, usually it's: Amount + Code. 
        # Correct Formula: (Amount_Wei // 10000 * 10000) + 9004
        
        wei_amount = self.w3.to_wei(amount_eth, 'ether')
        # Safety Check: Ensure amount > 0.005 (Orbiter Min)
        if amount_eth < 0.005:
            console.print("[red]⛔ Amount too low for Orbiter (Min ~0.005 ETH).[/red]")
            return

        final_wei = (wei_amount // 10000 * 10000) + STARKNET_CODE
        final_eth = self.w3.from_wei(final_wei, 'ether')
        
        console.print(f"   🎯 Destination: Starknet (Code: {STARKNET_CODE})")
        console.print(f"   💸 Sending: {final_eth:.18f} ETH")
        console.print(f"   📬 To Maker: {ORBITER_MAKER_BASE}")

        if self.dry_run:
            console.print(Panel(f"[DRY RUN] Transaction Payload:\n"
                              f"To: {ORBITER_MAKER_BASE}\n"
                              f"Value: {final_wei} wei\n"
                              f"ChainId: 8453 (Base)\n"
                              f"Nonce: (Pending)", title="Simulation"))
            return

        # Execute
        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            gas_price = self.w3.eth.gas_price
            
            tx = {
                'to': ORBITER_MAKER_BASE,
                'value': final_wei,
                'gas': 23000, # Simple Transfer is 21000, padding slightly
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': 8453
            }
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            console.print("[yellow]🚀 Broadcasting to Base Network...[/yellow]")
            
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            console.print(f"[green]✅ Bridge Tx Sent! Hash: {self.w3.to_hex(tx_hash)}[/green]")
            console.print("[dim]Wait ~2 mins for funds to arrive on Starknet.[/dim]")
            
        except Exception as e:
            console.print(f"[bold red]❌ Bridge Failed: {e}[/bold red]")

if __name__ == "__main__":
    is_dry = "--no-dry-run" not in sys.argv
    bridge = OrbiterBridge(dry_run=is_dry)
    # Default behavior: Bridge ALL available ETH minus gas
    bal = bridge.get_balance()
    if bal > 0.002:
        bridge.bridge_to_starknet(bal - 0.0005) # Leave small gas for Base execution
    else:
        console.print("[yellow]Transit wallet empty or below min threshold.[/yellow]")
