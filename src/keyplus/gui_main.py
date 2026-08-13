"""Dedicated windowed entry point used by desktop packaging."""

from keyplus.ui.gui.main import launch_gui


def main() -> int:
    return launch_gui()


if __name__ == "__main__":
    raise SystemExit(main())
