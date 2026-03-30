import pytest
import socket
from unittest.mock import MagicMock
from tftp_client.transport import UDPTransport
from tftp_client.errors import TransportError

def test_transport_receive_success():
    transport = UDPTransport()
    mock_sock = MagicMock()
    # Simula o socket retornando dados válidos
    mock_sock.recvfrom.return_value = (b"pacote_tftp", ("192.168.0.10", 69))
    
    data, addr = transport.receive(mock_sock)
    
    assert data == b"pacote_tftp"
    assert addr == ("192.168.0.10", 69)

def test_transport_receive_timeout_raises_custom_error():
    transport = UDPTransport()
    mock_sock = MagicMock()
    # Simula um estouro de tempo do socket nativo
    mock_sock.recvfrom.side_effect = socket.timeout("timeout")
    
    with pytest.raises(TransportError) as exc:
        transport.receive(mock_sock)
    
    assert "Tempo limite excedido" in str(exc.value)

def test_transport_receive_oserror_raises_custom_error():
    transport = UDPTransport()
    mock_sock = MagicMock()
    # Simula uma falha de rede (ex: cabo desconectado)
    mock_sock.recvfrom.side_effect = OSError("Network is unreachable")
    
    with pytest.raises(TransportError) as exc:
        transport.receive(mock_sock)
    
    assert "Falha na comunicação UDP" in str(exc.value)