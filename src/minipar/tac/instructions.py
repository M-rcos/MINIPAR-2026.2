"""Instruções do Código Intermediário de Três Endereços (TAC) da MiniPar 2026.2.

Cada instrução tem no máximo três endereços (dois operandos e um destino).
Operandos são: variáveis, temporários (t0, t1, ...), constantes numéricas,
strings entre aspas, true, false e null.

Conjunto de instruções (formato textual):

  x = a                  cópia                       x = a op b     operação binária
  x = -a   x = !a        operação unária
  label:                 rótulo                      goto L         desvio incondicional
  if a op b goto L       desvio por comparação       if a goto L    desvio se verdadeiro
  ifFalse a goto L       desvio se falso
  param a                empilha argumento           x = call f, n  chamada de função
  x = callm o.m, n       chamada de método           return [a]     retorno
  x = o.campo            leitura de atributo         o.campo = a    escrita de atributo
  x = v[i]   v[i] = a    acesso a lista/string
  x = new C              cria objeto                 x = new_list   x = new_matrix r, c, v
  append v, a            x = pop v   x = size v      print a, b, ...   x = input [p]
  x = new_channel h, p   send ch, a, ...             x = receive ch    close ch
  par_begin / par_end    bloco paralelo (par_end espera todas as tarefas do bloco)
  task nome -> f(a, b)   subtarefa do par: executa a função f com cópias de a e b
  fork nome [on core N | on host H, P] -> f(a, b)   subtarefa independente
  join [nome, ...]       espera subtarefas        x = join nome   espera e recebe o resultado

As subtarefas (par e fork) são funções separadas, chamadas "tarefas" (nome com $,
ex.: main$f1). Elas recebem como parâmetros cópias das variáveis locais que usam.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

_NUMBER = re.compile(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$")
_TEMP = re.compile(r"^t\d+$")


def is_literal(tok: str) -> bool:
    return bool(_NUMBER.match(tok)) or tok.startswith('"') or tok in ("true", "false", "null")


def is_temp(tok: str) -> bool:
    return bool(_TEMP.match(tok))


@dataclass
class TACInstr:
    op: str
    dst: Optional[str] = None
    a: Optional[str] = None
    b: Optional[str] = None
    c: Optional[str] = None
    extra: Optional[str] = None          # operador, número de argumentos etc.
    args: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return format_instr(self)

    def reads(self) -> List[Optional[str]]:
        """Campos que contêm operandos lidos (variáveis ou literais)."""
        op = self.op
        if op in ("assign", "unop", "pop", "size", "receive", "input", "if_true", "if_false",
                  "param", "return", "close", "callm", "load_member"):
            return [self.a]
        if op in ("binop", "load_index", "new_channel", "append", "if_rel"):
            return [self.a, self.b]
        if op == "store_member":
            return [self.a, self.c]
        if op in ("store_index", "new_matrix"):
            return [self.a, self.b, self.c]
        if op == "print":
            return list(self.args)
        if op == "send":
            return [self.a] + list(self.args)
        if op == "fork":
            return [self.b, self.c] + list(self.args)
        if op == "task":
            return list(self.args)
        return []

    def writes(self) -> List[Optional[str]]:
        if self.op in ("assign", "binop", "unop", "call", "callm", "load_member", "load_index",
                       "new_obj", "new_list", "pop", "size", "new_matrix", "new_channel",
                       "input", "receive", "join_value"):
            return [self.dst]
        return []

    def variables(self) -> Set[str]:
        """Nomes de variáveis (não literais) usados pela instrução."""
        names: Set[str] = set()
        for tok in self.reads() + self.writes():
            if tok is not None and not is_literal(tok):
                names.add(tok)
        return names

    def to_dict(self) -> dict:
        data = {"op": self.op, "text": format_instr(self)}
        for key in ("dst", "a", "b", "c", "extra"):
            value = getattr(self, key)
            if value is not None:
                data[key] = value
        if self.args:
            data["args"] = list(self.args)
        return data


def format_instr(i: TACInstr) -> str:
    op = i.op
    left = f"{i.dst} = " if i.dst else ""
    if op == "assign":
        return f"{i.dst} = {i.a}"
    if op == "binop":
        return f"{i.dst} = {i.a} {i.extra} {i.b}"
    if op == "unop":
        return f"{i.dst} = {i.extra}{i.a}"
    if op == "label":
        return f"{i.dst}:"
    if op == "goto":
        return f"goto {i.dst}"
    if op == "if_rel":
        return f"if {i.a} {i.extra} {i.b} goto {i.dst}"
    if op == "if_true":
        return f"if {i.a} goto {i.dst}"
    if op == "if_false":
        return f"ifFalse {i.a} goto {i.dst}"
    if op == "param":
        return f"param {i.a}"
    if op == "call":
        return f"{left}call {i.a}, {i.b}"
    if op == "callm":
        return f"{left}callm {i.a}.{i.b}, {i.extra}"
    if op == "return":
        return "return" + (f" {i.a}" if i.a is not None else "")
    if op == "load_member":
        return f"{i.dst} = {i.a}.{i.b}"
    if op == "store_member":
        return f"{i.a}.{i.b} = {i.c}"
    if op == "load_index":
        return f"{i.dst} = {i.a}[{i.b}]"
    if op == "store_index":
        return f"{i.a}[{i.b}] = {i.c}"
    if op == "new_obj":
        return f"{i.dst} = new {i.a}"
    if op == "new_list":
        return f"{i.dst} = new_list"
    if op == "append":
        return f"append {i.a}, {i.b}"
    if op == "pop":
        return f"{i.dst} = pop {i.a}"
    if op == "size":
        return f"{i.dst} = size {i.a}"
    if op == "new_matrix":
        return f"{i.dst} = new_matrix {i.a}, {i.b}, {i.c}"
    if op == "new_channel":
        return f"{i.dst} = new_channel {i.a}, {i.b}"
    if op == "print":
        return "print" + (" " + ", ".join(i.args) if i.args else "")
    if op == "input":
        return f"{i.dst} = input" + (f" {i.a}" if i.a is not None else "")
    if op == "send":
        return f"send {i.a}" + "".join(f", {x}" for x in i.args)
    if op == "receive":
        return f"{i.dst} = receive {i.a}"
    if op == "close":
        return f"close {i.a}"
    if op == "par_begin":
        return "par_begin"
    if op == "par_end":
        return "par_end"
    if op == "task":
        return f"task {i.dst} -> {i.a}({', '.join(i.args)})"
    if op == "fork":
        if i.a == "core":
            where = f" on core {i.b}"
        elif i.a == "host":
            where = f" on host {i.b}" + (f", {i.c}" if i.c is not None else "")
        else:
            where = ""
        return f"fork {i.dst}{where} -> {i.extra}({', '.join(i.args)})"
    if op == "join":
        return "join" + (" " + ", ".join(i.args) if i.args else "")
    if op == "join_value":
        return f"{i.dst} = join {i.a}"
    return f"{op} {i.dst} {i.a} {i.b} {i.c}"


@dataclass
class TACFunction:
    name: str
    params: List[str]
    instrs: List[TACInstr] = field(default_factory=list)
    is_task: bool = False          # função criada a partir de um par/fork

    def format_lines(self) -> List[str]:
        kind = "task" if self.is_task else "func"
        lines = [f"{kind} {self.name}({', '.join(self.params)}):"]
        depth = 0
        for ins in self.instrs:
            if ins.op == "par_end":
                depth -= 1
            if ins.op == "label":
                lines.append(f"  {ins}")
            else:
                lines.append("    " + "  " * depth + str(ins))
            if ins.op == "par_begin":
                depth += 1
        lines.append("endfunc")
        return lines

    def to_dict(self) -> dict:
        return {"name": self.name, "params": list(self.params), "is_task": self.is_task,
                "instrs": [i.to_dict() for i in self.instrs]}


@dataclass
class TACClass:
    name: str
    superclass: Optional[str]
    fields: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)

    def format_lines(self) -> List[str]:
        head = f"class {self.name}" + (f" extends {self.superclass}" if self.superclass else "") + ":"
        lines = [head]
        lines += [f"    field {f}" for f in self.fields]
        lines += [f"    method {m}" for m in self.methods]
        lines.append("endclass")
        return lines


@dataclass
class TACProgram:
    globals: List[str] = field(default_factory=list)
    classes: List[TACClass] = field(default_factory=list)
    channels: List[Tuple[str, str, str]] = field(default_factory=list)
    functions: List[TACFunction] = field(default_factory=list)

    def function(self, name: str) -> Optional[TACFunction]:
        for f in self.functions:
            if f.name == name:
                return f
        return None

    def format(self) -> str:
        blocks: List[str] = []
        for c in self.classes:
            blocks.append("\n".join(c.format_lines()))
        header: List[str] = [f"channel {n} {a} {b}" for n, a, b in self.channels]
        header += [f"global {g}" for g in self.globals]
        if header:
            blocks.append("\n".join(header))
        for f in self.functions:
            blocks.append("\n".join(f.format_lines()))
        return "\n\n".join(blocks) + "\n"

    def to_dict(self) -> dict:
        return {
            "globals": list(self.globals),
            "channels": [list(c) for c in self.channels],
            "classes": [
                {"name": c.name, "superclass": c.superclass,
                 "fields": c.fields, "methods": c.methods}
                for c in self.classes
            ],
            "functions": [f.to_dict() for f in self.functions],
        }
