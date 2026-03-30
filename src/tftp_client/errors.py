"""Exceções personalizadas do cliente TFTP."""


class TFTPClientError(Exception):
    """Erro base do cliente TFTP."""


class InvalidCommandError(TFTPClientError):
    """Comando inválido informado na CLI."""


class ProtocolError(TFTPClientError):
    """Erro na construção, leitura ou validação de pacotes TFTP."""


class TransportError(TFTPClientError):
    """Falha de comunicação via rede."""


class FileError(TFTPClientError):
    """Falha ao ler ou gravar arquivos."""
