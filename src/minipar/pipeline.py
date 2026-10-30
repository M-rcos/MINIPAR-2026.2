"""Pipeline do compilador: léxico -> sintático -> semântico -> TAC -> C++."""

from __future__ import annotations

from typing import List, Optional, Tuple

from .common import MiniParError
from .lexer import Lexer
from .parser import Parser
from .parser.ast_nodes import Program
from .semantic import SemanticAnalyzer
from .tac import TACGenerator, TACProgram


class CompileErrors(Exception):
    """Erros de compilação (léxicos, sintáticos ou semânticos)."""

    def __init__(self, errors: List[MiniParError], source: str):
        super().__init__(f"{len(errors)} erro(s) de compilação")
        self.errors = errors
        self.source = source

    def format(self) -> str:
        return "\n".join(e.format(self.source) for e in self.errors)


def front_end(source: str) -> Tuple[Program, Optional[SemanticAnalyzer], List[MiniParError]]:
    """Análises léxica, sintática e semântica.

    Devolve (AST, analisador semântico ou None, erros ordenados). A análise
    semântica só roda se não houver erros léxicos ou sintáticos.
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    tree = parser.parse()
    errors = sorted(list(lexer.errors) + list(parser.errors), key=lambda e: (e.line, e.col))
    if errors:
        return tree, None, errors
    analyzer = SemanticAnalyzer()
    analyzer.analyze(tree)
    return tree, analyzer, sorted(analyzer.errors, key=lambda e: (e.line, e.col))


def to_tac(source: str) -> TACProgram:
    tree, analyzer, errors = front_end(source)
    if errors:
        raise CompileErrors(errors, source)
    return TACGenerator(analyzer).generate(tree)


def to_cpp(source: str) -> str:
    from .codegen import CppGenerator
    return CppGenerator().generate(to_tac(source))
