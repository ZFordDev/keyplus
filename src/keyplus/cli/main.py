"""Interactive command-line presentation for KeyPlus."""

from __future__ import annotations

import shlex
import sys
from getpass import getpass
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from keyplus.application.errors import (
    AmbiguousEntryError,
    EntryNotFoundError,
    KeyPlusError,
    UnlockFailedError,
    VaultLockedError,
)
from keyplus.application.models import EntryChanges, EntryDraft, VaultEntry
from keyplus.bootstrap import build_service
from keyplus.storage.migration import discover_legacy_pairs

from .help import print_help

COMMANDS = (
    "help",
    "list",
    "view",
    "add",
    "edit",
    "delete",
    "backup",
    "restore",
    "lock",
    "exit",
    "quit",
)


def cli_main(
    arguments: list[str] | None = None, *, service=None, console: Console | None = None
) -> int:
    arguments = list(sys.argv[1:] if arguments is None else arguments)
    if "--gui" in arguments:
        from keyplus.ui.gui.main import launch_gui

        return launch_gui(service or build_service())
    service = service or build_service()
    console = console or Console()
    console.print(
        Panel("KeyPlus 0.3 — Encrypted Vault", border_style="blue", expand=False)
    )
    try:
        _prepare_vault(service, console, arguments)
        return run_repl(service, console)
    except KeyboardInterrupt:
        service.lock()
        console.print("\n[yellow]KeyPlus locked.[/yellow]")
        return 130
    except (KeyPlusError, ValueError) as exc:
        service.lock()
        console.print(f"[bold red]Error:[/bold red] {exc}")
        return 1


def _prepare_vault(service, console: Console, arguments: list[str]) -> None:
    if service.initialized:
        _unlock(service, console)
        return
    migration_path = _option_value(arguments, "--migrate")
    candidates = [Path.cwd()]
    if migration_path:
        candidates.insert(0, Path(migration_path).expanduser())
    pairs = discover_legacy_pairs(candidates)
    if migration_path and not any(
        pair.directory == Path(migration_path).expanduser().resolve() for pair in pairs
    ):
        raise ValueError(
            "The migration directory must contain both KeyPlus 0.2 files: auth.db and vault.json."
        )
    if pairs:
        pair = pairs[0]
        answer = console.input(
            f"Legacy KeyPlus 0.2 vault found at {pair.directory}. Migrate it? [y/N] "
        )
        if answer.strip().lower() == "y":
            service.migrate_legacy(pair, getpass("Legacy master password: "))
            console.print(
                "[green]Legacy vault migrated. Original files were preserved.[/green]"
            )
            return
    console.print(
        "No KeyPlus 0.3 vault exists. Create a master password to initialize one."
    )
    password = _new_password()
    service.initialize(password)
    console.print("[green]Vault initialized and unlocked.[/green]")


def _option_value(arguments: list[str], option: str) -> str | None:
    if option not in arguments:
        return None
    index = arguments.index(option)
    if index + 1 >= len(arguments):
        raise ValueError(f"{option} requires a directory")
    return arguments[index + 1]


def _new_password() -> str:
    first = getpass("New master password: ")
    second = getpass("Confirm master password: ")
    if not first:
        raise ValueError("The master password cannot be empty.")
    if first != second:
        raise ValueError("The master passwords do not match.")
    return first


def _unlock(service, console: Console) -> None:
    while not service.unlocked:
        try:
            service.unlock(getpass("Master password: "))
        except UnlockFailedError as exc:
            console.print(f"[red]{exc}[/red]")


def run_repl(service, console: Console) -> int:
    prompt = PromptSession(completer=WordCompleter(COMMANDS, ignore_case=True))
    while True:
        try:
            line = prompt.prompt("KeyPlus ❯ ").strip()
        except (EOFError, KeyboardInterrupt):
            service.lock()
            console.print("\n[yellow]KeyPlus locked. Goodbye.[/yellow]")
            return 0
        if not line:
            continue
        try:
            parts = shlex.split(line)
        except ValueError as exc:
            console.print(f"[red]Input error: {exc}[/red]")
            continue
        command, args = parts[0].lower(), parts[1:]
        if command in {"exit", "quit"}:
            service.lock()
            console.print("[yellow]KeyPlus locked. Goodbye.[/yellow]")
            return 0
        try:
            if command == "help":
                print_help(console)
            elif command == "list":
                _list(service, console)
            elif command == "view":
                _view(service, console, args)
            elif command == "add":
                _add(service, console)
            elif command == "edit":
                _edit(service, console, args)
            elif command == "delete":
                _delete(service, console, args)
            elif command == "backup":
                console.print(
                    f"[green]Encrypted backup created:[/green] {service.create_backup()}"
                )
            elif command == "restore":
                _restore(service, console, args)
            elif command == "lock":
                service.lock()
                _unlock(service, console)
            else:
                console.print("[red]Unknown command. Type 'help' for options.[/red]")
        except VaultLockedError:
            _unlock(service, console)
            console.print("[yellow]Vault unlocked. Run the command again.[/yellow]")
        except (KeyPlusError, ValueError) as exc:
            console.print(f"[red]Error: {exc}[/red]")


def _resolve(service, identifier: str) -> VaultEntry:
    entries = service.list_entries()
    exact = [entry for entry in entries if entry.id == identifier]
    if exact:
        return exact[0]
    prefixes = [entry for entry in entries if entry.id.startswith(identifier)]
    if len(prefixes) == 1:
        return prefixes[0]
    if len(prefixes) > 1:
        raise AmbiguousEntryError(f"Entry ID prefix '{identifier}' is ambiguous.")
    names = [
        entry for entry in entries if entry.name.casefold() == identifier.casefold()
    ]
    if len(names) == 1:
        return names[0]
    if len(names) > 1:
        raise AmbiguousEntryError(f"Entry name '{identifier}' is ambiguous; use an ID.")
    raise EntryNotFoundError(f"No entry matches '{identifier}'.")


def _require_identifier(args: list[str], usage: str) -> str:
    if len(args) != 1:
        raise ValueError(f"Usage: {usage}")
    return args[0]


def _list(service, console: Console) -> None:
    entries = service.list_entries()
    if not entries:
        console.print("[dim]No entries found.[/dim]")
        return
    table = Table("ID", "Name", "Domain")
    for entry in entries:
        table.add_row(entry.id[:8], entry.name, entry.domain)
    console.print(table)


def _view(service, console: Console, args: list[str]) -> None:
    entry = _resolve(service, _require_identifier(args, "view <id>"))
    table = Table.grid()
    table.add_row("ID", entry.id)
    table.add_row("Name", entry.name)
    table.add_row("Domain", entry.domain)
    table.add_row("Password", entry.password)
    console.print(Panel(table, title=entry.name, expand=False))


def _add(service, console: Console) -> None:
    name = console.input("Entry name: ").strip()
    domain = console.input("Domain: ").strip()
    password = getpass("Password: ")
    entry = service.add_entry(EntryDraft(name, domain, password))
    console.print(f"[green]Added {entry.name} ({entry.id[:8]}).[/green]")


def _edit(service, console: Console, args: list[str]) -> None:
    entry = _resolve(service, _require_identifier(args, "edit <id>"))
    name = console.input(f"Name [{entry.name}]: ").strip() or None
    domain = console.input(f"Domain [{entry.domain}]: ").strip() or None
    password = getpass("New password [leave blank to keep]: ") or None
    updated = service.update_entry(entry.id, EntryChanges(name, domain, password))
    console.print(f"[green]Updated {updated.name}.[/green]")


def _delete(service, console: Console, args: list[str]) -> None:
    entry = _resolve(service, _require_identifier(args, "delete <id>"))
    if (
        console.input(f"Delete '{entry.name}' permanently? [y/N] ").strip().lower()
        != "y"
    ):
        console.print("Delete cancelled.")
        return
    service.delete_entry(entry.id)
    console.print(f"[green]Deleted {entry.name}.[/green]")


def _restore(service, console: Console, args: list[str]) -> None:
    backup = Path(_require_identifier(args, "restore <path>"))
    answer = console.input(f"Replace the active vault with '{backup}'? [y/N] ")
    if answer.strip().lower() != "y":
        console.print("Restore cancelled.")
        return
    service.restore_backup(backup.expanduser(), getpass("Backup master password: "))
    console.print(
        "[green]Encrypted backup restored. The previous vault was preserved "
        "as last-good.vault.[/green]"
    )
