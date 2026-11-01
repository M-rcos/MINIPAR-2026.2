# Canais de comunicação (c_channel) da MiniPar 2026.2

Os canais são a única forma de dois programas MiniPar (ou duas subtarefas) trocarem informação: **comunicação somente por mensagem**, sem memória compartilhada. Eles são implementados com sockets TCP no runtime em C++ (POSIX e Winsock).

## Dois jeitos de declarar um canal

```
c_channel calculadora computador_1 computador_2;     # canal entre dois computadores nomeados
var c = c_channel("192.168.0.20", 7000);             # canal por endereço e porta
```

* **Canal entre computadores nomeados** (forma do enunciado). O primeiro nome conecta; o segundo escuta. Cada programa precisa saber quem ele é: `--node computador_1` ou `--node computador_2`.
* **Canal por endereço e porta** (forma da 2026.1). Conecta ao endereço dado. Com `""` ou `"0.0.0.0"` no lugar do endereço, escuta na porta.

## Enviar e receber

```
calculadora.send(operacao, valor1, valor2);     # envia uma mensagem com 3 campos
var resposta = calculadora.receive();           # bloqueia até chegar; devolve uma lista
print(resposta[0]);
calculadora.close();                            # opcional (o canal fecha ao final do programa)
```

As formas `send(canal, a, b)` e `receive(canal)` também funcionam. Uma mensagem pode conter números, strings, booleanos, `null` e listas (aninhadas). Objetos e canais não podem ser enviados (erro claro). O `send` não espera o outro lado ler; o `receive` espera chegar uma mensagem. A conexão é feita na primeira vez que o canal é usado, então a ordem em que os programas são iniciados não importa (quem conecta tenta de novo por até 120 s).

## Como executar o Teste 1 (calculadora) em localhost

Dois terminais, na pasta do projeto:

```
# terminal 1 (servidor)
python3 mp.py build exemplos/teste01_servidor.mp
./build/teste01_servidor --node computador_2

# terminal 2 (cliente)
python3 mp.py build exemplos/teste01_cliente.mp
./build/teste01_cliente --node computador_1
```

Atalhos com `make`: `make teste1-servidor`, `make teste1-cliente` (um por terminal) ou `make teste1-demo` (tudo em um terminal, com entrada automática).

No Windows: `build\teste01_servidor.exe --node computador_2` e `build\teste01_cliente.exe --node computador_1`.

## Configuração: arquivo minipar.hosts

Sem configuração, todos os computadores são `127.0.0.1` e a porta de cada canal é calculada a partir do nome do canal (entre 20000 e 39999, igual em todos os computadores). Para mudar isso, crie um arquivo `minipar.hosts` na pasta onde o programa roda (modelo em `exemplos/minipar.hosts.exemplo`) ou indique outro com `--hosts arquivo`:

```
# endereço de cada computador
computador_1 = 127.0.0.1
computador_2 = 192.168.0.20
# porta do canal (opcional)
port.calculadora = 7000
```

| Opção ou variável | Efeito |
|---|---|
| `--node NOME` ou `MINIPAR_NODE` | quem este programa é |
| `--hosts ARQ` ou `MINIPAR_HOSTS` | arquivo de endereços (padrão: `minipar.hosts`, se existir) |
| `MINIPAR_TIMEOUT` | segundos para conectar ou aguardar conexão (padrão: 120) |
| `--help` | mostra as opções |

## Passar para dois computadores de verdade (quando for a hora)

Não é preciso recompilar. No computador que escuta (`computador_2`), descubra o endereço (`ip addr`), libere a porta do canal no firewall e, nos **dois** computadores, coloque no `minipar.hosts`:

```
computador_2 = <endereço do computador_2>
port.calculadora = 7000
```

Depois execute o servidor no `computador_2` com `--node computador_2` e o cliente no `computador_1` com `--node computador_1`.

## Protocolo (para o relatório)

Uma conexão TCP por canal. Cada mensagem é um quadro: 4 bytes com o tamanho (big-endian) seguidos do conteúdo, que é uma lista codificada recursivamente: um byte de tipo (`0` null, `1` bool, `2` número, `3` string, `4` lista) e os dados (número como 8 bytes IEEE 754 big-endian; string e lista com um contador de 4 bytes). Envios e recebimentos usam travas separadas, então threads diferentes podem usar o mesmo canal.
