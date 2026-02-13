#!/usr/bin/env python3
"""
Encrypted Signer Setup - Automated Security Configuration
Sets up encrypted key storage for StarkNet private keys
"""

import os
import sys
from pathlib import Path

# Add core to path
sys.path.append(str(Path(__file__).parent.parent))

from core.safety import get_signer
from rich.console import Console as console
from loguru import logger

def setup_encrypted_signer():
    """Setup encrypted signer with default password for demo"""
    
    console = console()
    console.print("🔐 Encrypted Signer Setup", style="bold blue")
    console.print("Setting up professional key encryption...", style="dim")
    
    # Use a default password for demo (in production, use secure password)
    demo_password = "StarkNet_Security_Demo_2026"
    
    # Set environment variable for password
    os.environ["SIGNER_PASSWORD"] = demo_password
    
    # Initialize signer
    signer = get_signer()
    
    # Migrate from environment
    console.print("🔄 Migrating private key from .env to encrypted storage...")
    success = signer.migrate_from_env(demo_password)
    
    if success:
        console.print("✅ Migration completed successfully", style="bold green")
        
        # Verify encryption
        console.print("🔍 Verifying encryption system...")
        if signer.verify_encryption(demo_password):
            console.print("✅ Encryption system working correctly", style="bold green")
        else:
            console.print("❌ Encryption verification failed", style="bold red")
            return False
        
        # Test keypair retrieval
        console.print("🧪 Testing encrypted keypair retrieval...")
        keypair = signer.get_starknet_keypair(demo_password)
        if keypair:
            console.print("✅ Successfully retrieved encrypted keypair", style="bold green")
            console.print(f"  Address: {keypair['address'][:10]}...")
        else:
            console.print("❌ Failed to retrieve keypair", style="bold red")
            return False
        
        # Show security info
        console.print("\n📊 Final Security Status:")
        info = signer.get_security_info()
        for key, value in info.items():
            status = "✅" if value else "❌"
            console.print(f"  {status} {key.replace('_', ' ').title()}: {value}")
        
        console.print("\n🎯 Encrypted Signer Setup Complete!", style="bold green")
        console.print("Your private keys are now professionally encrypted and secured.")
        
        return True
    else:
        console.print("❌ Migration failed", style="bold red")
        return False

if __name__ == "__main__":
    try:
        success = setup_encrypted_signer()
        if success:
            console.print("\n💡 Next steps:")
            console.print("  1. Your private key is now encrypted")
            console.print("  2. The system will automatically use encrypted storage")
            console.print("  3. Keep your SIGNER_PASSWORD secure")
        else:
            console.print("\n❌ Setup failed. Check logs for details.")
            sys.exit(1)
    except Exception as e:
        console.print(f"❌ Setup error: {e}", style="bold red")
        sys.exit(1)
