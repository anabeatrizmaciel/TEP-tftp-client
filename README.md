# Cliente TFTP

Cliente TFTP em Python, organizado por módulos, com interface CLI e fluxo real do protocolo TFTP (RFC 1350).

## Objetivo

Este projeto implementa o lado cliente de uma arquitetura cliente-servidor 2-tier, com foco em:

- leitura de comandos pela linha de comando;
- download de arquivos do servidor TFTP;
- upload de arquivos para o servidor TFTP;
- tratamento de pacotes TFTP;
- comunicação via UDP;
- organização para uso de Git pull requests.

## Protocolo estudado

- [TFTP na Wikipedia](https://en.wikipedia.org/wiki/Trivial_File_Transfer_Protocol)
- [RFC 1350](https://datatracker.ietf.org/doc/html/rfc1350)

## Fluxo do protocolo

### Download (RRQ)
1. Cliente envia `RRQ`.
2. Servidor responde com `DATA`.
3. Cliente envia `ACK` do bloco recebido.
4. O processo se repete até chegar ao último bloco, menor que 512 bytes.

### Upload (WRQ)
1. Cliente envia `WRQ`.
2. Servidor responde com `ACK 0`.
3. Cliente envia `DATA` em blocos de até 512 bytes.
4. Cliente aguarda o `ACK` de cada bloco até finalizar.

## Diagrama de Componentes C4

![Diagrama C4 do cliente](docs/c4-client-diagram.png)

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
