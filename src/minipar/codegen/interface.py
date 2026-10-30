"""Interface (contrato) do componente Gerador de Código C++."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..tac import TACProgram


class ICodeGenerator(ABC):
    @abstractmethod
    def generate(self, program: TACProgram) -> str:
        """Traduz o código de três endereços para um arquivo-fonte C++."""
