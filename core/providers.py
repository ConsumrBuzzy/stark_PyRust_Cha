#!/usr/bin/env python3
"""
RPC Diagnostic Hub - Network Sentinel for StarkNet Infrastructure
Tests provider health, latency, and method support with parallel execution
"""

import asyncio
import aiohttp
import time
import os
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

# Load environment
load_dotenv()

@dataclass
class RPCResult:
    name: str
    status: str
    latency_ms: float
    block_number: Any
    error_msg: str = ""

class NetworkSentinel:
    """Advanced RPC health monitoring with parallel testing"""
    
    def __init__(self):
        self.console = Console()
        self.endpoints = self._load_endpoints()
        self.results: List[RPCResult] = []
        
    def _load_endpoints(self) -> Dict[str, str]:
        """Load RPC endpoints from environment with fallbacks"""
        endpoints = {}
        
        # Primary endpoints from .env
        if os.getenv("STARKNET_MAINNET_URL"):
            endpoints["Alchemy"] = os.getenv("STARKNET_MAINNET_URL")
        if os.getenv("STARKNET_LAVA_URL"):
            endpoints["Lava"] = os.getenv("STARKNET_LAVA_URL")
        if os.getenv("STARKNET_1RPC_URL"):
            endpoints["1RPC"] = os.getenv("STARKNET_1RPC_URL")
        if os.getenv("STARKNET_ONFINALITY_URL"):
            endpoints["OnFinality"] = os.getenv("STARKNET_ONFINALITY_URL")
        if os.getenv("STARKNET_RPC_URL"):
            endpoints["BlastAPI"] = os.getenv("STARKNET_RPC_URL")
            
        # Additional public endpoints for testing
        endpoints.update({
            "QuickNode": "https://starknet-mainnet.quiknode.pro/your-key-here",
            "Chainbase": "https://starknet-mainnet.chainbase.online/v1/your-key-here",
            "Ankr": "https://rpc.ankr.com/starknet",
            "PublicNode": "https://starknet.publicnode.com",
            "Nownodes": "https://starknet.nownodes.io/your-key-here"
        })
        
        self.console.print(f"📡 Loaded {len(endpoints)} RPC endpoints for testing")
        return endpoints
    
    async def test_endpoint_basic(self, name: str, url: str) -> RPCResult:
        """Test basic connectivity with starknet_blockNumber"""
        payload = {
            "jsonrpc": "2.0",
            "method": "starknet_blockNumber",
            "params": [],
            "id": 1
        }
        
        start_time = time.time()
        
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:
                    latency_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        block = data.get("result", "N/A")
                        return RPCResult(
                            name=name,
                            status="✅ ONLINE",
                            latency_ms=latency_ms,
                            block_number=block
                        )
                    else:
                        return RPCResult(
                            name=name,
                            status=f"❌ {response.status}",
                            latency_ms=latency_ms,
                            block_number="N/A",
                            error_msg=f"HTTP {response.status}"
                        )
                        
        except asyncio.TimeoutError:
            return RPCResult(
                name=name,
                status="⏱️ TIMEOUT",
                latency_ms=5000,
                block_number="N/A",
                error_msg="Request timeout"
            )
        except Exception as e:
            return RPCResult(
                name=name,
                status="⚠️ ERROR",
                latency_ms=0,
                block_number="N/A",
                error_msg=str(e)[:50]
            )
    
    async def test_endpoint_advanced(self, name: str, url: str) -> Dict[str, Any]:
        """Test advanced method support (balanceOf, getClassAt, etc.)"""
        methods = {
            "blockNumber": {
                "method": "starknet_blockNumber",
                "params": []
            },
            "getNonce": {
                "method": "starknet_getNonce",
                "params": {
                    "contract_address": os.getenv("STARKNET_WALLET_ADDRESS"),
                    "block_number": "latest"
                }
            },
            "getClassHashAt": {
                "method": "starknet_getClassHashAt",
                "params": {
                    "contract_address": os.getenv("STARKNET_WALLET_ADDRESS"),
                    "block_number": "latest"
                }
            },
            "getClassAt": {
                "method": "starknet_getClassAt",
                "params": {
                    "contract_address": os.getenv("STARKNET_WALLET_ADDRESS"),
                    "block_number": "latest"
                }
            },
            "chainId": {
                "method": "starknet_chainId",
                "params": []
            },
            "syncing": {
                "method": "starknet_syncing",
                "params": []
            },
            "estimateFee": {
                "method": "starknet_estimateFee",
                "params": {
                    "request": {
                        "type": "INVOKE",
                        "max_fee": "0x0",
                        "version": "0x1",
                        "signature": [],
                        "nonce": "0x0",
                        "calldata": [
                            "0x1",
                            "0x83afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e"
                        ]
                    },
                    "block_number": "latest"
                }
            }
        }
        
        results = {}
        
        for method_name, method_data in methods.items():
            payload = {
                "jsonrpc": "2.0",
                "method": method_data["method"],
                "params": method_data["params"],
                "id": 1
            }
            
            try:
                timeout = aiohttp.ClientTimeout(total=3)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            if "result" in data:
                                result = data["result"]
                                
                                # Special handling for different result types
                                if method_name == "getClassHashAt":
                                    results[method_name] = "✅" if result and result != "0x0" else "⚪ EMPTY"
                                elif method_name == "getNonce":
                                    results[method_name] = f"✅ {result}" if result != "0x0" else "⚪ 0x0"
                                elif method_name == "chainId":
                                    results[method_name] = f"✅ {result}"
                                elif method_name == "syncing":
                                    results[method_name] = "✅ SYNCED" if not result.get("syncing") else "⚠️ SYNCING"
                                elif method_name == "estimateFee":
                                    if isinstance(result, dict) and "overall_fee" in result:
                                        results[method_name] = f"✅ {result['overall_fee']}"
                                    else:
                                        results[method_name] = "✅ COMPLEX"
                                else:
                                    results[method_name] = "✅"
                            else:
                                results[method_name] = "❌ NO_RESULT"
                        else:
                            results[method_name] = f"❌ {response.status}"
            except Exception as e:
                error_msg = str(e)[:20]
                if "timeout" in error_msg.lower():
                    results[method_name] = "⏱️ TIMEOUT"
                elif "403" in error_msg:
                    results[method_name] = "🚫 BLOCKED"
                else:
                    results[method_name] = "⚠️ ERROR"
        
        return results
    
    async def run_diagnostics(self, advanced: bool = False):
        """Run comprehensive RPC diagnostics"""
        self.console.print(Panel.fit(
            "[bold blue]🔍 NETWORK SENTINEL - RPC DIAGNOSTICS[/bold blue]\n"
            f"Testing {len(self.endpoints)} endpoints in parallel...",
            title="StarkNet Infrastructure Health"
        ))
        
        # Parallel basic testing
        start_time = time.time()
        basic_tasks = [self.test_endpoint_basic(name, url) for name, url in self.endpoints.items()]
        basic_results = await asyncio.gather(*basic_tasks, return_exceptions=True)
        
        # Filter valid results
        self.results = [r for r in basic_results if isinstance(r, RPCResult)]
        
        basic_time = time.time() - start_time
        self.console.print(f"⚡ Basic tests completed in {basic_time:.2f}s")
        
        # Advanced testing for online endpoints only
        if advanced:
            online_endpoints = {r.name: url for r in self.results if "✅" in r.status 
                              for name, url in self.endpoints.items() if name == r.name}
            
            if online_endpoints:
                self.console.print(f"🔬 Running advanced tests on {len(online_endpoints)} healthy endpoints...")
                advanced_tasks = [self.test_endpoint_advanced(name, url) 
                                for name, url in online_endpoints.items()]
                advanced_results = await asyncio.gather(*advanced_tasks, return_exceptions=True)
                
                # Merge advanced results
                for i, (name, _) in enumerate(online_endpoints.items()):
                    if i < len(advanced_results) and not isinstance(advanced_results[i], Exception):
                        # Find corresponding basic result and add advanced data
                        for result in self.results:
                            if result.name == name:
                                result.advanced_methods = advanced_results[i]
                                break
    
    def display_results(self):
        """Display diagnostic results in rich format"""
        # Basic connectivity table
        basic_table = Table(title="RPC Connectivity Test")
        basic_table.add_column("Provider", style="cyan")
        basic_table.add_column("Status", style="bold")
        basic_table.add_column("Latency", justify="right", style="green")
        basic_table.add_column("Block", justify="right", style="blue")
        basic_table.add_column("Error", style="red")
        
        online_count = 0
        for result in self.results:
            latency_str = f"{result.latency_ms:.0f}ms" if result.latency_ms > 0 else "N/A"
            block_str = str(result.block_number) if result.block_number != "N/A" else "N/A"
            
            basic_table.add_row(
                result.name,
                result.status,
                latency_str,
                block_str,
                result.error_msg
            )
            
            if "✅" in result.status:
                online_count += 1
        
        self.console.print(basic_table)
        
        # Advanced method support (if available)
        if any(hasattr(r, 'advanced_methods') for r in self.results):
            advanced_table = Table(title="Advanced Method Support Matrix")
            advanced_table.add_column("Provider", style="cyan")
            advanced_table.add_column("blockNumber", justify="center")
            advanced_table.add_column("getNonce", justify="center")
            advanced_table.add_column("getClassHashAt", justify="center")
            advanced_table.add_column("getClassAt", justify="center")
            advanced_table.add_column("chainId", justify="center")
            advanced_table.add_column("syncing", justify="center")
            advanced_table.add_column("estimateFee", justify="center")
            
            for result in self.results:
                if hasattr(result, 'advanced_methods'):
                    methods = result.advanced_methods
                    advanced_table.add_row(
                        result.name,
                        methods.get("blockNumber", "❌"),
                        methods.get("getNonce", "❌"),
                        methods.get("getClassHashAt", "❌"),
                        methods.get("getClassAt", "❌"),
                        methods.get("chainId", "❌"),
                        methods.get("syncing", "❌"),
                        methods.get("estimateFee", "❌")
                    )
            
            self.console.print(advanced_table)
            
            # Deep analysis of main wallet status
            self.analyze_main_wallet_status()
        
        # Summary panel
        success_rate = (online_count / len(self.results)) * 100 if self.results else 0
        
        summary = f"""
📊 SUMMARY
• Total Endpoints: {len(self.results)}
• Online: {online_count} ({success_rate:.1f}%)
• Offline: {len(self.results) - online_count}
• Fastest: {min((r for r in self.results if r.latency_ms > 0), key=lambda x: x.latency_ms).name if any(r.latency_ms > 0 for r in self.results) else 'N/A'}
        """.strip()
        
        self.console.print(Panel(
            summary,
            title="Network Health Overview",
            border_style="green" if success_rate > 50 else "yellow" if success_rate > 20 else "red"
        ))
        
        # Recommendations
        recommendations = []
        
        if online_count == 0:
            recommendations.append("🚨 CRITICAL: All RPC endpoints failed - check network/firewall")
        elif online_count < len(self.results) * 0.5:
            recommendations.append("⚠️ WARNING: Less than 50% endpoints online - consider backup providers")
        
        if online_count > 0:
            fastest = min((r for r in self.results if r.latency_ms > 0), key=lambda x: x.latency_ms)
            recommendations.append(f"✅ RECOMMENDED: Use {fastest.name} ({fastest.latency_ms:.0f}ms) as primary")
        
        # Missing providers
        missing_providers = []
        if not os.getenv("STARKNET_MAINNET_URL"):
            missing_providers.append("Alchemy Starknet")
        if not os.getenv("STARKNET_LAVA_URL"):
            missing_providers.append("Lava Network")
        
        if missing_providers:
            recommendations.append(f"🔧 SETUP: Add {', '.join(missing_providers)} for better reliability")
        
        if recommendations:
            self.console.print(Panel(
                "\n".join(recommendations),
                title="Recommendations",
                border_style="yellow"
            ))
    
    def analyze_main_wallet_status(self):
        """Deep analysis of main wallet deployment status"""
        
        main_wallet = os.getenv("STARKNET_WALLET_ADDRESS")
        
        self.console.print(Panel(
            f"[bold blue]🔍 MAIN WALLET DEEP ANALYSIS[/bold blue]\n"
            f"Address: {main_wallet}\n"
            f"Analyzing deployment status across providers...",
            title="Protocol-Level Verification"
        ))
        
        # Check getClassHashAt results across providers
        deployment_status = {}
        nonce_status = {}
        
        for result in self.results:
            if hasattr(result, 'advanced_methods'):
                methods = result.advanced_methods
                
                # Parse getClassHashAt result
                class_hash_result = methods.get("getClassHashAt", "")
                if "⚪ EMPTY" in class_hash_result:
                    deployment_status[result.name] = "❌ NOT DEPLOYED"
                elif "✅" in class_hash_result:
                    deployment_status[result.name] = "✅ DEPLOYED"
                else:
                    deployment_status[result.name] = "⚠️ UNKNOWN"
                
                # Parse getNonce result
                nonce_result = methods.get("getNonce", "")
                if "⚪ 0x0" in nonce_result:
                    nonce_status[result.name] = "⚪ ZERO_NONCE"
                elif "✅" in nonce_result:
                    nonce_status[result.name] = f"✅ NONCE_{nonce_result.split()[-1]}"
                else:
                    nonce_status[result.name] = "⚠️ ERROR"
        
        # Display deployment status table
        deploy_table = Table(title="Main Wallet Deployment Status")
        deploy_table.add_column("Provider", style="cyan")
        deploy_table.add_column("getClassHashAt", justify="center")
        deploy_table.add_column("getNonce", justify="center")
        deploy_table.add_column("Status", style="bold")
        
        consensus_deployed = 0
        consensus_undeployed = 0
        
        for result in self.results:
            if result.name in deployment_status:
                deploy_status = deployment_status[result.name]
                nonce_stat = nonce_status.get(result.name, "⚠️ ERROR")
                
                if "✅ DEPLOYED" in deploy_status:
                    consensus_deployed += 1
                elif "❌ NOT DEPLOYED" in deploy_status:
                    consensus_undeployed += 1
                
                deploy_table.add_row(
                    result.name,
                    deploy_status,
                    nonce_stat,
                    deploy_status
                )
        
        self.console.print(deploy_table)
        
        # Consensus analysis
        total_votes = consensus_deployed + consensus_undeployed
        if total_votes > 0:
            deployed_percentage = (consensus_deployed / total_votes) * 100
            
            if deployed_percentage >= 75:
                consensus = "✅ CONSENSUS: DEPLOYED"
                border_style = "green"
                implication = "Account is deployed and ready for transactions"
            elif deployed_percentage <= 25:
                consensus = "❌ CONSENSUS: NOT DEPLOYED"
                border_style = "red"
                implication = "Account requires deployment before transactions"
            else:
                consensus = "⚠️ CONSENSUS: MIXED SIGNALS"
                border_style = "yellow"
                implication = "Network state inconsistent - may be syncing"
        else:
            consensus = "❓ NO CONSENSUS"
            border_style = "dim"
            implication = "Unable to determine deployment status"
        
        self.console.print(Panel(
            f"[bold]{consensus}[/bold]\n\n"
            f"Deployed Votes: {consensus_deployed}/{total_votes}\n"
            f"Undeployed Votes: {consensus_undeployed}/{total_votes}\n\n"
            f"Implication: {implication}",
            title="Deployment Consensus Analysis",
            border_style=border_style
        ))
        
        # Log results to audit report
        self.update_audit_report(deployment_status, nonce_status, consensus)
    
    def update_audit_report(self, deployment_status: Dict, nonce_status: Dict, consensus: str):
        """Update audit report with deep diagnostic results"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_lines = [
            f"# StarkNet Deep Diagnostic Report",
            "",
            f"**Timestamp**: {timestamp}",
            "**Method**: Advanced RPC Method Surface Mapping",
            "**Target**: Main Wallet Deployment Analysis",
            "",
            "## Method Support Matrix",
            "",
            "| Provider | getClassHashAt | getNonce | Chain Status |",
            "|----------|---------------|----------|--------------|"
        ]
        
        for result in self.results:
            if result.name in deployment_status:
                report_lines.append(f"| {result.name} | {deployment_status[result.name]} | {nonce_status.get(result.name, '⚠️ ERROR')} | {'✅ ONLINE' if '✅' in result.status else '❌ OFFLINE'} |")
        
        report_lines.extend([
            "",
            "## Deployment Consensus Analysis",
            "",
            f"**Result**: {consensus}",
            "",
            "**Implications**:",
            "- If NOT DEPLOYED: Account initialization required before any transactions",
            "- If DEPLOYED: Ready for transaction execution and fund sweeps",
            "- If MIXED: Network may be syncing or experiencing inconsistencies",
            "",
            "## Strategic Recommendations",
            "",
            "- **Force Deployment**: Consider using starkli deploy if consensus shows NOT DEPLOYED",
            "- **Fund Recovery**: Ghost funds can only be swept to a deployed account",
            "- **Network Health**: Monitor for consensus changes over time",
            "",
            "## Technical Notes",
            "",
            "- `getClassHashAt` returns 0x0 for undeployed accounts",
            "- `getNonce` returns 0x0 for accounts without transaction history",
            "- Consensus across multiple providers provides ground truth",
            "",
            "---",
            "*Generated by rpc_diagnostic_hub.py - Deep Diagnostics*"
        ])
        
        report_content = "\n".join(report_lines)
        
        with open("starknet_deep_diagnostic_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        self.console.print(f"\n📄 Deep diagnostic report saved to: starknet_deep_diagnostic_report.md")
    
    def get_signup_urls(self):
        """Provide signup URLs for missing premium providers"""
        urls = {
            "Alchemy Starknet": "https://www.alchemy.com/starknet",
            "Lava Network": "https://www.lavanet.xyz/",
            "Infura Starknet": "https://www.infura.io/product/starknet",
            "QuickNode": "https://www.quicknode.com/blockchain/starknet",
            "Chainbase": "https://chainbase.com/starknet"
        }
        
        self.console.print(Panel(
            "\n".join([f"• {name}: {url}" for name, url in urls.items()]),
            title="Provider Signup URLs",
            border_style="blue"
        ))

async def main():
    """Main execution"""
    console = Console()
    console.print("🚀 Network Sentinel - RPC Diagnostic Hub", style="bold blue")
    
    sentinel = NetworkSentinel()
    
    # Run diagnostics
    await sentinel.run_diagnostics(advanced=True)
    
    # Display results
    sentinel.display_results()
    
    # Show signup URLs for missing providers
    sentinel.get_signup_urls()
    
    console.print("\n✅ Diagnostic complete. Use results to optimize RPC configuration.", style="bold green")

if __name__ == "__main__":
    asyncio.run(main())
