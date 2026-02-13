#!/usr/bin/env python3
"""
Repository Refactor - Structural Hardening
Reorganizes tangled scripts into professional directory structure
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List
import sys

class RepoRefactor:
    """Hardens repository structure for production deployment"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.new_structure = {
            "core/": [
                "providers.py",
                "shadow.py", 
                "models.py",
                "__init__.py"
            ],
            "tools/": [
                "sentry.py",
                "activate.py",
                "inventory.py",
                "__init__.py"
            ],
            "docs/": [
                "ARCHITECTURE.md",
                "SECURITY.md",
                "README.md"
            ],
            "data/": [
                "reports/",
                "logs/"
            ]
        }
        
        # File mappings (old -> new location)
        self.file_mappings = {
            "ghost_sentry_v3_shadow.py": "tools/sentry.py",
            "shadow_state_check.py": "core/shadow.py",
            "rpc_diagnostic_hub.py": "core/providers.py",
            "inventory_heartbeat.py": "tools/inventory.py",
            "rescue_funds.py": "tools/rescue.py",
            "simple_starknet_check.py": "tools/simple_check.py",
            "orbiter_bridge_checker.py": "tools/orbiter_checker.py",
            "verify_ghost.py": "tools/verify_ghost.py",
            "ghost_sentry_loop.py": "tools/legacy_sentry.py",
            "starknet_audit.py": "tools/audit.py"
        }
        
        # Files to keep in root
        self.root_files = [
            ".env",
            ".env.example", 
            "requirements.txt",
            "setup_venv.py",
            "README.md",
            ".gitignore"
        ]
    
    def create_directory_structure(self):
        """Create the hardened directory structure"""
        
        print("🏗️ Creating hardened directory structure...")
        
        for directory, files in self.new_structure.items():
            dir_path = self.project_root / directory
            
            # Create directory
            dir_path.mkdir(exist_ok=True)
            print(f"  📁 Created: {directory}")
            
            # Create subdirectories
            for file_or_dir in files:
                if file_or_dir.endswith("/"):
                    (dir_path / file_or_dir).mkdir(exist_ok=True)
                    print(f"    📁 Created: {directory}{file_or_dir}")
        
        print("✅ Directory structure created")
    
    def move_files_to_new_structure(self):
        """Move files to their new locations"""
        
        print("\n📦 Moving files to hardened structure...")
        
        moved_files = []
        failed_moves = []
        
        for old_file, new_location in self.file_mappings.items():
            old_path = self.project_root / old_file
            
            if old_path.exists():
                new_path = self.project_root / new_location
                
                # Create parent directory if needed
                new_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.move(str(old_path), str(new_path))
                    moved_files.append((old_file, new_location))
                    print(f"  📄 {old_file} -> {new_location}")
                except Exception as e:
                    failed_moves.append((old_file, str(e)))
                    print(f"  ❌ Failed to move {old_file}: {e}")
            else:
                print(f"  ⚠️ File not found: {old_file}")
        
        print(f"\n✅ Moved {len(moved_files)} files")
        if failed_moves:
            print(f"❌ Failed to move {len(failed_moves)} files")
        
        return moved_files, failed_moves
    
    def update_imports_in_moved_files(self):
        """Update import statements in moved files"""
        
        print("\n🔧 Updating imports in moved files...")
        
        updated_files = []
        failed_updates = []
        
        for old_file, new_location in self.file_mappings.items():
            new_path = self.project_root / new_location
            
            if new_path.exists():
                try:
                    with open(new_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Update sys.path additions
                    if 'sys.path.append(os.path.join(os.getcwd()' in content:
                        content = content.replace(
                            'sys.path.append(os.path.join(os.getcwd(), \'python-logic\'))',
                            'sys.path.append(os.path.join(os.path.dirname(__file__), \'..\'))'
                        )
                    
                    # Update relative imports for core modules
                    if new_location.startswith('tools/'):
                        # Tools files should import from core
                        content = content.replace(
                            'from shadow_state_check import',
                            'from core.shadow import'
                        )
                        content = content.replace(
                            'from rpc_diagnostic_hub import',
                            'from core.providers import'
                        )
                    
                    # Update python-logic imports
                    content = content.replace(
                        'sys.path.append(os.path.join(os.getcwd(), \'python-logic\'))',
                        'sys.path.append(os.path.join(os.path.dirname(__file__), \'..\'))'
                    )
                    
                    # Save updated content
                    if content != original_content:
                        with open(new_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        updated_files.append(new_location)
                        print(f"  🔧 Updated imports in {new_location}")
                    
                except Exception as e:
                    failed_updates.append((new_location, str(e)))
                    print(f"  ❌ Failed to update {new_location}: {e}")
        
        print(f"\n✅ Updated imports in {len(updated_files)} files")
        if failed_updates:
            print(f"❌ Failed to update {len(failed_updates)} files")
        
        return updated_files, failed_updates
    
    def create_core_modules(self):
        """Create core module files"""
        
        print("\n🧱 Creating core modules...")
        
        # Create core/__init__.py
        core_init = self.project_root / "core/__init__.py"
        with open(core_init, 'w') as f:
            f.write('"""StarkNet Core Infrastructure\n\n hardened modules for RPC resilience, shadow protocols, and data models\n"""\n\nfrom .providers import NetworkSentinel\nfrom .shadow import ShadowStateChecker\nfrom .models import AccountBalance, TransactionResult\n\n__all__ = ["NetworkSentinel", "ShadowStateChecker", "AccountBalance", "TransactionResult"]\n')
        print("  📄 Created: core/__init__.py")
        
        # Create tools/__init__.py
        tools_init = self.project_root / "tools/__init__.py"
        with open(tools_init, 'w') as f:
            f.write('"""StarkNet Operational Tools\n\n production scripts for monitoring, activation, and recovery\n"""\n')
        print("  📄 Created: tools/__init__.py")
        
        # Create models.py (basic structure)
        models_py = self.project_root / "core/models.py"
        with open(models_py, 'w') as f:
            f.write('''"""Data Models for StarkNet Operations"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AccountBalance(BaseModel):
    """Account balance information"""
    address: str
    balance_eth: float
    balance_usd: float
    last_updated: datetime
    provider: str
    
class TransactionResult(BaseModel):
    """Transaction execution result"""
    hash: str
    status: str
    gas_used: int
    timestamp: datetime
    
class RPCProvider(BaseModel):
    """RPC provider information"""
    name: str
    url: str
    latency_ms: float
    success_rate: float
    methods_supported: Dict[str, bool]
''')
        print("  📄 Created: core/models.py")
    
    def create_activation_script(self):
        """Create the account activation script"""
        
        print("\n[ACTIVATION] Creating activation script...")
        
        activate_py = self.project_root / "tools/activate.py"
        with open(activate_py, 'w', encoding='utf-8') as f:
            f.write('''#!/usr/bin/env python3
"""
Account Activation - Self-Funded Proxy Deploy
Activates undeployed StarkNet account using internal ETH balance
"""

import asyncio
import os
import sys
from pathlib import Path

# Add core to path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.models import StarknetChainId
from rich.console import Console

class AccountActivator:
    """Activates undeployed StarkNet accounts"""
    
    def __init__(self):
        self.console = Console()
        self.load_env()
        
        # Account configuration
        self.wallet_address = os.getenv("STARKNET_WALLET_ADDRESS")
        self.private_key = os.getenv("STARKNET_PRIVATE_KEY")
        self.rpc_url = os.getenv("STARKNET_MAINNET_URL")  # Alchemy
        
        # Argent proxy class hash (standard for most accounts)
        self.argent_proxy_hash = 0x06d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b
        
        if not all([self.wallet_address, self.private_key, self.rpc_url]):
            raise ValueError("Missing required environment variables")
    
    def load_env(self):
        """Load environment variables"""
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key.strip()] = value.strip()
    
    async def activate_account(self):
        """Activate the undeployed account"""
        
        self.console.print("🚀 Account Activation - Self-Funded Proxy Deploy", style="bold blue")
        
        try:
            # Initialize client
            client = FullNodeClient(node_url=self.rpc_url)
            
            # Create key pair
            private_key_int = int(self.private_key, 16)
            key_pair = KeyPair.from_private_key(private_key_int)
            
            # Convert address to int
            address_int = int(self.wallet_address, 16)
            
            self.console.print(f"📍 Target Address: {self.wallet_address}")
            self.console.print(f"🔑 Key Pair: {key_pair.public_key:064x}")
            self.console.print(f"📡 RPC: {self.rpc_url[:50]}...")
            
            # Attempt V3 deployment (ETH fees)
            self.console.print("🔥 Attempting account activation...")
            
            deploy_result = await Account.deploy_account_v3(
                address=address_int,
                class_hash=self.argent_proxy_hash,
                salt=0,  # Standard salt
                key_pair=key_pair,
                client=client,
                constructor_calldata=[key_pair.public_key, 0],
                chain=StarknetChainId.MAINNET,
                max_fee=int(0.01e18),  # 0.01 ETH max fee
            )
            
            self.console.print(f"✅ Activation Broadcast: {hex(deploy_result.hash)}")
            self.console.print("⏳ Waiting for transaction acceptance...")
            
            # Wait for acceptance
            await deploy_result.wait_for_acceptance()
            
            self.console.print("🎉 ACCOUNT IS NOW LIVE!", style="bold green")
            self.console.print(f"🔗 Transaction: {deploy_result.hash}")
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Activation Failed: {e}", style="bold red")
            
            # Provide troubleshooting tips
            if "insufficient balance" in str(e).lower():
                self.console.print("💡 Tip: Ensure account has at least 0.01 ETH for activation fees")
            elif "already deployed" in str(e).lower():
                self.console.print("💡 Tip: Account appears to already be deployed")
            elif "invalid signature" in str(e).lower():
                self.console.print("💡 Tip: Check private key matches the account address")
            
            return False

async def main():
    """Main execution"""
    
    try:
        activator = AccountActivator()
        success = await activator.activate_account()
        
        if success:
            print("\\n✅ Account activation completed successfully!")
            print("💼 The account is now ready for transactions")
        else:
            print("\\n❌ Account activation failed")
            print("🔧 Check the error message above and retry")
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
''')
        print("  📄 Created: tools/activate.py")
    
    def update_gitignore(self):
        """Update .gitignore for new structure"""
        
        print("\n📝 Updating .gitignore...")
        
        gitignore_path = self.project_root / ".gitignore"
        
        # Read existing content
        existing_content = ""
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                existing_content = f.read()
        
        # New additions
        additions = """
# Data and logs
data/
*.log
ghost_sentry_*.log
shadow_state_check.log

# Reports and temporary files
*_report.md
*_command.txt
*.tmp

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# Virtual environment
venv/
.venv/
env/
.env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        
        # Combine and write
        full_content = existing_content + additions
        
        with open(gitignore_path, 'w') as f:
            f.write(full_content)
        
        print("  📄 Updated .gitignore")
    
    def update_readme(self):
        """Update README.md with new structure"""
        
        print("\n📖 Updating README.md...")
        
        readme_path = self.project_root / "README.md"
        
        readme_content = '''# StarkNet Infrastructure - Hardened

A professional StarkNet infrastructure suite with L7 DPI bypass capabilities and automated account management.

## 🏗️ Architecture

```
stark_PyRust_Chain/
├── core/               # Core infrastructure modules
│   ├── providers.py    # RPC resilience and rotation
│   ├── shadow.py       # L7 DPI bypass (ERC-20 calls)
│   └── models.py       # Pydantic data models
├── tools/              # Operational scripts
│   ├── sentry.py       # Ghost monitoring (Shadow Protocol)
│   ├── activate.py     # Account activation
│   └── inventory.py    # Balance auditing
├── docs/               # Documentation
│   ├── ARCHITECTURE.md # System architecture
│   └── SECURITY.md     # Security analysis
└── data/               # Persistent data (gitignored)
    └── reports/        # Generated reports
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
# STARKNET_WALLET_ADDRESS, STARKNET_PRIVATE_KEY, etc.
```

### 2. Virtual Environment

```bash
# Setup Python 3.12 environment
python setup_venv.py

# Activate manually
source venv/bin/activate  # Linux/Mac
# or
venv\\Scripts\\activate   # Windows
```

### 3. Core Operations

#### Monitor Ghost Funds (L7 DPI Bypass)
```bash
python tools/sentry.py
```

#### Activate Undeployed Account
```bash
python tools/activate.py
```

#### Audit Balances
```bash
python tools/inventory.py
```

#### Diagnose RPC Health
```bash
python core/providers.py
```

## 🔐 Security Features

### L7 DPI Bypass
- Uses ERC-20 contract calls instead of account state queries
- Bypasses Deep Packet Inspection filtering
- Works without VPN in restrictive network environments

### RPC Resilience
- Multi-provider rotation with health monitoring
- Automatic failover and recovery
- Provider performance analytics

## 📊 Capabilities

- **Balance Monitoring**: Real-time ETH balance tracking
- **Account Activation**: Self-funded proxy deployment
- **Transaction Recovery**: Ghost fund sweep automation
- **Network Diagnostics**: Comprehensive RPC analysis
- **Shadow Protocol**: Stealth monitoring capabilities

## 🛠️ Development

### Core Modules
- `core/providers.py`: NetworkSentinel class for RPC management
- `core/shadow.py`: ShadowStateChecker for L7 bypass
- `core/models.py`: Pydantic data contracts

### Tools
- `tools/sentry.py`: Production Ghost monitoring
- `tools/activate.py`: Account deployment automation
- `tools/inventory.py`: Multi-chain balance auditing

## 📈 Architecture

This system demonstrates advanced blockchain infrastructure techniques:

1. **L7 DPI Bypass**: Circumvents network-level filtering
2. **RPC Resilience**: Handles provider failures gracefully
3. **Shadow Protocol**: Stealth balance monitoring
4. **Automated Recovery**: Ghost fund detection and sweep

## 📋 Requirements

- Python 3.12+
- starknet-py
- aiohttp
- loguru
- rich
- pydantic

See `requirements.txt` for complete dependency list.

## 🔍 Monitoring

The system includes comprehensive logging and reporting:
- Real-time console output
- Structured log files
- Markdown audit reports
- Telegram notifications (optional)

## 🚨 Security Notes

- Never commit `.env` files
- Use secure RPC endpoints
- Monitor for unauthorized access
- Keep private keys secure

---
*Hardened StarkNet Infrastructure with L7 DPI Bypass*
'''
        
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print("  📄 Updated README.md")
    
    def run_refactor(self):
        """Execute the complete refactoring process"""
        
        print("🔧 Starting Repository Refactoring - Structural Hardening")
        print("=" * 60)
        
        try:
            # Step 1: Create directory structure
            self.create_directory_structure()
            
            # Step 2: Move files
            moved_files, failed_moves = self.move_files_to_new_structure()
            
            # Step 3: Update imports
            updated_files, failed_updates = self.update_imports_in_moved_files()
            
            # Step 4: Create core modules
            self.create_core_modules()
            
            # Step 5: Create activation script
            self.create_activation_script()
            
            # Step 6: Update .gitignore
            self.update_gitignore()
            
            # Step 7: Update README
            self.update_readme()
            
            # Summary
            print("\n" + "=" * 60)
            print("🎉 REFACTORING COMPLETE")
            print("=" * 60)
            print(f"✅ Directories created: {len(self.new_structure)}")
            print(f"✅ Files moved: {len(moved_files)}")
            print(f"✅ Imports updated: {len(updated_files)}")
            print(f"✅ Core modules created")
            print(f"✅ Activation script created")
            print(f"✅ Documentation updated")
            
            if failed_moves:
                print(f"⚠️ Failed moves: {len(failed_moves)}")
            if failed_updates:
                print(f"⚠️ Failed updates: {len(failed_updates)}")
            
            print("\n🚀 Repository is now hardened and production-ready!")
            print("📖 See README.md for updated usage instructions")
            
        except Exception as e:
            print(f"\n❌ Refactoring failed: {e}")
            sys.exit(1)

def main():
    """Main execution"""
    
    refactor = RepoRefactor()
    refactor.run_refactor()

if __name__ == "__main__":
    main()
