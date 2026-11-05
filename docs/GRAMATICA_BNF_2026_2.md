# Gramática Formal BNF da Linguagem MiniPar 2026.2

Base: gramática MiniPar 2026.1, revisada e
ampliada para atender aos Programas de Teste 1 a 11 da versão 2026.2.

## 1. Notação

| Símbolo | Significado |
|---|---|
| `::=` | definição |
| `\|` | alternativa |
| `{ x }` | zero ou mais repetições |
| `[ x ]` | opcional |
| `( x )` | agrupamento |
| `"tok"` | terminal literal |
| `<nt>` | não-terminal |
| `"on"` com marca (ctx) | palavra contextual: é um IDENTIFIER cujo texto é igual ao indicado |

## 2. O que mudou em relação à 2026.1

| # | Mudança | Motivo (teste) |
|---|---|---|
| 1 | Novo tipo `float` e literal `null` | Testes 3, 4 e 5 (pesos, taxa de aprendizado) |
| 2 | Atribuição composta `+=  -=  *=  /=` | Teste 3 (`peso += ...`) |
| 3 | Declaração de canal `c_channel canal comp1 comp2;` | Enunciado e Teste 1 (forma textual do professor); a forma de expressão `c_channel("ip", porta)` da 2026.1 continua válida |
| 4 | Métodos de canal `canal.send(...)` e `canal.receive()` | Teste 1; as formas `send(canal, msg)` e `receive(canal)` continuam válidas |
| 5 | Comando `fork` com alocação opcional (`on core N` ou `on host "ip", porta`) e comando `join` | Enunciado (Fork e Join), Testes 8, 9 e 10 |
| 6 | Construtor de classe é o método `init` | Testes 3, 4, 5 e 11 (`new Neuronio(1, 0)`) |
| 7 | Atributos de classe: `var nome = valor;` direto no corpo da classe | Correção: na 2026.1 a regra `"var" <declaracao_variavel>` repetia o `var` |
| 8 | Correção do `for`: `"for" "(" ( <for_classico> \| <for_iterador> ) ")"` | A regra original tinha o parêntese de fechamento mal agrupado |
| 9 | `send` e `receive` aceitos após o ponto (`canal.send`) | Necessário para o item 4 |
| 10 | Biblioteca nativa ampliada (seção 6) | Testes 3 a 11 |
| 11 | `return valor;` dentro de `fork` e a expressão `join nome` (recebe o valor) | Testes 8, 9 e 10 (substitui a `Queue` do Python) |

## 3. Gramática consolidada

```bnf
(* ---------- ESTRUTURA GLOBAL ---------- *)

<programa> ::= { <declaracao_global> | <comando> }

<declaracao_global> ::= <declaracao_classe>
                      | <declaracao_funcao>
                      | <declaracao_variavel>
                      | <declaracao_canal>


(* ---------- DECLARAÇÕES ---------- *)

<declaracao_variavel> ::= "var" <IDENTIFIER> [ "=" <expressao> ] ";"
                        | <tipo> <IDENTIFIER> [ "=" <expressao> ] ";"

<declaracao_funcao>   ::= "func" <IDENTIFIER> "(" [ <lista_parametros> ] ")" <bloco_seq>
<lista_parametros>    ::= <parametro> { "," <parametro> }
<parametro>           ::= [ <tipo> ] <IDENTIFIER>

<declaracao_classe>   ::= "class" <IDENTIFIER> [ "extends" <IDENTIFIER> ]
                          "{" { <membro_classe> } "}"
<membro_classe>       ::= <declaracao_variavel>      (* atributo *)
                        | <declaracao_funcao>        (* método; "init" é o construtor *)

<declaracao_canal>    ::= "c_channel" <IDENTIFIER> <IDENTIFIER> <IDENTIFIER> ";"
                          (* canal, computador_1, computador_2 *)


(* ---------- COMANDOS ---------- *)

<comando> ::= <declaracao_variavel>
            | <atribuicao>
            | <bloco_seq>
            | <bloco_par>
            | <comando_fork>
            | <comando_join>
            | <comando_if>
            | <comando_while>
            | <comando_do_while>
            | <comando_for>
            | <comando_print>
            | <comando_send>
            | <comando_return>
            | <comando_break>
            | <comando_continue>
            | <chamada_funcao> ";"
            | <chamada_metodo> ";"

<atribuicao>       ::= <alvo_atribuicao> <op_atribuicao> <expressao> ";"
<op_atribuicao>    ::= "=" | "+=" | "-=" | "*=" | "/="
<alvo_atribuicao>  ::= <IDENTIFIER>
                     | <expressao_posfixo> "." <IDENTIFIER>
                     | <expressao_posfixo> "[" <expressao> "]"

<comando_print>    ::= "print" "(" [ <expressao> { "," <expressao> } ] ")" ";"
<comando_send>     ::= "send" "(" <expressao> "," <expressao> { "," <expressao> } ")" ";"
<comando_return>   ::= "return" [ <expressao> ] ";"
<comando_break>    ::= "break" ";"
<comando_continue> ::= "continue" ";"


(* ---------- BLOCOS SEQ, PAR, FORK E JOIN ---------- *)

<bloco_seq> ::= "seq" "{" { <comando> } "}"
              | "{" { <comando> } "}"

<bloco_par> ::= "par" "{" { <comando> } "}"
                (* cada comando filho executa em uma thread; join implícito no fim *)

<comando_fork> ::= "fork" <IDENTIFIER> [ <alocacao> ] <bloco_seq>
<alocacao>     ::= "on"(ctx) "core" (ctx) <expressao>
                 | "on"(ctx) "host" (ctx) <expressao> [ "," <expressao> ]
                   (* core N: núcleo da CPU; host "ip", porta: outro computador *)

<comando_join> ::= "join" [ <IDENTIFIER> { "," <IDENTIFIER> } ] ";"
                   (* sem nomes: aguarda todas as subtarefas criadas por fork *)

<expressao_join> ::= "join" <IDENTIFIER>
                   (* espera a subtarefa e devolve o valor do "return" do corpo do fork *)


(* ---------- ESTRUTURAS DE CONTROLE ---------- *)

<comando_if>       ::= "if" "(" <expressao> ")" <comando> [ "else" <comando> ]
<comando_while>    ::= "while" "(" <expressao> ")" <comando>
<comando_do_while> ::= "do" <comando> "while" "(" <expressao> ")" [ ";" ]

<comando_for>      ::= "for" "(" ( <for_classico> | <for_iterador> ) ")" <comando>
<for_classico>     ::= [ <inicializador_for> ] ";" [ <expressao> ] ";" [ <incremento_for> ]
<inicializador_for>::= "var" <IDENTIFIER> [ "=" <expressao> ]
                     | <tipo> <IDENTIFIER> [ "=" <expressao> ]
                     | <alvo_atribuicao> <op_atribuicao> <expressao>
                     | <expressao>
<incremento_for>   ::= <alvo_atribuicao> <op_atribuicao> <expressao>
                     | <expressao>
<for_iterador>     ::= "var" <IDENTIFIER> "in" <expressao>


(* ---------- ORIENTAÇÃO A OBJETOS ---------- *)

<expressao_new>      ::= "new" <IDENTIFIER> "(" [ <lista_argumentos> ] ")"
<chamada_metodo>     ::= <expressao_posfixo> "." <nome_membro> "(" [ <lista_argumentos> ] ")"
<acesso_propriedade> ::= <expressao_posfixo> "." <IDENTIFIER>
<expressao_this>     ::= "this"
<nome_membro>        ::= <IDENTIFIER> | "send" | "receive"


(* ---------- CANAIS DE COMUNICAÇÃO ---------- *)

<expressao_c_channel> ::= "c_channel" "(" <expressao> "," <expressao> ")"
<expressao_receive>   ::= "receive" "(" <expressao> ")"
                          (* canal.receive() é tratado como chamada de método *)


(* ---------- COLEÇÕES, ENTRADA E SAÍDA ---------- *)

<expressao_lista>  ::= "[" [ <expressao> { "," <expressao> } ] "]"
<expressao_matrix> ::= "matrix" "(" <expressao> "," <expressao> "," <expressao> ")"
<expressao_input>  ::= "input" "(" [ <expressao> ] ")"


(* ---------- EXPRESSÕES (da menor para a maior precedência) ---------- *)

<expressao>        ::= <expressao_ou>
<expressao_ou>     ::= <expressao_e> { "||" <expressao_e> }
<expressao_e>      ::= <expressao_comp> { "&&" <expressao_comp> }
<expressao_comp>   ::= <expressao_termo>
                       { ( "==" | "!=" | "<" | ">" | "<=" | ">=" ) <expressao_termo> }
<expressao_termo>  ::= <expressao_fator> { ( "+" | "-" ) <expressao_fator> }
<expressao_fator>  ::= <expressao_unaria> { ( "*" | "/" | "%" ) <expressao_unaria> }
<expressao_unaria> ::= ( "-" | "+" | "!" ) <expressao_unaria>
                     | <expressao_posfixo>
<expressao_posfixo>::= <expressao_primaria>
                       { "." <nome_membro> [ "(" [ <lista_argumentos> ] ")" ]
                       | "[" <expressao> "]" }
<expressao_primaria>::= <NUMBER> | <STRING_LITERAL> | <BOOL_LITERAL> | "null"
                       | <IDENTIFIER> [ "(" [ <lista_argumentos> ] ")" ]
                       | "this"
                       | <expressao_new>
                       | <expressao_c_channel>
                       | <expressao_receive>
                       | <expressao_input>
                       | <expressao_lista>
                       | <expressao_matrix>
                       | <expressao_join>
                       | "(" <expressao> ")"

<lista_argumentos> ::= <expressao> { "," <expressao> }
<chamada_funcao>   ::= <IDENTIFIER> "(" [ <lista_argumentos> ] ")"


(* ---------- TIPOS, LITERAIS E COMENTÁRIOS ---------- *)

<tipo>           ::= "number" | "int" | "float" | "string" | "bool" | "void" | "list" | "dict"
<NUMBER>         ::= <digito> { <digito> } [ "." <digito> { <digito> } ]
<STRING_LITERAL> ::= '"' { <caractere_string> } '"'
<caractere_string> ::= <qualquer_char_exceto_aspas_barra_e_quebra_de_linha>
                     | "\n" | "\t" | "\r" | "\0" | '\"' | "\\"
<BOOL_LITERAL>   ::= "true" | "false"
<IDENTIFIER>     ::= ( <letra> | "_" ) { <letra> | <digito> | "_" }
<letra>          ::= "A" | ... | "Z" | "a" | ... | "z"
<digito>         ::= "0" | ... | "9"

<comentario>     ::= "#" { <qualquer_char> } <fim_de_linha>   (* descartado pelo lexer *)
```

## 4. Tabela de precedência (maior nível avaliado primeiro)

| Nível | Operadores | Associatividade |
|---|---|---|
| 7 | `()` `[]` `.` (pós-fixos) | esquerda |
| 6 | `!` `-` `+` (unários) | direita |
| 5 | `*` `/` `%` | esquerda |
| 4 | `+` `-` | esquerda |
| 3 | `==` `!=` `<` `>` `<=` `>=` | esquerda |
| 2 | `&&` | esquerda |
| 1 | `\|\|` | esquerda |

## 5. Semântica dos blocos e canais (resumo)

* `seq { ... }`: execução sequencial.
* `par { c1 c2 ... }`: cada comando filho vira uma thread (`std::thread` no C++ gerado), com `join` ao final do bloco. Threads não compartilham variáveis; a comunicação é só por mensagem.
* `fork nome [on ...] { ... }`: cria a subtarefa `nome` (pode terminar com `return valor;`). Sem `on`, roda em uma thread local. Com `on core N`, a thread é fixada no núcleo N. Com `on host "ip", porta`, a subtarefa é despachada para outro computador. `join` espera as subtarefas.
* `c_channel canal computador_1 computador_2;`: declara o canal. O primeiro computador conecta e o segundo escuta. Cada programa informa quem é com `--node` e os endereços ficam em `minipar.hosts` (padrão: localhost). Ver `docs/CANAIS.md`.
* `canal.send(a, b, c)` envia uma mensagem com 3 campos; `canal.receive()` bloqueia até chegar uma mensagem e devolve uma lista com os campos.

## 6. Biblioteca nativa (identificadores pré-declarados)

| Função | Descrição | Usada em |
|---|---|---|
| `len(x)` | tamanho de lista, string ou matriz | 4, 5, 6, 7, 11 |
| `range(n)`, `range(a, b)` | lista de inteiros | 4, 5 |
| `to_number(x)`, `to_int(x)`, `to_string(x)` | conversões | 1, 6, 11 |
| `parse_ints(s)` | lê inteiros separados por espaço | 6 |
| `exp(x)`, `sqrt(x)`, `abs(x)`, `floor(x)`, `pow(a, b)`, `max(a, b)`, `min(a, b)` | matemática | 4, 5, 9 |
| `random()` | número aleatório entre 0 e 1 | 4 |
| `fmt(x, casas)` | número como string com N casas decimais (`peso:.4f`) | 3, 4 |
| `is_digit(s)`, `is_alpha(s)` | classificação de caractere | 11 |
| `substr(s, inicio, tamanho)`, `split(s, separador)`, `trim(s)` | manipulação de strings | 6, 11 |
| `seed(n)` | fixa a semente do gerador aleatório | 4 |
| `write_file(caminho, texto)` | grava um texto em arquivo | 11 |
| `clock()` | tempo em segundos (benchmark) | 8, 9, 10 |
| `sleep(s)` | pausa em segundos | 2 |

Métodos nativos: `lista.append(v)`, `lista.push_back(v)`, `lista.pop()`, `lista.size()`,
`string.size()`, `canal.send(a, ...)`, `canal.receive()`, `canal.close()`.
