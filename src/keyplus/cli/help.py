"""Help presentation for the interactive KeyPlus CLI."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def print_help(console: Console) -> None:
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("Command", style="bold magenta", width=24)
    table.add_column("Description")
    for command, description in (
        ("list", "List vault entries"),
        ("view <id>", "View an entry by full ID or unambiguous ID prefix"),
        ("add", "Prompt for and add a credential"),
        ("edit <id>", "Prompt for changes to an entry"),
        ("delete <id>", "Delete an entry after confirmation"),
        ("backup", "Create an encrypted vault backup"),
        ("restore <path>", "Validate and restore an encrypted vault backup"),
        ("lock", "Lock and reauthenticate this session"),
        ("help", "Show this help"),
        ("exit / quit", "Lock and close KeyPlus"),
    ):
        table.add_row(command, description)
    console.print(
        Panel(table, title="Available Commands", border_style="blue", expand=False)
    )
