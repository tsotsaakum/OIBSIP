"""App launcher: GUI by default, or CLI with --cli / --city / --ip."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OIBSIP Weather App — GUI by default, or --cli.")
    parser.add_argument("--cli", action="store_true", help="Command-line interface.")
    parser.add_argument("--city", help="City or ZIP for a one-shot CLI lookup.")
    parser.add_argument("--ip", action="store_true", help="Detect city from IP (CLI).")
    parser.add_argument("--loop", action="store_true", help="CLI: ask for another city after each lookup.")
    parser.add_argument("--gui", action="store_true", help="Force the dashboard GUI.")
    args = parser.parse_args(argv)

    if args.cli or args.city or args.ip:
        from weather_cli import run_cli

        return run_cli(city=args.city, use_ip=args.ip, loop=args.loop)

    from weather_gui import run_gui

    run_gui()
    return 0


if __name__ == "__main__":
    sys.exit(main())
