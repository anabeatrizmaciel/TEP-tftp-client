# ponto de entrada do cliente TFTP

from __future__ import annotations

from .cli import run


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
