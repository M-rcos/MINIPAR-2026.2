"""Interface (contrato) do componente Tabela de Símbolos."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .symbols import Symbol


class ISymbolTable(ABC):
    @abstractmethod
    def enter_scope(self, name: str, isolated: bool = False):
        """Abre um novo escopo filho do escopo corrente."""

    @abstractmethod
    def exit_scope(self) -> None:
        """Fecha o escopo corrente, voltando ao pai."""

    @abstractmethod
    def define(self, symbol: Symbol) -> Optional[Symbol]:
        """Insere no escopo corrente. Devolve o símbolo já existente (duplicado) ou None."""

    @abstractmethod
    def resolve(self, name: str) -> Optional[Symbol]:
        """Procura o nome do escopo corrente até o global."""
