# camada de transporte UDP do cliente TFTP

from __future__ import annotations

import socket
from dataclasses import dataclass

from .errors import TransportError


@dataclass
class UDPTransport:
    timeout: float = 5.0

    def send_and_receive(
        self,
        host: str,
        port: int,
        payload: bytes,
        buffer_size: int = 516,
    ) -> bytes:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(self.timeout)
                sock.sendto(payload, (host, port))
                data, _ = sock.recvfrom(buffer_size)
                return data
        except socket.timeout as exc:
            raise TransportError("Tempo limite excedido ao comunicar com o servidor.") from exc
        except OSError as exc:
            raise TransportError(f"Falha na comunicação UDP: {exc}") from exc
