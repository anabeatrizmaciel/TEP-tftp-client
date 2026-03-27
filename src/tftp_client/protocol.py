# funções para criação e leitura de pacotes TFTP

from __future__ import annotations

from dataclasses import dataclass


OP_RRQ = 1
OP_WRQ = 2
OP_DATA = 3
OP_ACK = 4
OP_ERROR = 5


@dataclass(frozen=True)
class Packet:
    opcode: int
    payload: bytes = b""


def build_rrq(filename: str, mode: str = "octet") -> bytes:
    return _build_request(OP_RRQ, filename, mode)


def build_wrq(filename: str, mode: str = "octet") -> bytes:
    return _build_request(OP_WRQ, filename, mode)


def build_data(block: int, data: bytes) -> bytes:
    return bytes([0, OP_DATA]) + block.to_bytes(2, "big") + data


def build_ack(block: int) -> bytes:
    return bytes([0, OP_ACK]) + block.to_bytes(2, "big")


def build_error(code: int, message: str) -> bytes:
    return bytes([0, OP_ERROR]) + code.to_bytes(2, "big") + message.encode("utf-8") + b"\x00"


def parse_packet(data: bytes) -> Packet:
    if len(data) < 2:
        raise ValueError("Pacote TFTP inválido.")
    opcode = int.from_bytes(data[:2], "big")
    return Packet(opcode=opcode, payload=data[2:])


def _build_request(opcode: int, filename: str, mode: str) -> bytes:
    return (
        bytes([0, opcode])
        + filename.encode("utf-8")
        + b"\x00"
        + mode.encode("utf-8")
        + b"\x00"
    )
