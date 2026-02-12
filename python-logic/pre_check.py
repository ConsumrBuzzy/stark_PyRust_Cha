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
    
    revenue = 100 * p_steel
    
    gross_profit = revenue - total_cost
    
    # 4. Gas Estimation
    # Assume Refine tx uses ~15,000 gas units (L2 is cheap, but let's be safe)
    # gas_wei is usually low on Starknet (e.g. 1 Gwei = 1e9 wei).
    # ETH Price in SWAY? We don't have it.
    # Let's assume 1 SWAY ~ $0.0005.
    # Gas cost in ETH... we need to convert to SWAY to compare.
    # For now, we'll just check if Gross Profit is substantial (> 100 SWAY).
    # And allow the user to make the final call on Gas.
    
    gas_gwei = gas_wei / 1e9

    # 5. Report
    grid = Table.grid(expand=True)
    grid.add_column(justify="left")
    grid.add_column(justify="right")
    
    grid.add_row("[dim]Iron Ore (x250):[/dim]", f"{250 * p_iron:.2f} SWAY (@ {p_iron})")
    grid.add_row("[dim]Propellant (x20):[/dim]", f"{20 * p_prop:.2f} SWAY (@ {p_prop})")
    grid.add_row("[dim]Refinery Lease:[/dim]", f"{cost_lease:.2f} SWAY")
    grid.add_row("[bold]Total Cost:[/bold]", f"[red]{total_cost:.2f} SWAY[/red]")
    grid.add_row("", "")
    grid.add_row("[bold]Revenue (Steel x100):[/bold]", f"[green]{revenue:.2f} SWAY[/green] (@ {p_steel})")
    grid.add_row("", "")
    
    color = "green" if gross_profit > 0 else "red"
    grid.add_row("[bold]Projected Profit:[/bold]", f"[bold {color}]{gross_profit:.2f} SWAY[/bold {color}]")
    
    console.print(Panel(grid, title="Unit Economics (Per Batch)"))
    
    console.print(f"\n⛽ [bold]Network Status:[/bold] Gas: {gas_gwei:.2f} Gwei | Block: {block}")
    
    if gross_profit > 150.0: # Arbitrary buffer for Gas
        console.print(Panel("[bold green]✅ GO SIGNAL: Profitable Entry[/bold green]\nRecruit your Crewmate. The loop is viable.", style="green"))
    else:
         console.print(Panel("[bold red]⛔ NO-GO SIGNAL: Margins too thin[/bold red]\nWait for spreads to widen.", style="red"))

if __name__ == "__main__":
    run_ghost_scanner()
