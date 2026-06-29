# src/cli/cli_main.py

from logic import vault, history, session, auth
from .help import print_help

def cli_main():
    print("KeyPlus (runtime mode)")

    # First run: no password set
    if not auth.password_exists():
        print("No password set. Create a new master password.")
        pw1 = input("New password: ").strip()
        pw2 = input("Confirm password: ").strip()

        if pw1 != pw2:
            print("Passwords do not match.")
            return

        auth.create_password(pw1)
        print("Password created.")
        session.set_session_key(pw1)
        print("KeyPlus unlocked, Welcome!")

    else:
        # Normal login
        while True:
            master = input("Please enter password: ").strip()
            if auth.verify_password(master):
                session.set_session_key(master)
                print("KeyPlus unlocked, Welcome!")
                break
            else:
                print("Incorrect password.")


    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting KeyPlus.")
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        # -------------------------
        # Exit
        # -------------------------
        if cmd in ("exit", "quit"):
            print("Goodbye.")
            break

        # -------------------------
        # Help
        # -------------------------
        if cmd == "help":
            print_help()
            continue

        # -------------------------
        # List entries
        # -------------------------
        if cmd == "list":
            entries = vault.list_entries()
            if not entries:
                print("No entries found.")
            else:
                for e in entries:
                    print(f"- {e['name']}")
            continue

        # -------------------------
        # View entry
        # -------------------------
        if cmd == "view":
            if not args:
                print("Usage: view <name>")
                continue

            entry = vault.get_entry(args[0])
            if not entry:
                print("Entry not found.")
            else:
                print(f"Name: {entry['name']}")
                print(f"Domain: {entry['domain']}")
                print(f"Password: {entry['password']}")
            continue

        # -------------------------
        # Add entry
        # -------------------------
        if cmd == "add":
            if len(args) < 3:
                print("Usage: add <name> <domain> <password>")
                continue

            name, domain, password = args[0], args[1], args[2]
            entry = vault.add_entry(name, domain, password)
            print(f"Added entry: {entry['name']}")
            continue

        # -------------------------
        # Edit entry
        # -------------------------
        if cmd == "edit":
            if len(args) < 1:
                print("Usage: edit <name>")
                continue

            identifier = args[0]
            entry = vault.get_entry(identifier)
            if not entry:
                print("Entry not found.")
                continue

            print("Leave fields blank to keep current values.")
            new_domain = input(f"Domain [{entry['domain']}]: ").strip() or entry["domain"]
            new_password = input(f"Password [{entry['password']}]: ").strip() or entry["password"]

            updated = vault.edit_entry(identifier, domain=new_domain, password=new_password)
            print(f"Updated entry: {updated['name']}")
            continue

        # -------------------------
        # History
        # -------------------------
        if cmd == "history":
            if not args:
                print("Usage: history <name>")
                continue

            hist = history.get_history(args[0])
            if not hist:
                print("No history found.")
            else:
                for h in hist:
                    print(f"- {h}")
            continue

        # -------------------------
        # Unknown command
        # -------------------------
        print("Unknown command. Type 'help' for options.")
