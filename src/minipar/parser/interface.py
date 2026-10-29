"""Interface (contrato) do componente Analisador Sintático."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..common import MiniParError
from .ast_nodes import Program


class IParser(ABC):
    """Interface fornecida pelo componente Analisador Sintático."""

    @abstractmethod
    def parse(self) -> Program:
        """Constrói a AST a partir dos tokens. Retorna a árvore (possivelmente
        parcial, se houver erros)."""

    @property
    @abstractmethod
    def errors(self) -> List[MiniParError]:
        """Erros sintáticos encontrados."""
