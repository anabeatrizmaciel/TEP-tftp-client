import pytest
from unittest.mock import patch
from tftp_client.cli import run

@patch("tftp_client.cli.TFTPClient.get_file")
def test_cli_get_success(mock_get_file):
    # Simula o retorno de um download bem-sucedido
    mock_get_file.return_value = b"dados recebidos com sucesso"
    
    # Executa a CLI passando a lista de argumentos
    exit_code = run(["get", "127.0.0.1", "arquivo_remoto.txt"])
    
    # Verifica se o método correto foi chamado com os argumentos esperados
    mock_get_file.assert_called_once_with("arquivo_remoto.txt", None)
    assert exit_code == 0

@patch("tftp_client.cli.TFTPClient.put_file")
def test_cli_put_success(mock_put_file):
    # Simula o retorno de um upload (bytes de confirmação)
    mock_put_file.return_value = b"ack_data"
    
    exit_code = run(["put", "192.168.0.10", "local.txt", "--remote-name", "remoto.txt"])
    
    mock_put_file.assert_called_once_with("local.txt", "remoto.txt")
    assert exit_code == 0

@patch("tftp_client.cli.TFTPClient.get_file")
def test_cli_handles_client_error_gracefully(mock_get_file, capsys):
    from tftp_client.errors import TFTPClientError
    
    # Simula uma falha interna na lógica do TFTP
    mock_get_file.side_effect = TFTPClientError("Arquivo não encontrado no servidor")
    
    exit_code = run(["get", "127.0.0.1", "inexistente.txt"])
    
    # Captura a saída do console (sys.stdout e sys.stderr)
    captured = capsys.readouterr()
    
    # A CLI deve retornar código de erro 1 e imprimir a mensagem amigável no stderr
    assert exit_code == 1
    assert "Erro: Arquivo não encontrado no servidor" in captured.err