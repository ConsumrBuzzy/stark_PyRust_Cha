import time
import json
import logging
from rich.console import Console
from rich.panel import Panel

try:
    import stark_pyrust_chain
except ImportError:
    stark_pyrust_chain = None

# Configure Logging
logging.basicConfig(
    filename='strategy.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

console = Console()

class BaseStrategy:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        
    def log(self, message):
        logging.info(message)
        console.print(f"[dim]{message}[/dim]")

class RefiningStrategy(BaseStrategy):
    """
    Automates the Iron -> Steel refining loop.
    """
    def __init__(self, dry_run=True):
        super().__init__(dry_run)
        self.client = stark_pyrust_chain.PyInfluenceClient()
        self.graph = stark_pyrust_chain.PySupplyChain()
        # Explicitly pass URL from Env to avoid Rust-side dot-env issues
        import os
        rpc_url = os.getenv("STARKNET_MAINNET_URL") or os.getenv("STARKNET_RPC_URL")
        self.starknet = stark_pyrust_chain.PyStarknetClient(rpc_url)
        
        # Load or generate Session Key (In real app, load from Vault)
        # For v0.1.0 demo, we generate a fresh one or assume it's loaded
        try:
            self.session_key = stark_pyrust_chain.PySessionKey()
            self.log("Session Key loaded.")
        except Exception as e:
            self.log(f"Warning: Session Key missing ({e}). Only read-ops available.")
            self.session_key = None

    def tick(self):
        """
        Execute one cycle of the strategy.
        """
        self.log("🔎 Scanning Adalia Markets...")
        
        # 1. Fetch Market Prices (Mocked for now as we don't have full Market API yet)
        # In real implementation: market_prices = self.client.get_market_prices(["Iron Ore", "Steel", "Fuel"])
        market_prices = {
            "Iron Ore": 5.0,
            "Fuel": 2.0,
            "Steel": 20.0 # 20 * 100 = 2000 Rev. Cost = 5*250 (1250) + 2*20 (40) = 1290. Profit ~710.
        }
        
        # 2. Calculate Profitability
        try:
            profit = self.graph.calculate_profitability("Refine Steel", market_prices)
            self.log(f"Computed Profitability: {profit:.2f} SWAY")
            
            # 3. Decision Logic
            if profit > 100.0: # Threshold
                self.execute_refine(profit)
            else:
                self.log("Profit too low. Waiting...")
                
        except Exception as e:
            self.log(f"Error calculating profit: {e}")

    def execute_refine(self, profit):
        self.log(f"[bold green]🚀 Opportunity Detected! Profit: {profit:.2f}[/bold green]")
        
        payload = {
            "contract": "0xInfluenceRefinery",
            "action": "REFINE",
            "recipe": "Iron -> Steel",
            "quantity": 1,
            "timestamp": time.time()
        }
        
        if self.dry_run:
            console.print(Panel(json.dumps(payload, indent=2), title="[DRY RUN] Transaction Payload"))
            self.log("Dry Run complete. No transaction sent.")
        else:
            if self.session_key:
                # Sign and Submit
                # sig = self.session_key.sign(payload)
                # tx = self.starknet.send_tx(payload, sig)
                self.log("Transaction submitted (Mock).")
            else:
                self.log("[red]Cannot Execute: No Session Key[/red]")
