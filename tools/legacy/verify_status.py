import sys
import os
from rich.console import Console
from rich.panel import Panel

try:
    import stark_pyrust_chain
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Robust Env Loader
def load_env_manual():
    env_path = ".env"
    if not os.path.exists(env_path): return
    try:
        # Try UTF-8 then Latin-1
        lines = []
        try:
            with open(env_path, "r", encoding="utf-8") as f: lines = f.readlines()
        except UnicodeDecodeError:
            with open(env_path, "r", encoding="latin-1") as f: lines = f.readlines()
            
        for line in lines:
            if line.strip() and not line.strip().startswith("#") and "=" in line:
                key, val = line.strip().split("=", 1)
                if key.strip() not in os.environ: os.environ[key.strip()] = val.strip()
                
        # Aliases
        if "STARKNET_RPC_URL" not in os.environ:
             for alias in ["STARKNET_MAINNET_URL", "STARKNET_LAVA_URL"]:
                 if os.environ.get(alias): os.environ["STARKNET_RPC_URL"] = os.environ[alias]; break
    except: pass

load_env_manual()
console = Console()

def verify_status():
    console.print(Panel.fit("[bold blue]🩺 Crew Status & Life Support (ADR-041)[/bold blue]"))
    
    try:
        # Use Influence Client for Metadata
        inf_client = stark_pyrust_chain.PyInfluenceClient()
        crew_id = 1 # Mock
        
        console.print(f"   🔎 Fetching Metadata for Crew #{crew_id}...")
        
        # Unpack 5 values (ADR-043)
        is_busy, busy_until, food_kg, location, class_id = inf_client.get_crew_metadata(crew_id)
        
        # Logic Interpretation
        status_text = "BUSY" if is_busy else "ACTIVE"
        status_color = "red" if is_busy else "green"
        
        food_text = f"{food_kg} kg"
        food_color = "green" if food_kg > 550 else "red"
        
        class_name = "Engineer" if class_id == 1 else f"Unknown ({class_id})"
        
        console.print(f"   🛠️ Status:   [{status_color}]{status_text}[/{status_color}]")
        if is_busy:
            console.print(f"      ⏳ Until: {busy_until}")
            
        console.print(f"   👷 Class:    [bold cyan]{class_name}[/bold cyan]")
        console.print(f"   🍎 Food:     [{food_color}]{food_text}[/{food_color}]")
        console.print(f"   📍 Location: Lot {location}")
        
        if food_kg < 550:
             console.print("[red]⚠️  STARVATION WARNING: Rations needed![/red]")
        else:
             console.print("[green]✅ Rations Sufficient (> 500kg)[/green]")

    except Exception as e:
        console.print(f"[bold red]❌ Failed:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_status()
