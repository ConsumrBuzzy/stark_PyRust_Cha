"""
Deprecated legacy dashboard. Use src/core/ui/dashboard.py.
"""

from rich.console import Console

console = Console()


class Dashboard:
    def __init__(self, *args, **kwargs):
        console.print("[yellow]Dashboard is deprecated. Use src/core/ui/dashboard.py[/yellow]")

    def log(self, *args, **kwargs):
        pass

    def update_roi(self, *args, **kwargs):
        pass

    def render(self, *args, **kwargs):
        return None
