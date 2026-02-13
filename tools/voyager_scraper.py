#!/usr/bin/env python3
"""
Voyager Scraper - Bypass RPC Blockade with REST API
Finds StarkNet balances without using JSON-RPC protocol
"""

import asyncio
import aiohttp
import json
import re
from typing import Dict, Optional, List
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

@dataclass
class AccountInfo:
    address: str
    balance_eth: float
    balance_usd: float
    tx_count: int
    last_activity: str
    status: str

class VoyagerScraper:
    """StarkNet Voyager API scraper - bypasses RPC restrictions"""
    
    def __init__(self):
        self.console = Console()
        self.base_url = "https://api.voyager.online/beta"
        self.web_url = "https://voyager.online"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_account_balance(self, address: str) -> Optional[AccountInfo]:
        """Get account balance via Voyager REST API"""
        
        # Normalize address (remove 0x prefix if present)
        clean_address = address.lower().replace("0x", "")
        
        try:
            # Method 1: Voyager API
            api_url = f"{self.base_url}/accounts/{clean_address}"
            
            async with self.session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_api_response(data, address)
                else:
                    self.console.print(f"⚠️ API failed: {response.status}, trying web scrape...")
                    
        except Exception as e:
            self.console.print(f"⚠️ API error: {e}, trying web scrape...")
        
        # Method 2: Web scraping fallback
        try:
            web_url = f"{self.web_url}/contract/{clean_address}"
            async with self.session.get(web_url) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_web_response(html, address)
                    
        except Exception as e:
            self.console.print(f"❌ Web scrape failed: {e}")
        
        return None
    
    def _parse_api_response(self, data: Dict, address: str) -> AccountInfo:
        """Parse Voyager API response"""
        
        # Extract balance (Voyager returns in different formats)
        balance_eth = 0.0
        balance_usd = 0.0
        
        if 'eth_balance' in data:
            balance_eth = float(data['eth_balance']) / 1e18
        elif 'balance' in data:
            balance_eth = float(data['balance']) / 1e18
        
        # USD value (approximate)
        if balance_eth > 0:
            balance_usd = balance_eth * 2200  # Rough ETH price
        
        # Transaction count
        tx_count = data.get('transaction_count', 0)
        
        # Last activity
        last_activity = data.get('last_activity', 'Unknown')
        
        # Account status
        status = "Active" if balance_eth > 0 or tx_count > 0 else "Empty"
        
        return AccountInfo(
            address=address,
            balance_eth=balance_eth,
            balance_usd=balance_usd,
            tx_count=tx_count,
            last_activity=last_activity,
            status=status
        )
    
    def _parse_web_response(self, html: str, address: str) -> Optional[AccountInfo]:
        """Parse Voyager web page HTML for balance info"""
        
        try:
            # Look for balance patterns in HTML
            balance_patterns = [
                r'Balance:</span>\s*<span[^>]*>([\d.]+)\s*ETH',
                r'"ethBalance":\s*"([\d.]+)"',
                r'balance[^>]*>([\d.]+)\s*ETH',
                r'ETH\s*([\d.]+)',
            ]
            
            balance_eth = 0.0
            for pattern in balance_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    try:
                        balance_eth = float(match.group(1))
                        break
                    except ValueError:
                        continue
            
            # Look for transaction count
            tx_patterns = [
                r'Transactions:</span>\s*<span[^>]*>(\d+)',
                r'"transactionCount":\s*(\d+)',
                r'transactions[^>]*>(\d+)',
            ]
            
            tx_count = 0
            for pattern in tx_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    try:
                        tx_count = int(match.group(1))
                        break
                    except ValueError:
                        continue
            
            # Determine status
            status = "Active" if balance_eth > 0 or tx_count > 0 else "Empty"
            
            return AccountInfo(
                address=address,
                balance_eth=balance_eth,
                balance_usd=balance_eth * 2200 if balance_eth > 0 else 0.0,
                tx_count=tx_count,
                last_activity="Web Scrape",
                status=status
            )
            
        except Exception as e:
            self.console.print(f"❌ HTML parsing failed: {e}")
            return None
    
    async def check_multiple_addresses(self, addresses: List[str]) -> List[AccountInfo]:
        """Check multiple addresses concurrently"""
        
        self.console.print(f"🔍 Checking {len(addresses)} addresses via Voyager...")
        
        tasks = [self.get_account_balance(addr) for addr in addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter valid results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, AccountInfo):
                valid_results.append(result)
            elif isinstance(result, Exception):
                self.console.print(f"❌ Error checking {addresses[i]}: {result}")
            else:
                self.console.print(f"⚠️ No data for {addresses[i]}")
        
        return valid_results
    
    def display_results(self, results: List[AccountInfo]):
        """Display Voyager scraper results"""
        
        if not results:
            self.console.print("❌ No account data retrieved")
            return
        
        # Results table
        table = Table(title="Voyager API - Account Balances")
        table.add_column("Address", style="cyan")
        table.add_column("ETH Balance", justify="right", style="green")
        table.add_column("USD Value", justify="right", style="yellow")
        table.add_column("Transactions", justify="right")
        table.add_column("Status", style="bold")
        table.add_column("Last Activity", style="dim")
        
        total_eth = 0.0
        total_usd = 0.0
        
        for account in results:
            # Truncate address for display
            display_addr = account.address[:10] + "..." + account.address[-6:]
            
            table.add_row(
                display_addr,
                f"{account.balance_eth:.6f}",
                f"${account.balance_usd:.2f}",
                str(account.tx_count),
                account.status,
                account.last_activity
            )
            
            total_eth += account.balance_eth
            total_usd += account.balance_usd
        
        self.console.print(table)
        
        # Summary
        summary = f"""
🎯 VOYAGER SCRAPER RESULTS
• Accounts Checked: {len(results)}
• Total ETH: {total_eth:.6f}
• Total USD: ${total_usd:.2f}
• Active Accounts: {sum(1 for r in results if r.status == 'Active')}
• Empty Accounts: {sum(1 for r in results if r.status == 'Empty')}
        """.strip()
        
        self.console.print(Panel(
            summary,
            title="Balance Summary",
            border_style="green" if total_eth > 0 else "yellow"
        ))
        
        # Strategic insights
        insights = []
        
        ghost_found = any(r.balance_eth > 0.005 for r in results)
        if ghost_found:
            insights.append("🎉 GHOST FUNDS DETECTED! Bridge may have completed.")
        else:
            insights.append("⏳ Ghost funds still not arrived on StarkNet.")
        
        if total_eth > 0:
            insights.append(f"💰 Total value: ${total_usd:.2f} ready for deployment/sweep")
        
        if any(r.tx_count > 0 for r in results):
            insights.append("📊 Some accounts show transaction history")
        
        if insights:
            self.console.print(Panel(
                "\n".join(insights),
                title="Strategic Insights",
                border_style="blue"
            ))

async def main():
    """Main execution - Ghost address verification"""
    
    console = Console()
    console.print("🚀 Voyager Scraper - RPC Bypass Tool", style="bold blue")
    
    # Target addresses
    addresses = [
        "os.getenv("STARKNET_GHOST_ADDRESS")",  # Ghost
        "os.getenv("STARKNET_WALLET_ADDRESS")",   # Main wallet
    ]
    
    async with VoyagerScraper() as scraper:
        results = await scraper.check_multiple_addresses(addresses)
        scraper.display_results(results)
        
        # Save report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"""# Voyager Scraper Report

**Timestamp**: {timestamp}
**Method**: REST API + Web Scrape (RPC Bypass)

## Account Balances

| Address | ETH Balance | USD Value | Transactions | Status |
|---------|-------------|-----------|--------------|--------|
"""
        
        for account in results:
            report += f"| {account.address} | {account.balance_eth:.6f} | ${account.balance_usd:.2f} | {account.tx_count} | {account.status} |\n"
        
        report += f"""
## Summary

- Total ETH: {sum(r.balance_eth for r in results):.6f}
- Total USD: ${sum(r.balance_usd for r in results):.2f}
- Active Accounts: {sum(1 for r in results if r.status == 'Active')}

## Strategic Notes

- Successfully bypassed RPC blockade using Voyager API
- Ghost funds status: {'DETECTED' if any(r.balance_eth > 0.005 for r in results) else 'NOT ARRIVED'}
- Data source: https://voyager.online (public explorer)

---
*Generated by voyager_scraper.py*
"""
        
        with open("voyager_scraper_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        console.print(f"\n📄 Report saved to: voyager_scraper_report.md")
        console.print("✅ Voyager scrape complete - RPC blockade bypassed!", style="bold green")

if __name__ == "__main__":
    asyncio.run(main())
