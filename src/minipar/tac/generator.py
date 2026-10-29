"""Gerador de Código Intermediário de Três Endereços (TAC).

Percorre a AST já validada pelo analisador semântico e produz, para cada
função, método e para o programa principal ("main"), uma lista de instruções
TAC. Pontos principais:

  * Expressões viram temporários (t0, t1, ...). Quando possível, o resultado
    é gravado direto na variável de destino (x = a + b), sem cópia extra.
  * Condições usam avaliação em curto-circuito: && e || viram desvios, e as
    comparações viram "if a < b goto L" (o operador é invertido quando o
    desvio ocorre no caso falso).
  * Variáveis com o mesmo nome em escopos diferentes recebem nomes distintos
    (x, x_1, ...), usando os símbolos resolvidos pelo analisador semântico.
  * Objetos: "new C" chama C.__attrs (inicializa atributos, inclusive os das
    superclasses) e depois o construtor "init", se existir.
  * par/fork geram regiões "task ... end_task" que o gerador de C++ transforma
    em threads ou processos.
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, Optional, Set

from ..parser.ast_nodes import (
    Assign, Binary, Block, Break, Call, ChannelDecl, ChannelExpr, ClassDecl,
    Continue, DoWhile, Expr, ExprStmt, For, ForIn, Fork, FuncDecl, Identifier,
    If, Index, Input, Join, ListLiteral, Literal, MatrixExpr, Member,
    MethodCall, New, Node, ParBlock, Print, Program, Receive, Return, Send,
    This, Unary, VarDecl, While,
)
from ..semantic import SemanticAnalyzer
from ..symtable import CHANNEL_SYM, VARIABLE, Symbol
from ..symtable.types import CHANNEL, LIST, STRING, VOID
from .instructions import TACClass, TACFunction, TACInstr, TACProgram
from .interface import ITACGenerator

_RELATIONAL = {"==", "!=", "<", ">", "<=", ">="}
_INVERSE = {"==": "!=", "!=": "==", "<": ">=", ">=": "<", ">": "<=", "<=": ">"}
_TEMP_LIKE = re.compile(r"^t\d+$")


class _Ctx:
    """Estado da função que está sendo gerada."""

    def __init__(self, name: str, used: Set[str]):
        self.name = name
        self.instrs: List[TACInstr] = []
        self.temp = 0
        self.names: Dict[Symbol, str] = {}
        self.used: Set[str] = set(used)
        self.used.add("this")
        self.loops: List[tuple] = []     # (rótulo do continue, rótulo do break)


class TACGenerator(ITACGenerator):
    def __init__(self, analyzer: SemanticAnalyzer):
        self.a = analyzer
        self.ctx: _Ctx = None            # type: ignore[assignment]
        self.labels = 0
        self.tasks = 0
        self._fresh: Optional[str] = None   # variável recém-declarada (destino seguro)
        self.global_names: Dict[Symbol, str] = {}

    # ==================================================================
    # Programa
    # ==================================================================
    def generate(self, program: Program) -> TACProgram:
        out = TACProgram()
        for sym in self.a.symbol_table.global_scope.symbols.values():
            if sym.kind in (VARIABLE, CHANNEL_SYM):
                self.global_names[sym] = self._safe(sym.name)
                if sym.kind == VARIABLE:
                    out.globals.append(self.global_names[sym])

        for node in program.body:
            if isinstance(node, ChannelDecl):
                out.channels.append((self._safe(node.name), node.endpoint_a, node.endpoint_b))
            elif isinstance(node, ClassDecl):
                self._gen_class(node, out)
            elif isinstance(node, FuncDecl):
                out.functions.append(
                    self._gen_function(node.name, node.params, node.body.statements, False))

        main_nodes = [n for n in program.body
                      if not isinstance(n, (FuncDecl, ClassDecl, ChannelDecl))]
        self.ctx = _Ctx("main", set(self.global_names.values()))
        for node in main_nodes:
            self._stmt(node)
        self._ensure_return()
        out.functions.append(TACFunction("main", [], self.ctx.instrs))
        return out

    # ------------------------------------------------------------------
    @staticmethod
    def _safe(name: str) -> str:
        """Evita que um nome do usuário colida com os temporários (t0, t1...)."""
        return name + "_v" if _TEMP_LIKE.match(name) else name

    def _gen_function(self, name: str, params, statements, has_this: bool) -> TACFunction:
        self.ctx = _Ctx(name, set(self.global_names.values()))
        plist = ["this"] if has_this else []
        for p in params:
            plist.append(self._declare(self.a.resolved.get(p), p.name))
        for stmt in statements:
            self._stmt(stmt)
        self._ensure_return()
        return TACFunction(name, plist, self.ctx.instrs)

    def _ensure_return(self) -> None:
        if not self.ctx.instrs or self.ctx.instrs[-1].op != "return":
            self._emit("return")

    def _gen_class(self, node: ClassDecl, out: TACProgram) -> None:
        info = self.a._class_of_node.get(node)
        if info is None:
            return
        attrs = [m for m in node.members if isinstance(m, VarDecl)]
        methods = [m for m in node.members if isinstance(m, FuncDecl)]
        out.classes.append(TACClass(node.name, info.superclass,
                                    [m.name for m in attrs], [m.name for m in methods]))

        # Inicializador de atributos: Classe.__attrs(this)
        self.ctx = _Ctx(f"{node.name}.__attrs", set(self.global_names.values()))
        if info.superclass:
            self._emit("param", a="this")
            self._emit("call", a=f"{info.superclass}.__attrs", b="1")
        for m in attrs:
            if m.init is not None:
                value = self.gen(m.init)
            else:
                value = self._default_value(m.type_name)
            self._emit("store_member", a="this", b=m.name, c=value)
        self._ensure_return()
        out.functions.append(TACFunction(f"{node.name}.__attrs", ["this"], self.ctx.instrs))

        for m in methods:
            out.functions.append(self._gen_function(
                f"{node.name}.{m.name}", m.params, m.body.statements, True))

    # ==================================================================
    # Utilitários de emissão
    # ==================================================================
    def _emit(self, op: str, **kw) -> TACInstr:
        ins = TACInstr(op, **kw)
        self.ctx.instrs.append(ins)
        return ins

    def _temp(self) -> str:
        name = f"t{self.ctx.temp}"
        self.ctx.temp += 1
        return name

    def _label(self, kind: str) -> str:
        self.labels += 1
        return f"{kind}{self.labels}"

    def _place(self, label: str) -> None:
        self._emit("label", dst=label)

    def _declare(self, sym: Optional[Symbol], fallback: str) -> str:
        """Dá um nome único (dentro da função) a uma variável ou parâmetro."""
        if sym is not None and sym in self.global_names:
            return self.global_names[sym]
        base = self._safe(fallback)
        name, n = base, 1
        while name in self.ctx.used:
            name = f"{base}_{n}"
            n += 1
        self.ctx.used.add(name)
        if sym is not None:
            self.ctx.names[sym] = name
        return name

    def _ref(self, sym: Optional[Symbol], fallback: str) -> str:
        if sym is not None:
            if sym in self.ctx.names:
                return self.ctx.names[sym]
            if sym in self.global_names:
                return self.global_names[sym]
        return self._safe(fallback)

    @staticmethod
    def _default_value(type_name: Optional[str]) -> str:
        if type_name in ("int", "float", "number"):
            return "0"
        if type_name == "string":
            return '""'
        if type_name == "bool":
            return "false"
        return "null"

    def _out(self, dst: Optional[str]) -> str:
        """Destino de expressões que constroem valores (lista, objeto, canal...).
        Só escreve direto em ``dst`` se for uma variável recém-declarada, pois
        em uma atribuição comum o destino poderia aparecer na própria expressão."""
        return dst if (dst is not None and dst == self._fresh) else self._temp()

    def _type(self, expr: Expr) -> Optional[str]:
        return self.a.types.get(expr)

    # ==================================================================
    # Comandos
    # ==================================================================
    def _stmt(self, node: Node) -> None:
        handler = getattr(self, "_s_" + type(node).__name__, None)
        if handler is not None:
            handler(node)

    def _s_VarDecl(self, n: VarDecl) -> None:
        name = self._declare(self.a.resolved.get(n), n.name)
        if n.init is not None:
            self._fresh = name
            self._gen_into(n.init, name)
            self._fresh = None
        elif n.type_name == "list":
            self._emit("new_list", dst=name)
        else:
            self._emit("assign", dst=name, a=self._default_value(n.type_name))

    def _s_Block(self, n: Block) -> None:
        for s in n.statements:
            self._stmt(s)

    def _s_ExprStmt(self, n: ExprStmt) -> None:
        e = n.expr
        if isinstance(e, Call):
            self._call(e, None, want=False)
        elif isinstance(e, MethodCall):
            self._method_call(e, None, want=False)
        else:
            self.gen(e)

    def _s_Print(self, n: Print) -> None:
        args = [self.gen(a) for a in n.args]
        self._emit("print", args=args)

    def _s_Send(self, n: Send) -> None:
        vals = [self.gen(a) for a in n.args]
        self._emit("send", a=vals[0], args=vals[1:])

    def _s_Return(self, n: Return) -> None:
        if n.value is None:
            self._emit("return")
        else:
            self._emit("return", a=self.gen(n.value))

    def _s_Break(self, n: Break) -> None:
        self._emit("goto", dst=self.ctx.loops[-1][1])

    def _s_Continue(self, n: Continue) -> None:
        self._emit("goto", dst=self.ctx.loops[-1][0])

    # ---- atribuição -------------------------------------------------
    def _s_Assign(self, n: Assign) -> None:
        t = n.target
        compound = n.op != "="
        op = n.op[0]
        if isinstance(t, Identifier):
            name = self._ident_name(t)
            if not compound:
                self._gen_into(n.value, name)
            else:
                v = self.gen(n.value)
                self._emit("binop", dst=name, a=name, b=v, extra=op)
        elif isinstance(t, Member):
            obj = self.gen(t.obj)
            if not compound:
                v = self.gen(n.value)
            else:
                cur = self._temp()
                self._emit("load_member", dst=cur, a=obj, b=t.name)
                rhs = self.gen(n.value)
                v = self._temp()
                self._emit("binop", dst=v, a=cur, b=rhs, extra=op)
            self._emit("store_member", a=obj, b=t.name, c=v)
        elif isinstance(t, Index):
            obj = self.gen(t.obj)
            idx = self.gen(t.index)
            if not compound:
                v = self.gen(n.value)
            else:
                cur = self._temp()
                self._emit("load_index", dst=cur, a=obj, b=idx)
                rhs = self.gen(n.value)
                v = self._temp()
                self._emit("binop", dst=v, a=cur, b=rhs, extra=op)
            self._emit("store_index", a=obj, b=idx, c=v)

    # ---- controle de fluxo -------------------------------------------
    def _s_If(self, n: If) -> None:
        if n.else_branch is None:
            end = self._label("endif")
            self._cond_jump(n.cond, end, False)
            self._stmt(n.then_branch)
            self._place(end)
        else:
            els = self._label("else")
            end = self._label("endif")
            self._cond_jump(n.cond, els, False)
            self._stmt(n.then_branch)
            self._emit("goto", dst=end)
            self._place(els)
            self._stmt(n.else_branch)
            self._place(end)

    def _s_While(self, n: While) -> None:
        start = self._label("while")
        end = self._label("endwhile")
        self._place(start)
        self._cond_jump(n.cond, end, False)
        self.ctx.loops.append((start, end))
        self._stmt(n.body)
        self.ctx.loops.pop()
        self._emit("goto", dst=start)
        self._place(end)

    def _s_DoWhile(self, n: DoWhile) -> None:
        start = self._label("do")
        cont = self._label("docond")
        end = self._label("enddo")
        self._place(start)
        self.ctx.loops.append((cont, end))
        self._stmt(n.body)
        self.ctx.loops.pop()
        self._place(cont)
        self._cond_jump(n.cond, start, True)
        self._place(end)

    def _s_For(self, n: For) -> None:
        start = self._label("for")
        cont = self._label("forstep")
        end = self._label("endfor")
        if n.init is not None:
            self._stmt(n.init)
        self._place(start)
        if n.cond is not None:
            self._cond_jump(n.cond, end, False)
        self.ctx.loops.append((cont, end))
        self._stmt(n.body)
        self.ctx.loops.pop()
        self._place(cont)
        if n.update is not None:
            self._stmt(n.update)
        self._emit("goto", dst=start)
        self._place(end)

    def _s_ForIn(self, n: ForIn) -> None:
        seq = self.gen(n.iterable)
        # congela a coleção em um temporário (se ainda não for um)
        if not re.fullmatch(r"t\d+", seq):
            tmp = self._temp()
            self._emit("assign", dst=tmp, a=seq)
            seq = tmp
        size = self._temp()
        self._emit("size", dst=size, a=seq)
        idx = self._temp()
        self._emit("assign", dst=idx, a="0")
        var = self._declare(self.a.resolved.get(n), n.var_name)
        start = self._label("foreach")
        cont = self._label("foreachstep")
        end = self._label("endforeach")
        self._place(start)
        self._emit("if_rel", dst=end, a=idx, b=size, extra=">=")
        self._emit("load_index", dst=var, a=seq, b=idx)
        self.ctx.loops.append((cont, end))
        self._stmt(n.body)
        self.ctx.loops.pop()
        self._place(cont)
        self._emit("binop", dst=idx, a=idx, b="1", extra="+")
        self._emit("goto", dst=start)
        self._place(end)

    # ---- paralelismo ---------------------------------------------------
    def _s_ParBlock(self, n: ParBlock) -> None:
        self.tasks += 1
        pid = self.tasks
        self._emit("par_begin")
        for i, stmt in enumerate(n.statements, 1):
            self._emit("task", dst=f"par{pid}_t{i}")
            self._stmt(stmt)
            self._emit("end_task")
        self._emit("par_end")

    def _s_Fork(self, n: Fork) -> None:
        alloc = n.allocation
        kind = target = port = None
        if alloc is not None:
            kind = alloc.kind
            target = self.gen(alloc.target)
            if alloc.port is not None:
                port = self.gen(alloc.port)
        self._emit("fork", dst=n.name, a=kind, b=target, c=port)
        for s in n.body.statements:
            self._stmt(s)
        self._emit("end_task")

    def _s_Join(self, n: Join) -> None:
        self._emit("join", args=list(n.names))

    # ==================================================================
    # Condições com curto-circuito
    # ==================================================================
    def _cond_jump(self, e: Expr, label: str, when: bool) -> None:
        """Emite desvio para ``label`` se a condição ``e`` valer ``when``."""
        if isinstance(e, Literal) and e.kind == "bool":
            if bool(e.value) == when:
                self._emit("goto", dst=label)
            return
        if isinstance(e, Unary) and e.op == "!":
            self._cond_jump(e.operand, label, not when)
            return
        if isinstance(e, Binary) and e.op == "&&":
            if when:
                skip = self._label("skip")
                self._cond_jump(e.left, skip, False)
                self._cond_jump(e.right, label, True)
                self._place(skip)
            else:
                self._cond_jump(e.left, label, False)
                self._cond_jump(e.right, label, False)
            return
        if isinstance(e, Binary) and e.op == "||":
            if when:
                self._cond_jump(e.left, label, True)
                self._cond_jump(e.right, label, True)
            else:
                skip = self._label("skip")
                self._cond_jump(e.left, skip, True)
                self._cond_jump(e.right, label, False)
                self._place(skip)
            return
        if isinstance(e, Binary) and e.op in _RELATIONAL:
            l = self.gen(e.left)
            r = self.gen(e.right)
            op = e.op if when else _INVERSE[e.op]
            self._emit("if_rel", dst=label, a=l, b=r, extra=op)
            return
        v = self.gen(e)
        self._emit("if_true" if when else "if_false", dst=label, a=v)

    # ==================================================================
    # Expressões: cada _e_* devolve o operando (átomo) com o resultado
    # ==================================================================
    def gen(self, e: Expr, dst: Optional[str] = None) -> str:
        return getattr(self, "_e_" + type(e).__name__)(e, dst)

    def _gen_into(self, e: Expr, name: str) -> None:
        r = self.gen(e, name)
        if r != name:
            self._emit("assign", dst=name, a=r)

    def _ident_name(self, e: Identifier) -> str:
        return self._ref(self.a.resolved.get(e), e.name)

    def _e_Literal(self, e: Literal, dst) -> str:
        if e.kind == "number":
            return repr(e.value)
        if e.kind == "string":
            return json.dumps(e.value, ensure_ascii=False)
        if e.kind == "bool":
            return "true" if e.value else "false"
        return "null"

    def _e_Identifier(self, e: Identifier, dst) -> str:
        return self._ident_name(e)

    def _e_This(self, e: This, dst) -> str:
        return "this"

    def _e_Binary(self, e: Binary, dst) -> str:
        if e.op in ("&&", "||"):
            return self._logical(e, dst)
        l = self.gen(e.left)
        r = self.gen(e.right)
        d = dst or self._temp()
        self._emit("binop", dst=d, a=l, b=r, extra=e.op)
        return d

    def _logical(self, e: Binary, dst: Optional[str] = None) -> str:
        t = self._out(dst)
        end = self._label("endlogic")
        if e.op == "&&":
            self._emit("assign", dst=t, a="false")
            self._cond_jump(e.left, end, False)
        else:
            self._emit("assign", dst=t, a="true")
            self._cond_jump(e.left, end, True)
        v = self.gen(e.right)
        self._emit("assign", dst=t, a=v)
        self._place(end)
        return t

    def _e_Unary(self, e: Unary, dst) -> str:
        if e.op == "+":
            return self.gen(e.operand, dst)
        if e.op == "-" and isinstance(e.operand, Literal) and e.operand.kind == "number":
            return "-" + repr(e.operand.value)
        o = self.gen(e.operand)
        d = dst or self._temp()
        self._emit("unop", dst=d, a=o, extra=e.op)
        return d

    def _e_Call(self, e: Call, dst) -> str:
        return self._call(e, dst, want=True)

    def _call(self, e: Call, dst: Optional[str], want: bool) -> Optional[str]:
        args = [self.gen(a) for a in e.args]
        for a in args:
            self._emit("param", a=a)
        d = None
        if want and self._type(e) != VOID:
            d = dst or self._temp()
        self._emit("call", dst=d, a=e.name, b=str(len(args)))
        return d

    def _e_MethodCall(self, e: MethodCall, dst) -> str:
        return self._method_call(e, dst, want=True)

    def _method_call(self, e: MethodCall, dst: Optional[str], want: bool) -> Optional[str]:
        obj = self.gen(e.obj)
        args = [self.gen(a) for a in e.args]
        ot = self._type(e.obj)
        name = e.name

        def result() -> str:
            return dst or self._temp()

        if ot == CHANNEL:
            if name == "send":
                self._emit("send", a=obj, args=args)
                return None
            if name == "receive":
                d = result()
                self._emit("receive", dst=d, a=obj)
                return d
            if name == "close":
                self._emit("close", a=obj)
                return None
        if ot == LIST:
            if name in ("append", "push_back"):
                self._emit("append", a=obj, b=args[0])
                return None
            if name == "pop":
                d = result()
                self._emit("pop", dst=d, a=obj)
                return d
            if name == "size":
                d = result()
                self._emit("size", dst=d, a=obj)
                return d
        if ot == STRING and name == "size":
            d = result()
            self._emit("size", dst=d, a=obj)
            return d

        for a in args:
            self._emit("param", a=a)
        d = None
        if want and self._type(e) != VOID:
            d = result()
        self._emit("callm", dst=d, a=obj, b=name, extra=str(len(args)))
        return d

    def _e_Member(self, e: Member, dst) -> str:
        obj = self.gen(e.obj)
        d = dst or self._temp()
        self._emit("load_member", dst=d, a=obj, b=e.name)
        return d

    def _e_Index(self, e: Index, dst) -> str:
        obj = self.gen(e.obj)
        idx = self.gen(e.index)
        d = dst or self._temp()
        self._emit("load_index", dst=d, a=obj, b=idx)
        return d

    def _e_New(self, e: New, dst) -> str:
        args = [self.gen(a) for a in e.args]
        t = self._out(dst)
        self._emit("new_obj", dst=t, a=e.class_name)
        self._emit("param", a=t)
        self._emit("call", a=f"{e.class_name}.__attrs", b="1")
        init = self.a._find_method(e.class_name, "init")
        if init is not None:
            self._emit("param", a=t)
            for a in args:
                self._emit("param", a=a)
            self._emit("call", a=f"{init.owner}.init", b=str(len(args) + 1))
        return t

    def _e_ChannelExpr(self, e: ChannelExpr, dst) -> str:
        h = self.gen(e.host)
        p = self.gen(e.port)
        t = self._out(dst)
        self._emit("new_channel", dst=t, a=h, b=p)
        return t

    def _e_Receive(self, e: Receive, dst) -> str:
        ch = self.gen(e.channel)
        d = dst or self._temp()
        self._emit("receive", dst=d, a=ch)
        return d

    def _e_Input(self, e: Input, dst) -> str:
        p = self.gen(e.prompt) if e.prompt is not None else None
        d = dst or self._temp()
        self._emit("input", dst=d, a=p)
        return d

    def _e_ListLiteral(self, e: ListLiteral, dst) -> str:
        t = self._out(dst)
        self._emit("new_list", dst=t)
        for el in e.elements:
            v = self.gen(el)
            self._emit("append", a=t, b=v)
        return t

    def _e_MatrixExpr(self, e: MatrixExpr, dst) -> str:
        r = self.gen(e.rows)
        c = self.gen(e.cols)
        f = self.gen(e.fill)
        t = self._out(dst)
        self._emit("new_matrix", dst=t, a=r, b=c, c=f)
        return t
