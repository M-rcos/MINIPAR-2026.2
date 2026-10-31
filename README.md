# Compilador MiniPar 2026.2

Projeto da disciplina de Compiladores (UFAL / IC). Implementação em Python 3,
arquitetura por componentes, gerando C++ compilado com GCC.

## Requisitos (Arch Linux)

    sudo pacman -S --needed python make gcc

Windows: instale o Python 3 e o MSYS2 (https://www.msys2.org), depois
`pacman -S mingw-w64-ucrt-x86_64-gcc` e coloque `C:\msys64\ucrt64\bin` no PATH. Use
`python run_tests.py` no lugar de `make test`. Alternativa: WSL2 com Ubuntu.

## Estrutura

    src/minipar/common/    erros compartilhados
    src/minipar/lexer/     Analisador Léxico (ILexer, Lexer, Token)
    src/minipar/parser/    Analisador Sintático (IParser, Parser), nós da AST, visitor, printer
    src/minipar/symtable/  Tabela de Símbolos (ISymbolTable, SymbolTable, Scope, Symbol)
    src/minipar/semantic/  Analisador Semântico (ISemanticAnalyzer, SemanticAnalyzer, biblioteca nativa)
    src/minipar/tac/       Gerador de Código de Três Endereços (ITACGenerator, TACGenerator, instruções)
    src/minipar/codegen/   Gerador de C++ (ICodeGenerator, CppGenerator), runtime C++ e integração com o GCC
    src/minipar/pipeline.py  encadeia todas as fases
    src/minipar/cli.py     interface de terminal
    tests/                 testes unitários
    exemplos/              programas .mp
    docs/                  gramática BNF, relatório, diagramas UML

## Uso

    make test                                                    # roda todos os testes (ou: python run_tests.py)
    make test-rapido                                             # só os testes que não compilam (menos de 1 s)
    make tokens F=exemplos/teste02_par_fatorial_fibonacci.mp     # tokenização
    make ast F=exemplos/teste03_neuronio.mp                      # árvore sintática
    make check F=exemplos/teste03_neuronio.mp                    # semântica + tabela de símbolos
    make tac F=exemplos/teste07_quicksort_iterativo.mp           # código de três endereços
    make cpp F=exemplos/teste03_neuronio.mp                      # código C++
    make run F=exemplos/teste03_neuronio.mp                      # compila com o GCC e executa
    make teste1-demo                                             # calculadora cliente/servidor (sockets)
    python3 minipar.py run exemplos/teste03_neuronio.mp          # atalho que dispensa PYTHONPATH (Windows também)
    python3 -m minipar build programa.mp -O2                     # gera o executável em build/
    PYTHONPATH=src python3 -m minipar tokens arquivo.mp --json
    PYTHONPATH=src python3 -m minipar ast arquivo.mp --json

## Estado

- [x] Etapa 1: gramática 2026.2, tratamento de erros, analisador léxico
- [x] Etapa 2: parser e AST
- [x] Etapa 3: tabela de símbolos e analisador semântico
- [x] Etapa 4: código de 3 endereços
- [x] Etapa 5: gerador C++ e integração com GCC
- [x] Etapa 6: testes 4, 5, 6 e 11 (redes neurais, quicksort recursivo, minicompilador); ver docs/PROGRAMAS_DE_TESTE.md
- [x] Etapa 7: canais com sockets (Teste 1); ver docs/CANAIS.md
- [ ] Etapa 8: fork/join em núcleos e em outro computador (Testes 8, 9 e 10)
