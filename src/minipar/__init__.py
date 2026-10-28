"""Compilador da linguagem MiniPar 2026.2 (orientada a objetos, com PAR, fork/join e canais).

Arquitetura baseada em componentes de software. Cada componente fica em um
subpacote e expõe uma interface (classe abstrata) para os demais componentes:

    common/    -> erros e utilitários compartilhados
    lexer/     -> Analisador Léxico            (ILexer)
    parser/    -> Analisador Sintático + AST   (a implementar)
    symtable/  -> Tabela de Símbolos           (a implementar)
    semantic/  -> Analisador Semântico         (a implementar)
    tac/       -> Gerador de Código de 3 Endereços (a implementar)
    codegen/   -> Gerador de Código C++        (a implementar)
"""

__version__ = "2026.2.0"
