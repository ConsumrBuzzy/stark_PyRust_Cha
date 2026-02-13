#!/usr/bin/env python3
"""
StarkNet Environment Setup - Python 3.12 Venv + starknet-py
Uses DuggerGitTools venv_manager for reliable environment creation
"""

import sys
import os
from pathlib import Path

# Add DuggerGitTools to path
sys.path.append(str(Path("C:/Github/DuggerGitTools").resolve()))

from dgt.core.venv_manager import VenvManager
from loguru import logger

def main():
    """Setup Python 3.12 venv and install starknet-py"""
    
    project_root = Path.cwd()
    logger.info(f"Setting up environment for: {project_root}")
    
    # Initialize venv manager
    venv_manager = VenvManager(project_root)
    
    # Check current Python version
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    logger.info(f"Current Python: {current_version}")
    
    # Try to get or create Python 3.12 venv
    try:
        venv_info = venv_manager.get_or_create_venv(
            min_version=(3, 12),
            auto_create=True
        )
        
        if venv_info:
            logger.success(f"✅ Venv ready: {venv_info.path}")
            logger.info(f"Python version: {venv_info.version}")
            logger.info(f"Executable: {venv_info.python_executable}")
        else:
            logger.error("❌ Failed to setup venv")
            return False
            
    except Exception as e:
        logger.error(f"❌ Venv setup failed: {e}")
        logger.info("💡 Try installing Python 3.12 from python.org")
        return False
    
    # Install starknet-py in the venv
    logger.info("📦 Installing starknet-py in venv...")
    
    try:
        import subprocess
        
        # Install starknet-py with venv pip
        result = subprocess.run(
            [str(venv_info.python_executable), "-m", "pip", "install", "starknet-py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            logger.success("✅ starknet-py installed successfully")
        else:
            logger.error(f"❌ starknet-py installation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ starknet-py installation timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Installation error: {e}")
        return False
    
    # Install project requirements
    logger.info("📦 Installing project requirements...")
    try:
        venv_manager.install_dependencies(venv_info)
        logger.success("✅ Dependencies installed")
    except Exception as e:
        logger.warning(f"⚠️ Dependencies install failed: {e}")
    
    # Test starknet-py import
    logger.info("🧪 Testing starknet-py import...")
    try:
        result = subprocess.run(
            [str(venv_info.python_executable), "-c", "import starknet_py; print('starknet-py import successful')"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logger.success("✅ starknet-py import test passed")
            print(result.stdout.strip())
        else:
            logger.error(f"❌ Import test failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Import test error: {e}")
        return False
    
    # Show usage instructions
    venv_python = venv_info.python_executable
    print("\n" + "="*60)
    print("🚀 ENVIRONMENT SETUP COMPLETE")
    print("="*60)
    print(f"Venv Location: {venv_info.path}")
    print(f"Python: {venv_info.version}")
    print(f"Executable: {venv_python}")
    print("\n📋 USAGE:")
    print(f"1. Activate venv: {venv_info.path}\\Scripts\\activate")
    print(f"2. Or use directly: {venv_python} your_script.py")
    print(f"3. Test Ghost scripts: {venv_python} rescue_funds.py --find")
    print("="*60)
    
    return True

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    success = main()
    sys.exit(0 if success else 1)
