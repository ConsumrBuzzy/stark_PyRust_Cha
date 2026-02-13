#!/usr/bin/env python3
"""
Secret Scrubbing Script - Remove hardcoded secrets from codebase
Replaces hardcoded addresses and secrets with environment variable references
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Known secrets to scrub
SECRETS_PATTERNS = {
    # StarkNet addresses
    r'os.getenv("STARKNET_WALLET_ADDRESS")': 'os.getenv("STARKNET_WALLET_ADDRESS")',
    r'os.getenv("STARKNET_GHOST_ADDRESS")': 'os.getenv("STARKNET_GHOST_ADDRESS")',
    
    # Contract addresses
    r'int(os.getenv("STARKNET_ETH_CONTRACT", "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"), 16)': 'int(os.getenv("STARKNET_ETH_CONTRACT", "int(os.getenv("STARKNET_ETH_CONTRACT", "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"), 16)"), 16)',
    r'int(os.getenv("STARKNET_ARGENT_PROXY_HASH", "0x06d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b"), 16)': 'int(os.getenv("STARKNET_ARGENT_PROXY_HASH", "int(os.getenv("STARKNET_ARGENT_PROXY_HASH", "0x06d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b"), 16)"), 16)',
    
    # RPC URLs (partial patterns)
    r'https://starknet-mainnet\.g\.alchemy\.com/v2/[A-Za-z0-9]+': 'os.getenv("STARKNET_MAINNET_URL")',
    r'https://rpc\.starknet\.lava\.build': 'os.getenv("STARKNET_LAVA_URL")',
    r'https://1rpc\.io/starknet': 'os.getenv("STARKNET_1RPC_URL")',
    r'https://starknet\.api\.onfinality\.io/public': 'os.getenv("STARKNET_ONFINALITY_URL")',
}

# Files to skip (binary, generated, etc.)
SKIP_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.exe', '.dll', '.so', '.dylib'}
SKIP_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}

def should_skip_file(file_path: Path) -> bool:
    """Check if file should be skipped"""
    
    # Skip directories
    if any(skip_dir in file_path.parts for skip_dir in SKIP_DIRS):
        return True
    
    # Skip by extension
    if file_path.suffix.lower() in SKIP_EXTENSIONS:
        return True
    
    # Skip if file is binary (heuristic)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)  # Try to read first 1KB
        return False
    except UnicodeDecodeError:
        return True

def scrub_file(file_path: Path) -> Tuple[bool, int]:
    """Scrub secrets from a single file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacements = 0
        
        # Apply each pattern
        for pattern, replacement in SECRETS_PATTERNS.items():
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                replacements += len(matches)
                print(f"  🔄 Replaced {len(matches)} instances in {file_path.name}")
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, replacements
        
        return False, 0
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False, 0

def check_env_file() -> bool:
    """Check if .env file exists and has required variables"""
    
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    required_vars = [
        'STARKNET_WALLET_ADDRESS',
        'STARKNET_GHOST_ADDRESS',
        'STARKNET_MAINNET_URL'
    ]
    
    with open(env_path, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if var not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ .env file has required variables")
    return True

def create_gitignore_update():
    """Create .gitignore update for secrets"""
    
    gitignore_path = Path('.gitignore')
    
    # Secrets to add to gitignore
    secret_patterns = [
        '# Environment files with secrets',
        '.env',
        '.env.local',
        '.env.production',
        '',
        '# Secret backup files',
        '*.env.bak',
        '*.secrets',
        '',
        '# Private key files',
        '*.key',
        '*.pem',
        'private_keys/',
    ]
    
    existing_content = ""
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    # Add missing patterns
    new_patterns = []
    for pattern in secret_patterns:
        if pattern and pattern not in existing_content:
            new_patterns.append(pattern)
    
    if new_patterns:
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write('\n' + '\n'.join(new_patterns))
        print(f"✅ Added {len(new_patterns)} patterns to .gitignore")
    else:
        print("✅ .gitignore already up to date")

def main():
    """Main scrubbing process"""
    
    print("🧹 Secret Scrubbing Utility")
    print("=" * 50)
    
    # Check .env file
    if not check_env_file():
        print("\n❌ Please create .env file with required variables before scrubbing")
        sys.exit(1)
    
    # Update .gitignore
    create_gitignore_update()
    
    print("\n🔍 Scanning for hardcoded secrets...")
    
    # Find all Python files
    repo_root = Path('.')
    python_files = list(repo_root.rglob('*.py'))
    
    # Filter files to skip
    files_to_process = []
    for file_path in python_files:
        if not should_skip_file(file_path):
            files_to_process.append(file_path)
    
    print(f"📁 Found {len(files_to_process)} Python files to check")
    
    # Process files
    total_replacements = 0
    modified_files = 0
    
    for file_path in files_to_process:
        print(f"\n🔍 Checking: {file_path}")
        modified, replacements = scrub_file(file_path)
        if modified:
            modified_files += 1
            total_replacements += replacements
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SCRUBBING SUMMARY")
    print("=" * 50)
    print(f"Files processed: {len(files_to_process)}")
    print(f"Files modified: {modified_files}")
    print(f"Total replacements: {total_replacements}")
    
    if total_replacements > 0:
        print(f"\n✅ Successfully scrubbed {total_replacements} hardcoded secrets")
        print("🔐 Repository is now more secure")
        print("\n⚠️  IMPORTANT:")
        print("   - Review the changes with 'git diff'")
        print("   - Ensure .env file contains all required values")
        print("   - Test that scripts still work after scrubbing")
    else:
        print("\n✅ No hardcoded secrets found")
    
    print("\n🎯 Next steps:")
    print("   1. Review changes: git diff")
    print("   2. Commit changes: git add . && git commit -m '🧹 Scrub hardcoded secrets'")
    print("   3. Test functionality: python tools/combined_audit.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Scrubbing cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
