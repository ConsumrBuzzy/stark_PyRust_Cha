#!/usr/bin/env python3
"""
Self-Funding Pipeline - Coinbase to StarkNet Automated Bridge
Unified pipeline for automated funding from Coinbase to StarkNet via Base/Orbiter
Based on PhantomArbiter execution patterns and CDP SDK integration
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add core to path
sys.path.append(str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger
from web3 import Web3
from eth_account import Account

# Import core components
from core.factory import get_provider_factory
from core.safety import get_signer
from core.ui import get_dashboard

class SelfFundingPipeline:
    """
    Automated funding pipeline from Coinbase to StarkNet
    Stage 1: Coinbase CDP → Phantom (Base)
    Stage 2: Base Confirmation
    Stage 3: Orbiter Bridge (Base → StarkNet)
    Stage 4: War Room Alert
    """
    
    def __init__(self):
        self.console = Console()
        self.dashboard = get_dashboard()
        self.provider_factory = get_provider_factory()
        self.signer = get_signer()
        
        # Pipeline configuration
        self.stages = {
            "coinbase_withdrawal": {
                "name": "Coinbase API Withdrawal",
                "status": "PENDING",
                "required_creds": ["COINBASE_CLIENT_API_KEY", "COINBASE_API_PRIVATE_KEY"]
            },
            "base_confirmation": {
                "name": "Base Network Confirmation", 
                "status": "PENDING",
                "timeout": 60
            },
            "orbiter_bridge": {
                "name": "Orbiter Bridge (Base → StarkNet)",
                "status": "PENDING",
                "required_creds": ["ORBITER_MAKER_ADDRESS", "BASE_RPC_URL"]
            },
            "starknet_alert": {
                "name": "StarkNet War Room Alert",
                "status": "PENDING",
                "target_balance": 0.018
            }
        }
        
        # Bridge configuration
        self.orbiter_config = {
            "starknet_chain_id": 14,  # Orbiter tag for StarkNet
            "maker_address": os.getenv("ORBITER_MAKER_ADDRESS", "0x0000000000000000000000000000000000000000"),
            "min_bridge_amount": 0.005,  # Minimum for bridge
            "max_bridge_amount": 0.1,   # Maximum for safety
        }
        
        # Base network configuration
        self.base_config = {
            "rpc_url": os.getenv("BASE_RPC_URL", "https://mainnet.base.org"),
            "phantom_address": os.getenv("PHANTOM_BASE_ADDRESS"),
            "gas_limit": 21000,
            "gas_price_gwei": 0.01  # Base has very low gas
        }
        
        logger.info("🚀 Self-Funding Pipeline initialized")
    
    def check_credentials(self) -> Dict[str, bool]:
        """Check if required credentials are available"""
        
        self.console.print("🔍 Checking pipeline credentials...", style="bold blue")
        
        creds_status = {}
        
        # Check Coinbase API credentials
        coinbase_creds = [
            "COINBASE_CLIENT_API_KEY",
            "COINBASE_API_PRIVATE_KEY"
        ]
        
        for cred in coinbase_creds:
            creds_status[cred] = bool(os.getenv(cred))
        
        # Check Bridge credentials
        bridge_creds = [
            "ORBITER_MAKER_ADDRESS",
            "BASE_RPC_URL",
            "PHANTOM_BASE_ADDRESS"
        ]
        
        for cred in bridge_creds:
            creds_status[cred] = bool(os.getenv(cred))
        
        # Check StarkNet credentials
        starknet_creds = [
            "STARKNET_WALLET_ADDRESS",
            "STARKNET_GHOST_ADDRESS"
        ]
        
        for cred in starknet_creds:
            creds_status[cred] = bool(os.getenv(cred))
        
        # Display results
        table = Table(title="🔐 Credential Status")
        table.add_column("Credential", style="cyan")
        table.add_column("Status", style="bold")
        
        for cred, status in creds_status.items():
            status_icon = "✅" if status else "❌"
            table.add_row(cred, f"{status_icon} {'Set' if status else 'Missing'}")
        
        self.console.print(table)
        
        return creds_status
    
    async def stage_1_coinbase_withdrawal(self, amount_eth: float) -> Dict[str, Any]:
        """Stage 1: Withdraw ETH from Coinbase API to Phantom (Base)"""
        
        self.console.print("🏦 Stage 1: Coinbase API Withdrawal", style="bold blue")
        
        try:
            # Import Coinbase SDK (placeholder - would need coinbase-python SDK)
            # import coinbase
            # from coinbase.wallet.client import Client
            
            # Get credentials
            api_key = os.getenv("COINBASE_CLIENT_API_KEY")
            api_secret = os.getenv("COINBASE_API_PRIVATE_KEY")
            
            if not api_key or not api_secret:
                raise Exception("Coinbase API credentials not found")
            
            # Initialize Coinbase client
            # client = Client(api_key, api_secret)
            
            # Placeholder implementation using existing API
            self.console.print("📝 Using existing Coinbase API credentials", style="green")
            self.console.print(f"� API Key: {api_key[:20]}...")
            
            # Simulate withdrawal for demo
            # In production, this would be:
            # 1. Get primary account
            # 2. Create withdrawal to Base network
            # 3. Return transaction hash
            
            await asyncio.sleep(2)
            
            result = {
                "status": "SIMULATED",
                "transaction_hash": "0x0000000000000000000000000000000000000000000000000000000000000000",
                "amount": amount_eth,
                "from_address": "COINBASE_ACCOUNT",
                "to_address": self.base_config["phantom_address"],
                "network": "base",
                "timestamp": datetime.now().isoformat()
            }
            
            self.console.print(f"✅ Withdrawal simulated: {amount_eth} ETH → {self.base_config['phantom_address']}")
            self.console.print("📝 Ready for live implementation with coinbase-python SDK")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Coinbase withdrawal failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def stage_2_base_confirmation(self, tx_hash: str) -> Dict[str, Any]:
        """Stage 2: Wait for Base network confirmation"""
        
        self.console.print("⏳ Stage 2: Base Network Confirmation", style="bold blue")
        
        try:
            # Connect to Base network
            w3 = Web3(Web3.HTTPProvider(self.base_config["rpc_url"]))
            
            if not w3.is_connected():
                raise Exception("Failed to connect to Base network")
            
            # Wait for confirmation
            timeout = self.stages["base_confirmation"]["timeout"]
            start_time = time.time()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Waiting for confirmation...", total=None)
                
                while time.time() - start_time < timeout:
                    try:
                        receipt = w3.eth.get_transaction_receipt(tx_hash)
                        if receipt and receipt['status'] == 1:
                            progress.update(task, description="✅ Confirmed!")
                            break
                    except:
                        pass
                    
                    progress.update(task, description=f"Checking... ({int(time.time() - start_time)}s)")
                    await asyncio.sleep(2)
                else:
                    raise Exception(f"Confirmation timeout after {timeout} seconds")
            
            result = {
                "status": "CONFIRMED",
                "block_number": receipt['blockNumber'],
                "gas_used": receipt['gasUsed'],
                "timestamp": datetime.now().isoformat()
            }
            
            self.console.print(f"✅ Transaction confirmed in block {receipt['blockNumber']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Base confirmation failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def stage_3_orbiter_bridge(self, amount_eth: float) -> Dict[str, Any]:
        """Stage 3: Trigger Orbiter Bridge (Base → StarkNet)"""
        
        self.console.print("🌉 Stage 3: Orbiter Bridge (Base → StarkNet)", style="bold blue")
        
        try:
            # Validate amount
            if amount_eth < self.orbiter_config["min_bridge_amount"]:
                raise Exception(f"Amount {amount_eth} below minimum {self.orbiter_config['min_bridge_amount']}")
            
            if amount_eth > self.orbiter_config["max_bridge_amount"]:
                raise Exception(f"Amount {amount_eth} above maximum {self.orbiter_config['max_bridge_amount']}")
            
            # Calculate Orbiter tag amount
            # For StarkNet (chain_id 14), we add 0.000014 to the amount
            tag_amount = 0.000014
            bridge_amount = amount_eth + tag_amount
            
            # Connect to Base network
            w3 = Web3(Web3.HTTPProvider(self.base_config["rpc_url"]))
            
            # Get private key from encrypted signer
            # Note: This would need to be extended for Base network keys
            demo_password = "StarkNet_Security_Demo_2026"  # Placeholder
            os.environ["SIGNER_PASSWORD"] = demo_password
            
            # For demo, simulate bridge transaction
            self.console.print("⚠️  Bridge transaction simulated", style="yellow")
            self.console.print(f"📊 Bridge amount: {bridge_amount:.6f} ETH (includes {tag_amount:.6f} tag)")
            
            await asyncio.sleep(3)
            
            result = {
                "status": "SIMULATED",
                "transaction_hash": "0x1111111111111111111111111111111111111111111111111111111111111111",
                "amount": bridge_amount,
                "tag": tag_amount,
                "target_chain": "StarkNet",
                "maker_address": self.orbiter_config["maker_address"],
                "timestamp": datetime.now().isoformat()
            }
            
            self.console.print(f"✅ Bridge transaction simulated: {bridge_amount:.6f} ETH → StarkNet")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Orbiter bridge failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def stage_4_starknet_alert(self, target_balance: float) -> Dict[str, Any]:
        """Stage 4: Alert War Room when target balance reached"""
        
        self.console.print("🚨 Stage 4: StarkNet War Room Alert", style="bold blue")
        
        try:
            # Monitor StarkNet balance
            max_attempts = 30  # 5 minutes max
            target_balance = self.stages["starknet_alert"]["target_balance"]
            
            for attempt in range(max_attempts):
                # Get best StarkNet provider
                provider_name, client = self.provider_factory.get_best_provider()
                
                # Check combined balance
                from starknet_py.hash.selector import get_selector_from_name
                from starknet_py.net.client_models import Call
                
                # ETH contract
                eth_contract = int(os.getenv("STARKNET_ETH_CONTRACT", "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"), 16)
                
                # Check main wallet
                main_wallet = os.getenv("STARKNET_WALLET_ADDRESS")
                ghost_address = os.getenv("STARKNET_GHOST_ADDRESS")
                
                main_call = Call(
                    to_addr=eth_contract,
                    selector=get_selector_from_name("balanceOf"),
                    calldata=[int(main_wallet, 16)]
                )
                
                ghost_call = Call(
                    to_addr=eth_contract,
                    selector=get_selector_from_name("balanceOf"),
                    calldata=[int(ghost_address, 16)]
                )
                
                main_result = await client.call_contract(main_call)
                ghost_result = await client.call_contract(ghost_call)
                
                main_balance = main_result[0] / 1e18
                ghost_balance = ghost_result[0] / 1e18
                combined_balance = main_balance + ghost_balance
                
                self.console.print(f"📊 Balance check {attempt + 1}/{max_attempts}: {combined_balance:.6f} ETH")
                
                # Update dashboard
                self.dashboard.update_state({
                    "starknet_balance": main_balance,
                    "ghost_balance": ghost_balance,
                    "combined_balance": combined_balance
                })
                
                if combined_balance >= target_balance:
                    self.console.print(f"🎯 TARGET REACHED: {combined_balance:.6f} ETH ≥ {target_balance} ETH", style="bold green")
                    
                    # Trigger alert
                    alert_panel = Panel(
                        f"🚀 ACTIVATION READY!\n\n"
                        f"Combined Balance: {combined_balance:.6f} ETH\n"
                        f"Target: {target_balance:.6f} ETH\n"
                        f"Status: READY FOR ATOMIC ACTIVATION",
                        title="🚨 WAR ROOM ALERT",
                        border_style="green"
                    )
                    
                    self.console.print(alert_panel)
                    
                    return {
                        "status": "TARGET_REACHED",
                        "combined_balance": combined_balance,
                        "target_balance": target_balance,
                        "main_balance": main_balance,
                        "ghost_balance": ghost_balance,
                        "timestamp": datetime.now().isoformat()
                    }
                
                await asyncio.sleep(10)  # Wait 10 seconds between checks
            
            # Timeout reached
            return {
                "status": "TIMEOUT",
                "final_balance": combined_balance,
                "target_balance": target_balance,
                "error": f"Target balance not reached after {max_attempts * 10} seconds"
            }
            
        except Exception as e:
            logger.error(f"❌ StarkNet alert failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def run_fee_audit(self) -> Dict[str, Any]:
        """Perform fee audit before executing pipeline"""
        
        self.console.print("💰 Performing Fee Audit...", style="bold blue")
        
        try:
            # Base network fees
            w3 = Web3(Web3.HTTPProvider(self.base_config["rpc_url"]))
            gas_price = w3.eth.gas_price
            base_fee_eth = (gas_price * self.base_config["gas_limit"]) / 1e18
            
            # StarkNet fees (estimate)
            provider_name, client = self.provider_factory.get_best_provider()
            
            # StarkNet deployment cost estimate
            estimated_starknet_fee = 0.016  # Conservative estimate
            
            # Orbiter bridge fee (typically small)
            orbiter_fee = 0.0001
            
            total_fees = base_fee_eth + estimated_starknet_fee + orbiter_fee
            
            fee_table = Table(title="💰 Fee Audit Results")
            fee_table.add_column("Component", style="cyan")
            fee_table.add_column("Fee (ETH)", justify="right", style="yellow")
            fee_table.add_column("Fee (USD)", justify="right", style="green")
            
            eth_price = 2200  # Placeholder
            
            fee_table.add_row(
                "Base Network Gas",
                f"{base_fee_eth:.6f}",
                f"${base_fee_eth * eth_price:.2f}"
            )
            fee_table.add_row(
                "StarkNet Deployment",
                f"{estimated_starknet_fee:.6f}",
                f"${estimated_starknet_fee * eth_price:.2f}"
            )
            fee_table.add_row(
                "Orbiter Bridge",
                f"{orbiter_fee:.6f}",
                f"${orbiter_fee * eth_price:.2f}"
            )
            fee_table.add_row(
                "TOTAL",
                f"{total_fees:.6f}",
                f"${total_fees * eth_price:.2f}",
                style="bold"
            )
            
            self.console.print(fee_table)
            
            return {
                "status": "COMPLETE",
                "base_fee": base_fee_eth,
                "starknet_fee": estimated_starknet_fee,
                "orbiter_fee": orbiter_fee,
                "total_fees": total_fees,
                "total_usd": total_fees * eth_price
            }
            
        except Exception as e:
            logger.error(f"❌ Fee audit failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    async def execute_pipeline(self, amount_eth: float = 0.02) -> Dict[str, Any]:
        """Execute the complete self-funding pipeline"""
        
        self.console.print("🚀 Self-Funding Pipeline Execution", style="bold blue")
        self.console.print("=" * 50, style="dim")
        
        # Stage 0: Credential check
        creds = self.check_credentials()
        missing_creds = [k for k, v in creds.items() if not v]
        
        if missing_creds:
            self.console.print(f"❌ Missing credentials: {', '.join(missing_creds)}", style="bold red")
            return {"status": "FAILED", "error": "Missing credentials"}
        
        # Stage 0: Fee audit
        fee_audit = await self.run_fee_audit()
        if fee_audit["status"] == "FAILED":
            return {"status": "FAILED", "error": "Fee audit failed"}
        
        # Execute stages
        pipeline_results = {}
        
        # Stage 1: Coinbase withdrawal
        self.stages["coinbase_withdrawal"]["status"] = "RUNNING"
        stage1_result = await self.stage_1_coinbase_withdrawal(amount_eth)
        pipeline_results["stage1"] = stage1_result
        
        if stage1_result["status"] == "FAILED":
            self.stages["coinbase_withdrawal"]["status"] = "FAILED"
            return {"status": "FAILED", "stage": "coinbase_withdrawal", "error": stage1_result["error"]}
        
        self.stages["coinbase_withdrawal"]["status"] = "COMPLETE"
        
        # Stage 2: Base confirmation
        self.stages["base_confirmation"]["status"] = "RUNNING"
        stage2_result = await self.stage_2_base_confirmation(stage1_result["transaction_hash"])
        pipeline_results["stage2"] = stage2_result
        
        if stage2_result["status"] == "FAILED":
            self.stages["base_confirmation"]["status"] = "FAILED"
            return {"status": "FAILED", "stage": "base_confirmation", "error": stage2_result["error"]}
        
        self.stages["base_confirmation"]["status"] = "COMPLETE"
        
        # Stage 3: Orbiter bridge
        self.stages["orbiter_bridge"]["status"] = "RUNNING"
        stage3_result = await self.stage_3_orbiter_bridge(amount_eth)
        pipeline_results["stage3"] = stage3_result
        
        if stage3_result["status"] == "FAILED":
            self.stages["orbiter_bridge"]["status"] = "FAILED"
            return {"status": "FAILED", "stage": "orbiter_bridge", "error": stage3_result["error"]}
        
        self.stages["orbiter_bridge"]["status"] = "COMPLETE"
        
        # Stage 4: StarkNet alert
        self.stages["starknet_alert"]["status"] = "RUNNING"
        stage4_result = await self.stage_4_starknet_alert(self.stages["starknet_alert"]["target_balance"])
        pipeline_results["stage4"] = stage4_result
        
        if stage4_result["status"] == "FAILED":
            self.stages["starknet_alert"]["status"] = "FAILED"
            return {"status": "FAILED", "stage": "starknet_alert", "error": stage4_result["error"]}
        
        self.stages["starknet_alert"]["status"] = "COMPLETE"
        
        # Pipeline complete
        self.console.print("🎉 Self-Funding Pipeline COMPLETE!", style="bold green")
        
        return {
            "status": "COMPLETE",
            "stages": self.stages,
            "results": pipeline_results,
            "fee_audit": fee_audit,
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """Main pipeline execution"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Funding Pipeline")
    parser.add_argument("--amount", type=float, default=0.02, help="Amount to transfer (ETH)")
    parser.add_argument("--fee-audit", action="store_true", help="Run fee audit only")
    parser.add_argument("--check-creds", action="store_true", help="Check credentials only")
    args = parser.parse_args()
    
    console = Console()
    
    try:
        pipeline = SelfFundingPipeline()
        
        if args.check_creds:
            pipeline.check_credentials()
        elif args.fee_audit:
            await pipeline.run_fee_audit()
        else:
            result = await pipeline.execute_pipeline(args.amount)
            
            if result["status"] == "COMPLETE":
                console.print("🎯 Pipeline executed successfully!", style="bold green")
            else:
                console.print(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}", style="bold red")
                sys.exit(1)
    
    except Exception as e:
        console.print(f"❌ Pipeline error: {e}", style="bold red")
        logger.error(f"❌ Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Pipeline stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
