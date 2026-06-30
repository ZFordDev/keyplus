# src/cli/cli_main.py
import sys
from logic import vault, history, session, auth
from .help import print_help
from getpass import getpass

# Premium UI Libraries
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

# Initialize Rich Console
console = Console()

def print_banner():
    """Prints a stylish, modern application header."""
    console.print("\n")
    console.print(
        Panel(
            Text("🔑 KeyPlus — Secure Vault Client", justify="center", style="bold cyan"),
            subtitle="[dim]Runtime Mode Active[/dim]",
            subtitle_align="right",
            border_style="blue",
            expand=False
        )
    )

def cli_main():
    # Detect the GUI flag before triggering terminal authentication strings
    if "--gui" in sys.argv:
        from ui.gui.gui_main import launch_gui
        launch_gui()
        return

    print_banner()

    # -------------------------
    # Authentication UI
    # -------------------------
    if not auth.password_exists():
        console.print(Panel("[yellow]⚠️  No Master Password detected. Let's secure your vault.[/yellow]", border_style="yellow"))
        pw1 = getpass("New password: ").strip()
        pw2 = getpass("Confirm password: ").strip()

        if pw1 != pw2:
            console.print("[bold red]❌ Passwords do not match. Exiting.[/bold red]")
            return

        auth.create_password(pw1)
        session.set_session_key(pw1)
        console.print("[bold green]✨ Password created successfully. KeyPlus unlocked, Welcome![/bold green]\n")

    else:
        while True:
            master = getpass("🔒 Please enter master password: ").strip()
            if auth.verify_password(master):
                session.set_session_key(master)
                console.print("[bold green]🔓 KeyPlus unlocked, Welcome![/bold green]\n")
                break
            else:
                console.print("[bold red]❌ Incorrect password. Try again.[/bold red]")

    # -------------------------
    # Interactive Shell Setup
    # -------------------------
    # Auto-completion setup for commands
    commands = ["help", "list", "view", "add", "edit", "history", "exit", "quit"]
    completer = WordCompleter(commands, ignore_case=True)
    
    # Custom styling for the Prompt Toolkit input line
    prompt_style = Style.from_dict({
        'prompt': 'bold magenta',
    })
    
    pt_session = PromptSession(completer=completer, style=prompt_style)

    while True:
        try:
            # Enhanced interactive input prompt
            line = pt_session.prompt("KeyPlus ❯ ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]👋 Exiting KeyPlus safely.[/yellow]")
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        # Exit
        if cmd in ("exit", "quit"):
            console.print("[yellow]Goodbye![/yellow]")
            break

        # Help
        if cmd == "help":
            print_help()  # Pro-tip: Refactor print_help to use Rich Tables/Panels later!
            continue

        # List entries
        if cmd == "list":
            entries = vault.list_entries()
            if not entries:
                console.print("[dim italic]No entries found in your vault.[/dim italic]")
            else:
                table = Table(title="Vault Entries", show_header=True, header_style="bold magenta", border_style="dim")
                table.add_column("Index", justify="right", style="dim", width=6)
                table.add_column("Account Name", style="cyan")
                
                for idx, e in enumerate(entries, start=1):
                    table.add_row(str(idx), e['name'])
                
                console.print(table)
            continue

        # View entry
        if cmd == "view":
            if not args:
                console.print("[bold red]Usage:[/bold red] view <name>")
                continue

            entry = vault.get_entry(args[0])
            if not entry:
                console.print(f"[bold red]❌ Entry '{args[0]}' not found.[/bold red]")
            else:
                grid = Table.grid(expand=True)
                grid.add_column(style="bold cyan", width=12)
                grid.add_column(style="green")
                grid.add_row("Name:", entry['name'])
                grid.add_row("Domain:", entry['domain'])
                grid.add_row("Password:", f"[on black white]{entry['password']}[/on black white]") # Boxed styling for security visibility
                
                console.print(Panel(grid, title=f"🔒 {entry['name']}", border_style="green", expand=False))
            continue

        # Add entry
        if cmd == "add":
            if len(args) < 3:
                console.print("[bold red]Usage:[/bold red] add <name> <domain> <password>")
                continue

            name, domain, password = args[0], args[1], args[2]
            entry = vault.add_entry(name, domain, password)
            console.print(f"[bold green]➕ Added entry:[/bold green] [cyan]{entry['name']}[/cyan]")
            continue

        # Edit entry
        if cmd == "edit":
            if len(args) < 1:
                console.print("[bold red]Usage:[/bold red] edit <name>")
                continue

            identifier = args[0]
            entry = vault.get_entry(identifier)
            if not entry:
                console.print(f"[bold red]❌ Entry '{identifier}' not found.[/bold red]")
                continue

            console.print("[dim]Leave fields blank to keep current values.[/dim]")
            new_domain = input(f"Domain [{entry['domain']}]: ").strip() or entry["domain"]
            new_password = getpass(f"Password [{entry['password']}]: ").strip() or entry["password"]

            updated = vault.edit_entry(identifier, domain=new_domain, password=new_password)
            console.print(f"[bold green]📝 Updated entry:[/bold green] [cyan]{updated['name']}[/cyan]")
            continue

        # History
        if cmd == "history":
            if not args:
                console.print("[bold red]Usage:[/bold red] history <name>")
                continue

            hist = history.get_history(args[0])
            if not hist:
                console.print("[dim italic]No modification history found.[/dim italic]")
            else:
                table = Table(title=f"History for {args[0]}", show_header=True, header_style="bold yellow", border_style="dim")
                table.add_column("Event Logs", style="yellow")
                for h in hist:
                    table.add_row(str(h))
                console.print(table)
            continue

        # Unknown command
        console.print("[bold red]❓ Unknown command.[/bold red] Type [bold cyan]'help'[/bold cyan] for options.")