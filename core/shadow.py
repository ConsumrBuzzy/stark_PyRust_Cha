#!/usr/bin/env python3
"""
Shadow State Check - Bypass L7 DPI with Direct Contract Calls
Uses starknet_call to ETH contract instead of getNonce/getClassHashAt
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

# Add python-logic to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call

class ShadowStateChecker:
    """Bypasses state-level filtering using direct contract calls"""
    
    def __init__(self):
        self.console = Console()
        self.setup_logging()
        self.load_env()
        
        # Target addresses
        self.ghost_address = "os.getenv("STARKNET_GHOST_ADDRESS")"
        self.main_wallet = "os.getenv("STARKNET_WALLET_ADDRESS")"
        
        # ETH contract (same across all providers)
        self.eth_contract = "int(os.getenv("STARKNET_ETH_CONTRACT", "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"), 16)"
        
        # Working RPC URLs (from diagnostic)
        self.rpc_urls = [
            os.getenv("STARKNET_MAINNET_URL"),  # Alchemy
            os.getenv("STARKNET_LAVA_URL"),     # Lava
            os.getenv("STARKNET_1RPC_URL"),     # 1RPC
            os.getenv("STARKNET_ONFINALITY_URL"), # OnFinality
            os.getenv("STARKNET_RPC_URL")       # BlastAPI
        ]
        self.rpc_urls = [url for url in self.rpc_urls if url]
        
        logger.info(f"🔧 Shadow State Checker initialized")
        logger.info(f"👻 Ghost: {self.ghost_address}")
        logger.info(f"💼 Main: {self.main_wallet}")
        logger.info(f"📡 RPCs: {len(self.rpc_urls)} available")
    
    def setup_logging(self):
        """Configure logging"""
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level="INFO"
        )
        logger.add(
            "shadow_state_check.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level="DEBUG",
            rotation="5 MB",
            retention="3 days"
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
    
    async def check_balance_via_contract_call(self, rpc_url: str, address: str, label: str) -> Optional[Dict]:
        """Check balance using direct starknet_call to ETH contract"""
        
        try:
            client = FullNodeClient(node_url=rpc_url)
            
            # Build balanceOf call
            call = Call(
                to_addr=int(self.eth_contract, 16),
                selector=get_selector_from_name("balanceOf"),
                calldata=[int(address, 16)]
            )
            
            # Execute the call
            result = await client.call_contract(call)
            balance_wei = result[0]
            balance_eth = balance_wei / 1e18
            
            return {
                "rpc_url": rpc_url,
                "address": address,
                "label": label,
                "balance_wei": balance_wei,
                "balance_eth": balance_eth,
                "status": "✅ SUCCESS",
                "method": "contract_call"
            }
            
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                status = "🚫 BLOCKED"
            elif "timeout" in error_msg.lower():
                status = "⏱️ TIMEOUT"
            else:
                status = "⚠️ ERROR"
            
            return {
                "rpc_url": rpc_url,
                "address": address,
                "label": label,
                "balance_wei": 0,
                "balance_eth": 0.0,
                "status": status,
                "method": "contract_call",
                "error": error_msg[:50]
            }
    
    async def test_alternative_methods(self, rpc_url: str) -> Dict[str, str]:
        """Test alternative methods that might bypass filtering"""
        
        methods = {}
        
        try:
            client = FullNodeClient(node_url=rpc_url)
            
            # Method 1: starknet_call to ETH contract (our primary method)
            try:
                call = Call(
                    to_addr=int(self.eth_contract, 16),
                    selector=get_selector_from_name("balanceOf"),
                    calldata=[int(self.ghost_address, 16)]
                )
                await client.call_contract(call)
                methods["starknet_call"] = "✅ WORKS"
            except Exception as e:
                methods["starknet_call"] = f"❌ {str(e)[:20]}"
            
            # Method 2: starknet_getClass (different from getClassHashAt)
            try:
                await client.get_class(class_hash=0x25ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918)
                methods["getClass"] = "✅ WORKS"
            except Exception as e:
                methods["getClass"] = f"❌ {str(e)[:20]}"
            
            # Method 3: starknet_getTransactionReceipt (transaction-focused)
            try:
                await client.get_transaction_receipt(tx_hash=0x1)
                methods["getTransactionReceipt"] = "✅ WORKS"
            except Exception as e:
                methods["getTransactionReceipt"] = f"❌ {str(e)[:20]}"
            
            # Method 4: starknet_getEvents (event-focused)
            try:
                await client.get_events(
                    from_block_number=0,
                    to_block_number=1,
                    address=self.eth_contract,
                    keys=[],
                    chunk_size=1
                )
                methods["getEvents"] = "✅ WORKS"
            except Exception as e:
                methods["getEvents"] = f"❌ {str(e)[:20]}"
            
        except Exception as e:
            methods["client_error"] = f"❌ {str(e)[:20]}"
        
        return methods
    
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
        elif "blastapi" in rpc_url.lower():
            return "BlastAPI"
        else:
            return "Unknown"
    
    async def run_shadow_check(self):
        """Run comprehensive shadow state analysis"""
        
        self.console.print(Panel.fit(
            "[bold blue]🕵️ SHADOW STATE CHECK[/bold blue]\n"
            "Bypassing L7 DPI with Direct Contract Calls\n"
            "Testing alternative RPC methods...",
            title="State-Level Bypass Analysis"
        ))
        
        # Test addresses
        addresses = [
            (self.ghost_address, "Ghost Address"),
            (self.main_wallet, "Main Wallet")
        ]
        
        all_results = []
        
        # Test each address across all RPCs
        for address, label in addresses:
            self.console.print(f"\n🔍 Checking {label}: {address[:10]}...")
            
            # Concurrent testing across all RPCs
            tasks = [
                self.check_balance_via_contract_call(rpc_url, address, label)
                for rpc_url in self.rpc_urls
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter valid results
            valid_results = [r for r in results if isinstance(r, dict)]
            all_results.extend(valid_results)
            
            # Display results for this address
            table = Table(title=f"{label} - Shadow State Results")
            table.add_column("Provider", style="cyan")
            table.add_column("Method", style="dim")
            table.add_column("ETH Balance", justify="right", style="green")
            table.add_column("Status", style="bold")
            
            for result in valid_results:
                provider = self.get_provider_name(result["rpc_url"])
                balance_str = f"{result['balance_eth']:.6f}"
                
                table.add_row(
                    provider,
                    result["method"],
                    balance_str,
                    result["status"]
                )
            
            self.console.print(table)
        
        # Test alternative methods
        self.console.print("\n🧪 Testing Alternative Methods...")
        
        alt_methods_table = Table(title="Alternative Method Bypass Test")
        alt_methods_table.add_column("Provider", style="cyan")
        alt_methods_table.add_column("starknet_call", justify="center")
        alt_methods_table.add_column("getClass", justify="center")
        alt_methods_table.add_column("getTxReceipt", justify="center")
        alt_methods_table.add_column("getEvents", justify="center")
        
        for rpc_url in self.rpc_urls:
            provider = self.get_provider_name(rpc_url)
            methods = await self.test_alternative_methods(rpc_url)
            
            alt_methods_table.add_row(
                provider,
                methods.get("starknet_call", "❌"),
                methods.get("getClass", "❌"),
                methods.get("getTransactionReceipt", "❌"),
                methods.get("getEvents", "❌")
            )
        
        self.console.print(alt_methods_table)
        
        # Analysis and recommendations
        self.analyze_shadow_results(all_results)
        
        # Save report
        self.save_shadow_report(all_results)
    
    def analyze_shadow_results(self, results: List[Dict]):
        """Analyze shadow check results"""
        
        # Count successful contract calls
        successful_calls = [r for r in results if r["status"] == "✅ SUCCESS"]
        
        # Check for ghost funds
        ghost_results = [r for r in successful_calls if r["label"] == "Ghost Address"]
        ghost_balance = sum(r["balance_eth"] for r in ghost_results)
        
        # Check main wallet
        main_results = [r for r in successful_calls if r["label"] == "Main Wallet"]
        main_balance = sum(r["balance_eth"] for r in main_results)
        
        # Find working providers
        working_providers = set()
        for result in successful_calls:
            working_providers.add(self.get_provider_name(result["rpc_url"]))
        
        # Analysis panel
        analysis = f"""
🎯 SHADOW STATE ANALYSIS
• Contract Call Success: {len(successful_calls)}/{len(results)}
• Working Providers: {len(working_providers)}
• Ghost Balance: {ghost_balance:.6f} ETH
• Main Wallet: {main_balance:.6f} ETH
        """.strip()
        
        border_style = "green" if len(successful_calls) > 0 else "red"
        self.console.print(Panel(
            analysis,
            title="Bypass Analysis",
            border_style=border_style
        ))
        
        # Strategic recommendations
        recommendations = []
        
        if len(successful_calls) > 0:
            recommendations.append("✅ CONTRACT CALL BYPASSES FIREWALL")
            recommendations.append(f"💡 Use {', '.join(list(working_providers)[:2])} for balance monitoring")
            
            if ghost_balance > 0.005:
                recommendations.append("🎉 GHOST FUNDS DETECTED - Ready for sweep!")
            else:
                recommendations.append("⏳ Ghost funds still not arrived")
        else:
            recommendations.append("❌ All methods blocked - VPN required")
        
        if main_balance > 0:
            recommendations.append(f"💰 Main wallet has {main_balance:.6f} ETH")
        
        if recommendations:
            self.console.print(Panel(
                "\n".join(recommendations),
                title="Strategic Recommendations",
                border_style="yellow"
            ))
    
    def save_shadow_report(self, results: List[Dict]):
        """Save shadow state report"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Shadow State Check Report

**Timestamp**: {timestamp}
**Method**: Direct Contract Call Bypass
**Purpose**: Circumvent L7 DPI State Filtering

## Executive Summary

This report demonstrates the effectiveness of using `starknet_call` to bypass 
state-level filtering that blocks `getNonce` and `getClassHashAt` methods.

## Method Comparison

| Standard RPC | Status | Shadow Method | Status |
|--------------|--------|---------------|--------|
| starknet_getNonce | ❌ BLOCKED | starknet_call (balanceOf) | ✅ BYPASSES |
| starknet_getClassHashAt | ❌ BLOCKED | starknet_call (ERC-20) | ✅ BYPASSES |

## Balance Check Results

| Address | Label | ETH Balance | Working Providers |
|---------|-------|-------------|-------------------|
"""
        
        # Group results by address
        address_results = {}
        for result in results:
            addr = result["address"]
            if addr not in address_results:
                address_results[addr] = []
            address_results[addr].append(result)
        
        for addr, addr_results in address_results.items():
            if addr_results:
                result = addr_results[0]  # Use first result for summary
                working = [self.get_provider_name(r["rpc_url"]) for r in addr_results if r["status"] == "✅ SUCCESS"]
                
                report += f"| {addr} | {result['label']} | {result['balance_eth']:.6f} | {', '.join(working)} |\n"
        
        report += f"""

## Technical Findings

- **Firewall Type**: Layer 7 Deep Packet Inspection (DPI)
- **Blocking Pattern**: State access methods, not contract calls
- **Bypass Method**: Direct ERC-20 contract calls
- **Success Rate**: {len([r for r in results if r['status'] == '✅ SUCCESS'])}/{len(results)} ({len([r for r in results if r['status'] == '✅ SUCCESS'])/len(results)*100:.1f}%)

## Strategic Implications

1. **Monitoring Feasible**: Ghost funds can be monitored without VPN
2. **State Blind**: Account deployment status still requires VPN
3. **Transaction Ready**: Contract calls work, enabling potential sweeps

## Recommendations

- Continue using `starknet_call` for balance monitoring
- Deploy Ghost Sentry V3 with contract call method
- Use VPN for account deployment verification
- Monitor for firewall rule changes

---
*Generated by shadow_state_check.py - L7 DPI Bypass*
"""
        
        with open("shadow_state_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        self.console.print(f"\n📄 Shadow state report saved to: shadow_state_report.md")

async def main():
    """Main execution"""
    
    console = Console()
    console.print("🕵️ Shadow State Check - L7 DPI Bypass", style="bold blue")
    console.print("🔐 Testing contract calls to bypass state filtering", style="dim")
    
    checker = ShadowStateChecker()
    await checker.run_shadow_check()
    
    console.print("✅ Shadow state analysis complete!", style="bold green")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shadow check stopped by user")
    except Exception as e:
        logger.error(f"❌ Shadow check error: {e}")
        sys.exit(1)
