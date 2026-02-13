"""
PyPro Systems - Etherscan API Client
Comprehensive blockchain analytics and fund tracking system
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class TransactionInfo:
    """Transaction information structure"""
    tx_hash: str
    block_number: int
    timestamp: datetime
    from_address: str
    to_address: str
    value: float  # ETH
    gas_used: int
    gas_price: int
    status: int  # 1 = success, 0 = failure
    method: Optional[str] = None
    confirmations: int = 0

@dataclass
class BalanceInfo:
    """Balance information structure"""
    address: str
    balance_eth: float
    balance_usd: float
    last_updated: datetime
    token_balances: Dict[str, float] = None

class EtherscanClient:
    """Enhanced Etherscan API client with caching and analytics"""
    
    def __init__(self, network: str = "base", api_key: Optional[str] = None):
        self.network = network
        self.api_key = api_key or "YourApiKeyToken"
        
        # API endpoints for different networks
        self.endpoints = {
            "base": "https://api.basescan.org/api",
            "ethereum": "https://api.etherscan.io/api", 
            "arbitrum": "https://api.arbiscan.io/api",
            "optimism": "https://api-optimistic.etherscan.io/api"
        }
        
        self.base_url = self.endpoints.get(network, self.endpoints["base"])
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Cache for balance and transaction data
        self.balance_cache: Dict[str, BalanceInfo] = {}
        self.tx_cache: Dict[str, List[TransactionInfo]] = {}
        self.cache_ttl = timedelta(minutes=5)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "PyPro-Etherscan-Client/1.0"}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with error handling"""
        if not self.session:
            raise RuntimeError("Client not initialized - use async context manager")
        
        try:
            params.setdefault("apikey", self.api_key)
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(f"HTTP {response.status}: {response.text}")
                
                data = await response.json()
                
                if data.get("status") == "0":
                    error_msg = data.get("result", "Unknown error")
                    if "Invalid API Key" in error_msg:
                        logger.warning("Using free API endpoint (rate limited)")
                        # Retry without API key for free tier
                        params_no_key = {k: v for k, v in params.items() if k != "apikey"}
                        async with self.session.get(self.base_url, params=params_no_key) as retry_response:
                            data = await retry_response.json()
                    else:
                        raise RuntimeError(f"API Error: {error_msg}")
                
                return data
                
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    async def get_balance(self, address: str, force_refresh: bool = False) -> BalanceInfo:
        """Get ETH balance with USD conversion and caching"""
        # Check cache first
        if not force_refresh and address in self.balance_cache:
            cached = self.balance_cache[address]
            if datetime.now() - cached.last_updated < self.cache_ttl:
                logger.debug(f"Using cached balance for {address}")
                return cached
        
        try:
            params = {
                "module": "account",
                "action": "balance",
                "address": address,
                "tag": "latest"
            }
            
            data = await self._make_request(params)
            balance_wei = int(data["result"])
            balance_eth = balance_wei / 1e18
            
            # Get ETH price for USD conversion
            eth_price = await self.get_eth_price()
            balance_usd = balance_eth * eth_price
            
            balance_info = BalanceInfo(
                address=address,
                balance_eth=balance_eth,
                balance_usd=balance_usd,
                last_updated=datetime.now()
            )
            
            # Update cache
            self.balance_cache[address] = balance_info
            
            logger.info(f"Balance for {address}: {balance_eth:.6f} ETH (${balance_usd:.2f})")
            return balance_info
            
        except Exception as e:
            logger.error(f"Failed to get balance for {address}: {e}")
            raise
    
    async def get_eth_price(self) -> float:
        """Get current ETH price in USD"""
        try:
            params = {
                "module": "stats",
                "action": "ethprice"
            }
            
            data = await self._make_request(params)
            eth_price = float(data["result"]["ethusd"])
            return eth_price
            
        except Exception as e:
            logger.warning(f"Failed to get ETH price: {e}, using fallback")
            return 3500.0  # Fallback price
    
    async def get_transactions(self, address: str, limit: int = 100) -> List[TransactionInfo]:
        """Get transaction history for address"""
        try:
            params = {
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "sort": "desc",
                "limit": limit
            }
            
            data = await self._make_request(params)
            transactions = []
            
            for tx_data in data["result"]:
                tx_info = TransactionInfo(
                    tx_hash=tx_data["hash"],
                    block_number=int(tx_data["blockNumber"]),
                    timestamp=datetime.fromtimestamp(int(tx_data["timeStamp"])),
                    from_address=tx_data["from"],
                    to_address=tx_data["to"],
                    value=float(tx_data["value"]) / 1e18,
                    gas_used=int(tx_data["gasUsed"]),
                    gas_price=int(tx_data["gasPrice"]),
                    status=int(tx_data["isError"]) == 0,
                    confirmations=int(tx_data["confirmations"])
                )
                transactions.append(tx_info)
            
            # Update cache
            self.tx_cache[address] = transactions
            
            logger.info(f"Retrieved {len(transactions)} transactions for {address}")
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to get transactions for {address}: {e}")
            raise
    
    async def get_bridge_transactions(self, address: str, bridge_address: str) -> List[TransactionInfo]:
        """Filter transactions to/from specific bridge contract"""
        all_txs = await self.get_transactions(address)
        
        bridge_txs = [
            tx for tx in all_txs
            if (tx.to_address.lower() == bridge_address.lower() or 
                tx.from_address.lower() == bridge_address.lower())
        ]
        
        logger.info(f"Found {len(bridge_txs)} bridge transactions")
        return bridge_txs
    
    async def track_fund_flow(self, addresses: List[str]) -> Dict[str, Any]:
        """Comprehensive fund flow analysis for multiple addresses"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "network": self.network,
            "addresses": {},
            "total_balance_eth": 0.0,
            "total_balance_usd": 0.0,
            "recent_transactions": []
        }
        
        # Get balances for all addresses
        for address in addresses:
            try:
                balance = await self.get_balance(address)
                results["addresses"][address] = {
                    "balance_eth": balance.balance_eth,
                    "balance_usd": balance.balance_usd,
                    "last_updated": balance.last_updated.isoformat()
                }
                results["total_balance_eth"] += balance.balance_eth
                results["total_balance_usd"] += balance.balance_usd
                
            except Exception as e:
                logger.error(f"Failed to get balance for {address}: {e}")
                results["addresses"][address] = {
                    "error": str(e)
                }
        
        # Get recent transactions for all addresses
        for address in addresses:
            try:
                txs = await self.get_transactions(address, limit=10)
                results["recent_transactions"].extend([
                    {
                        "address": address,
                        "tx_hash": tx.tx_hash,
                        "value_eth": tx.value,
                        "timestamp": tx.timestamp.isoformat(),
                        "status": "success" if tx.status else "failed"
                    }
                    for tx in txs
                ])
            except Exception as e:
                logger.error(f"Failed to get transactions for {address}: {e}")
        
        # Sort transactions by timestamp
        results["recent_transactions"].sort(
            key=lambda x: x["timestamp"], 
            reverse=True
        )
        
        return results
    
    async def monitor_bridge_status(self, from_address: str, to_address: str, 
                                 bridge_address: str, timeout_minutes: int = 30) -> Dict[str, Any]:
        """Monitor bridge transaction status"""
        start_time = datetime.now()
        timeout = timedelta(minutes=timeout_minutes)
        
        # Get recent bridge transactions
        bridge_txs = await self.get_bridge_transactions(from_address, bridge_address)
        
        if not bridge_txs:
            return {
                "status": "no_transactions",
                "message": "No bridge transactions found",
                "monitoring_time": (datetime.now() - start_time).total_seconds()
            }
        
        # Check most recent transaction
        latest_tx = bridge_txs[0]
        
        # Get current balances
        from_balance = await self.get_balance(from_address)
        to_balance = await self.get_balance(to_address)
        
        result = {
            "status": "monitoring",
            "latest_tx": {
                "hash": latest_tx.tx_hash,
                "timestamp": latest_tx.timestamp.isoformat(),
                "value_eth": latest_tx.value,
                "confirmations": latest_tx.confirmations,
                "success": latest_tx.status
            },
            "balances": {
                "from_address": {
                    "address": from_address,
                    "balance_eth": from_balance.balance_eth,
                    "balance_usd": from_balance.balance_usd
                },
                "to_address": {
                    "address": to_address, 
                    "balance_eth": to_balance.balance_eth,
                    "balance_usd": to_balance.balance_usd
                }
            },
            "monitoring_time": (datetime.now() - start_time).total_seconds()
        }
        
        # Determine if bridge completed
        if latest_tx.status and latest_tx.confirmations > 12:
            result["status"] = "completed"
        elif datetime.now() - latest_tx.timestamp > timeout:
            result["status"] = "timeout"
        
        return result
    
    async def generate_fund_report(self, addresses: List[str], 
                                 output_file: Optional[str] = None) -> str:
        """Generate comprehensive fund report"""
        fund_flow = await self.track_fund_flow(addresses)
        
        report = f"""# Fund Tracking Report

**Generated**: {fund_flow['timestamp']}  
**Network**: {fund_flow['network'].upper()}  
**Addresses Monitored**: {len(addresses)}

## Summary

| Metric | Value |
|--------|-------|
| Total ETH Balance | {fund_flow['total_balance_eth']:.6f} ETH |
| Total USD Value | ${fund_flow['total_balance_usd']:.2f} |
| Addresses with Funds | {sum(1 for addr_data in fund_flow['addresses'].values() if 'balance_eth' in addr_data and addr_data['balance_eth'] > 0)} |

## Address Breakdown

"""
        
        for addr, data in fund_flow['addresses'].items():
            if 'balance_eth' in data:
                report += f"### {addr[:10]}...{addr[-8:]}\n"
                report += f"- **Balance**: {data['balance_eth']:.6f} ETH (${data['balance_usd']:.2f})\n"
                report += f"- **Last Updated**: {data['last_updated']}\n\n"
            else:
                report += f"### {addr[:10]}...{addr[-8:]}\n"
                report += f"- **Error**: {data['error']}\n\n"
        
        if fund_flow['recent_transactions']:
            report += "## Recent Transactions\n\n"
            for tx in fund_flow['recent_transactions'][:10]:
                report += f"- **{tx['timestamp']}**: {tx['address'][:10]}...{tx['address'][-8:]} "
                report += f"sent {tx['value_eth']:.6f} ETH ({tx['status']}) "
                report += f"[{tx['tx_hash'][:10]}...{tx['tx_hash'][-8:]}]\n"
        
        # Save report if requested
        if output_file:
            report_path = Path(output_file)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report)
            logger.info(f"Report saved to {output_file}")
        
        return report
    
    def clear_cache(self):
        """Clear all cached data"""
        self.balance_cache.clear()
        self.tx_cache.clear()
        logger.info("Cache cleared")

class FundTracker:
    """High-level fund tracking and monitoring system"""
    
    def __init__(self, network: str = "base"):
        self.network = network
        self.etherscan = EtherscanClient(network)
    
    async def track_missing_funds(self, expected_amount: float, 
                                 addresses: List[str]) -> Dict[str, Any]:
        """Track down missing funds across multiple addresses"""
        analysis = {
            "expected_amount_eth": expected_amount,
            "expected_amount_usd": expected_amount * 3500,  # Approximate
            "addresses_checked": len(addresses),
            "total_found_eth": 0.0,
            "total_found_usd": 0.0,
            "missing_eth": expected_amount,
            "missing_usd": expected_amount * 3500,
            "address_breakdown": {},
            "recommendations": []
        }
        
        async with self.etherscan:
            for address in addresses:
                try:
                    balance_info = await self.etherscan.get_balance(address)
                    
                    analysis["address_breakdown"][address] = {
                        "balance_eth": balance_info.balance_eth,
                        "balance_usd": balance_info.balance_usd,
                        "last_updated": balance_info.last_updated.isoformat()
                    }
                    
                    analysis["total_found_eth"] += balance_info.balance_eth
                    analysis["total_found_usd"] += balance_info.balance_usd
                    
                except Exception as e:
                    analysis["address_breakdown"][address] = {
                        "error": str(e)
                    }
            
            # Calculate missing amounts
            analysis["missing_eth"] = max(0, expected_amount - analysis["total_found_eth"])
            analysis["missing_usd"] = max(0, analysis["expected_amount_usd"] - analysis["total_found_usd"])
            
            # Generate recommendations
            if analysis["missing_eth"] > 0:
                analysis["recommendations"].append(
                    f"Missing {analysis['missing_eth']:.6f} ETH (${analysis['missing_usd']:.2f})"
                )
                
                # Check for recent transactions
                for address in addresses:
                    try:
                        txs = await self.etherscan.get_transactions(address, limit=5)
                        for tx in txs:
                            if tx.value > 0 and tx.status:
                                analysis["recommendations"].append(
                                    f"Recent outflow: {tx.value:.6f} ETH from {address[:10]}... "
                                    f"on {tx.timestamp.strftime('%Y-%m-%d %H:%M')}"
                                )
                    except Exception:
                        pass
            else:
                analysis["recommendations"].append("All expected funds accounted for")
        
        return analysis
    
    async def monitor_bridge_recovery(self, phantom_address: str, 
                                    starknet_address: str,
                                    bridge_address: str) -> Dict[str, Any]:
        """Monitor bridge recovery process"""
        async with self.etherscan:
            # Get current status
            status = await self.etherscan.monitor_bridge_status(
                phantom_address, starknet_address, bridge_address
            )
            
            # Get detailed transaction history
            try:
                bridge_txs = await self.etherscan.get_bridge_transactions(
                    phantom_address, bridge_address
                )
                
                status["bridge_history"] = [
                    {
                        "hash": tx.tx_hash,
                        "timestamp": tx.timestamp.isoformat(),
                        "value": tx.value,
                        "confirmations": tx.confirmations,
                        "success": tx.status
                    }
                    for tx in bridge_txs
                ]
                
            except Exception as e:
                status["bridge_history_error"] = str(e)
            
            return status

# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Initialize tracker
        tracker = FundTracker(network="base")
        
        # Your addresses from the audit
        addresses = [
            "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9",
            "0x000000000000000000000000ff01e0776369ce51debb16dfb70f23c16d875463",
            "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
        ]
        
        # Track missing funds (you expected $63 worth ~0.018 ETH)
        analysis = await tracker.track_missing_funds(0.018, addresses)
        
        print("=== Fund Analysis ===")
        print(f"Expected: {analysis['expected_amount_eth']:.6f} ETH (${analysis['expected_amount_usd']:.2f})")
        print(f"Found: {analysis['total_found_eth']:.6f} ETH (${analysis['total_found_usd']:.2f})")
        print(f"Missing: {analysis['missing_eth']:.6f} ETH (${analysis['missing_usd']:.2f})")
        
        print("\n=== Address Breakdown ===")
        for addr, data in analysis["address_breakdown"].items():
            if "balance_eth" in data:
                print(f"{addr[:10]}...{addr[-8:]}: {data['balance_eth']:.6f} ETH (${data['balance_usd']:.2f})")
            else:
                print(f"{addr[:10]}...{addr[-8:]}: ERROR - {data['error']}")
        
        print("\n=== Recommendations ===")
        for rec in analysis["recommendations"]:
            print(f"- {rec}")
    
    asyncio.run(main())
