"""Escopos léxicos aninhados."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .symbols import Symbol


class Scope:
    def __init__(self, name: str, parent: Optional["Scope"] = None, isolated: bool = False):
        self.name = name
        self.parent = parent
        self.isolated = isolated           # fronteira de fork/par (sem memória compartilhada)
        self.symbols: Dict[str, Symbol] = {}
        self.children: List["Scope"] = []
        if parent is not None:
            parent.children.append(self)

    def define(self, symbol: Symbol) -> Optional[Symbol]:
        """Insere o símbolo. Se o nome já existir neste escopo, não altera nada
        e devolve o símbolo existente (permite reportar redeclaração)."""
        existing = self.symbols.get(symbol.name)
        if existing is not None:
            return existing
        self.symbols[symbol.name] = symbol
        return None

    def lookup_local(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)

    def lookup(self, name: str) -> Optional[Tuple[Symbol, "Scope"]]:
        scope: Optional[Scope] = self
        while scope is not None:
            sym = scope.symbols.get(name)
            if sym is not None:
                return sym, scope
            scope = scope.parent
        return None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "isolated": self.isolated,
            "symbols": [s.to_dict() for s in self.symbols.values()],
            "children": [c.to_dict() for c in self.children],
        }
