"""Interface (contrato) do componente Analisador Semântico."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..common import MiniParError
from ..parser.ast_nodes import Program
from ..symtable import SymbolTable


class ISemanticAnalyzer(ABC):
    @abstractmethod
    def analyze(self, program: Program) -> List[MiniParError]:
        """Verifica a AST e devolve a lista de erros semânticos."""

    @property
    @abstractmethod
    def symbol_table(self) -> SymbolTable:
        """Tabela de símbolos construída durante a análise."""
