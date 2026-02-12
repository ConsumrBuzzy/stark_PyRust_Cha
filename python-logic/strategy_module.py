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
        self.influence = stark_pyrust_chain.PyInfluenceClient() # New for ADR-041
        
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
        # --- Safety Checks (ADR-029) ---
        try:
            block, gas_wei = self.starknet.get_network_status()
            gas_gwei = gas_wei / 1e9
            
            # --- ADR-029: Solvency Check ---
            import os
            wallet = os.getenv("STARKNET_WALLET_ADDRESS")
            if wallet:
                wei = self.starknet.get_eth_balance(wallet)
                eth = wei / 1e18
                self.log(f"   Solvency: [{ 'green' if eth > 0.005 else 'red' }]{eth:.4f} ETH[/{ 'green' if eth > 0.005 else 'red' }]")
                
                if eth < 0.005 and not self.dry_run:
                    self.log("[bold red]⛔ Solvency Alert: Balance < 0.005 ETH. Aborting Cycle.[/bold red]")
                    return
            else:
                 self.log("[yellow]⚠️  No Wallet Address. Skipping Solvency Check.[/yellow]")
            
            # --- ADR-041/043: Life Support & Class Affinity ---
            # Mock Crew ID: 1
            # Returns: (is_busy, busy_until, food_kg, location, class_id)
            is_busy, busy_until, food_kg, location, class_id = self.influence.get_crew_metadata(1)
            
            status_color = "red" if is_busy else "green"
            food_color = "green" if food_kg > 550 else "red"
            class_name = "Engineer" if class_id == 1 else f"Unknown ({class_id})"
            class_color = "green" if class_id == 1 else "yellow"

            self.log(f"🔎 Scanning Adalia... [Block: {block} | Gas: {gas_gwei:.2f}] [Status: [{status_color}]{'BUSY' if is_busy else 'ACTIVE'}[/{status_color}]]")
            self.log(f"   Health: [Food: [{food_color}]{food_kg}kg[/{food_color}] | Class: [{class_color}]{class_name}[/{class_color}]]")
            
            if is_busy:
                self.log("[bold yellow]Crew Busy - Standing Down.[/bold yellow]")
                return

            if food_kg < 550:
                 self.log("[bold red]Crew Hungry (<550kg). Triggering Restock Protocol (Manual).[/bold red]")
                 return

            if class_id != 1:
                self.log("[yellow]⚠️  Efficiency Warning: Crew is not an Engineer. -50% Speed penalty active.[/yellow]")
            
            # --- ADR-043: Propellant Lock ---
            # Logic: Ensure Fuel is bought BEFORE Iron.
            # (Implemented in order execution flow - Placeholder for Phase 5)
            
            if gas_gwei > 30.0:
                self.log(f"[bold red]⛔ High Gas Detected ({gas_gwei:.2f} > 30.0). Yielding...[/bold red]")
                return
        except Exception as e:
            self.log(f"⚠️ Failed to fetch status: {e}")
            return # Exit if network/status fails

        # --- Market Logic ---
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
