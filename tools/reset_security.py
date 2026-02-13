#!/usr/bin/env python3
"""
Security Reset - Manual Password Initialization
Corrects the security gap by forcing interactive password setup
Ensures user sovereignty over private key encryption
"""

import os
import sys
import getpass
from pathlib import Path

# Add core to path
sys.path.append(str(Path(__file__).parent.parent))

from rich.console import Console
from loguru import logger

def reset_security():
    """Reset security with manual password initialization"""
    
    console = Console()
    
    console.print("🔐 [SECURITY] MASTER SIGNER PASSWORD RESET", style="bold red")
    console.print("=" * 50, style="dim")
    console.print("This will wipe existing encrypted files and re-encrypt", style="yellow")
    console.print("your private key with a password you choose.", style="yellow")
    console.print()
    
    # Confirmation
    confirm = console.input("⚠️  Are you sure you want to continue? [y/N]: ")
    if confirm.lower() != 'y':
        console.print("❌ Security reset cancelled", style="bold red")
        return
    
    console.print()
    
    # Force manual password prompt
    console.print("🔑 Set your Master Signer Password", style="bold blue")
    console.print("This password will encrypt your private key", style="dim")
    console.print("and will be required for all operations.", style="dim")
    console.print()
    
    try:
        password = getpass.getpass("Set your NEW Master Signer Password: ")
        if not password:
            console.print("❌ Password cannot be empty", style="bold red")
            return
        
        if len(password) < 8:
            console.print("❌ Password must be at least 8 characters", style="bold red")
            return
        
        confirm = getpass.getpass("Confirm Password: ")
        if password != confirm:
            console.print("❌ Passwords do not match. Aborting.", style="bold red")
            return
            
    except KeyboardInterrupt:
        console.print("\n❌ Security reset cancelled", style="bold red")
        return
    
    console.print()
    console.print("🗑️  Wiping existing encrypted files...", style="yellow")
    
    # Remove existing encrypted files
    data_dir = Path("data")
    key_file = data_dir / "encrypted_keys.dat"
    salt_file = data_dir / "key_salt.dat"
    
    if key_file.exists():
        key_file.unlink()
        console.print(f"  ✅ Removed {key_file}")
    
    if salt_file.exists():
        salt_file.unlink()
        console.print(f"  ✅ Removed {salt_file}")
    
    # Load environment
    env_path = Path(".env")
    if not env_path.exists():
        console.print("❌ .env file not found", style="bold red")
        return
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key.strip()] = value.strip()
    
    # Get private key
    raw_pk = os.getenv("STARKNET_PRIVATE_KEY")
    if not raw_pk:
        console.print("❌ STARKNET_PRIVATE_KEY not found in .env", style="bold red")
        return
    
    console.print("🔐 Encrypting private key with your password...", style="blue")
    
    # Import and initialize signer with manual password
    try:
        from core.safety import EncryptedSigner
        
        # Set password for this session
        os.environ["SIGNER_PASSWORD"] = password
        
        signer = EncryptedSigner()
        
        # Encrypt the private key
        success = signer.encrypt_private_key(raw_pk, password)
        
        if not success:
            console.print("❌ Failed to encrypt private key", style="bold red")
            return
        
        console.print("✅ Private key encrypted successfully", style="bold green")
        
    except Exception as e:
        console.print(f"❌ Encryption failed: {e}", style="bold red")
        return
    
    console.print()
    console.print("🧪 Verifying encryption...", style="blue")
    
    # Test decryption
    try:
        test_signer = EncryptedSigner()
        decrypted_key = test_signer.decrypt_private_key(password)
        
        if decrypted_key == raw_pk:
            console.print("✅ Encryption verification passed", style="bold green")
        else:
            console.print("❌ Encryption verification failed", style="bold red")
            return
            
    except Exception as e:
        console.print(f"❌ Verification failed: {e}", style="bold red")
        return
    
    # Test keypair retrieval
    try:
        keypair = test_signer.get_starknet_keypair(password)
        if keypair:
            console.print(f"✅ Keypair retrieval successful: {keypair['address'][:10]}...", style="bold green")
        else:
            console.print("❌ Keypair retrieval failed", style="bold red")
            return
            
    except Exception as e:
        console.print(f"❌ Keypair test failed: {e}", style="bold red")
        return
    
    console.print()
    console.print("🎯 SECURITY RESET COMPLETE", style="bold green")
    console.print("=" * 40, style="dim")
    console.print("✅ Private key is now locked behind your password", style="green")
    console.print("✅ Encryption verified and tested", style="green")
    console.print("✅ Keypair retrieval working", style="green")
    console.print()
    console.print("⚠️  IMPORTANT SECURITY NOTES:", style="bold yellow")
    console.print("  • Your password is now required for all operations")
    console.print("  • Store your password securely (password manager)")
    console.print("  • Never share your SIGNER_PASSWORD")
    console.print("  • Consider removing STARKNET_PRIVATE_KEY from .env")
    console.print()
    console.print("🚀 Your StarkNet infrastructure is now properly secured!", style="bold green")

def verify_security():
    """Verify current security setup"""
    
    console = Console()
    
    console.print("🔍 Security Verification", style="bold blue")
    console.print("=" * 30, style="dim")
    
    try:
        from core.safety import EncryptedSigner
        
        signer = EncryptedSigner()
        security_info = signer.get_security_info()
        
        console.print("📊 Current Security Status:")
        for key, value in security_info.items():
            status = "✅" if value else "❌"
            console.print(f"  {status} {key.replace('_', ' ').title()}: {value}")
        
        # Test password requirement
        if security_info["key_file_exists"]:
            console.print()
            console.print("🧪 Testing password requirement...")
            
            # This should fail without password
            try:
                keypair = signer.get_starknet_keypair()
                if keypair:
                    console.print("⚠️  WARNING: Keypair retrieved without password!", style="bold yellow")
                    console.print("   This suggests a default password is being used")
                else:
                    console.print("✅ Password requirement confirmed", style="bold green")
            except Exception:
                console.print("✅ Password requirement confirmed", style="bold green")
        
    except Exception as e:
        console.print(f"❌ Security verification failed: {e}", style="bold red")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Security Reset Utility")
    parser.add_argument("--verify", action="store_true", help="Verify current security setup")
    args = parser.parse_args()
    
    if args.verify:
        verify_security()
    else:
        reset_security()
