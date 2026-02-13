#!/usr/bin/env python3
"""
PyPro Systems - Main CLI Entry Point
Unified command interface for all operations
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.engines.recovery_kernel import RecoveryKernel

async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="PyPro Systems - StarkNet Protocol Engine")
    parser.add_argument("--recover", action="store_true", help="Execute account recovery mission")
    parser.add_argument("--phantom-address", type=str, help="Phantom wallet address")
    parser.add_argument("--starknet-address", type=str, help="StarkNet wallet address")
    parser.add_argument("--status", action="store_true", help="Check recovery status")
    parser.add_argument("--resume", action="store_true", help="Resume previous recovery mission")
    
    args = parser.parse_args()
    
    if args.recover:
        await execute_recovery(args)
    elif args.status:
        await check_status()
    elif args.resume:
        await resume_recovery()
    else:
        parser.print_help()

async def execute_recovery(args):
    """Execute recovery mission"""
    print("🚀 PyPro Systems - Recovery Mission")
    print("=" * 50)
    
    # Get addresses
    phantom_address = args.phantom_address or "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
    starknet_address = args.starknet_address or "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
    
    print(f"📍 Phantom: {phantom_address}")
    print(f"📍 StarkNet: {starknet_address}")
    
    # Initialize kernel
    kernel = RecoveryKernel(phantom_address, starknet_address)
    
    if not await kernel.initialize():
        print("❌ Failed to initialize Recovery Kernel")
        return
    
    # Get master password
    import getpass
    print("\n🔐 Security Vault - Master Password Required")
    password = getpass.getpass("Enter Master Password: ")
    
    if not await kernel.unlock_security(password):
        print("❌ Invalid password - aborting mission")
        return
    
    # Execute recovery
    success = await kernel.execute_recovery()
    
    # Shutdown
    await kernel.shutdown()
    
    if success:
        print("\n🎉 RECOVERY MISSION SUCCESSFUL!")
    else:
        print("\n❌ RECOVERY MISSION FAILED!")

async def check_status():
    """Check recovery status"""
    print("📊 Recovery Status Check")
    print("=" * 30)
    
    # Load state registry directly
    from src.foundation.state import StateRegistry
    
    try:
        state_registry = StateRegistry()
        recovery_state = await state_registry.load_state()
        
        if recovery_state:
            state_registry.print_status()
        else:
            print("📂 No previous recovery session found")
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")

async def resume_recovery():
    """Resume previous recovery mission"""
    print("🔄 Resuming Recovery Mission")
    print("=" * 30)
    
    # Load previous state
    from src.foundation.state import StateRegistry
    
    try:
        state_registry = StateRegistry()
        recovery_state = await state_registry.load_state()
        
        if not recovery_state:
            print("❌ No previous recovery session found")
            return
        
        print(f"📂 Resuming from: {recovery_state.current_phase}")
        
        # Initialize kernel with previous state
        kernel = RecoveryKernel(recovery_state.phantom_address, recovery_state.starknet_address)
        kernel.recovery_state = recovery_state
        kernel.state_registry = state_registry
        
        if not await kernel.initialize():
            print("❌ Failed to initialize Recovery Kernel")
            return
        
        # Check if security is already unlocked
        if not recovery_state.security_unlocked:
            import getpass
            print("\n🔐 Security Vault - Master Password Required")
            password = getpass.getpass("Enter Master Password: ")
            
            if not await kernel.unlock_security(password):
                print("❌ Invalid password - aborting mission")
                return
        
        # Resume execution
        success = await kernel.execute_recovery()
        
        # Shutdown
        await kernel.shutdown()
        
        if success:
            print("\n🎉 RECOVERY MISSION SUCCESSFUL!")
        else:
            print("\n❌ RECOVERY MISSION FAILED!")
            
    except Exception as e:
        print(f"❌ Resume failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
