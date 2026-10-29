# Regras do Analisador Semântico da MiniPar 2026.2

O analisador percorre a AST em duas passagens. Na primeira declara as classes e funções globais
(podem ser usadas antes da definição no arquivo). Na segunda analisa os comandos na ordem do
arquivo, construindo a Tabela de Símbolos hierárquica.

## Sistema de tipos

| Tipo | Origem |
|---|---|
| `number` | literais numéricos; `int`, `float` e `number` pertencem à mesma família |
| `string`, `bool` | literais, `input()`, `to_string()`, comparações |
| `list`, `matrix` | `[...]`, `matrix(l, c, v)`, `range()`, `receive()` |
| `c_channel` | declaração `c_channel` e expressão `c_channel(ip, porta)` |
| `null` | literal `null` (atribuível a listas, objetos e canais, não a number, bool e string) |
| nome de classe | `new Classe(...)` e `this` |
| `unknown` | parâmetro sem tipo ou valor ainda não inferido; compatível com qualquer tipo |
| `void` | retorno de função sem valor; não pode ser usado como valor |

Variáveis `var` recebem o tipo do inicializador. Uma variável sem inicializador recebe o tipo da primeira atribuição. O tipo de retorno de funções e métodos é inferido a partir dos `return`.

## Regras verificadas

| Grupo | Regra | Mensagem (resumo) |
|---|---|---|
| Declaração | redeclaração no mesmo escopo | `A variável 'x' já foi declarada neste escopo` |
| Declaração | uso antes da declaração | `Variável 'x' não declarada` |
| Declaração | nome de função igual ao de função nativa | `... pertence à biblioteca nativa` |
| Tipos | atribuição e declaração com tipo incompatível | `Tipo incompatível na atribuição` |
| Tipos | operadores aritméticos, relacionais, lógicos e unários | `O operador '+' não se aplica a string e number` |
| Tipos | condição de if/while/do/for deve ser bool | `A condição do 'if' deve ser booleana` |
| Funções | número e tipo dos argumentos | `A função 'f' espera 2 argumento(s)` |
| Funções | função inexistente | `Função 'f' não declarada` |
| Funções | retornos com tipos diferentes ou com e sem valor | `retorna tipos diferentes` |
| Funções | uso de função sem void como valor | `Esta expressão não produz valor` |
| Controle | `break` e `continue` fora de laço | `'break' usado fora de um laço` |
| Controle | `return` fora de função ou dentro de fork/par | `'return' só pode ser usado dentro de uma função` |
| Classes | superclasse inexistente, herança circular | `Superclasse 'X' não declarada` |
| Classes | método ou atributo inexistente | `Método 'm' não declarado em 'C'` |
| Classes | construtor (`init`) com número errado de argumentos | `O construtor de 'C' espera N argumento(s)` |
| Classes | sobrescrita com número diferente de parâmetros | `sobrescreve ... com número diferente` |
| Classes | `this` fora de método; atributo sem `this.` dentro do método | `'this' só pode ser usado dentro de métodos` |
| Canais | `send`/`receive` em algo que não é canal | `exige um canal (c_channel)` |
| Canais | computadores iguais na declaração | `devem ter nomes diferentes` |
| Paralelismo | subtarefa altera variável de fora | `A subtarefa (fork/par) não compartilha memória` |
| Paralelismo | `join` de nome que não é subtarefa; `fork` repetido | `não é uma subtarefa criada com 'fork'` |
| Coleções | índice não numérico, indexação de tipo errado, string mutável | `Strings são imutáveis` |

## Regra de isolamento (fork e par)

O enunciado define as subtarefas como processos independentes que só se comunicam por mensagem.
Por isso, dentro de `fork` ou de cada filho de `par`, é permitido **ler** variáveis declaradas
fora (o valor é copiado na criação), mas é **erro** atribuir a elas, inclusive por campo ou índice
(`obj.campo = ...`, `lista[i] = ...`). Resultados devem voltar por canal.

## Pseudocódigo (resumo)

```
analisar(programa):
    para cada classe e função global:  declarar na tabela (1a passagem)
    para cada classe: verificar superclasse, herança circular, sobrescrita
    para cada comando do programa:     visitar(comando)

visitar(VarDecl):  t = tipo(init); se declarado e incompatível: erro; definir símbolo ou erro de duplicata
visitar(Assign):   resolver destino; se atravessa fronteira fork/par: erro; checar tipos
visitar(Call):     resolver função; checar aridade e tipos dos argumentos; devolver tipo de retorno
visitar(Fork):     definir subtarefa; abrir escopo isolado; visitar corpo; fechar escopo
visitar(Binary):   tipos dos operandos; verificar operador; devolver tipo resultante
```
