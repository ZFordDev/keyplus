# src/cli/help.py
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def print_help():
    # Create a stylized table for the commands
    table = Table(
        show_header=True, 
        header_style="bold cyan", 
        border_style="dim",
        box=None, # Clean, borderless table look inside the panel
        padding=(0, 2)
    )
    
    table.add_column("Command", style="bold magenta", width=35)
    table.add_column("Description", style="white")

    # Add command rows with argument styling
    table.add_row("list", "List all entries in your vault")
    table.add_row("view [dim]<name>[/dim]", "View specific entry details")
    table.add_row("add [dim]<name> <domain> <password>[/dim]", "Add a brand new entry to the vault")
    table.add_row("edit [dim]<name>[/dim]", "Modify fields of an existing entry")
    table.add_row("history [dim]<name>[/dim]", "Show password modification history")
    table.add_row("help", "Show this help menu")
    table.add_row("exit / quit", "Securely close KeyPlus")

    # Wrap the table in a clean Panel block
    console.print(
        Panel(
            table,
            title="💡 [bold white]Available Commands[/bold white]",
            border_style="blue",
            expand=False
        )
    )