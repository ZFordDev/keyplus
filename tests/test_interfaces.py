import os
from io import StringIO

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from rich.console import Console

from keyplus.application.models import EntryDraft
from keyplus.cli import main as cli_main
from keyplus.ui.gui.change_password import ChangePasswordDialog
from keyplus.ui.gui.main import KeyPlusFrame
from tests.test_core import make_service


class FakePromptSession:
    def __init__(self, lines):
        self.lines = iter(lines)

    def prompt(self, _prompt):
        return next(self.lines)


def test_cli_repl_exit_locks_shared_service(tmp_path, monkeypatch):
    service, _ = make_service(tmp_path)
    service.initialize("correct")
    monkeypatch.setattr(
        cli_main,
        "PromptSession",
        lambda **_kwargs: FakePromptSession(["list", "exit"]),
    )
    output = StringIO()
    code = cli_main.run_repl(service, Console(file=output, force_terminal=False))
    assert code == 0
    assert "No entries" in output.getvalue()
    assert not service.unlocked


def test_cli_resolves_unambiguous_id_prefix(tmp_path):
    service, _ = make_service(tmp_path)
    service.initialize("correct")
    entry = service.add_entry(EntryDraft("Site", "site.test", "secret"))
    assert cli_main._resolve(service, entry.id[:8]) == entry


def test_cli_lists_encrypted_backups(tmp_path):
    service, _ = make_service(tmp_path)
    service.initialize("correct")
    backup = service.create_backup()
    output = StringIO()

    cli_main._list_backups(service, Console(file=output, force_terminal=False))

    assert backup.name in output.getvalue()


def test_gui_logout_invalidates_shared_service(tmp_path):
    app = QApplication.instance() or QApplication([])
    service, _ = make_service(tmp_path)
    service.initialize("correct")
    frame = KeyPlusFrame(service)
    frame.logout()
    assert not service.unlocked
    frame.close()
    app.processEvents()


def test_cli_password_change_uses_shared_service(tmp_path, monkeypatch):
    service, _ = make_service(tmp_path)
    service.initialize("old")
    answers = iter(["old", "new", "new"])
    monkeypatch.setattr(cli_main, "getpass", lambda _prompt: next(answers))
    output = StringIO()

    cli_main._change_master_password(
        service, Console(file=output, force_terminal=False)
    )

    service.lock()
    service.unlock("new")
    assert "Master password changed" in output.getvalue()


def test_gui_password_change_dialog_uses_shared_service(tmp_path):
    app = QApplication.instance() or QApplication([])
    service, _ = make_service(tmp_path)
    service.initialize("old")
    dialog = ChangePasswordDialog(service)
    dialog.current_password.setText("old")
    dialog.new_password.setText("new")
    dialog.confirm_password.setText("new")

    dialog._submit()

    assert dialog.result() == dialog.DialogCode.Accepted
    service.lock()
    service.unlock("new")
    dialog.close()
    app.processEvents()
