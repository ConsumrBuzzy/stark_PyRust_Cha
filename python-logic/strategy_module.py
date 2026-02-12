from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseStrategy(ABC):
    """
    Abstract Base Class for stark_PyRust_Chain strategies.
    
    Strategies define the 'Business Logic' of the supply chain.
    The Rust core handles the execution and data fetching.
    """
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def evaluate(self, state: Dict[str, Any]) -> str:
        """
        Evaluate the current state and return an action.
        
        State is a dictionary of game data (Resources, Market Prices, etc.) provided by Rust.
        Returns a string command or JSON payload for the Rust engine to execute.
        """
        pass

class SimpleRefineryStrategy(BaseStrategy):
    """
    A basic strategy that refines resources if profitable.
    """
    
    def evaluate(self, state: Dict[str, Any]) -> str:
        # Example logic
        iron_price = state.get("prices", {}).get("Iron", 0)
        steel_price = state.get("prices", {}).get("Steel", 0)
        
        # Simple margin check
        if steel_price > (iron_price * 1.5):
            return "ACTION: REFINE_STEEL"
        
        return "ACTION: HOLD"
