"""
PyPro Systems - Telegram Reporting System
Extracted from PhantomArbiter and adapted for SRP compliance
"""

import os
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

# Load .env file
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

@dataclass
class TelegramMessage:
    """Telegram message structure"""
    title: str
    content: str
    priority: str = "normal"  # low, normal, high, critical

class TelegramNotifier:
    """Async Telegram notification system"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if self.enabled:
            print("📱 Telegram notifications enabled")
        else:
            print("📱 Telegram notifications disabled (missing credentials)")
    
    async def send_message(self, message: TelegramMessage) -> bool:
        """Send Telegram message asynchronously"""
        if not self.enabled:
            print("📱 Telegram not configured - message not sent")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                "chat_id": self.chat_id,
                "text": f"{message.title}\n\n{message.content}",
                "parse_mode": "HTML"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        print("📱 Telegram message sent successfully")
                        return True
                    else:
                        print(f"📱 Telegram failed: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            print(f"📱 Telegram error: {e}")
            return False
    
    async def send_alert(self, title: str, message: str) -> bool:
        """Send high-priority alert"""
        alert_msg = TelegramMessage(
            title=f"🚨 {title}",
            content=message,
            priority="critical"
        )
        return await self.send_message(alert_msg)
    
    async def send_status(self, title: str, status_data: Dict[str, Any]) -> bool:
        """Send status update"""
        content_lines = []
        for key, value in status_data.items():
            content_lines.append(f"<b>{key}:</b> {value}")
        
        status_msg = TelegramMessage(
            title=f"📊 {title}",
            content="\n".join(content_lines),
            priority="normal"
        )
        return await self.send_message(status_msg)

class ReportingSystem:
    """SRP-compliant reporting system for the RecoveryKernel"""
    
    def __init__(self):
        self.telegram = TelegramNotifier()
        self.alert_history = []
    
    async def bridge_minted(self, balance: float, address: str) -> None:
        """Notify when bridge mint is confirmed"""
        message = f"""🎉 BRIDGE MINT CONFIRMED

📍 StarkNet Address: {address[:10]}...
💰 New Balance: {balance:.6f} ETH
💵 Value: ${balance * 2200:.2f} USD
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Status: Genesis Sequence Ready

🚀 Full-Auto will now execute the Genesis Bundle!"""
        
        await self.telegram.send_alert("BRIDGE MINTED", message)
        self.alert_history.append(("bridge_minted", datetime.now()))
    
    async def account_activated(self, address: str, tx_hash: str) -> None:
        """Notify when account is successfully activated"""
        message = f"""🏭 ACCOUNT ACTIVATED

📍 StarkNet Address: {address[:10]}...
🔗 Transaction: {tx_hash[:10]}...
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Status: Iron → Steel Mining Ready

⚡ The autonomous agent is now live!"""
        
        await self.telegram.send_alert("ACCOUNT ACTIVATED", message)
        self.alert_history.append(("account_activated", datetime.now()))
    
    async def mining_cycle_complete(self, cycle_data: Dict[str, Any]) -> None:
        """Notify when Iron → Steel cycle completes"""
        message = f"""⚡ MINING CYCLE COMPLETE

🔄 Cycle #{cycle_data.get('cycle_number', 'N/A')}
📊 Yield: {cycle_data.get('yield_amount', 'N/A')} ETH
💰 Profit: ${cycle_data.get('profit_usd', 'N/A')} USD
⛽ Gas Used: {cycle_data.get('gas_used', 'N/A')} Gwei
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Status: Next Cycle Starting

🏭 Autonomous mining continues..."""
        
        await self.telegram.send_alert("MINING CYCLE COMPLETE", message)
        self.alert_history.append(("mining_cycle_complete", datetime.now()))
    
    async def gas_spike_alert(self, gas_price: float, threshold: float) -> None:
        """Alert on gas price spike"""
        message = f"""⛽ GAS SPIKE DETECTED

📈 Current Gas: {gas_price:.2f} Gwei
🚨 Threshold: {threshold:.2f} Gwei
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🛡️ Status: Auto-Pilot Paused

⚠️ Full-Auto operation paused until gas prices normalize."""
        
        await self.telegram.send_alert("GAS SPIKE ALERT", message)
        self.alert_history.append(("gas_spike", datetime.now()))
    
    async def mission_failed(self, error: str, phase: str) -> None:
        """Alert on mission failure"""
        message = f"""❌ MISSION FAILED

🎯 Phase: {phase}
🚨 Error: {error}
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔧 Status: Manual Review Required

⚠️ Autonomous operation halted. Please investigate."""
        
        await self.telegram.send_alert("MISSION FAILED", message)
        self.alert_history.append(("mission_failed", datetime.now()))
    
    async def send_heartbeat(self, status_data: Dict[str, Any]) -> None:
        """Send periodic heartbeat status"""
        heartbeat_msg = TelegramMessage(
            title="💓 Full-Auto Heartbeat",
            content=f"""📍 Status: {status_data.get('status', 'Unknown')}
💰 StarkNet: {status_data.get('starknet_balance', 'N/A')} ETH
👻 Phantom: {status_data.get('phantom_balance', 'N/A')} ETH
⛽ Gas: {status_data.get('gas_price', 'N/A')} Gwei
🎯 Threshold: {'MET' if status_data.get('threshold_met', False) else 'WAITING'}
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🐕 Watchdog monitoring...""",
            priority="low"
        )
        await self.telegram.send_message(heartbeat_msg)
    
    def get_alert_history(self) -> list:
        """Get recent alert history"""
        return self.alert_history[-10:]  # Last 10 alerts
    
    def is_enabled(self) -> bool:
        """Check if Telegram reporting is enabled"""
        return self.telegram.enabled
