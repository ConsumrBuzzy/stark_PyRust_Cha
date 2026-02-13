"""
PyPro Systems - Foundation Security Manager
High-level security API for the Recovery Kernel
"""

import os
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

# Import the existing encrypted signer
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.safety.encrypted_signer import EncryptedSigner

class SecurityManager:
    """High-level security manager for recovery operations"""
    
    def __init__(self):
        self.encrypted_signer = EncryptedSigner()
        self.is_unlocked = False
        self.master_password: Optional[str] = None
        self.private_key_cache: Dict[str, str] = {}
    
    async def initialize(self) -> bool:
        """Initialize security manager"""
        try:
            # The encrypted signer initializes itself
            self.is_unlocked = False
            return True
        except Exception as e:
            print(f"❌ Security manager initialization failed: {e}")
            return False
    
    async def unlock_vault(self, master_password: str) -> bool:
        """Unlock the security vault with master password"""
        try:
            # Set password in environment for encrypted signer
            os.environ["SIGNER_PASSWORD"] = master_password
            
            # Test decryption by trying to get keypair
            keypair = self.encrypted_signer.get_starknet_keypair()
            if not keypair:
                raise Exception("Failed to retrieve keypair")
            
            self.master_password = master_password
            self.is_unlocked = True
            
            print("✅ Security vault unlocked successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to unlock security vault: {e}")
            self.is_unlocked = False
            return False
    
    async def unlock_vault_auto(self) -> bool:
        """Unlock the security vault using environment variable (Full-Auto mode)"""
        # Check for password in environment first
        password = os.getenv('SIGNER_PASSWORD')
        
        if not password:
            print("❌ SIGNER_PASSWORD not found in environment")
            print("   Full-Auto mode requires SIGNER_PASSWORD to be set")
            return False
        
        print("🔓 Full-Auto mode: Using SIGNER_PASSWORD from environment")
        return await self.unlock_vault(password)
    
    def lock_vault(self) -> None:
        """Lock the security vault"""
        self.master_password = None
        self.is_unlocked = False
        self.private_key_cache.clear()
        
        # Clear password from environment
        if "SIGNER_PASSWORD" in os.environ:
            del os.environ["SIGNER_PASSWORD"]
        
        print("🔒 Security vault locked")
    
    def is_vault_unlocked(self) -> bool:
        """Check if vault is unlocked"""
        return self.is_unlocked
    
    async def get_starknet_private_key(self) -> Optional[str]:
        """Get StarkNet private key"""
        if not self.is_unlocked:
            print("❌ Security vault is locked")
            return None
        
        try:
            # Check cache first
            if "starknet" in self.private_key_cache:
                return self.private_key_cache["starknet"]
            
            # Get from encrypted signer
            keypair = self.encrypted_signer.get_starknet_keypair()
            if keypair and "private_key" in keypair:
                private_key = keypair["private_key"]
                self.private_key_cache["starknet"] = private_key
                return private_key
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to get StarkNet private key: {e}")
            return None
    
    async def get_phantom_private_key(self) -> Optional[str]:
        """Get Phantom/EVM private key"""
        if not self.is_unlocked:
            print("❌ Security vault is locked")
            return None
        
        try:
            # Check cache first
            if "phantom" in self.private_key_cache:
                return self.private_key_cache["phantom"]
            
            # Try PHANTOM_BASE_PRIVATE_KEY first
            phantom_key = os.getenv("PHANTOM_BASE_PRIVATE_KEY")
            if phantom_key:
                self.private_key_cache["phantom"] = phantom_key
                return phantom_key
            
            # Fallback to SOLANA_PRIVATE_KEY
            solana_key = os.getenv("SOLANA_PRIVATE_KEY")
            if solana_key:
                self.private_key_cache["phantom"] = solana_key
                return solana_key
            
            print("❌ No Phantom private key found in environment")
            return None
            
        except Exception as e:
            print(f"❌ Failed to get Phantom private key: {e}")
            return None
    
    async def get_starknet_keypair(self) -> Optional[Dict[str, Any]]:
        """Get complete StarkNet keypair"""
        if not self.is_unlocked:
            print("❌ Security vault is locked")
            return None
        
        try:
            return self.encrypted_signer.get_starknet_keypair()
        except Exception as e:
            print(f"❌ Failed to get StarkNet keypair: {e}")
            return None
    
    async def sign_starknet_transaction(self, transaction: Dict[str, Any]) -> Optional[str]:
        """Sign StarkNet transaction"""
        if not self.is_unlocked:
            print("❌ Security vault is locked")
            return None
        
        try:
            # This would integrate with the encrypted signer's signing method
            # Implementation depends on the specific signing interface
            private_key = await self.get_starknet_private_key()
            if not private_key:
                return None
            
            # Placeholder for actual signing logic
            # In practice, this would use the private key to sign the transaction
            print("🔐 Signing StarkNet transaction...")
            return "signed_transaction_placeholder"
            
        except Exception as e:
            print(f"❌ Failed to sign StarkNet transaction: {e}")
            return None
    
    async def sign_evm_transaction(self, transaction: Dict[str, Any]) -> Optional[str]:
        """Sign EVM transaction"""
        if not self.is_unlocked:
            print("❌ Security vault is locked")
            return None
        
        try:
            from web3 import Web3
            
            private_key = await self.get_phantom_private_key()
            if not private_key:
                return None
            
            # Sign the transaction
            signed_tx = Web3().eth.account.sign_transaction(transaction, private_key)
            return signed_tx.raw_transaction.hex()
            
        except Exception as e:
            print(f"❌ Failed to sign EVM transaction: {e}")
            return None
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security status summary"""
        return {
            "vault_unlocked": self.is_unlocked,
            "cached_keys": list(self.private_key_cache.keys()),
            "environment_keys": {
                "phantom_base": bool(os.getenv("PHANTOM_BASE_PRIVATE_KEY")),
                "solana": bool(os.getenv("SOLANA_PRIVATE_KEY")),
                "signer_password": bool(os.getenv("SIGNER_PASSWORD"))
            }
        }
    
    def print_security_status(self) -> None:
        """Print security status summary"""
        status = self.get_security_status()
        
        print(f"🔐 Security Status")
        print(f"   Vault: {'🔓 Unlocked' if status['vault_unlocked'] else '🔒 Locked'}")
        print(f"   Cached Keys: {len(status['cached_keys'])}")
        print(f"   Environment Keys:")
        print(f"     Phantom Base: {'✅' if status['environment_keys']['phantom_base'] else '❌'}")
        print(f"     Solana: {'✅' if status['environment_keys']['solana'] else '❌'}")
        print(f"     Signer Password: {'✅' if status['environment_keys']['signer_password'] else '❌'}")
    
    async def shutdown(self) -> None:
        """Shutdown security manager"""
        print("🛑 Shutting down security manager...")
        
        # Lock vault and clear sensitive data
        self.lock_vault()
        
        # Clear encrypted signer
        if hasattr(self.encrypted_signer, 'cleanup'):
            self.encrypted_signer.cleanup()
        
        print("✅ Security manager shutdown complete")
