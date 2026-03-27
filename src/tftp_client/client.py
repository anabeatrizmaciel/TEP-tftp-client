from __future__ import annotations

from dataclasses import dataclass

from .files import FileManager
from .protocol import build_rrq, build_wrq
from .transport import UDPTransport


@dataclass
class TFTPClient:
    host: str
    port: int = 69
    timeout: float = 5.0

    def __post_init__(self) -> None:
        self.transport = UDPTransport(timeout=self.timeout)
        self.files = FileManager()

    def get_file(self, remote_filename: str, local_filename: str | None = None) -> bytes:
        # faz o download de um arquivo do servidor TFTP
        request = build_rrq(remote_filename)
        response = self.transport.send_and_receive(self.host, self.port, request)
        if local_filename:
            self.files.write_bytes(local_filename, response)
        return response

    def put_file(self, local_filename: str, remote_filename: str | None = None) -> bytes:
        # envia um arquivo para o servidor TFTP
        remote_name = remote_filename or local_filename
        request = build_wrq(remote_name)
        content = self.files.read_bytes(local_filename)
        payload = request + content
        return self.transport.send_and_receive(self.host, self.port, payload)
