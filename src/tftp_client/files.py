# operações locais de leitura e gravação de arquivos

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
