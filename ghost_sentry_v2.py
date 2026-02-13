#!/usr/bin/env python3
"""
Ghost Sentry V2 - Network Blackout Protocol
Monitors Ghost address using Alchemy RPC under firewall conditions
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add python-logic to path for existing modules
sys.path.append(os.path.join(os.getcwd(), 'python-logic'))

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call

class GhostSentryV2:
    """Advanced Ghost monitoring under network blackout conditions"""
    
    def __init__(self):
        self.console = Console()
        self.setup_logging()
        self.ghost_address = "0x000000000000000000000000ff01e0776369ce51debb16dfb70f23c16d875463"
        self.threshold_eth = 0.005
        self.poll_interval = 180  # 3 minutes
        
        # Load environment
        self.load_env()
        
        # RPC configuration - prioritize working endpoints
        self.rpc_urls = [
            os.getenv("STARKNET_MAINNET_URL"),  # Alchemy (confirmed working)
            os.getenv("STARKNET_LAVA_URL"),     # Lava (backup)
            os.getenv("STARKNET_1RPC_URL"),     # 1RPC (backup)
            os.getenv("STARKNET_ONFINALITY_URL") # OnFinality (backup)
        ]
        self.rpc_urls = [url for url in self.rpc_urls if url]
        
        if not self.rpc_urls:
            logger.error("❌ No RPC URLs found in environment")
            sys.exit(1)
        
        logger.info(f"🔧 Sentry initialized with {len(self.rpc_urls)} RPC endpoints")
        logger.info(f"👻 Monitoring Ghost: {self.ghost_address}")
        logger.info(f"💰 Threshold: {self.threshold_eth} ETH")
    
    def setup_logging(self):
        """Configure structured logging"""
        logger.remove()
        
        # Console logging
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level="INFO"
        )
        
        # File logging
        logger.add(
            "ghost_sentry_v2.log",
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
    
    async def check_balance_rpc(self, rpc_url: str) -> Optional[float]:
        """Check Ghost balance via specific RPC endpoint"""
        
        try:
            client = FullNodeClient(node_url=rpc_url)
            
            # ETH token contract
            eth_contract = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
            
            # Build balanceOf call
            call = Call(
                to_addr=int(eth_contract, 16),
                selector=get_selector_from_name("balanceOf"),
                calldata=[int(self.ghost_address, 16)]
            )
            
            # Execute call
            result = await client.call_contract(call)
            balance_wei = result[0]
            balance_eth = balance_wei / 1e18
            
            return balance_eth
            
        except Exception as e:
            logger.warning(f"⚠️ RPC Error ({rpc_url[:30]}...): {str(e)[:50]}")
            return None
    
    async def check_balance_with_rotation(self) -> Optional[float]:
        """Check balance with RPC rotation"""
        
        for rpc_url in self.rpc_urls:
            balance = await self.check_balance_rpc(rpc_url)
            if balance is not None:
                provider_name = self.get_provider_name(rpc_url)
                logger.info(f"✅ Success via {provider_name}")
                return balance
        
        logger.error("❌ All RPC endpoints failed")
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
    
    def generate_starkli_command(self, balance_eth: float) -> str:
        """Generate Starkli command for manual execution"""
        
        # Get environment variables
        private_key = os.getenv("TRANSIT_EVM_PRIVATE_KEY")
        target_address = os.getenv("STARKNET_WALLET_ADDRESS")
        
        if not private_key or not target_address:
            return "❌ Missing TRANSIT_EVM_PRIVATE_KEY or STARKNET_WALLET_ADDRESS"
        
        # Calculate sweep amount (leave some for gas)
        sweep_amount = balance_eth - 0.0001  # Leave 0.0001 ETH for gas
        
        command = f"""# Starkli Sweep Command (Execute when ready)
starkli invoke \\
  --network starknet-mainnet \\
  --account {self.ghost_address} \\
  --private-key {private_key} \\
  0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7 \\
  transfer \\
  {int(target_address, 16)} \\
  {int(sweep_amount * 1e18)}

# Alternative: Use rescue_funds.py --sweep
python .\\venv\\Scripts\\rescue_funds.py --sweep --confirm
"""
        
        return command
    
    def send_telegram_notification(self, balance_eth: float):
        """Send Telegram notification if configured"""
        
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            logger.info("📱 Telegram not configured")
            return
        
        try:
            import requests
            
            message = f"""🎉 GHOST FUNDS DETECTED!
            
💰 Balance: {balance_eth:.6f} ETH
💵 Value: ${balance_eth * 2200:.2f} USD
👻 Address: {self.ghost_address}
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Ready for sweep execution!
"""
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                logger.success("📱 Telegram notification sent")
            else:
                logger.warning(f"📱 Telegram failed: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"📱 Telegram error: {e}")
    
    def create_status_table(self, balance_eth: float, provider: str, poll_count: int) -> Table:
        """Create rich status table"""
        
        table = Table(title=f"👻 Ghost Sentry V2 - Poll #{poll_count}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Ghost Address", self.ghost_address[:10] + "...")
        table.add_row("Current Balance", f"{balance_eth:.6f} ETH")
        table.add_row("USD Value", f"${balance_eth * 2200:.2f}")
        table.add_row("Provider", provider)
        table.add_row("Threshold", f"{self.threshold_eth} ETH")
        table.add_row("Status", "🟡 MONITORING" if balance_eth < self.threshold_eth else "🟢 DETECTED")
        table.add_row("Next Poll", f"{self.poll_interval}s")
        
        return table
    
    async def run_sentry(self):
        """Main sentry loop"""
        
        self.console.print(Panel.fit(
            "[bold red]🚨 GHOST SENTRY V2 - NETWORK BLACKOUT[/bold red]\n"
            "Operating under firewall conditions\n"
            f"Monitoring: {self.ghost_address[:10]}...\n"
            f"Threshold: {self.threshold_eth} ETH\n"
            f"RPC Endpoints: {len(self.rpc_urls)} available",
            title="Blackout Protocol"
        ))
        
        poll_count = 0
        
        while True:
            poll_count += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"🔍 Poll #{poll_count} - {timestamp}")
            
            # Check balance with rotation
            balance_eth = await self.check_balance_with_rotation()
            
            if balance_eth is None:
                logger.error("❌ All RPCs failed - waiting 60s before retry")
                await asyncio.sleep(60)
                continue
            
            # Get provider name for display
            provider = "Unknown"
            for rpc_url in self.rpc_urls:
                if await self.check_balance_rpc(rpc_url) is not None:
                    provider = self.get_provider_name(rpc_url)
                    break
            
            # Display status
            table = self.create_status_table(balance_eth, provider, poll_count)
            self.console.print(table)
            
            # Check threshold
            if balance_eth > self.threshold_eth:
                logger.success(f"🎉 BRIDGE SETTLED: {balance_eth:.6f} ETH detected!")
                
                # Success panel
                self.console.print(Panel.fit(
                    f"[bold green]💰 GHOST FUNDS DETECTED![/bold green]\n\n"
                    f"Amount: {balance_eth:.6f} ETH\n"
                    f"Value: ${balance_eth * 2200:.2f} USD\n"
                    f"Provider: {provider}\n"
                    f"Time: {timestamp}\n\n"
                    f"[bold yellow]🚀 READY FOR SWEEP EXECUTION[/bold yellow]",
                    title="MISSION SUCCESS",
                    border_style="green"
                ))
                
                # Generate Starkli command
                command = self.generate_starkli_command(balance_eth)
                
                self.console.print(Panel(
                    command,
                    title="🛠️ Execution Commands",
                    border_style="yellow"
                ))
                
                # Save command to file
                with open("ghost_sweep_command.txt", "w") as f:
                    f.write(f"# Ghost Sweep Command - {timestamp}\n")
                    f.write(command)
                
                # Send notification
                self.send_telegram_notification(balance_eth)
                
                # Log success
                logger.success(f"✅ Ghost funds detected and ready for sweep")
                logger.info(f"💰 Amount: {balance_eth:.6f} ETH (${balance_eth * 2200:.2f})")
                
                # Continue monitoring (in case of additional funds)
                logger.info("🔄 Continuing monitoring for additional funds...")
                
            else:
                logger.info(f"⌛ No funds yet. Balance: {balance_eth:.6f} ETH")
            
            # Wait for next poll
            logger.info(f"⏳ Waiting {self.poll_interval}s...")
            await asyncio.sleep(self.poll_interval)

async def main():
    """Main execution"""
    
    # Display startup banner
    console = Console()
    console.print("🚀 Ghost Sentry V2 - Network Blackout Protocol", style="bold red")
    console.print("🔐 Operating under firewall conditions - RPC only", style="dim")
    
    # Initialize and run sentry
    sentry = GhostSentryV2()
    await sentry.run_sentry()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Sentry stopped by user")
    except Exception as e:
        logger.error(f"❌ Sentry error: {e}")
        sys.exit(1)
