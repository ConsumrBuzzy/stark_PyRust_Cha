"""Data Models for StarkNet Operations"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AccountBalance(BaseModel):
    """Account balance information"""
    address: str
    balance_eth: float
    balance_usd: float
    last_updated: datetime
    provider: str
    
class TransactionResult(BaseModel):
    """Transaction execution result"""
    hash: str
    status: str
    gas_used: int
    timestamp: datetime
    
class RPCProvider(BaseModel):
    """RPC provider information"""
    name: str
    url: str
    latency_ms: float
    success_rate: float
    methods_supported: Dict[str, bool]
