"""
Deprecated legacy strategy module. Use engines.influence.RefiningStrategy.
"""

from rich.console import Console

console = Console()


class RefiningStrategy:
    def __init__(self, *args, **kwargs):
        console.print("[yellow]strategy_module.py is deprecated. Use engines.influence.RefiningStrategy[/yellow]")

    def tick(self, *args, **kwargs):
        return None
