"""
Core UI Module - PhantomArbiter Pattern Implementation
Provides professional dashboard and console interfaces
"""

from .rich_dashboard import StarkNetDashboard, get_dashboard, run_dashboard

__all__ = [
    "StarkNetDashboard",
    "get_dashboard",
    "run_dashboard"
]
