"""
app/keyplus.py
--------------

main entry point
"""

import sys

def main():
    # Future: detect flags, config, or environment
    mode = "cli"

    if mode == "cli":
        from app.cli.main import main as cli_main
        cli_main()

    # Future GUI mode (disabled for now)
    # elif mode == "gui":
    #     from app.gui.main import main as gui_main
    #     gui_main()

    else:
        print("Unknown mode:", mode)
        sys.exit(1)


if __name__ == "__main__":
    main()
