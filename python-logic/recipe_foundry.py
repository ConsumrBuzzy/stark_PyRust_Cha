"""
Deprecated legacy derivation helper. Use engines.search.AddressSearchEngine via unlock_derivation.py.
"""

from rich.console import Console

console = Console()


def find_recovery_recipe():
    console.print("[yellow]recipe_foundry.py is deprecated. Use unlock_derivation.py (AddressSearchEngine).[/yellow]")
    return None


if __name__ == "__main__":
    find_recovery_recipe()
