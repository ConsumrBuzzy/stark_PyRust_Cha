import sys
import os
from rich.console import Console

# Add python-logic to path to find strategy_module
sys.path.append(os.path.join(os.getcwd(), 'python-logic'))

# INJECT MOCK ENV for logic testing
# The StarknetClient.new() will look for this.
os.environ["STARKNET_RPC_URL"] = "https://mock.rpc.url"

try:
    from strategy_module import RefiningStrategy
    import stark_pyrust_chain
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

console = Console()

def test_strategy_logic():
    print("\n🏭 Testing Refining Strategy Logic...")
    
    try:
        # Initialize in Dry Run mode
        # This will now find the STARKNET_RPC_URL we injected above
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
        else:
             print(f"   ⚠️ Profit calculation negative? {profit}")

    except Exception as e:
        print(f"   ❌ Strategy Logic failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_strategy_logic()
