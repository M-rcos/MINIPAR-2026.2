# Compilador MiniPar 2026.2

Projeto da disciplina de Compiladores (UFAL / IC). Implementação em Python 3,
arquitetura por componentes, gerando C++ compilado com GCC.

## Requisitos (Arch Linux)

    sudo pacman -S --needed python make gcc

## Estrutura

    src/minipar/common/    erros compartilhados
    src/minipar/lexer/     Analisador Léxico (ILexer, Lexer, Token)
    src/minipar/cli.py     interface de terminal
    tests/                 testes unitários
    exemplos/              programas .mp
    docs/                  gramática BNF, relatório, diagramas UML

## Uso

    make test                                                    # roda os testes
    make tokens F=exemplos/teste02_par_fatorial_fibonacci.mp     # tokenização
    PYTHONPATH=src python3 -m minipar tokens arquivo.mp --json

## Estado

- [x] Etapa 1: gramática 2026.2, tratamento de erros, analisador léxico
- [ ] Etapa 2: parser e AST
- [ ] Etapa 3: tabela de símbolos e analisador semântico
- [ ] Etapa 4: código de 3 endereços
- [ ] Etapa 5: gerador C++ e integração com GCC
