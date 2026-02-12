import sys
import os
from rich.console import Console

# Add python-logic to path to find strategy_module
sys.path.append(os.path.join(os.getcwd(), 'python-logic'))

# Robust Env Loader for Windows/UTF-8 issues (Same as Orchestrator)
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

load_env_manual()

try:
    from strategy_module import RefiningStrategy
    import stark_pyrust_chain
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

console = Console()

def test_strategy_logic():
    print("\n🏭 Testing Refining Strategy Logic (Real Env Load)...")
    
    try:
        # Initialize in Dry Run mode
        strategy = RefiningStrategy(dry_run=True)
        print("   ✅ Strategy Initialized.")
        
        print("   ⏳ Triggering Tick (Simulating Market Scan)...")
        strategy.tick()
        
        print("   ✅ Tick completed without error.")
        
        # Verify Rust Graph Logic explicitly for clarity
        graph = stark_pyrust_chain.PySupplyChain()
        prices = {"Iron Ore": 5.0, "Fuel": 2.0, "Steel": 20.0}
        profit = graph.calculate_profitability("Refine Steel", prices)
        
        print(f"   📊 Rust Profit Calc Verify: {profit} SWAY") 
        
        if profit > 0:
             print("   ✅ Profit calculation positive as expected.")

    except Exception as e:
        print(f"   ❌ Strategy Logic failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_strategy_logic()
