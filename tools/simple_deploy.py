#!/usr/bin/env python3
"""
Simple StarkNet Account Deployment
Using existing deployment patterns
"""

import asyncio
import os
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def deploy_account():
    """Deploy StarkNet account using existing patterns"""
    print("🚀 Simple StarkNet Account Deployment")
    print("=" * 40)
    
    try:
        # Import existing deployment engine
        from ops.env import build_config
        from foundation.network import NetworkOracle
        from foundation.security import SecurityManager
        
        # Initialize systems
        config = build_config()
        network_oracle = NetworkOracle()
        await network_oracle.initialize()
        
        security_manager = SecurityManager()
        await security_manager.initialize()
        
        print(f"📍 Address: {config.starknet_address}")
        print(f"📡 Network: StarkNet Mainnet")
        
        # Check current balance
        balance = await network_oracle.get_balance(config.starknet_address, "starknet")
        print(f"💰 Balance: {balance:.6f} ETH")
        
        if balance < 0.01:
            print("❌ Insufficient balance for deployment")
            return False
        
        print("✅ Sufficient balance for deployment")
        
        # Use existing deployment engine
        from ops.activation import AccountActivator
        
        activator = AccountActivator()
        
        # Try activation
        print("🔥 Attempting deployment...")
        success = await activator.activate_account(dry_run=False)
        
        if success:
            print("🎉 ACCOUNT DEPLOYED SUCCESSFULLY!")
            print("💼 Ready for transactions")
            return True
        else:
            print("❌ Deployment failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(deploy_account())
