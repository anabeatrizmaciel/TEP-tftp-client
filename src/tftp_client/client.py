"""Lógica principal do cliente TFTP."""

from __future__ import annotations

import socket
from dataclasses import dataclass, field
from typing import Iterable

from .errors import FileError, ProtocolError, TFTPClientError, TransportError
from .files import FileManager
from .protocol import (
    DEFAULT_MODE,
    MAX_BLOCK_NUMBER,
    MAX_DATA_SIZE,
    OP_ACK,
    OP_DATA,
    OP_ERROR,
    Packet,
    build_ack,
    build_data,
    build_rrq,
    build_wrq,
    parse_ack,
    parse_data,
    parse_error,
    parse_packet,
)
from .transport import UDPTransport


@dataclass
class TFTPClient:
    host: str
    port: int = 69
    timeout: float = 5.0
    retries: int = 3
    mode: str = DEFAULT_MODE
    transport: UDPTransport = field(default_factory=UDPTransport)
    files: FileManager = field(default_factory=FileManager)

    def __post_init__(self) -> None:
        self.transport.timeout = self.timeout

    def get_file(self, remote_filename: str, local_filename: str | None = None) -> bytes:
        """Baixa um arquivo do servidor TFTP usando o fluxo RRQ/DATA/ACK."""
        request = build_rrq(remote_filename, self.mode)
        chunks: list[bytes] = []
        server_peer = (self.host, self.port)
        expected_block = 1
        last_sent = request

        sock = self.transport.open()
        try:
            self.transport.send(sock, request, self.host, self.port)
            while True:
                data, addr = self._recv_with_retry(sock, server_peer, last_sent)
                server_peer = addr
                packet = parse_packet(data)

                if packet.opcode == OP_ERROR:
                    raise self._protocol_error_from_packet(packet)

                if packet.opcode != OP_DATA:
                    raise ProtocolError(f"Pacote inesperado durante download: opcode {packet.opcode}")

                block, payload = parse_data(data)

                if block == expected_block:
                    chunks.append(payload)
                    ack = build_ack(block)
                    self.transport.send(sock, ack, server_peer[0], server_peer[1])
                    last_sent = ack
                    expected_block = self._next_block(expected_block)

                    if len(payload) < MAX_DATA_SIZE:
                        break
                elif block == self._previous_block(expected_block):
                    ack = build_ack(block)
                    self.transport.send(sock, ack, server_peer[0], server_peer[1])
                    last_sent = ack
                else:
                    raise ProtocolError(
                        f"Bloco inesperado durante download. Esperado {expected_block}, recebido {block}."
                    )
        finally:
            sock.close()

        content = b"".join(chunks)
        if local_filename:
            self.files.write_bytes(local_filename, content)
        return content

    def put_file(self, local_filename: str, remote_filename: str | None = None) -> bytes:
        """Envia um arquivo ao servidor TFTP usando o fluxo WRQ/ACK/DATA."""
        remote_name = remote_filename or local_filename
        request = build_wrq(remote_name, self.mode)
        server_peer = (self.host, self.port)

        sock = self.transport.open()
        try:
            self.transport.send(sock, request, self.host, self.port)
            last_sent = request
            ack0 = self._wait_for_ack(sock, server_peer, last_sent, expected_block=0)
            server_peer = ack0[1]

            response_bytes = bytearray()
            block = 1
            for chunk in self.files.iter_chunks(local_filename, MAX_DATA_SIZE):
                data_packet = build_data(block, chunk)
                self.transport.send(sock, data_packet, server_peer[0], server_peer[1])
                last_sent = data_packet
                ack_data = self._wait_for_ack(sock, server_peer, last_sent, expected_block=block)
                server_peer = ack_data[1]
                response_bytes.extend(ack_data[0])
                if len(chunk) < MAX_DATA_SIZE:
                    break
                block = self._next_block(block)
            return bytes(response_bytes)
        finally:
            sock.close()

    def _recv_with_retry(
        self,
        sock: socket.socket,
        peer: tuple[str, int],
        last_sent: bytes,
    ) -> tuple[bytes, tuple[str, int]]:
        attempts = 0
        while True:
            try:
                return self.transport.receive(sock)
            except TransportError:
                attempts += 1
                if attempts > self.retries:
                    raise
                self.transport.send(sock, last_sent, peer[0], peer[1])

    def _wait_for_ack(
        self,
        sock: socket.socket,
        peer: tuple[str, int],
        last_sent: bytes,
        expected_block: int,
    ) -> tuple[bytes, tuple[str, int]]:
        attempts = 0
        while True:
            try:
                data, addr = self.transport.receive(sock)
            except TransportError:
                attempts += 1
                if attempts > self.retries:
                    raise
                self.transport.send(sock, last_sent, peer[0], peer[1])
                continue

            packet = parse_packet(data)
            if packet.opcode == OP_ERROR:
                raise self._protocol_error_from_packet(packet)
            if packet.opcode != OP_ACK:
                raise ProtocolError(f"Pacote inesperado durante upload: opcode {packet.opcode}")

            block = parse_ack(data)
            if block == expected_block:
                return data, addr
            if block < expected_block:
                continue
            raise ProtocolError(
                f"ACK inesperado durante upload. Esperado {expected_block}, recebido {block}."
            )

    @staticmethod
    def _next_block(block: int) -> int:
        return 0 if block >= MAX_BLOCK_NUMBER else block + 1

    @staticmethod
    def _previous_block(block: int) -> int:
        return MAX_BLOCK_NUMBER if block == 0 else block - 1

    @staticmethod
    def _protocol_error_from_packet(packet: Packet) -> ProtocolError:
        code, message = parse_error(packet.payload)
        return ProtocolError(f"Servidor TFTP retornou ERROR {code}: {message}")
