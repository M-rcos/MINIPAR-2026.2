"""Gerador de Código C++ a partir do código de três endereços (TAC).

Estratégia de tradução:

  * Todo valor da MiniPar é um ``mp::Value`` (runtime dinâmico: número, string,
    bool, lista, objeto, canal). Isso reproduz a semântica da linguagem mesmo
    onde o tipo só é conhecido em tempo de execução (parâmetros sem tipo).
  * Cada função/método TAC vira uma função C++ ``fn_<nome>``. Todas as
    variáveis e temporários são declarados no início da função, o que permite
    traduzir os desvios do TAC diretamente para ``goto`` sem violar as regras
    de inicialização do C++.
  * ``param`` + ``call`` viram uma chamada C++ com os argumentos na ordem.
  * ``par``/``fork`` viram lambdas executadas em threads (``mp::TaskGroup`` e
    ``mp::ForkTable``). A captura por cópia ([=]) faz cada subtarefa trabalhar
    com a sua própria cópia das variáveis locais, como processos independentes.
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, Optional, Set

from ..tac import TACFunction, TACInstr, TACProgram
from .interface import ICodeGenerator

_NUMBER = re.compile(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$")
_TEMP = re.compile(r"^t\d+$")

BUILTINS = {
    "len", "range", "to_number", "to_int", "to_string", "parse_ints", "exp", "sqrt",
    "abs", "floor", "pow", "max", "min", "random", "fmt", "is_digit", "is_alpha",
    "substr", "split", "clock", "sleep",
}

_BIN = {"+": "add", "-": "sub", "*": "mul", "/": "div", "%": "mod"}
_REL = {"==": "eq", "!=": "ne", "<": "lt", ">": "gt", "<=": "le", ">=": "ge"}


def fn_name(tac_name: str) -> str:
    return "fn_" + tac_name.replace(".", "_D_")


def var_name(name: str) -> str:
    return name if _TEMP.match(name) else "v_" + name


def cstring(text: str) -> str:
    """Literal de string C++ seguro (UTF-8 em octal, sem armadilhas de escape)."""
    out = []
    for b in text.encode("utf-8"):
        ch = chr(b)
        if ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "\r":
            out.append("\\r")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "?" or b < 32 or b >= 127:
            out.append("\\%03o" % b)
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def is_literal(tok: str) -> bool:
    return (bool(_NUMBER.match(tok)) or tok.startswith('"')
            or tok in ("true", "false", "null"))


def opd(tok: Optional[str]) -> str:
    """Operando TAC -> expressão C++ do tipo mp::Value."""
    if tok is None:
        return "mp::Value()"
    if _NUMBER.match(tok):
        return f"mp::Value({float(tok)!r})"
    if tok.startswith('"'):
        text = json.loads(tok)
        return f"mp::Value(std::string({cstring(text)}, {len(text.encode('utf-8'))}))"
    if tok == "true":
        return "mp::Value(true)"
    if tok == "false":
        return "mp::Value(false)"
    if tok == "null":
        return "mp::Value()"
    if tok == "this":
        return "self"
    return var_name(tok)


def _operand_fields(i: TACInstr) -> List[Optional[str]]:
    """Campos da instrução que contêm operandos (variáveis ou literais)."""
    op = i.op
    if op in ("assign", "unop", "pop", "size", "receive", "input"):
        return [i.a]
    if op in ("binop", "load_index", "new_channel", "append"):
        return [i.a, i.b]
    if op in ("if_rel",):
        return [i.a, i.b]
    if op in ("if_true", "if_false", "param", "return", "close"):
        return [i.a]
    if op == "callm":
        return [i.a]
    if op == "load_member":
        return [i.a]
    if op == "store_member":
        return [i.a, i.c]
    if op == "store_index":
        return [i.a, i.b, i.c]
    if op == "new_matrix":
        return [i.a, i.b, i.c]
    if op == "print":
        return list(i.args)
    if op == "send":
        return [i.a] + list(i.args)
    if op == "fork":
        return [i.b, i.c]
    return []


def _dest_fields(i: TACInstr) -> List[Optional[str]]:
    if i.op in ("assign", "binop", "unop", "call", "callm", "load_member", "load_index",
                "new_obj", "new_list", "pop", "size", "new_matrix", "new_channel",
                "input", "receive"):
        return [i.dst]
    return []


class CppGenerator(ICodeGenerator):
    def __init__(self) -> None:
        self.lines: List[str] = []
        self.indent = 1
        self.group_n = 0
        self.group_stack: List[int] = []
        self.pending: List[str] = []
        self.user_funcs: Set[str] = set()
        self.globals: Set[str] = set()

    # ------------------------------------------------------------------
    def generate(self, program: TACProgram) -> str:
        self.user_funcs = {f.name for f in program.functions}
        self.globals = set(program.globals) | {c[0] for c in program.channels}
        out: List[str] = []
        out.append("// Código gerado automaticamente pelo compilador MiniPar 2026.2")
        out.append('#include "minipar_runtime.hpp"')
        out.append("")
        out.append("// ---- variáveis globais ----")
        for g in sorted(self.globals):
            out.append(f"static mp::Value {var_name(g)};")
        out.append("")
        out.append("// ---- protótipos ----")
        for f in program.functions:
            out.append(self._prototype(f) + ";")
        out.append("")
        for f in program.functions:
            out.extend(self._function(f))
            out.append("")
        out.extend(self._registration(program))
        out.extend(self._main(program))
        return "\n".join(out) + "\n"

    # ------------------------------------------------------------------
    def _params(self, f: TACFunction) -> str:
        ps = []
        for p in f.params:
            ps.append("mp::Value self" if p == "this" else f"mp::Value {var_name(p)}")
        return ", ".join(ps)

    def _prototype(self, f: TACFunction) -> str:
        return f"mp::Value {fn_name(f.name)}({self._params(f)})"

    def _locals_of(self, f: TACFunction) -> List[str]:
        names: Set[str] = set()
        for ins in f.instrs:
            for tok in _operand_fields(ins) + _dest_fields(ins):
                if tok is None or is_literal(tok) or tok == "this":
                    continue
                names.add(tok)
        names -= set(f.params)
        names -= self.globals
        return sorted(names, key=lambda n: (not _TEMP.match(n), n))

    # ------------------------------------------------------------------
    def _function(self, f: TACFunction) -> List[str]:
        self.lines = []
        self.indent = 1
        self.group_n = 0
        self.group_stack = []
        self.pending = []

        used_labels = {i.dst for i in f.instrs
                       if i.op in ("goto", "if_rel", "if_true", "if_false")}
        local_vars = self._locals_of(f)
        has_fork = any(i.op == "fork" for i in f.instrs)

        self._emit(f"// {f.name}")
        if local_vars:
            # declara em blocos de 8 por linha
            for k in range(0, len(local_vars), 8):
                chunk = ", ".join(var_name(v) for v in local_vars[k:k + 8])
                self._emit(f"mp::Value {chunk};")
        if has_fork:
            self._emit("mp::ForkTable __forks;")
        if "this" in f.params:
            self._emit("(void)self;")

        for ins in f.instrs:
            self._instr(ins, used_labels)

        head = self._prototype(f) + " {"
        return [head] + self.lines + ["}"]

    def _emit(self, text: str) -> None:
        self.lines.append("    " * self.indent + text)

    def _take_params(self, n: int) -> List[str]:
        if n == 0:
            return []
        args = self.pending[-n:]
        del self.pending[-n:]
        return args

    # ------------------------------------------------------------------
    def _instr(self, i: TACInstr, used_labels: Set[str]) -> None:
        op = i.op
        e = self._emit

        if op == "label":
            if i.dst in used_labels:
                e(f"L_{i.dst}: ;")
        elif op == "goto":
            e(f"goto L_{i.dst};")
        elif op == "assign":
            e(f"{var_name(i.dst)} = {opd(i.a)};")
        elif op == "binop":
            a, b = opd(i.a), opd(i.b)
            if i.extra in _BIN:
                e(f"{var_name(i.dst)} = mp::{_BIN[i.extra]}({a}, {b});")
            else:
                e(f"{var_name(i.dst)} = mp::Value(mp::{_REL[i.extra]}({a}, {b}));")
        elif op == "unop":
            if i.extra == "-":
                e(f"{var_name(i.dst)} = mp::neg({opd(i.a)});")
            else:
                e(f"{var_name(i.dst)} = mp::Value(!({opd(i.a)}).truthy());")
        elif op == "if_rel":
            e(f"if (mp::{_REL[i.extra]}({opd(i.a)}, {opd(i.b)})) goto L_{i.dst};")
        elif op == "if_true":
            e(f"if (({opd(i.a)}).truthy()) goto L_{i.dst};")
        elif op == "if_false":
            e(f"if (!({opd(i.a)}).truthy()) goto L_{i.dst};")
        elif op == "param":
            self.pending.append(opd(i.a))
        elif op == "call":
            args = ", ".join(self._take_params(int(i.b)))
            if i.a in self.user_funcs:
                call = f"{fn_name(i.a)}({args})"
            elif i.a in BUILTINS:
                call = f"mp::bi_{i.a}({args})"
            else:
                raise ValueError(f"Função desconhecida no TAC: {i.a}")
            e(f"{var_name(i.dst)} = {call};" if i.dst else f"{call};")
        elif op == "callm":
            args = ", ".join(self._take_params(int(i.extra)))
            call = f'mp::call_method({opd(i.a)}, {cstring(i.b)}, {{{args}}})'
            e(f"{var_name(i.dst)} = {call};" if i.dst else f"{call};")
        elif op == "return":
            e(f"return {opd(i.a)};" if i.a is not None else "return mp::Value();")
        elif op == "load_member":
            e(f"{var_name(i.dst)} = mp::get_member({opd(i.a)}, {cstring(i.b)});")
        elif op == "store_member":
            e(f"mp::set_member({opd(i.a)}, {cstring(i.b)}, {opd(i.c)});")
        elif op == "load_index":
            e(f"{var_name(i.dst)} = mp::get_index({opd(i.a)}, {opd(i.b)});")
        elif op == "store_index":
            e(f"mp::set_index({opd(i.a)}, {opd(i.b)}, {opd(i.c)});")
        elif op == "new_obj":
            e(f"{var_name(i.dst)} = mp::new_obj({cstring(i.a)});")
        elif op == "new_list":
            e(f"{var_name(i.dst)} = mp::new_list();")
        elif op == "append":
            e(f"mp::append({opd(i.a)}, {opd(i.b)});")
        elif op == "pop":
            e(f"{var_name(i.dst)} = mp::pop({opd(i.a)});")
        elif op == "size":
            e(f"{var_name(i.dst)} = mp::size_of({opd(i.a)});")
        elif op == "new_matrix":
            e(f"{var_name(i.dst)} = mp::new_matrix({opd(i.a)}, {opd(i.b)}, {opd(i.c)});")
        elif op == "new_channel":
            e(f"{var_name(i.dst)} = mp::new_channel({opd(i.a)}, {opd(i.b)});")
        elif op == "print":
            e("mp::print({" + ", ".join(opd(a) for a in i.args) + "});")
        elif op == "input":
            arg = opd(i.a) if i.a is not None else ""
            e(f"{var_name(i.dst)} = mp::input({arg});")
        elif op == "send":
            e(f"mp::chan_send({opd(i.a)}, {{{', '.join(opd(a) for a in i.args)}}});")
        elif op == "receive":
            e(f"{var_name(i.dst)} = mp::chan_receive({opd(i.a)});")
        elif op == "close":
            e(f"mp::chan_close({opd(i.a)});")
        elif op == "par_begin":
            self.group_n += 1
            self.group_stack.append(self.group_n)
            e("{")
            self.indent += 1
            e(f"mp::TaskGroup __g{self.group_n};")
        elif op == "task":
            gid = self.group_stack[-1]
            e(f"__g{gid}.spawn({cstring(i.dst)}, -1, [=]() mutable {{")
            self.indent += 1
        elif op == "fork":
            name = cstring(i.dst)
            if i.a == "core":
                e(f"__forks.spawn({name}, {opd(i.b)}, [=]() mutable {{")
            elif i.a == "host":
                e(f"__forks.spawn_host({name}, {opd(i.b)}, {opd(i.c)}, [=]() mutable {{")
            else:
                e(f"__forks.spawn_local({name}, [=]() mutable {{")
            self.indent += 1
        elif op == "end_task":
            self.indent -= 1
            e("});")
        elif op == "par_end":
            gid = self.group_stack.pop()
            e(f"__g{gid}.join();")
            self.indent -= 1
            e("}")
        elif op == "join":
            if i.args:
                names = ", ".join(cstring(n) for n in i.args)
                e(f"__forks.join({{{names}}});")
            else:
                e("__forks.join_all();")
        else:
            raise ValueError(f"Instrução TAC sem tradução para C++: {op}")

    # ------------------------------------------------------------------
    def _registration(self, program: TACProgram) -> List[str]:
        out = ["static void register_classes() {"]
        by_name = {f.name: f for f in program.functions}
        for c in program.classes:
            out.append(f"    mp::register_class({cstring(c.name)}, {cstring(c.superclass or '')}, {{")
            for m in c.methods:
                f = by_name[f"{c.name}.{m}"]
                n = len(f.params) - 1            # sem o 'this'
                call_args = ", ".join(f"a[{k}]" for k in range(n))
                call = f"{fn_name(f.name)}(self" + (", " + call_args if n else "") + ")"
                out.append(
                    f"        {{{cstring(m)}, [](const mp::Value& self, mp::Args& a) -> mp::Value {{ "
                    f"mp::check_arity({cstring(c.name + '.' + m)}, a, {n}); return {call}; }}}},")
            out.append("    });")
        out.append("}")
        out.append("")
        return out

    def _main(self, program: TACProgram) -> List[str]:
        out = ["int main() {"]
        out.append("    return mp::run_program([]() {")
        out.append("        register_classes();")
        for name, a, b in program.channels:
            out.append(f"        {var_name(name)} = mp::make_channel({cstring(name)}, "
                       f"{cstring(a)}, {cstring(b)});")
        out.append("    }, []() { fn_main(); });")
        out.append("}")
        return out
