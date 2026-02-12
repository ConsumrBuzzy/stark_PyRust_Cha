import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

try:
    import stark_pyrust_chain
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

console = Console()

# Robust Env Loader for Windows/UTF-8 issues
def load_env_manual():
    env_path = ".env"
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = val.strip()
    except Exception as e:
        print(f"Warning: Failed to load .env manually: {e}")

def run_ghost_scanner():
    console.print(Panel.fit("[bold cyan]👻 stark_PyRust_Chain: Ghost Scanner[/bold cyan]", subtitle="ADR-031 Pre-Entry Validation"))
    
    load_env_manual()
    
    # 1. Initialize Clients
    try:
        inf_client = stark_pyrust_chain.PyInfluenceClient()
        sn_client = stark_pyrust_chain.PyStarknetClient(None) # Auto-detect RPC
    except Exception as e:
        console.print(f"[bold red]❌ Client Init Failed:[/bold red] {e}")
        return

    # 2. Fetch Data
    with console.status("[bold green]👻 Ghost Scanning Adalia Prime...[/bold green]"):
        try:
            prices = inf_client.get_market_prices()
            block, gas_wei = sn_client.get_network_status()
        except Exception as e:
             console.print(f"[red]Scan Failed: {e}[/red]")
             return

    # 3. Market Math (Iron -> Steel)
    # Recipe: 250 Iron + 20 Propellant -> 100 Steel (Standard Batch?)
    # Wait, simple recipe in ADR-029 was Iron->Steel logic.
    # ADR-031 Context: "Cost: 250*Iron + 20*Propellant + 50 (Lease)".
    
    p_iron = prices.get("Iron Ore", 0.0)
    p_steel = prices.get("Steel", 0.0)
    p_prop = prices.get("Propellant", 0.0)
    
    cost_materials = (250 * p_iron) + (20 * p_prop)
    cost_lease = 50.0
    total_cost = cost_materials + cost_lease
    
    # --- ADR-040: Logistics & Inventory ---
    # Mock Distance (In real app, fetch from SAGE)
    distance_lots = 0 
    logistics_cost = distance_lots * 15.0
    
    # Mock Inventory (In real app, fetch from SAGE)
    inventory_full = False 
    
    revenue = 100 * p_steel
    gross_profit = revenue - (total_cost + logistics_cost)
    
    # 4. Gas Estimation
    # Assume Refine tx uses ~15,000 gas units
    gas_gwei = gas_wei / 1e9

    # 5. Report
    grid = Table.grid(expand=True)
    grid.add_column(justify="left")
    grid.add_column(justify="right")
    
    grid.add_row("[dim]Iron Ore (x250):[/dim]", f"{250 * p_iron:.2f} SWAY (@ {p_iron})")
    grid.add_row("[dim]Propellant (x20):[/dim]", f"{20 * p_prop:.2f} SWAY (@ {p_prop})")
    grid.add_row("[dim]Refinery Lease:[/dim]", f"{cost_lease:.2f} SWAY")
    if logistics_cost > 0:
        grid.add_row("[dim]Logistics (Fuel/Time):[/dim]", f"[yellow]{logistics_cost:.2f} SWAY[/yellow]")
    
    grid.add_row("[bold]Total Cost:[/bold]", f"[red]{total_cost + logistics_cost:.2f} SWAY[/red]")
    grid.add_row("", "")
    grid.add_row("[bold]Revenue (Steel x100):[/bold]", f"[green]{revenue:.2f} SWAY[/green] (@ {p_steel})")
    grid.add_row("", "")
    
    color = "green" if gross_profit > 0 else "red"
    grid.add_row("[bold]Projected Profit:[/bold]", f"[bold {color}]{gross_profit:.2f} SWAY[/bold {color}]")
    
    console.print(Panel(grid, title="Unit Economics (Per Batch)"))
    
    console.print(f"\n📦 [bold]Inventory Status:[/bold] {'[green]Space Available[/green]' if not inventory_full else '[red]FULL[/red]'}")

    
    # --- ADR-035: Market Calibration (Direct vs Secondary) ---
    market_direct_usd = 5.00
    market_secondary_eth = 0.005
    eth_price_usd = 1920.00 # Feb 2026 Est? Or just use $9.60 from ADR context.
    market_secondary_usd = 9.60 # As per ADR-035
    
    calib_grid = Table.grid(expand=True)
    calib_grid.add_column(justify="left")
    calib_grid.add_column(justify="right")
    
    calib_grid.add_row("Direct Recruitment:", f"[green]${market_direct_usd:.2f}[/green] (Adalia Prime)")
    calib_grid.add_row("Secondary Market (Floor):", f"[red]${market_secondary_usd:.2f}[/red] (~{market_secondary_eth} ETH)")
    
    console.print(Panel(calib_grid, title="Market Entry Calibration"))
    
    calibration_pass = market_direct_usd < market_secondary_usd
    
    # ---------------------------------------------------------

    # --- ADR-037: Capital Detection ---
    wallet = os.getenv("STARKNET_WALLET_ADDRESS")
    capital_pass = False
    eth_balance = 0.0
    
    if wallet:
        try:
            wei = sn_client.get_eth_balance(wallet)
            eth_balance = wei / 1e18
            # Threshold: $12.00 ~ 0.0048 ETH. Let's say 0.004 safe.
            if eth_balance > 0.004:
                capital_pass = True
        except: pass
    
    console.print(f"\n💰 [bold]Wallet Balance:[/bold] {eth_balance:.6f} ETH")

    console.print(f"\n⛽ [bold]Network Status:[/bold] Gas: {gas_gwei:.2f} Gwei | Block: {block}")
    
    if gross_profit > 150.0 and calibration_pass: 
        if capital_pass:
            console.print(Panel("[bold green]✅ CAPITAL DETECTED. PROCEED TO RECRUITMENT.[/bold green]\n"
                                "1. Profit Margin confirmed.\n"
                                "2. Direct Recruit optimal.\n"
                                "3. Funds Ready.", style="green"))
        else:
            console.print(Panel("[bold yellow]⚠️  Recruitment Viable but NO CAPITAL[/bold yellow]\n"
                                "Margins good, but Wallet < $12.00.\n"
                                "Run 'onramp.py' first.", style="yellow"))
    else:
         console.print(Panel("[bold red]⛔ NO-GO SIGNAL[/bold red]\nEither margins thin OR Secondary market cheaper.", style="red"))


if __name__ == "__main__":
    run_ghost_scanner()
