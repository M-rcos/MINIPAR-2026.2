"""Visitante genérico da AST (usado pelo semântico, TAC e gerador C++)."""

from __future__ import annotations

from dataclasses import fields
from typing import Any

from .ast_nodes import Node


class NodeVisitor:
    """Despacha para ``visit_<NomeDoNo>``; se não existir, visita os filhos."""

    def visit(self, node: Node) -> Any:
        method = getattr(self, "visit_" + node.__class__.__name__, self.generic_visit)
        return method(node)

    def generic_visit(self, node: Node) -> Any:
        for child in iter_children(node):
            self.visit(child)


def iter_children(node: Node):
    """Itera sobre os filhos diretos (nós) de um nó, na ordem dos campos."""
    for f in fields(node):
        value = getattr(node, f.name)
        if isinstance(value, Node):
            yield value
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, Node):
                    yield item
