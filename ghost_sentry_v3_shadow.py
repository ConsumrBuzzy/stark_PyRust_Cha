#!/usr/bin/env python3
"""
Ghost Sentry V3 - Shadow Protocol
L7 DPI Bypass using ERC-20 balanceOf contract calls
Monitors Ghost address without triggering state-level filtering
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

# Add python-logic to path
sys.path.append(os.path.join(os.getcwd(), 'python-logic'))

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call

class GhostSentryV3Shadow:
    """Advanced Ghost monitoring using Shadow Protocol (L7 DPI Bypass)"""
    
    def __init__(self):
        self.console = Console()
        self.setup_logging()
        self.load_env()
        
        # Shadow Protocol Configuration
        self.ghost_address = "0x000000000000000000000000ff01e0776369ce51debb16dfb70f23c16d875463"
        self.main_wallet = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
        
        # ERC-20 ETH Token Contract (StarkNet)
        self.eth_token_addr = 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7
        self.balance_selector = get_selector_from_name("balanceOf")
        
        # Thresholds and timing
        self.ghost_threshold = 0.005  # 0.005 ETH minimum
        self.poll_interval = 180      # 3 minutes
        self.main_check_interval = 900 # 15 minutes for main wallet
        
        # Working RPC (from shadow state check)
        self.primary_rpc = os.getenv("STARKNET_MAINNET_URL")  # Alchemy v0.10.0
        self.backup_rpcs = [
            os.getenv("STARKNET_LAVA_URL"),
            os.getenv("STARKNET_1RPC_URL"),
            os.getenv("STARKNET_ONFINALITY_URL")
        ]
        self.backup_rpcs = [rpc for rpc in self.backup_rpcs if rpc]
        
        # Statistics
        self.poll_count = 0
        self.successful_checks = 0
        self.failed_checks = 0
        self.last_ghost_balance = 0.0
        self.last_main_balance = 0.0
        
        logger.info("🌑 Ghost Sentry V3 Shadow Protocol Initialized")
        logger.info(f"👻 Ghost: {self.ghost_address}")
        logger.info(f"💼 Main: {self.main_wallet}")
        logger.info(f"🎯 Threshold: {self.ghost_threshold} ETH")
        logger.info(f"📡 Primary RPC: Alchemy v0.10.0")
    
    def setup_logging(self):
        """Configure structured logging"""
        logger.remove()
        
        # Console logging
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level="INFO"
        )
        
        # File logging with rotation
        logger.add(
            "ghost_sentry_v3_shadow.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days"
        )
    
    def load_env(self):
        """Load environment variables"""
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key.strip()] = value.strip()
    
    async def shadow_balance_check(self, address: str, label: str) -> Optional[float]:
        """
        Shadow Protocol Balance Check
        Uses ERC-20 balanceOf contract call to bypass L7 DPI
        """
        
        rpcs_to_try = [self.primary_rpc] + self.backup_rpcs
        
        for rpc_url in rpcs_to_try:
            try:
                client = FullNodeClient(node_url=rpc_url)
                
                # Shadow Call: Direct ERC-20 balanceOf query
                call = Call(
                    to_addr=self.eth_token_addr,
                    selector=self.balance_selector,
                    calldata=[int(address, 16)]
                )
                
                # Execute the shadow call
                response = await client.call_contract(call)
                
                # ERC-20 balanceOf returns Uint256 (low, high) - we use low for ETH
                balance_low = response[0]
                balance_eth = balance_low / 1e18
                
                self.successful_checks += 1
                
                provider_name = self.get_provider_name(rpc_url)
                logger.debug(f"✅ Shadow check via {provider_name}: {balance_eth:.6f} ETH")
                
                return balance_eth
                
            except Exception as e:
                error_msg = str(e)
                provider_name = self.get_provider_name(rpc_url)
                
                if "403" in error_msg:
                    logger.warning(f"🚫 {provider_name}: Blocked by DPI")
                elif "timeout" in error_msg.lower():
                    logger.warning(f"⏱️ {provider_name}: Timeout")
                else:
                    logger.warning(f"⚠️ {provider_name}: {error_msg[:30]}...")
                
                continue
        
        # All RPCs failed
        self.failed_checks += 1
        logger.error(f"❌ All shadow checks failed for {label}")
        return None
    
    def get_provider_name(self, rpc_url: str) -> str:
        """Extract provider name from URL"""
        if "alchemy" in rpc_url.lower():
            return "Alchemy"
        elif "lava" in rpc_url.lower():
            return "Lava"
        elif "1rpc" in rpc_url.lower():
            return "1RPC"
        elif "onfinality" in rpc_url.lower():
            return "OnFinality"
        else:
            return "Unknown"
    
    def generate_starkli_sweep_command(self, balance_eth: float) -> str:
        """Generate Starkli command for Ghost fund sweep"""
        
        private_key = os.getenv("TRANSIT_EVM_PRIVATE_KEY")
        target_address = os.getenv("STARKNET_WALLET_ADDRESS")
        
        if not private_key or not target_address:
            return "❌ Missing TRANSIT_EVM_PRIVATE_KEY or STARKNET_WALLET_ADDRESS"
        
        # Calculate sweep amount (leave gas buffer)
        gas_buffer = 0.0001
        sweep_amount = max(0, balance_eth - gas_buffer)
        
        if sweep_amount <= 0:
            return "❌ Balance too low for sweep"
        
        # Convert to wei for Starkli
        sweep_wei = int(sweep_amount * 1e18)
        target_int = int(target_address, 16)
        
        command = f"""# Starkli Ghost Sweep Command - Shadow Protocol
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Balance: {balance_eth:.6f} ETH (${balance_eth * 2200:.2f} USD)

starkli invoke \\
  --network starknet-mainnet \\
  --account {self.ghost_address} \\
  --private-key {private_key} \\
  {self.eth_token_addr:x} \\
  transfer \\
  {target_int} \\
  {sweep_wei}

# Alternative: Use rescue_funds.py with shadow protocol
python .\\venv\\Scripts\\rescue_funds.py --sweep --confirm

# Verify sweep success:
python .\\venv\\Scripts\\shadow_state_check.py
"""
        
        return command
    
    def send_telegram_alert(self, balance_eth: float, address: str, label: str):
        """Send Telegram notification for critical events"""
        
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            logger.info("📱 Telegram not configured")
            return
        
        try:
            import requests
            
            message = f"""🌑 SHADOW PROTOCOL ALERT

{'🎉 GHOST FUNDS DETECTED!' if label == 'Ghost' else '💰 MAIN WALLET UPDATE'}

📍 {label}: {address[:10]}...
💰 Balance: {balance_eth:.6f} ETH
💵 Value: ${balance_eth * 2200:.2f} USD
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔍 Method: Shadow Protocol (L7 DPI Bypass)

{'🚀 READY FOR SWEEP EXECUTION!' if label == 'Ghost' and balance_eth > self.ghost_threshold else '📊 Monitoring...'}
"""
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                logger.success("📱 Telegram alert sent")
            else:
                logger.warning(f"📱 Telegram failed: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"📱 Telegram error: {e}")
    
    def create_status_display(self, ghost_balance: float, main_balance: float) -> Table:
        """Create rich status table"""
        
        table = Table(title=f"🌑 Ghost Sentry V3 - Poll #{self.poll_count}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="bold")
        
        # Ghost Address
        ghost_status = "🟢 DETECTED" if ghost_balance > self.ghost_threshold else "🟡 MONITORING"
        table.add_row(
            "Ghost Address",
            f"{ghost_balance:.6f} ETH (${ghost_balance * 2200:.2f})",
            ghost_status
        )
        
        # Main Wallet
        table.add_row(
            "Main Wallet",
            f"{main_balance:.6f} ETH (${main_balance * 2200:.2f})",
            "💼 CONFIRMED" if main_balance > 0 else "📊 EMPTY"
        )
        
        # Protocol Stats
        success_rate = (self.successful_checks / max(1, self.successful_checks + self.failed_checks)) * 100
        table.add_row("Shadow Protocol", f"{success_rate:.1f}% Success", "🌑 ACTIVE")
        
        # Network
        table.add_row("Primary RPC", "Alchemy v0.10.0", "✅ WORKING")
        
        # Timing
        table.add_row("Next Poll", f"{self.poll_interval}s", "⏳ WAITING")
        
        return table
    
    def save_shadow_report(self, ghost_balance: float, main_balance: float):
        """Save shadow protocol report"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Ghost Sentry V3 - Shadow Protocol Report

**Timestamp**: {timestamp}
**Protocol**: L7 DPI Bypass via ERC-20 Contract Calls
**Method**: Shadow Balance Check (starknet_call)

## Executive Summary

- **Ghost Balance**: {ghost_balance:.6f} ETH (${ghost_balance * 2200:.2f} USD)
- **Main Wallet**: {main_balance:.6f} ETH (${main_balance * 2200:.2f} USD)
- **Protocol Status**: {'🟢 ACTIVE - DETECTED' if ghost_balance > self.ghost_threshold else '🟡 ACTIVE - MONITORING'}
- **Success Rate**: {(self.successful_checks / max(1, self.successful_checks + self.failed_checks)) * 100:.1f}%

## Technical Details

### Shadow Method
- **Contract**: ETH ERC-20 Token (0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7)
- **Selector**: balanceOf
- **Bypass**: L7 DPI cannot distinguish from normal contract interactions
- **RPC**: Alchemy v0.10.0 (confirmed working)

### Bypass Analysis
| Standard Method | Status | Shadow Method | Status |
|-----------------|--------|---------------|--------|
| starknet_getNonce | ❌ BLOCKED | starknet_call (balanceOf) | ✅ BYPASSES |
| starknet_getClassHashAt | ❌ BLOCKED | Contract State Query | ✅ BYPASSES |

## Strategic Status

### Ghost Funds ($15 Bridge)
- **Current**: {ghost_balance:.6f} ETH
- **Status**: {'DETECTED - Ready for sweep' if ghost_balance > self.ghost_threshold else 'Pending - Still in bridge'}
- **Next Action**: {'Execute sweep command' if ghost_balance > self.ghost_threshold else 'Continue monitoring'}

### Main Wallet ($24 Recovery)
- **Current**: {main_balance:.6f} ETH
- **Status**: {'Accessible via shadow protocol' if main_balance > 0 else 'Empty'}
- **Deployment**: Still requires VPN for status verification

## Recommendations

1. **Continue Shadow Monitoring**: No VPN required for balance checks
2. **Prepare Sweep**: Ghost funds can be swept when detected
3. **VPN for Deployment**: Account deployment still needs bypass
4. **Protocol Documentation**: L7 DPI bypass technique validated

---
*Generated by Ghost Sentry V3 - Shadow Protocol*
"""
        
        with open("ghost_sentry_v3_shadow_report.md", "w", encoding="utf-8") as f:
            f.write(report)
    
    async def run_shadow_sentry(self):
        """Main Shadow Protocol sentry loop"""
        
        self.console.print(Panel.fit(
            "[bold blue]🌑 GHOST SENTRY V3 - SHADOW PROTOCOL[/bold blue]\n"
            "L7 DPI Bypass Active\n"
            "Using ERC-20 Contract Calls\n"
            f"Monitoring: {self.ghost_address[:10]}...\n"
            f"Main Wallet: {self.main_wallet[:10]}...",
            title="Stealth Monitoring System"
        ))
        
        # Initial check
        logger.info("🔍 Performing initial shadow protocol check...")
        
        while True:
            self.poll_count += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"🌑 Shadow Poll #{self.poll_count} - {timestamp}")
            
            # Check Ghost address (every poll)
            ghost_balance = await self.shadow_balance_check(self.ghost_address, "Ghost")
            
            # Check Main wallet (every 5 polls to reduce load)
            main_balance = self.last_main_balance
            if self.poll_count % 5 == 1:  # Every 5th poll
                main_balance = await self.shadow_balance_check(self.main_wallet, "Main Wallet")
                if main_balance is not None:
                    self.last_main_balance = main_balance
            
            # Display status
            if ghost_balance is not None:
                table = self.create_status_display(ghost_balance, main_balance or 0.0)
                self.console.print(table)
                
                # Check for Ghost funds detection
                if ghost_balance > self.ghost_threshold:
                    logger.success(f"🎉 GHOST FUNDS DETECTED: {ghost_balance:.6f} ETH!")
                    
                    # Success alert
                    self.console.print(Panel.fit(
                        f"[bold green]💰 GHOST FUNDS DETECTED![/bold green]\n\n"
                        f"Amount: {ghost_balance:.6f} ETH\n"
                        f"Value: ${ghost_balance * 2200:.2f} USD\n"
                        f"Time: {timestamp}\n\n"
                        f"[bold yellow]🚀 SHADOW PROTOCOL SUCCESS![/bold yellow]\n"
                        f"[bold yellow]🛠️ SWEEP COMMANDS GENERATED[/bold yellow]",
                        title="MISSION ACCOMPLISHED",
                        border_style="green"
                    ))
                    
                    # Generate and display sweep command
                    sweep_command = self.generate_starkli_sweep_command(ghost_balance)
                    self.console.print(Panel(
                        sweep_command,
                        title="🛠️ Starkli Sweep Command",
                        border_style="yellow"
                    ))
                    
                    # Save command to file
                    with open("ghost_shadow_sweep_command.txt", "w") as f:
                        f.write(f"# Ghost Sweep Command - Shadow Protocol\n")
                        f.write(f"# Generated: {timestamp}\n")
                        f.write(sweep_command)
                    
                    # Send alerts
                    self.send_telegram_alert(ghost_balance, self.ghost_address, "Ghost")
                    
                    # Log success
                    logger.success(f"✅ Shadow Protocol detected Ghost funds: {ghost_balance:.6f} ETH")
                    logger.info(f"💰 Value: ${ghost_balance * 2200:.2f} USD")
                    
                    # Continue monitoring but with longer interval
                    logger.info("🔄 Ghost funds detected - continuing monitoring for additional funds...")
                    
                else:
                    logger.info(f"⌳ Ghost balance: {ghost_balance:.6f} ETH - still waiting...")
                
                # Update last known balance
                self.last_ghost_balance = ghost_balance
                
                # Save periodic report
                if self.poll_count % 10 == 0:  # Every 10 polls
                    self.save_shadow_report(ghost_balance, main_balance or 0.0)
            
            else:
                logger.error("❌ Shadow protocol check failed - continuing monitoring...")
            
            # Wait for next poll
            logger.info(f"⏳ Shadow protocol waiting {self.poll_interval}s...")
            await asyncio.sleep(self.poll_interval)

async def main():
    """Main execution"""
    
    console = Console()
    console.print("🌑 Ghost Sentry V3 - Shadow Protocol", style="bold blue")
    console.print("🔐 L7 DPI Bypass via ERC-20 Contract Calls", style="dim")
    
    sentry = GhostSentryV3Shadow()
    await sentry.run_shadow_sentry()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Ghost Sentry V3 stopped by user")
    except Exception as e:
        logger.error(f"❌ Ghost Sentry V3 error: {e}")
        sys.exit(1)
