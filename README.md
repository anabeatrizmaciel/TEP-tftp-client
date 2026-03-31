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

## Testes e Qualidade

O projeto possui testes automatizados com `pytest`, cobrindo protocolo, transporte UDP, cliente, manipulação de arquivos e CLI.

Se ainda não tiver o `pytest` instalado:

```bash
python -m pip install pytest
```

Execução rápida de toda a suíte:

```bash
python -m pytest
```

Execução detalhada (útil para depuração):

```bash
python -m pytest -v -s
```

Executar apenas um arquivo de teste:

```bash
python -m pytest tests/test_protocol.py
```

Cobertura dos testes atuais:

- `tests/test_protocol.py`: montagem e parsing de pacotes TFTP (`RRQ`, `WRQ`, `DATA`, `ACK`, `ERROR`).
- `tests/test_transport.py`: envio/recebimento UDP, timeouts e cenários de retransmissão.
- `tests/test_client.py`: fluxo de download/upload e integração entre camadas.
- `tests/test_files.py`: leitura, escrita e validações de arquivos locais.
- `tests/test_cli.py`: argumentos de linha de comando e comportamento da interface CLI.
