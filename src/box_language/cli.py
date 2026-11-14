"""Command-line interface for Box."""
import argparse
import sys
from pathlib import Path

from .interpreter import BoxError, Interpreter


def main():
    parser = argparse.ArgumentParser(
        prog="box",
        description="Run a Box language source file."
    )
    parser.add_argument("file", help="Path to a .box source file")
    args = parser.parse_args()

    path = Path(args.file)
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Box: cannot read file: {exc}", file=sys.stderr)
        raise SystemExit(1)

    try:
        Interpreter().run(source)
    except BoxError as exc:
        print(f"Box error: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
