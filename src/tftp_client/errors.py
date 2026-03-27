# exceções personalizadas do cliente TFTP


class TFTPClientError(Exception):
    """erro base do cliente TFTP"""


class InvalidCommandError(TFTPClientError):
    """erro para comando inválido na CLI"""


class ProtocolError(TFTPClientError):
    """erro de protocolo TFTP: inserir lógica"""


class TransportError(TFTPClientError):
    """erro de rede/UDP: inserir lógica"""


class FileError(TFTPClientError):
    """erro de leitura/gravação de arquivos: inserir lógica"""
