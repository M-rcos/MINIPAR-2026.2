# Gerador de Código C++ e integração com o GCC

Pipeline completo: `.mp` -> Lexer -> Parser (AST) -> Semântico -> TAC -> **C++** -> **GCC** -> executável.

## Comandos

```
make cpp   F=exemplos/teste03_neuronio.mp     # só gera o C++ (mostra na tela)
python3 -m minipar build programa.mp -O2       # gera e compila (pasta build/)
python3 -m minipar run   programa.mp           # compila e executa
```

Opções: `-O0 -O1 -O2 -O3 -Os` (otimização do GCC, padrão `-O2`), `--dir pasta` (saída, padrão `build/`), `-o nome` (caminho do executável, só no `build`).

Arquivos gerados em `build/`: `programa.cpp`, `minipar_runtime.hpp` e o executável (`programa`, ou `programa.exe` no Windows). O GCC é chamado como `g++ -std=c++17 -O2 -pthread`.

## Como o TAC vira C++

| TAC | C++ gerado |
|---|---|
| `func f(a, b):` | `mp::Value fn_f(mp::Value v_a, mp::Value v_b)` (variáveis e temporários declarados no topo) |
| `x = a + b` | `v_x = mp::add(v_a, v_b);` |
| `if a < b goto L` | `if (mp::lt(a, b)) goto L_L;` |
| `param a` ... `r = call f, 2` | `v_r = fn_f(a, b);` (chamada nativa: `mp::bi_len(...)`) |
| `r = callm o.m, 1` | `mp::call_method(o, "m", {a})` (despacho dinâmico) |
| `x = new C` | `mp::new_obj("C")`; classes registradas em `register_classes()` |
| `o.campo = v`, `x = o.campo` | `mp::set_member`, `mp::get_member` |
| `par_begin` ... `task` ... `par_end` | `mp::TaskGroup` com uma thread por tarefa e `join` no fim |
| `fork t on core N` ... `end_task`, `join` | `mp::ForkTable`: thread nomeada, fixada no núcleo N (`pthread_setaffinity_np` ou `SetThreadAffinityMask`) |

## Runtime (`minipar_runtime.hpp`)

Cabeçalho único em C++17. Principais pontos:

* **`mp::Value`**: valor dinâmico (nulo, bool, número, string, lista, objeto, canal). Listas e objetos têm semântica de referência, como no Python. Números são `double`; um número inteiro é impresso sem casa decimal (`7`), os demais com a menor representação exata (`0.30000000000000004`).
* **Erros de execução** (divisão por zero, índice fora dos limites, método inexistente, conversão inválida) terminam o programa com a mensagem `Erro de execução: ...` e código de saída 1. Erros dentro de uma subtarefa também terminam com código 1.
* **Operadores**: `%` tem o sinal do divisor (`-7 % 3 = 2`, como no Python); índices negativos contam a partir do fim.
* **Subtarefas**: cada `par`/`fork` captura as variáveis locais **por cópia** (`[=]`), como processos independentes. Variáveis globais e o conteúdo de listas e objetos compartilham memória (o analisador semântico já bloqueia a atribuição direta a variáveis externas).
* **Saída**: o `print` monta a linha inteira e a escreve sob um `mutex`, para que linhas de threads diferentes não se misturem.

## O que ainda não está implementado

| Recurso | Etapa |
|---|---|
| Canais com sockets (`send`/`receive`/`c_channel`): o C++ é gerado, mas o runtime ainda responde com um erro claro | 7 |
| `fork ... on host "ip", porta` em outro computador: por enquanto executa localmente e avisa na tela | 8 |

## Desempenho

Laço com 24 milhões de iterações (equivalente ao `simular_atraso` dos Testes 8 a 10): 0,12 s com `-O2` e 4,2 s com `-O0`.
