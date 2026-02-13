#!/usr/bin/env python3
"""
Encrypted Signer - PhantomArbiter Security Pattern Implementation
Professional encryption for StarkNet private keys and sensitive data
Based on PhantomArbiter security architecture for key management
"""

import os
import sys
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass

# Add core to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from loguru import logger

class EncryptedSigner:
    """
    Professional encrypted key management system
    Based on PhantomArbiter security patterns for production-grade key protection
    """
    
    def __init__(self, key_file: Optional[str] = None):
        self.key_file = key_file or "data/encrypted_keys.dat"
        self.salt_file = "data/key_salt.dat"
        self.data_dir = Path(self.key_file).parent
        self.data_dir.mkdir(exist_ok=True)
        
        # Ensure secure permissions
        self._ensure_secure_permissions()
        
        logger.debug("🔐 EncryptedSigner initialized")
    
    def _ensure_secure_permissions(self):
        """Ensure data directory has secure permissions"""
        try:
            # On Unix systems, restrict directory permissions
            if os.name != 'nt':  # Not Windows
                os.chmod(self.data_dir, 0o700)
        except Exception as e:
            logger.warning(f"⚠️ Could not set secure permissions: {e}")
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _load_salt(self) -> bytes:
        """Load or generate salt for key derivation"""
        
        if os.path.exists(self.salt_file):
            with open(self.salt_file, 'rb') as f:
                return f.read()
        else:
            # Generate new salt
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            return salt
    
    def encrypt_private_key(self, private_key: str, password: Optional[str] = None) -> bool:
        """Encrypt and store private key securely"""
        
        try:
            # Get password (from prompt or environment)
            if password is None:
                password = os.getenv("SIGNER_PASSWORD")
                if not password:
                    password = getpass.getpass("🔐 Enter encryption password: ")
            
            # Derive encryption key
            salt = self._load_salt()
            key = self._derive_key(password, salt)
            
            # Encrypt private key
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(private_key.encode())
            
            # Store encrypted data
            key_data = {
                "encrypted_key": base64.b64encode(encrypted_data).decode(),
                "algorithm": "Fernet",
                "kdf": "PBKDF2",
                "created_at": str(Path().resolve())
            }
            
            with open(self.key_file, 'w') as f:
                json.dump(key_data, f, indent=2)
            
            # Secure file permissions
            if os.name != 'nt':
                os.chmod(self.key_file, 0o600)
            
            logger.info("✅ Private key encrypted and stored securely")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to encrypt private key: {e}")
            return False
    
    def decrypt_private_key(self, password: Optional[str] = None) -> Optional[str]:
        """Decrypt and retrieve private key"""
        
        try:
            # Check if key file exists
            if not os.path.exists(self.key_file):
                logger.error("❌ No encrypted key file found")
                return None
            
            # Get password
            if password is None:
                password = os.getenv("SIGNER_PASSWORD")
                if not password:
                    password = getpass.getpass("🔐 Enter decryption password: ")
            
            # Load encrypted data
            with open(self.key_file, 'r') as f:
                key_data = json.load(f)
            
            # Derive decryption key
            salt = self._load_salt()
            key = self._derive_key(password, salt)
            
            # Decrypt private key
            fernet = Fernet(key)
            encrypted_data = base64.b64decode(key_data["encrypted_key"])
            decrypted_data = fernet.decrypt(encrypted_data)
            
            logger.info("✅ Private key decrypted successfully")
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"❌ Failed to decrypt private key: {e}")
            return None
    
    def get_starknet_keypair(self, password: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Get StarkNet keypair from encrypted storage"""
        
        try:
            # Load environment for address
            env_path = Path(__file__).parent.parent.parent / ".env"
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if "=" in line and not line.startswith("#"):
                            key, value = line.strip().split("=", 1)
                            os.environ[key.strip()] = value.strip()
            
            # Get wallet address
            wallet_address = os.getenv("STARKNET_WALLET_ADDRESS")
            if not wallet_address:
                logger.error("❌ STARKNET_WALLET_ADDRESS not found in environment")
                return None
            
            # Decrypt private key
            private_key = self.decrypt_private_key(password)
            if not private_key:
                return None
            
            return {
                "address": wallet_address,
                "private_key": private_key
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get StarkNet keypair: {e}")
            return None
    
    def migrate_from_env(self, password: Optional[str] = None) -> bool:
        """Migrate private key from environment to encrypted storage"""
        
        try:
            # Load environment
            env_path = Path(__file__).parent.parent.parent / ".env"
            if not env_path.exists():
                logger.error("❌ .env file not found")
                return False
            
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key.strip()] = value.strip()
            
            # Get private key from environment
            private_key = os.getenv("STARKNET_PRIVATE_KEY")
            if not private_key:
                logger.error("❌ STARKNET_PRIVATE_KEY not found in environment")
                return False
            
            # Encrypt and store
            success = self.encrypt_private_key(private_key, password)
            if success:
                logger.info("✅ Successfully migrated private key from .env to encrypted storage")
                
                # Optionally remove from .env (commented out for safety)
                # self._remove_from_env()
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    
    def _remove_from_env(self):
        """Remove private key from .env file (USE WITH CAUTION)"""
        
        try:
            env_path = Path(__file__).parent.parent.parent / ".env"
            
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Comment out private key line
            with open(env_path, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.startswith("STARKNET_PRIVATE_KEY="):
                        f.write(f"# MOVED TO ENCRYPTED STORAGE: {line}")
                    else:
                        f.write(line)
            
            logger.info("✅ Private key removed from .env file")
            
        except Exception as e:
            logger.error(f"❌ Failed to remove from .env: {e}")
    
    def verify_encryption(self, password: Optional[str] = None) -> bool:
        """Verify that encryption/decryption is working"""
        
        try:
            # Test with sample data
            test_data = "test_private_key_12345"
            
            # Get password
            if password is None:
                password = os.getenv("SIGNER_PASSWORD")
                if not password:
                    return False  # Can't test without password
            
            # Derive key
            salt = self._load_salt()
            key = self._derive_key(password, salt)
            
            # Encrypt and decrypt test data
            fernet = Fernet(key)
            encrypted = fernet.encrypt(test_data.encode())
            decrypted = fernet.decrypt(encrypted).decode()
            
            return decrypted == test_data
            
        except Exception as e:
            logger.error(f"❌ Encryption verification failed: {e}")
            return False
    
    def get_security_info(self) -> Dict[str, Any]:
        """Get security information about the signer"""
        
        info = {
            "key_file_exists": os.path.exists(self.key_file),
            "salt_file_exists": os.path.exists(self.salt_file),
            "data_dir_secure": False,
            "encryption_ready": False
        }
        
        # Check directory permissions
        try:
            if os.name != 'nt':
                stat_info = os.stat(self.data_dir)
                info["data_dir_secure"] = oct(stat_info.st_mode)[-3:] == "700"
        except:
            pass
        
        # Check if password is available
        if os.getenv("SIGNER_PASSWORD"):
            info["encryption_ready"] = True
        
        return info

# Global signer instance
_signer: Optional[EncryptedSigner] = None

def get_signer() -> EncryptedSigner:
    """Get global encrypted signer instance"""
    global _signer
    if _signer is None:
        _signer = EncryptedSigner()
    return _signer

def main():
    """CLI interface for encrypted signer management"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Encrypted Signer Management")
    parser.add_argument("--migrate", action="store_true", help="Migrate from .env to encrypted storage")
    parser.add_argument("--verify", action="store_true", help="Verify encryption is working")
    parser.add_argument("--info", action="store_true", help="Show security information")
    parser.add_argument("--test", action="store_true", help="Test encryption/decryption")
    args = parser.parse_args()
    
    console = Console()
    
    if args.migrate:
        console.print("🔄 Migrating private key from .env to encrypted storage...", style="bold blue")
        signer = get_signer()
        success = signer.migrate_from_env()
        if success:
            console.print("✅ Migration completed successfully", style="bold green")
        else:
            console.print("❌ Migration failed", style="bold red")
    
    elif args.verify:
        console.print("🔍 Verifying encryption system...", style="bold blue")
        signer = get_signer()
        if signer.verify_encryption():
            console.print("✅ Encryption system working correctly", style="bold green")
        else:
            console.print("❌ Encryption system verification failed", style="bold red")
    
    elif args.info:
        console.print("📊 Security Information:", style="bold blue")
        signer = get_signer()
        info = signer.get_security_info()
        
        for key, value in info.items():
            status = "✅" if value else "❌"
            console.print(f"  {status} {key.replace('_', ' ').title()}: {value}")
    
    elif args.test:
        console.print("🧪 Testing encryption/decryption...", style="bold blue")
        signer = get_signer()
        
        # Test keypair retrieval
        keypair = signer.get_starknet_keypair()
        if keypair:
            console.print("✅ Successfully retrieved encrypted keypair", style="bold green")
            console.print(f"  Address: {keypair['address'][:10]}...")
        else:
            console.print("❌ Failed to retrieve keypair", style="bold red")
    
    else:
        console.print("Encrypted Signer - PhantomArbiter Security Pattern", style="bold blue")
        console.print("Use --help to see available commands")

if __name__ == "__main__":
    from rich.console import Console
    main()
