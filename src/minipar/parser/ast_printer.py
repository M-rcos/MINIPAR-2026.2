"""Exibição da AST: árvore em texto (terminal) e dicionário (JSON / web)."""

from __future__ import annotations

from dataclasses import fields
from typing import Any, Dict, List

from .ast_nodes import Node

_HIDDEN = ("line", "col")


def _is_scalar(value: Any) -> bool:
    if isinstance(value, list):
        return len(value) > 0 and all(not isinstance(v, Node) for v in value)
    return not isinstance(value, Node)


def _label(node: Node) -> str:
    attrs = []
    for f in fields(node):
        if f.name in _HIDDEN:
            continue
        value = getattr(node, f.name)
        if isinstance(value, list) and len(value) == 0:
            continue
        if value is None:
            continue
        if _is_scalar(value):
            attrs.append(f"{f.name}={value!r}")
    name = node.__class__.__name__
    return name + (" " + " ".join(attrs) if attrs else "")


def _children(node: Node):
    result = []
    for f in fields(node):
        if f.name in _HIDDEN:
            continue
        value = getattr(node, f.name)
        if isinstance(value, Node):
            result.append((f.name, value))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, Node):
                    result.append((f"{f.name}[{i}]", item))
    return result


def format_tree(root: Node) -> str:
    """Árvore em texto com caracteres de caixa, uma linha por nó."""
    lines: List[str] = [_label(root)]

    def walk(node: Node, prefix: str) -> None:
        children = _children(node)
        for i, (tag, child) in enumerate(children):
            last = i == len(children) - 1
            lines.append(f"{prefix}{'└── ' if last else '├── '}{tag}: {_label(child)}")
            walk(child, prefix + ("    " if last else "│   "))

    walk(root, "")
    return "\n".join(lines)


def to_dict(node: Node) -> Dict[str, Any]:
    """Converte a AST em estrutura serializável (JSON)."""
    data: Dict[str, Any] = {
        "type": node.__class__.__name__,
        "line": node.line,
        "col": node.col,
    }
    for f in fields(node):
        if f.name in _HIDDEN:
            continue
        value = getattr(node, f.name)
        if isinstance(value, Node):
            data[f.name] = to_dict(value)
        elif isinstance(value, list):
            data[f.name] = [to_dict(v) if isinstance(v, Node) else v for v in value]
        else:
            data[f.name] = value
    return data
