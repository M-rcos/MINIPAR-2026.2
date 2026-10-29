"""Interface (contrato) do componente Gerador de Código Intermediário (TAC)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..parser.ast_nodes import Program
from .instructions import TACProgram


class ITACGenerator(ABC):
    @abstractmethod
    def generate(self, program: Program) -> TACProgram:
        """Traduz a AST (já validada pelo semântico) para código de três endereços."""
