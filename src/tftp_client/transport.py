"""Camada de transporte UDP do cliente TFTP."""

from __future__ import annotations

import socket
from dataclasses import dataclass
from typing import Tuple

from .errors import TransportError

Address = tuple[str, int]


@dataclass
class UDPTransport:
    timeout: float = 5.0
    buffer_size: int = 4 + 512

    def open(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        return sock

    @staticmethod
    def send(sock: socket.socket, payload: bytes, host: str, port: int) -> None:
        sock.sendto(payload, (host, port))

    def receive(self, sock: socket.socket) -> tuple[bytes, Address]:
        try:
            return sock.recvfrom(self.buffer_size)
        except socket.timeout as exc:
            raise TransportError("Tempo limite excedido ao comunicar com o servidor.") from exc
        except OSError as exc:
            raise TransportError(f"Falha na comunicação UDP: {exc}") from exc

    def send_and_receive(
        self,
        host: str,
        port: int,
        payload: bytes,
        buffer_size: int | None = None,
    ) -> bytes:
        size = buffer_size or self.buffer_size
        with self.open() as sock:
            sock.settimeout(self.timeout)
            sock.sendto(payload, (host, port))
            try:
                data, _ = sock.recvfrom(size)
                return data
            except socket.timeout as exc:
                raise TransportError("Tempo limite excedido ao comunicar com o servidor.") from exc
            except OSError as exc:
                raise TransportError(f"Falha na comunicação UDP: {exc}") from exc
