import os
import sys
import asyncio
import json

try:
    import ccxt.async_support as ccxt
except ImportError:
    print("ccxt not installed")
    sys.exit(1)

async def check_networks():
    # Load keys (simple loader for this script)
    api_key = os.getenv("COINBASE_CLIENT_API_KEY") or os.getenv("COINBASE_API_KEY")
    api_secret = os.getenv("COINBASE_API_PRIVATE_KEY") or os.getenv("COINBASE_API_SECRET")
    
    if api_secret: api_secret = api_secret.replace("\\n", "\n")

    if not api_key or not api_secret:
        # Try to read .env manually if not in env
        try:
             with open(".env", "r", encoding="utf-8") as f:
                 for line in f:
                     if "=" in line and not line.startswith("#"):
                         k, v = line.strip().split("=", 1)
                         if "API_KEY" in k and not api_key: api_key = v
                         if "PRIVATE_KEY" in k or "SECRET" in k and not api_secret: api_secret = v.replace("\\n", "\n")
        except: pass

    exchange = ccxt.coinbase({
        'apiKey': api_key,
        'secret': api_secret,
    })
    
    try:
        await exchange.load_markets()
        
        print("--- ETH Networks ---")
        if 'ETH' in exchange.currencies:
            networks = exchange.currencies['ETH'].get('networks', {})
            print(json.dumps(networks, indent=2))
        else:
            print("ETH not found in currencies")

        print("\n--- USDC Networks ---")
        if 'USDC' in exchange.currencies:
            networks = exchange.currencies['USDC'].get('networks', {})
            print(json.dumps(networks, indent=2))
        else:
            print("USDC not found in currencies")
            
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(check_networks())
