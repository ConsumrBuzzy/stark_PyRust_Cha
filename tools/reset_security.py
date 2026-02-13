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

from src.ops.security_reset import reset_security as reset_security_op, verify_security as verify_security_op


def reset_security():
    console = Console()
    console.print("🔐 [SECURITY] MASTER SIGNER PASSWORD RESET", style="bold red")
    console.print("=" * 50, style="dim")
    console.print("This will wipe existing encrypted files and re-encrypt", style="yellow")
    console.print("your private key with a password you choose.", style="yellow")
    console.print()

    confirm = console.input("⚠️  Are you sure you want to continue? [y/N]: ")
    if confirm.lower() != 'y':
        console.print("❌ Security reset cancelled", style="bold red")
        return

    console.print()
    console.print("🔑 Set your Master Signer Password", style="bold blue")
    console.print("This password will encrypt your private key", style="dim")
    console.print("and will be required for all operations.", style="dim")
    console.print()

    try:
        password = getpass.getpass("Set your NEW Master Signer Password: ")
        if not password or len(password) < 8:
            console.print("❌ Password must be at least 8 characters", style="bold red")
            return
        confirm_pw = getpass.getpass("Confirm Password: ")
        if password != confirm_pw:
            console.print("❌ Passwords do not match. Aborting.", style="bold red")
            return
    except KeyboardInterrupt:
        console.print("\n❌ Security reset cancelled", style="bold red")
        return

    try:
        ok = reset_security_op(password)
        if ok:
            console.print("🎯 SECURITY RESET COMPLETE", style="bold green")
            console.print("✅ Private key encrypted and verified", style="green")
            console.print("⚠️  Keep SIGNER_PASSWORD secure", style="yellow")
        else:
            console.print("❌ Security reset failed", style="bold red")
    except Exception as e:
        console.print(f"❌ Security reset error: {e}", style="bold red")


def verify_security():
    console = Console()
    console.print("🔍 Security Verification", style="bold blue")
    console.print("=" * 30, style="dim")

    try:
        info = verify_security_op()
        security_info = info.get("security_info", {})
        console.print("📊 Current Security Status:")
        for key, value in security_info.items():
            status = "✅" if value else "❌"
            console.print(f"  {status} {key.replace('_', ' ').title()}: {value}")
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
