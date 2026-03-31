import pytest
from tftp_client.client import TFTPClient
from tftp_client.errors import ProtocolError, TransportError
from tftp_client.protocol import build_ack, build_data, build_error

class FakeSocket:
    def __init__(self, responses):
        self.responses = list(responses)
        self.sent = []
        self.closed = False
        self.timeout = None

    def settimeout(self, timeout):
        self.timeout = timeout

    def sendto(self, payload, addr):
        # PRINT ADICIONADO PARA VERMOS O ENVIO
        print(f"\n[REDE -> ENVIO] A enviar para {addr}: {payload}")
        self.sent.append((payload, addr))

    def recvfrom(self, buffer_size):
        if not self.responses:
            raise TimeoutError("Sem mais respostas")
        data, addr = self.responses.pop(0)
        # PRINT ADICIONADO PARA VERMOS A RECEÇÃO
        print(f"[REDE <- RECEÇÃO] Recebido de {addr}: {data}")
        return data, addr

    def close(self):
        self.closed = True


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.socket = FakeSocket(self.responses)
        self.timeout = 5.0

    def open(self):
        return self.socket

    @staticmethod
    def send(sock, payload, host, port):
        sock.sendto(payload, (host, port))

    def receive(self, sock):
        return sock.recvfrom(516)


class FakeFiles:
    def __init__(self, content=b""):
        self.content = content
        self.written = None

    def read_bytes(self, path):
        return self.content

    def write_bytes(self, path, data):
        # PRINT ADICIONADO PARA VERMOS A ESCRITA NO DISCO
        print(f"[DISCO] A guardar ficheiro '{path}' com os dados: {data}")
        self.written = (path, data)

    def iter_chunks(self, path, chunk_size=512):
        print(f"[DISCO] A ler o ficheiro '{path}' para envio...")
        if not self.content:
            yield b""
            return
        for i in range(0, len(self.content), chunk_size):
            yield self.content[i:i+chunk_size]
        if len(self.content) % chunk_size == 0:
            yield b""


class FlakyTransport:
    def __init__(self, success_responses, fail_times=1):
        self.success_responses = list(success_responses)
        self.fail_times = fail_times
        self.failures_simulated = 0
        self.sent_packets = []

    def open(self):
        return self

    def send(self, sock, payload, host, port):
        print(f"\n[REDE INSTÁVEL -> ENVIO] A tentar enviar: {payload}")
        self.sent_packets.append(payload)

    def receive(self, sock):
        if self.failures_simulated < self.fail_times:
            self.failures_simulated += 1
            print(f"[REDE INSTÁVEL !!] Falha simulada na rede. O pacote perdeu-se! (Falha {self.failures_simulated}/{self.fail_times})")
            raise TransportError("Tempo limite excedido")
        if not self.success_responses:
            raise TimeoutError("Sem mais respostas mockadas")
        
        data, addr = self.success_responses.pop(0)
        print(f"[REDE INSTÁVEL <- RECEÇÃO] Sucesso! Recebido de {addr}: {data}")
        return data, addr

    def close(self):
        pass

def test_download_flow_writes_file():
    responses = [
        (build_data(1, b"hello"), ("127.0.0.1", 7000)),
    ]
    client = TFTPClient(host="127.0.0.1")
    client.transport = FakeTransport(responses)
    client.files = FakeFiles()

    data = client.get_file("remote.txt", "local.txt")

    assert data == b"hello"
    assert client.files.written == ("local.txt", b"hello")
    # \x00\x01 garante que não há bytes nulos invisíveis
    assert client.transport.socket.sent[0][0][:2] == b"\x00\x01"
    assert client.transport.socket.sent[1][0] == build_ack(1)


def test_upload_flow_sends_data_blocks():
    responses = [
        (build_ack(0), ("127.0.0.1", 7000)),
        (build_ack(1), ("127.0.0.1", 7000)),
    ]
    client = TFTPClient(host="127.0.0.1")
    client.transport = FakeTransport(responses)
    client.files = FakeFiles(b"hello")

    response = client.put_file("local.txt", "remote.txt")

    assert response == build_ack(0) + build_ack(1)
    sent_packets = [packet for packet, _ in client.transport.socket.sent]
    # \x00\x02 garante que não há bytes nulos invisíveis
    assert sent_packets[0][:2] == b"\x00\x02"  # WRQ
    assert sent_packets[1].startswith(b"\x00\x03\x00\x01") # DATA bloco 1


def test_download_raises_protocol_error_on_tftp_error():
    responses = [
        (build_error(1, "File not found"), ("127.0.0.1", 7000)),
    ]
    client = TFTPClient(host="127.0.0.1")
    client.transport = FakeTransport(responses)
    client.files = FakeFiles()

    with pytest.raises(ProtocolError) as exc_info:
        client.get_file("inexistente.txt")
    
    assert "ERROR 1" in str(exc_info.value)
    assert "File not found" in str(exc_info.value)


def test_client_retries_on_timeout_and_recovers():
    responses = [
        (build_data(1, b"dados recuperados"), ("127.0.0.1", 7000)),
    ]
    client = TFTPClient(host="127.0.0.1", retries=3)
    flaky_transport = FlakyTransport(responses, fail_times=2)
    client.transport = flaky_transport
    client.files = FakeFiles()

    data = client.get_file("arquivo.txt")

    assert data == b"dados recuperados"
    assert flaky_transport.failures_simulated == 2
    assert len(flaky_transport.sent_packets) == 4 


def test_client_fails_after_max_retries_exceeded():
    client = TFTPClient(host="127.0.0.1", retries=2)
    flaky_transport = FlakyTransport([], fail_times=5)
    client.transport = flaky_transport
    client.files = FakeFiles()

    with pytest.raises(TransportError) as exc_info:
        client.get_file("arquivo.txt")
    
    assert "Tempo limite excedido" in str(exc_info.value)
    assert flaky_transport.failures_simulated == 3