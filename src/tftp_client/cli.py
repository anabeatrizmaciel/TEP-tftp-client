"""Interface de linha de comando do cliente TFTP."""

from __future__ import annotations

import argparse
import sys

from .client import TFTPClient
from .errors import TFTPClientError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tftp-client", description="Cliente TFTP em Python")
    parser.add_argument("action", choices=["get", "put"], help="Operação TFTP")
    parser.add_argument("host", help="IP ou hostname do servidor TFTP")
    parser.add_argument("filename", help="Nome do arquivo local ou remoto")
    parser.add_argument("--port", type=int, default=69, help="Porta do servidor TFTP")
    parser.add_argument("--timeout", type=float, default=5.0, help="Tempo limite em segundos")
    parser.add_argument("--retries", type=int, default=3, help="Quantidade de novas tentativas")
    parser.add_argument("--remote-name", help="Nome remoto do arquivo no servidor")
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    client = TFTPClient(host=args.host, port=args.port, timeout=args.timeout, retries=args.retries)

    try:
        if args.action == "get":
            response = client.get_file(args.filename, args.remote_name)
            print(f"Download concluído. Bytes recebidos: {len(response)}")
        else:
            response = client.put_file(args.filename, args.remote_name)
            print(f"Upload concluído. Resposta recebida: {len(response)} bytes")
        return 0
    except TFTPClientError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except (ValueError, OSError) as exc:
        print(f"Erro inesperado: {exc}", file=sys.stderr)
        return 1
