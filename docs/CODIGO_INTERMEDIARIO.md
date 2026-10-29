# Código Intermediário de Três Endereços (TAC) da MiniPar 2026.2

O gerador (`src/minipar/tac/generator.py`) recebe a AST já validada pelo analisador semântico e produz, para cada função, método e para o programa principal (`main`), uma lista de instruções com no máximo três endereços (dois operandos e um destino).

Ver a saída de qualquer programa: `make tac F=exemplos/teste07_quicksort_iterativo.mp`. As saídas dos exemplos estão em `exemplos/tac/`.

## Operandos

Variáveis (`x`), temporários (`t0`, `t1`, ...), números (`42`, `-3`, `0.5`), strings entre aspas (`"oi"`), `true`, `false` e `null`.

## Conjunto de instruções

| Instrução | Significado |
|---|---|
| `x = a` | cópia |
| `x = a op b` | operação binária (`+ - * / % == != < > <= >=`) |
| `x = -a`, `x = !a` | operação unária |
| `L:` | rótulo |
| `goto L` | desvio incondicional |
| `if a op b goto L` | desvio por comparação |
| `if a goto L`, `ifFalse a goto L` | desvio por valor booleano |
| `param a` | empilha argumento |
| `x = call f, n` | chamada de função com n argumentos (sem `x` quando retorna void) |
| `x = callm o.m, n` | chamada de método do objeto `o` (despacho dinâmico) |
| `return [a]` | retorno |
| `x = o.campo`, `o.campo = a` | leitura e escrita de atributo |
| `x = v[i]`, `v[i] = a` | leitura e escrita em lista, matriz ou string |
| `x = new C` | cria objeto da classe C |
| `x = new_list`, `append v, a`, `x = pop v`, `x = size v` | listas |
| `x = new_matrix r, c, v` | matriz |
| `print a, b, ...` | saída; `x = input [prompt]` lê uma linha |
| `x = new_channel h, p`, `send ch, a, ...`, `x = receive ch`, `close ch` | canais |
| `par_begin` / `task nome` ... `end_task` / `par_end` | bloco paralelo, uma tarefa por comando filho; `par_end` faz o join |
| `fork nome [on core N \| on host H, P]` ... `end_task` | subtarefa independente |
| `join [nome, ...]` | espera subtarefas (sem nomes: todas) |

## Estrutura da saída

```
class Nome [extends Base]:        classes, com campos e métodos
channel canal comp_1 comp_2       canais declarados
global variavel                   variáveis globais
func nome(params):                funções e programa principal (main)
func Classe.metodo(this, ...):    métodos (this é o primeiro parâmetro)
func Classe.__attrs(this):        inicializa os atributos da classe (chama o da superclasse antes)
```

## Decisões de tradução

* **Condições em curto-circuito.** `&&` e `||` viram desvios; a comparação inverte o operador quando o desvio ocorre no caso falso. Exemplo: `if (a < 5 && b > 1)` gera `if a >= 5 goto endif1` e `if b <= 1 goto endif1`.
* **Sem cópias desnecessárias.** `x = a + b` grava direto em `x`; só usa temporário quando o destino aparece na própria expressão.
* **Nomes únicos.** Variáveis de mesmo nome em escopos diferentes viram `x`, `x_1`, ... Um nome de usuário parecido com temporário (`t0`) vira `t0_v`.
* **Objetos.** `new C(args)` gera `new C`, chama `C.__attrs` e depois o construtor `init` (da própria classe ou herdado).
* **Laços.** `break` e `continue` desviam para os rótulos `endwhile`/`forstep` etc. O `for ... in` percorre por índice usando `size`.
* **Paralelismo.** As regiões `task`/`fork` são preservadas no TAC; o gerador de C++ (próxima etapa) as converte em threads, núcleos ou processos remotos.

## Exemplo (Teste 7: quicksort não recursivo)

Trecho do laço de particionamento gerado:

```
  for4:
    if j >= fim goto endfor6
    t3 = arr[j]
    if t3 > pivo goto endif7
    i = i + 1
    troca = arr[i]
    t4 = arr[j]
    arr[i] = t4
    arr[j] = troca
  endif7:
  forstep5:
    j = j + 1
    goto for4
  endfor6:
```

## Como o TAC é validado

`tests/tac_runner.py` é um interpretador mínimo de TAC usado só nos testes. Ele executa o código gerado e compara a saída com o esperado: fatorial e Fibonacci recursivos, laços com `break`/`continue`, curto-circuito, objetos com herança e polimorfismo, o Teste 7 (`Array ordenado: [5, 12, 33, 61, 98]`) e o Teste 3 (neurônio convergindo na iteração 51).
