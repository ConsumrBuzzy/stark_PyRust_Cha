"""
ADR-058: Chaser Strategy (Headless Bridge)
===========================================
Signs and sends a $15 'Chaser' from a reserve wallet to Starknet
via Orbiter Finance, bypassing visual UIs like Phantom/BaseScan.
"""

import os
import sys
from web3 import Web3
from rich.console import Console
from rich.panel import Panel

console = Console()

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

load_env()

# Orbiter Config
MAKER_ADDRESS = "0xe530d28960d48708ccf3e62aa7b42a80bc427aef"
STARKNET_CODE = 9004

class ChaserBot:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        # Use public Base RPC
        self.w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
        self.priv_key = os.getenv("TRANSIT_EVM_PRIVATE_KEY")
        if self.priv_key:
            self.account = self.w3.eth.account.from_key(self.priv_key)
        else:
            self.account = None

    def send_chaser(self, amount_eth=0.0063):
        """Amount includes the 9004 code."""
        if not self.account:
            console.print("[red]❌ TRANSIT_EVM_PRIVATE_KEY missing.[/red]")
            return

        console.print(Panel(f"🚀 [bold]Initiating ADR-058 Chaser[/bold]\nDest: Starknet\nAmt: {amount_eth} ETH", title="Chaser Engine"))
        
        # Orbiter Handshake: Amount_Wei = (Actual_Wei // 10000 * 10000) + Destination_Code
        wei_base = self.w3.to_wei(amount_eth, 'ether')
        final_wei = (wei_base // 10000 * 10000) + STARKNET_CODE
        
        tx = {
            'to': self.w3.to_checksum_address(MAKER_ADDRESS),
            'value': final_wei,
            'gas': 100000, # Hardened gas limit
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'chainId': 8453
        }

        if self.dry_run:
            console.print(f"[yellow][DRY RUN][/yellow] Tx Payload: {tx}")
            return

        signed = self.w3.eth.account.sign_transaction(tx, self.priv_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        console.print(f"[bold green]✅ Chaser Sent![/bold green] Hash: {self.w3.to_hex(tx_hash)}")

if __name__ == "__main__":
    is_dry = "--no-dry-run" not in sys.argv
    bot = ChaserBot(dry_run=is_dry)
    bot.send_chaser()
