"""Tabela de Símbolos hierárquica (pilha de escopos)."""

from __future__ import annotations

from typing import List, Optional, Tuple

from .interface import ISymbolTable
from .scope import Scope
from .symbols import Symbol


class SymbolTable(ISymbolTable):
    def __init__(self) -> None:
        self.global_scope = Scope("global")
        self.current = self.global_scope

    # ---- escopos ----------------------------------------------------
    def enter_scope(self, name: str, isolated: bool = False) -> Scope:
        self.current = Scope(name, self.current, isolated)
        return self.current

    def exit_scope(self) -> None:
        if self.current.parent is not None:
            self.current = self.current.parent

    # ---- símbolos ---------------------------------------------------
    def define(self, symbol: Symbol) -> Optional[Symbol]:
        return self.current.define(symbol)

    def resolve(self, name: str) -> Optional[Symbol]:
        found = self.current.lookup(name)
        return found[0] if found else None

    def resolve_with_scope(self, name: str) -> Optional[Tuple[Symbol, Scope]]:
        return self.current.lookup(name)

    def crosses_isolation(self, target_scope: Scope) -> bool:
        """True se, saindo do escopo corrente até ``target_scope``, atravessa uma
        fronteira de fork/par (ou seja, o símbolo pertence a outra tarefa)."""
        scope: Optional[Scope] = self.current
        while scope is not None:
            if scope is target_scope:
                return False
            if scope.isolated:
                return True
            scope = scope.parent
        return False

    # ---- exibição ---------------------------------------------------
    def to_dict(self) -> dict:
        return self.global_scope.to_dict()

    def format(self) -> str:
        lines: List[str] = []

        def has_symbols(scope: Scope) -> bool:
            return bool(scope.symbols) or any(has_symbols(c) for c in scope.children)

        def row(pad: str, sym: Symbol) -> str:
            return f"{pad}  {sym.name:<18} {sym.kind:<10} {sym.signature():<28} linha {sym.line}"

        def walk(scope: Scope, indent: int) -> None:
            pad = "    " * indent
            flag = "  [tarefa isolada]" if scope.isolated else ""
            lines.append(f"{pad}Escopo: {scope.name}{flag}")
            for sym in scope.symbols.values():
                lines.append(row(pad, sym))
                info = sym.class_info
                if info is not None:
                    if info.superclass:
                        lines.append(f"{pad}      herda de {info.superclass}")
                    for member in list(info.attributes.values()) + list(info.methods.values()):
                        lines.append(row(pad + "    ", member))
            for child in scope.children:
                if has_symbols(child):
                    walk(child, indent + 1)

        walk(self.global_scope, 0)
        return "\n".join(lines)
