"""Nós da Árvore Sintática Abstrata (AST) da linguagem MiniPar 2026.2.

Todos os nós guardam linha e coluna (para mensagens de erro nas fases
seguintes) e usam ``eq=False``: a comparação é por identidade, o que permite
usá-los como chave de dicionário (ex.: tabela de tipos do semântico).

Hierarquia:
    Node
     |- Program, Param, Allocation
     |- Stmt  (comandos e declarações)
     |- Expr  (expressões)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass(eq=False)
class Node:
    line: int = field(default=0, kw_only=True, repr=False)
    col: int = field(default=0, kw_only=True, repr=False)


@dataclass(eq=False)
class Stmt(Node):
    """Comando ou declaração."""


@dataclass(eq=False)
class Expr(Node):
    """Expressão (produz um valor)."""


# ----------------------------------------------------------------------
# Estrutura global
# ----------------------------------------------------------------------
@dataclass(eq=False)
class Program(Node):
    body: List[Node] = field(default_factory=list)


# ----------------------------------------------------------------------
# Declarações
# ----------------------------------------------------------------------
@dataclass(eq=False)
class VarDecl(Stmt):
    name: str
    type_name: Optional[str] = None      # None quando declarada com "var"
    init: Optional[Expr] = None


@dataclass(eq=False)
class Param(Node):
    name: str
    type_name: Optional[str] = None


@dataclass(eq=False)
class FuncDecl(Stmt):
    name: str
    params: List[Param]
    body: "Block"


@dataclass(eq=False)
class ClassDecl(Stmt):
    name: str
    superclass: Optional[str]
    members: List[Node] = field(default_factory=list)   # VarDecl | FuncDecl


@dataclass(eq=False)
class ChannelDecl(Stmt):
    """c_channel canal computador_1 computador_2;"""
    name: str
    endpoint_a: str
    endpoint_b: str


# ----------------------------------------------------------------------
# Blocos SEQ / PAR / FORK / JOIN
# ----------------------------------------------------------------------
@dataclass(eq=False)
class Block(Stmt):
    statements: List[Node] = field(default_factory=list)
    explicit_seq: bool = False           # True quando escrito com "seq { }"


@dataclass(eq=False)
class ParBlock(Stmt):
    statements: List[Node] = field(default_factory=list)


@dataclass(eq=False)
class Allocation(Node):
    """Onde a subtarefa do fork executa: 'core N' ou 'host "ip", porta'."""
    kind: str                            # "core" | "host"
    target: Expr
    port: Optional[Expr] = None


@dataclass(eq=False)
class Fork(Stmt):
    name: str
    allocation: Optional[Allocation]
    body: Block


@dataclass(eq=False)
class Join(Stmt):
    names: List[str] = field(default_factory=list)   # vazio = todas


# ----------------------------------------------------------------------
# Comandos
# ----------------------------------------------------------------------
@dataclass(eq=False)
class Assign(Stmt):
    target: Expr                         # Identifier | Member | Index
    op: str                              # = += -= *= /=
    value: Expr


@dataclass(eq=False)
class If(Stmt):
    cond: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt] = None


@dataclass(eq=False)
class While(Stmt):
    cond: Expr
    body: Stmt


@dataclass(eq=False)
class DoWhile(Stmt):
    body: Stmt
    cond: Expr


@dataclass(eq=False)
class For(Stmt):
    init: Optional[Node]
    cond: Optional[Expr]
    update: Optional[Node]
    body: Stmt


@dataclass(eq=False)
class ForIn(Stmt):
    var_name: str
    iterable: Expr
    body: Stmt


@dataclass(eq=False)
class Print(Stmt):
    args: List[Expr] = field(default_factory=list)


@dataclass(eq=False)
class Send(Stmt):
    """Forma de comando: send(canal, valor, ...);"""
    args: List[Expr] = field(default_factory=list)


@dataclass(eq=False)
class Return(Stmt):
    value: Optional[Expr] = None


@dataclass(eq=False)
class Break(Stmt):
    pass


@dataclass(eq=False)
class Continue(Stmt):
    pass


@dataclass(eq=False)
class ExprStmt(Stmt):
    """Chamada de função ou de método usada como comando."""
    expr: Expr


# ----------------------------------------------------------------------
# Expressões
# ----------------------------------------------------------------------
@dataclass(eq=False)
class Literal(Expr):
    kind: str                            # "number" | "string" | "bool" | "null"
    value: Any = None


@dataclass(eq=False)
class Identifier(Expr):
    name: str


@dataclass(eq=False)
class This(Expr):
    pass


@dataclass(eq=False)
class Binary(Expr):
    op: str
    left: Expr
    right: Expr


@dataclass(eq=False)
class Unary(Expr):
    op: str
    operand: Expr


@dataclass(eq=False)
class Call(Expr):
    name: str
    args: List[Expr] = field(default_factory=list)


@dataclass(eq=False)
class MethodCall(Expr):
    obj: Expr
    name: str
    args: List[Expr] = field(default_factory=list)


@dataclass(eq=False)
class Member(Expr):
    obj: Expr
    name: str


@dataclass(eq=False)
class Index(Expr):
    obj: Expr
    index: Expr


@dataclass(eq=False)
class New(Expr):
    class_name: str
    args: List[Expr] = field(default_factory=list)


@dataclass(eq=False)
class ChannelExpr(Expr):
    """c_channel("ip", porta)"""
    host: Expr
    port: Expr


@dataclass(eq=False)
class Receive(Expr):
    """receive(canal)"""
    channel: Expr


@dataclass(eq=False)
class Input(Expr):
    prompt: Optional[Expr] = None


@dataclass(eq=False)
class ListLiteral(Expr):
    elements: List[Expr] = field(default_factory=list)


@dataclass(eq=False)
class JoinExpr(Expr):
    """join nome: espera a subtarefa (fork) e devolve o valor do seu return."""
    name: str


@dataclass(eq=False)
class MatrixExpr(Expr):
    rows: Expr
    cols: Expr
    fill: Expr
