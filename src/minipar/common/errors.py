"""Tratamento de erros do compilador MiniPar 2026.2.

Todos os erros carregam fase, mensagem, linha e coluna. O método ``format``
produz uma mensagem didática, mostrando a linha do código-fonte e um
apontador (^) para a coluna do problema.
"""

from __future__ import annotations

from typing import List, Optional


class MiniParError(Exception):
    """Erro base. Cada fase do compilador define uma subclasse."""

    phase = "Erro"

    def __init__(self, message: str, line: int = 0, col: int = 0):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col

    def format(self, source: Optional[str] = None) -> str:
        head = f"[{self.phase}] linha {self.line}, coluna {self.col}: {self.message}"
        if source is None or self.line < 1:
            return head
        lines = source.splitlines()
        if self.line > len(lines):
            return head
        text = lines[self.line - 1].replace("\t", " ")
        pointer = " " * max(self.col - 1, 0) + "^"
        return f"{head}\n    {text}\n    {pointer}"

    def to_dict(self) -> dict:
        return {
            "phase": self.phase,
            "message": self.message,
            "line": self.line,
            "col": self.col,
        }


class LexicalError(MiniParError):
    phase = "Erro Léxico"


class ParseError(MiniParError):
    phase = "Erro Sintático"


class SemanticError(MiniParError):
    phase = "Erro Semântico"


class ErrorReporter:
    """Coletor de erros compartilhado entre as fases.

    Permite que o compilador continue após um erro (modo de recuperação) e
    mostre vários problemas de uma só vez.
    """

    def __init__(self) -> None:
        self.errors: List[MiniParError] = []

    def report(self, error: MiniParError) -> None:
        self.errors.append(error)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def format_all(self, source: Optional[str] = None) -> str:
        return "\n".join(e.format(source) for e in self.errors)
