"""Reporting helpers wrapping ReportingSystem for common alerts/pulses."""

from __future__ import annotations

import asyncio
import os
from typing import Optional

from src.foundation.reporting import ReportingSystem


def _ensure_reporting(reporting: ReportingSystem | None = None) -> ReportingSystem:
    return reporting or ReportingSystem()


async def send_pulse(
    pulse_type: str,
    message: str,
    *,
    reporting: ReportingSystem | None = None,
) -> bool:
    reporting_system = _ensure_reporting(reporting)
    if not reporting_system.is_enabled():
        print(f"❌ Telegram not configured for {pulse_type}")
        return False

    await reporting_system.telegram.send_alert(pulse_type, message)
    print(f"✅ {pulse_type} pulse sent successfully")
    return True


async def send_fuel_alert(
    *,
    starknet_address: str,
    balance_display: str,
    event_time: float,
    reporting: ReportingSystem | None = None,
) -> bool:
    reporting_system = _ensure_reporting(reporting)
    if not reporting_system.is_enabled():
        return False

    await reporting_system.telegram.send_alert(
        "⛽ FUEL_INJECTED",
        f"""0.0181 ETH Found on StarkNet!
            
📍 Address: {starknet_address}
💰 Balance: {balance_display} ETH
⏰ Time: {event_time}
🎯 Action: AUTO-EXECUTE GENESIS BUNDLE

The DuggerCore-Stark Engine is now initiating autonomous deployment...""",
    )
    return True


async def send_yield_report(
    *,
    production: str,
    roi: str,
    gas_used: str,
    event_time: float,
    reporting: ReportingSystem | None = None,
) -> bool:
    reporting_system = _ensure_reporting(reporting)
    if not reporting_system.is_enabled():
        return False

    await reporting_system.telegram.send_alert(
        "⛏️ STEEL_MILL_ACTIVE",
        f"""Cycle 1 Complete!
            
🏭 Production: {production}
💰 ROI: {roi}
⛽ Gas Used: {gas_used}
⏰ Time: {event_time}
🎯 Status: CONTINUING AUTONOMOUS OPERATION

The DuggerCore-Stark Engine is now running the Iron → Steel loop autonomously...""",
    )
    return True


async def send_status_report(
    *,
    status: str,
    workflow: str,
    run_id: str,
    event_time: float,
    reporting: ReportingSystem | None = None,
) -> bool:
    reporting_system = _ensure_reporting(reporting)
    if not reporting_system.is_enabled():
        print("❌ Telegram not configured")
        return False

    message = f"""📊 GITHUB ACTIONS REPORT

🔄 Workflow: {workflow}
🆔 Run ID: {run_id}
✅ Status: {status}
⏰ Time: {event_time}

🏭 Full-Auto Mining Rig Status Report"""

    await reporting_system.telegram.send_alert("GITHUB ACTIONS REPORT", message)
    print("✅ Status report sent to Telegram")
    return True


async def test_telegram_connection(reporting: ReportingSystem | None = None) -> bool:
    reporting_system = _ensure_reporting(reporting)
    if not reporting_system.is_enabled():
        print('❌ Telegram notifications disabled')
        return False

    success = await reporting_system.telegram.send_alert(
        'TEST MESSAGE',
        'This is a test from PyPro Systems Full-Auto integration.'
    )
    if success:
        print('✅ Test message sent successfully!')
    else:
        print('❌ Test message failed')
    return success


__all__ = [
    "send_pulse",
    "send_fuel_alert",
    "send_yield_report",
    "send_status_report",
    "test_telegram_connection",
]
