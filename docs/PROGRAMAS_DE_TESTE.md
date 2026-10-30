# Programas de Teste da MiniPar 2026.2: situação e como executar

Todos os comandos rodam na pasta do projeto. `make run F=arquivo.mp` compila com o GCC e executa.

| Teste | Programa | Situação | Como executar |
|---|---|---|---|
| 1 | `teste01_servidor.mp` e `teste01_cliente.mp` | Compila; os canais com sockets entram na Etapa 7 | (Etapa 7) |
| 2 | `teste02_par_fatorial_fibonacci.mp` | Executa em threads | `make run F=exemplos/teste02_par_fatorial_fibonacci.mp` |
| 3 | `teste03_neuronio.mp` | Saída idêntica ao enunciado (51 iterações) | `make run F=exemplos/teste03_neuronio.mp` |
| 4 | `teste04_rede_xor.mp` | Converge (cerca de 0,3 s com `-O2`) | `python3 -m minipar run exemplos/teste04_rede_xor.mp -O2` |
| 5 | `teste05_recomendacao.mp` | Saída idêntica ao enunciado | `make run F=exemplos/teste05_recomendacao.mp` |
| 6 | `teste06_quicksort_recursivo.mp` | Saída idêntica ao enunciado, com validação da entrada | `echo "10 -3 -40 80 70 -100" \| python3 -m minipar run exemplos/teste06_quicksort_recursivo.mp` |
| 7 | `teste07_quicksort_iterativo.mp` | Saída idêntica ao enunciado; TAC em `exemplos/tac/` | `make run F=exemplos/teste07_quicksort_iterativo.mp` |
| 8, 9, 10 | (a escrever) | Etapa 8 (fork/join em núcleos) | |
| 11 | `teste11_minicompilador.mp` | Saída idêntica ao enunciado; gera o `.arm` | veja abaixo |

## Teste 4: observações

* Os pesos iniciais são aleatórios (como no Python original), então os números mudam a cada execução. Em todas as execuções feitas a rede aprendeu o XOR (saídas próximas de 0, 1, 1, 0), por exemplo `0.0091, 0.9765, 0.9758, 0.0295`.
* Para repetir exatamente uma execução, coloque `seed(3);` na primeira linha do programa. A função nativa `seed(n)` fixa a semente.

## Teste 11: como executar e conferir no CPUlator

```
python3 -m minipar build exemplos/teste11_minicompilador.mp -o minicompilador
./minicompilador          # digite: ((2+4)*7)-(5*4)
```

O programa grava o assembly gerado em `Codigo-Assembly-ARMV7.arm` (na pasta onde foi executado). Exemplos já prontos em `exemplos/arm/`.

Para conferir: abra o CPUlator (ARMv7, DE1-SoC), cole o conteúdo do `.arm` em *Editor*, clique em *Compile and Load* e depois *Continue*. O resultado fica no último registrador usado:

| Expressão | Arquivo | Registrador final | Valor esperado |
|---|---|---|---|
| `((2+4)*7)-(5*4)` | `expressao1.arm` | `r8` | `0x00000016` (22) |
| `((10 -8*7)+4)*2` | `expressao2.arm` | `r8` | `0xFFFFFFAC` (-84) |

O arquivo da expressão 1 é idêntico, byte a byte, ao `Codigo-Assembly-ARMV7.arm.txt` do enunciado, que rodou no CPUlator. A expressão 2 usa as mesmas instruções (`MOV`, `MUL`, `SUB`, `ADD`); os testes automáticos confirmam o formato de cada linha, mas a execução no CPUlator deve ser conferida manualmente.

Limites herdados do programa original em Java: a divisão não gera instrução (o ARMv7 do CPUlator não tem divisão por hardware garantida) e é marcada com um comentário; variáveis e decimais viram `MOV rN, #0` e valor truncado, com aviso no comentário. Como melhoria, números acima de 255 usam `LDR rN, =valor`, porque o `MOV` só aceita imediatos de 8 bits.

## Testes automatizados

`make test` executa tudo (229 testes, cerca de 50 s). Os testes de `tests/test_programas.py` compilam cada programa com o g++ e comparam a saída com a do enunciado.
