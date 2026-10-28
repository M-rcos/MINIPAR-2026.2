"""Interface (contrato) do componente Analisador Léxico."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..common import MiniParError
from .tokens import Token


class ILexer(ABC):
    """Interface fornecida pelo componente Analisador Léxico."""

    @abstractmethod
    def tokenize(self) -> List[Token]:
        """Converte o código-fonte em uma lista de tokens (terminada em EOF)."""

    @property
    @abstractmethod
    def errors(self) -> List[MiniParError]:
        """Erros léxicos encontrados durante a análise."""
