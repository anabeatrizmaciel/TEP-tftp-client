# TFTP Client

Cliente TFTP desenvolvido em Python, com interface CLI, seguindo a RFC 1350.

## Objetivo

Implementar o lado cliente de um sistema TFTP cliente-servidor, permitindo:

- leitura de comandos pela linha de comando;
- download de arquivos do servidor TFTP;
- upload de arquivos para o servidor TFTP;
- tratamento de pacotes TFTP como `RRQ`, `WRQ`, `DATA`, `ACK` e `ERROR`;
- execução de testes com servidor externo e com o servidor desenvolvido pelo outro grupo.

# Diagrama de Componentes C4

## Organização do projeto

```bash
├── README.md
├── pyproject.toml
├── .gitignore
├── src/
│   └── tftp_client/
│       ├── __init__.py
│       ├── main.py
│       ├── cli.py
│       ├── client.py
│       ├── protocol.py
│       ├── transport.py
│       ├── files.py
│       └── errors.py
├── tests/
│   ├── __init__.py
│   ├── test_protocol.py
│   ├── test_client.py
│   └── test_files.py
└── docs/
    └── c4-client-diagram.png
```

## Como executar

```bash
python -m tftp_client.main --help
```

## Exemplos

```bash
python -m tftp_client.main get 192.168.0.10 arquivo.txt
python -m tftp_client.main put 192.168.0.10 arquivo.txt
```

