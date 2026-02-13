#!/usr/bin/env python3
"""
Advanced StarkGate Transaction Tracking System
"""

import asyncio
import aiohttp
import time
from datetime import datetime
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from starknet_py.net.full_node_client import FullNodeClient

class AdvancedStarkGateTracker:
    """Enhanced transaction tracking with multiple data sources"""
    
    def __init__(self):
        self.base_web3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
        self.base_web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.starknet_client = FullNodeClient(
            node_url='https://starknet-mainnet.g.alchemy.com/starknet/version/rpc/v0_10/9HtNv_yFeMgWsbW_gI2IN'
        )
        
        # Tracking endpoints
        self.starkgate_explorer = "https://starkgate.starknet.io/api"
        self.starkscan_api = "https://api.starkscan.co/api"
        self.voyager_api = "https://voyager.online/api"
    
    async def track_transaction_comprehensive(self, tx_hash: str):
        """Comprehensive transaction tracking across multiple sources"""
        
        print(f"🔍 ADVANCED TRANSACTION TRACKING")
        print(f"📋 Transaction: {tx_hash}")
        print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        tracking_data = {
            "tx_hash": tx_hash,
            "base_status": None,
            "starkgate_status": None,
            "starkscan_status": None,
            "l1_l2_message": None,
            "current_balance": None,
            "queue_position": None,
            "proof_status": None
        }
        
        while True:
            try:
                # Track Base transaction
                base_status = await self.check_base_transaction(tx_hash)
                tracking_data["base_status"] = base_status
                
                # Track StarkGate status
                starkgate_status = await self.check_starkgate_status(tx_hash)
                tracking_data["starkgate_status"] = starkgate_status
                
                # Track StarkScan
                starkscan_status = await self.check_starkscan_status(tx_hash)
                tracking_data["starkscan_status"] = starkscan_status
                
                # Track L1→L2 message
                message_status = await self.check_l1_l2_message(tx_hash)
                tracking_data["l1_l2_message"] = message_status
                
                # Check current balance
                current_balance = await self.check_starknet_balance()
                tracking_data["current_balance"] = current_balance
                
                # Display comprehensive status
                self.display_tracking_status(tracking_data)
                
                # Check if complete
                if current_balance and current_balance >= 0.018:
                    print(f"\n🎉 TRANSACTION COMPLETE - Balance reached: {current_balance:.6f} ETH")
                    break
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ Tracking error: {e}")
                await asyncio.sleep(30)
    
    async def check_base_transaction(self, tx_hash: str):
        """Check Base transaction status"""
        try:
            receipt = self.base_web3.eth.get_transaction_receipt(tx_hash)
            tx = self.base_web3.eth.get_transaction(tx_hash)
            
            return {
                "status": "SUCCESS" if receipt.status == 1 else "FAILED",
                "block": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "value": self.base_web3.from_wei(tx.value, 'ether'),
                "confirmations": self.base_web3.eth.block_number - receipt.blockNumber
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def check_starkgate_status(self, tx_hash: str):
        """Check StarkGate bridge status"""
        try:
            async with aiohttp.ClientSession() as session:
                # Try StarkGate API
                url = f"{self.starkgate_explorer}/bridge/tx/{tx_hash}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": data.get("status", "unknown"),
                            "bridge_amount": data.get("amount"),
                            "l2_tx_hash": data.get("l2_tx_hash"),
                            "message_nonce": data.get("message_nonce")
                        }
        except Exception as e:
            return {"error": str(e)}
    
    async def check_starkscan_status(self, tx_hash: str):
        """Check StarkScan for transaction"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.starkscan_api}/bridge"
                params = {"l1_tx_hash": tx_hash}
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("data"):
                            return {
                                "status": data["data"][0].get("status"),
                                "l2_tx_hash": data["data"][0].get("l2_tx_hash"),
                                "message_nonce": data["data"][0].get("message_nonce")
                            }
        except Exception as e:
            return {"error": str(e)}
    
    async def check_l1_l2_message(self, tx_hash: str):
        """Check L1→L2 message status"""
        try:
            # This would require more complex message queue analysis
            # For now, return basic status
            return {
                "status": "IN_TRANSIT",
                "queue_position": "UNKNOWN",
                "proof_status": "PENDING"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def check_starknet_balance(self):
        """Check current StarkNet balance"""
        try:
            from starknet_py.hash.selector import get_selector_from_name
            from starknet_py.net.client_models import Call
            
            call = Call(
                to_addr=int("0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7", 16),
                selector=get_selector_from_name("balanceOf"),
                calldata=[int("0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9", 16)]
            )
            
            result = await self.starknet_client.call_contract(call)
            return result[0] / 1e18
        except Exception as e:
            return None
    
    def display_tracking_status(self, data):
        """Display comprehensive tracking status"""
        print(f"\n📊 TRACKING UPDATE - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
        
        # Base status
        if data.get("base_status") and "error" not in data["base_status"]:
            base = data["base_status"]
            print(f"🔗 Base: ✅ {base['status']} | Block: {base['block']} | Gas: {base['gas_used']:,}")
        
        # StarkGate status
        if data.get("starkgate_status") and "error" not in data["starkgate_status"]:
            sg = data["starkgate_status"]
            print(f"🌉 StarkGate: {sg.get('status', 'UNKNOWN')} | Nonce: {sg.get('message_nonce', 'N/A')}")
        
        # StarkScan status
        if data.get("starkscan_status") and "error" not in data["starkscan_status"]:
            ss = data["starkscan_status"]
            print(f"🔍 StarkScan: {ss.get('status', 'UNKNOWN')} | L2 TX: {ss.get('l2_tx_hash', 'N/A')[:10]}...")
        
        # Balance
        if data.get("current_balance"):
            balance = data["current_balance"]
            needed = max(0, 0.018 - balance)
            print(f"💰 Balance: {balance:.6f} ETH | Need: {needed:.6f} ETH")
        
        print("-" * 50)

async def main():
    """Main tracking function"""
    tracker = AdvancedStarkGateTracker()
    tx_hash = "0x2dfc79aa3ad0ba437b7122a2b538eb72b2259f261a3f40818e7fa7a5074a64cd"
    await tracker.track_transaction_comprehensive(tx_hash)

if __name__ == "__main__":
    asyncio.run(main())
