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
    parser.add_argument("--full-auto", action="store_true", help="Execute Full-Auto recovery mission (requires SIGNER_PASSWORD env var)")
    parser.add_argument("--phantom-address", type=str, help="Phantom wallet address")
    parser.add_argument("--starknet-address", type=str, help="StarkNet wallet address")
    parser.add_argument("--status", action="store_true", help="Check recovery status")
    parser.add_argument("--resume", action="store_true", help="Resume previous recovery mission")
    
    # Legacy functionality modes
    parser.add_argument("--stargate-watch", action="store_true", help="Start StarkGate watch mode")
    parser.add_argument("--ghost-sentry", action="store_true", help="Start Ghost Sentry mode")
    parser.add_argument("--bridge-recovery", type=str, help="Start Bridge Recovery mode with TX hash")
    parser.add_argument("--advanced-tracking", type=str, help="Start Advanced Tracking mode with TX hash")
    parser.add_argument("--ghost-address", type=str, help="Ghost address for Ghost Sentry mode")
    parser.add_argument("--main-wallet", type=str, help="Main wallet address for Ghost Sentry mode")
    parser.add_argument("--list-modes", action="store_true", help="List available monitoring modes")
    
    args = parser.parse_args()
    
    if args.recover:
        await execute_recovery(args)
    elif args.full_auto:
        await execute_full_auto(args)
    elif args.status:
        await check_status()
    elif args.resume:
        await resume_recovery()
    elif args.stargate_watch:
        await execute_stargate_watch(args)
    elif args.ghost_sentry:
        await execute_ghost_sentry(args)
    elif args.bridge_recovery:
        await execute_bridge_recovery(args)
    elif args.advanced_tracking:
        await execute_advanced_tracking(args)
    elif args.list_modes:
        await list_available_modes()
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

async def execute_full_auto(args):
    """Execute Full-Auto recovery mission"""
    print("🚀 PyPro Systems - Full-Auto Recovery Mission")
    print("=" * 60)
    print("⚠️  WARNING: This will execute autonomously without human confirmation")
    print("🔒 Requires SIGNER_PASSWORD environment variable")
    print("=" * 60)
    
    # Get addresses
    phantom_address = args.phantom_address or "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
    starknet_address = args.starknet_address or "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
    
    # Check if SIGNER_PASSWORD is set
    if not os.getenv("SIGNER_PASSWORD"):
        print("❌ SIGNER_PASSWORD environment variable not found")
        print("   Full-Auto mode requires: export SIGNER_PASSWORD='your_password'")
        return
    
    # Initialize kernel
    kernel = RecoveryKernel(phantom_address, starknet_address)
    
    try:
        success = await kernel.execute_full_auto()
        
        if success:
            print("\n🎉 FULL-AUTO RECOVERY MISSION SUCCESSFUL!")
            print("🏭 Iron → Steel refining loop initiated autonomously")
        else:
            print("\n❌ FULL-AUTO RECOVERY MISSION FAILED!")
            
    except Exception as e:
        print(f"\n❌ Full-Auto mission error: {e}")
    finally:
        await kernel.shutdown()

async def execute_stargate_watch(args):
    """Execute StarkGate watch mode"""
    print("🔍 PyPro Systems - StarkGate Watch Mode")
    print("=" * 50)
    
    starknet_address = args.starknet_address or "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
    
    # Initialize kernel
    kernel = RecoveryKernel("0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9", starknet_address)
    
    if await kernel.initialize():
        try:
            result = await kernel.start_stargate_watch()
            if result.get("success"):
                print("🎉 StarkGate watch completed successfully!")
            else:
                print(f"❌ StarkGate watch failed: {result.get('error')}")
        finally:
            await kernel.shutdown()
    else:
        print("❌ Failed to initialize kernel")

async def execute_ghost_sentry(args):
    """Execute Ghost Sentry mode"""
    print("👻 PyPro Systems - Ghost Sentry Mode")
    print("=" * 50)
    
    ghost_address = args.ghost_address or os.getenv("STARKNET_GHOST_ADDRESS")
    main_wallet = args.main_wallet or os.getenv("STARKNET_WALLET_ADDRESS")
    
    if not ghost_address or not main_wallet:
        print("❌ Ghost address and main wallet required")
        return
    
    # Initialize kernel
    kernel = RecoveryKernel("0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9", main_wallet)
    
    if await kernel.initialize():
        try:
            result = await kernel.start_ghost_sentry(ghost_address, main_wallet)
            if result.get("success"):
                print("🎉 Ghost Sentry completed successfully!")
            else:
                print(f"❌ Ghost Sentry failed: {result.get('error')}")
        finally:
            await kernel.shutdown()
    else:
        print("❌ Failed to initialize kernel")

async def execute_bridge_recovery(args):
    """Execute Bridge Recovery mode"""
    print("🔄 PyPro Systems - Bridge Recovery Mode")
    print("=" * 50)
    
    bridge_tx_hash = args.bridge_recovery
    starknet_address = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
    
    # Initialize kernel
    kernel = RecoveryKernel("0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9", starknet_address)
    
    if await kernel.initialize():
        try:
            result = await kernel.start_bridge_recovery(bridge_tx_hash)
            if result.get("success"):
                print("🎉 Bridge Recovery completed successfully!")
            else:
                print(f"❌ Bridge Recovery failed: {result.get('error')}")
        finally:
            await kernel.shutdown()
    else:
        print("❌ Failed to initialize kernel")

async def execute_advanced_tracking(args):
    """Execute Advanced Tracking mode"""
    print("🔍 PyPro Systems - Advanced Tracking Mode")
    print("=" * 50)
    
    tx_hash = args.advanced_tracking
    starknet_address = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
    
    # Initialize kernel
    kernel = RecoveryKernel("0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9", starknet_address)
    
    if await kernel.initialize():
        try:
            result = await kernel.start_advanced_tracking(tx_hash)
            if result.get("success"):
                print("🎉 Advanced Tracking completed successfully!")
            else:
                print(f"❌ Advanced Tracking failed: {result.get('error')}")
        finally:
            await kernel.shutdown()
    else:
        print("❌ Failed to initialize kernel")

async def list_available_modes():
    """List available monitoring modes"""
    print("📋 Available Monitoring Modes")
    print("=" * 30)
    
    # Initialize kernel to get modes
    kernel = RecoveryKernel("0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9", "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9")
    
    if await kernel.initialize():
        modes = kernel.get_available_modes()
        print("Available modes:")
        for mode in modes:
            print(f"  - {mode}")
        
        print("\nUsage examples:")
        print("  python main.py --stargate-watch")
        print("  python main.py --ghost-sentry --ghost-address <addr> --main-wallet <addr>")
        print("  python main.py --bridge-recovery <tx_hash>")
        print("  python main.py --advanced-tracking <tx_hash>")
        
        await kernel.shutdown()
    else:
        print("❌ Failed to initialize kernel")

if __name__ == "__main__":
    asyncio.run(main())
