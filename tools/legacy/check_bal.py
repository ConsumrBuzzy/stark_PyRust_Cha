import os
import sys

# Add python-logic to path to import strategy
sys.path.append(os.path.join(os.getcwd(), 'python-logic'))

try:
    from strategy_module import RefiningStrategy
    from rich.console import Console
    console = Console()
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def check_bal():
    # Load env manually
    env_path = ".env"
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

    wallet = os.getenv("STARKNET_WALLET_ADDRESS")
    strategy = RefiningStrategy(dry_run=True)
    
    try:
        wei = strategy.starknet.get_eth_balance(wallet)
        eth = wei / 1e18
        result = f"Starknet Balance: {eth:.6f} ETH\nTarget Wallet: {wallet}"
        console.print(result)
        with open("bal_report.txt", "w", encoding="utf-8") as f:
            f.write(result)
    except Exception as e:
        console.print(f"[red]Error fetching balance: {e}[/red]")

if __name__ == "__main__":
    check_bal()
