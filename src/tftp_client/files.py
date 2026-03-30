"""Operações locais de leitura e gravação de arquivos."""

from __future__ import annotations

from pathlib import Path

from .errors import FileError


class FileManager:
    def read_bytes(self, path: str | Path) -> bytes:
        try:
            return Path(path).read_bytes()
        except OSError as exc:
            raise FileError(f"Não foi possível ler o arquivo: {path}") from exc

    def write_bytes(self, path: str | Path, data: bytes) -> None:
        try:
            Path(path).write_bytes(data)
        except OSError as exc:
            raise FileError(f"Não foi possível salvar o arquivo: {path}") from exc

    def iter_chunks(self, path: str | Path, chunk_size: int = 512):
        data = self.read_bytes(path)
        if not data:
            yield b""
            return

        for index in range(0, len(data), chunk_size):
            yield data[index:index + chunk_size]

        if len(data) % chunk_size == 0:
            yield b""
