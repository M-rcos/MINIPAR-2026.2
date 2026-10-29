"""Analisador Semântico da linguagem MiniPar 2026.2.

Percorre a AST (padrão Visitor) construindo a Tabela de Símbolos e
verificando as regras que a gramática não consegue expressar:

  * declaração antes do uso, redeclaração no mesmo escopo;
  * tipos em atribuições, operadores, condições e argumentos;
  * funções, métodos e construtores: existência e número de argumentos;
  * classes: superclasse existente, herança sem ciclo, atributos e métodos;
  * break/continue só em laços, return só em funções, this só em métodos;
  * canais: uso de send/receive apenas em c_channel;
  * fork/par: subtarefas não compartilham memória (só trocam mensagens),
    join só de subtarefas criadas com fork.

Duas passagens: (1) declara classes e funções globais (permite usá-las antes
da definição no arquivo); (2) analisa os comandos na ordem do arquivo.

Inferência de tipos: variáveis "var" recebem o tipo do inicializador;
parâmetros sem tipo têm tipo UNKNOWN, compatível com qualquer coisa (evita
erros em cascata). O tipo de retorno das funções é inferido dos "return".
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from ..common import MiniParError, SemanticError
from ..parser.ast_nodes import (
    Assign, Binary, Block, Break, Call, ChannelDecl, ChannelExpr, ClassDecl,
    Continue, DoWhile, Expr, ExprStmt, For, ForIn, Fork, FuncDecl, Identifier,
    If, Index, Input, Join, ListLiteral, Literal, MatrixExpr, Member,
    MethodCall, New, Node, ParBlock, Print, Program, Receive, Return, Send,
    This, Unary, VarDecl, While,
)
from ..parser.visitor import NodeVisitor
from ..symtable import (
    ATTRIBUTE, CHANNEL_SYM, CLASS, FUNCTION, METHOD, PARAMETER, TASK, VARIABLE,
    ClassInfo, ParamInfo, Symbol, SymbolTable,
)
from ..symtable.types import (
    BOOL, CHANNEL, DICT, LIST, MATRIX, NULL, NUMBER, STRING, UNKNOWN, VOID,
    normalize_declared,
)
from .builtins import CHANNEL_METHODS, FUNCTIONS, LIST_METHODS, STRING_METHODS
from .interface import ISemanticAnalyzer

_PRIMITIVES = {NUMBER, STRING, BOOL}


def _or_join(names) -> str:
    """['a', 'b', 'c'] -> 'a, b ou c' (para mensagens de erro)."""
    items = sorted(names)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " ou " + items[-1]


class _FuncCtx:
    def __init__(self, name: str):
        self.name = name
        self.returns: List[Tuple[str, Node]] = []


class SemanticAnalyzer(ISemanticAnalyzer, NodeVisitor):
    def __init__(self) -> None:
        self.table = SymbolTable()
        self._errors: List[MiniParError] = []
        self.classes: Dict[str, ClassInfo] = {}
        self.types: Dict[Node, str] = {}            # tipo inferido de cada expressão
        self.resolved: Dict[Node, Symbol] = {}      # símbolo ao qual cada nó se refere
        self._decl_symbol: Dict[Node, Symbol] = {}  # declaração -> símbolo (função/método)
        self._class_of_node: Dict[Node, ClassInfo] = {}

        self.loop_depth = 0
        self.func_ctx: Optional[_FuncCtx] = None
        self.cls_ctx: Optional[ClassInfo] = None
        self.in_method = False
        self.in_task = False

    # ==================================================================
    # Interface ISemanticAnalyzer
    # ==================================================================
    @property
    def symbol_table(self) -> SymbolTable:
        return self.table

    @property
    def errors(self) -> List[MiniParError]:
        return self._errors

    def analyze(self, program: Program) -> List[MiniParError]:
        self._declare_globals(program)
        for node in program.body:
            self.visit(node)
        return self._errors

    # ==================================================================
    # Utilitários
    # ==================================================================
    def _error(self, message: str, node: Node) -> None:
        err = SemanticError(message, node.line, node.col)
        for e in self._errors[-5:]:
            if (e.line, e.col, e.message) == (err.line, err.col, err.message):
                return
        self._errors.append(err)

    def visit(self, node: Node):
        result = super().visit(node)
        if isinstance(node, Expr) and isinstance(result, str):
            self.types[node] = result
        return result

    def _value(self, expr: Expr) -> str:
        """Visita uma expressão que precisa produzir valor."""
        t = self.visit(expr)
        if t == VOID:
            self._error("Esta expressão não produz valor (a função ou método retorna void)", expr)
            return UNKNOWN
        return t

    def _is_subclass(self, sub: str, sup: str) -> bool:
        seen = set()
        cur: Optional[str] = sub
        while cur is not None and cur not in seen:
            if cur == sup:
                return True
            seen.add(cur)
            info = self.classes.get(cur)
            cur = info.superclass if info else None
        return False

    def _assignable(self, target: str, value: str) -> bool:
        if target == UNKNOWN or value == UNKNOWN or target == value:
            return True
        if value == NULL:
            return target not in _PRIMITIVES
        if target in self.classes and value in self.classes:
            return self._is_subclass(value, target)
        return False

    def _find_attr(self, class_name: str, name: str) -> Optional[Symbol]:
        seen = set()
        cur: Optional[str] = class_name
        while cur is not None and cur not in seen:
            seen.add(cur)
            info = self.classes.get(cur)
            if info is None:
                return None
            if name in info.attributes:
                return info.attributes[name]
            cur = info.superclass
        return None

    def _find_method(self, class_name: str, name: str) -> Optional[Symbol]:
        seen = set()
        cur: Optional[str] = class_name
        while cur is not None and cur not in seen:
            seen.add(cur)
            info = self.classes.get(cur)
            if info is None:
                return None
            if name in info.methods:
                return info.methods[name]
            cur = info.superclass
        return None

    @staticmethod
    def _guess_literal(expr: Optional[Expr]) -> str:
        """Tipo aproximado de um inicializador simples (usado na 1ª passagem)."""
        if isinstance(expr, Literal):
            return {"number": NUMBER, "string": STRING, "bool": BOOL}.get(expr.kind, UNKNOWN)
        if isinstance(expr, ListLiteral):
            return LIST
        if isinstance(expr, Unary) and expr.op in "-+" and isinstance(expr.operand, Literal):
            return NUMBER
        return UNKNOWN

    # ==================================================================
    # 1ª passagem: declarações globais (classes e funções)
    # ==================================================================
    def _declare_globals(self, program: Program) -> None:
        for node in program.body:
            if isinstance(node, ClassDecl):
                self._declare_class(node)
            elif isinstance(node, FuncDecl):
                self._declare_function(node)
        for node in program.body:
            if isinstance(node, ClassDecl) and node in self._class_of_node:
                self._check_inheritance(node, self._class_of_node[node])

    def _params_of(self, node: FuncDecl) -> List[ParamInfo]:
        return [ParamInfo(p.name, normalize_declared(p.type_name)) for p in node.params]

    def _declare_function(self, node: FuncDecl) -> None:
        if node.name in FUNCTIONS:
            self._error(f"O nome '{node.name}' pertence à biblioteca nativa e não pode ser "
                        f"usado para uma função", node)
            return
        sym = Symbol(node.name, FUNCTION, "func", node.line, node.col,
                     params=self._params_of(node))
        dup = self.table.define(sym)
        if dup is not None:
            self._error(f"O nome '{node.name}' já foi declarado na linha {dup.line}", node)
            return
        self._decl_symbol[node] = sym

    def _declare_class(self, node: ClassDecl) -> None:
        info = ClassInfo(node.name, node.superclass)
        sym = Symbol(node.name, CLASS, node.name, node.line, node.col, class_info=info)
        dup = self.table.define(sym)
        if dup is not None:
            self._error(f"O nome '{node.name}' já foi declarado na linha {dup.line}", node)
            return
        self.classes[node.name] = info
        self._class_of_node[node] = info
        for member in node.members:
            if isinstance(member, VarDecl):
                if member.name in info.attributes or member.name in info.methods:
                    self._error(f"O membro '{member.name}' já foi declarado na classe "
                                f"'{node.name}'", member)
                    continue
                declared = normalize_declared(member.type_name) if member.type_name else None
                t = declared or self._guess_literal(member.init)
                info.attributes[member.name] = Symbol(
                    member.name, ATTRIBUTE, t, member.line, member.col,
                    declared_type=member.type_name, owner=node.name)
            elif isinstance(member, FuncDecl):
                if member.name in info.methods or member.name in info.attributes:
                    self._error(f"O membro '{member.name}' já foi declarado na classe "
                                f"'{node.name}'", member)
                    continue
                msym = Symbol(member.name, METHOD, "func", member.line, member.col,
                              params=self._params_of(member), owner=node.name)
                info.methods[member.name] = msym
                self._decl_symbol[member] = msym

    def _check_inheritance(self, node: ClassDecl, info: ClassInfo) -> None:
        if info.superclass is None:
            return
        if info.superclass not in self.classes:
            self._error(f"Superclasse '{info.superclass}' não declarada", node)
            info.superclass = None
            return
        # ciclo?
        seen = {info.name}
        cur: Optional[str] = info.superclass
        while cur is not None:
            if cur in seen:
                self._error(f"Herança circular envolvendo a classe '{info.name}'", node)
                info.superclass = None
                return
            seen.add(cur)
            cur = self.classes[cur].superclass if cur in self.classes else None
        # sobrescrita e atributos repetidos
        for name, msym in info.methods.items():
            parent = self._find_method(info.superclass, name)
            if parent is not None and len(parent.params or []) != len(msym.params or []):
                self._error(f"O método '{name}' sobrescreve o da superclasse '{parent.owner}' "
                            f"com número diferente de parâmetros "
                            f"({len(msym.params or [])} em vez de {len(parent.params or [])})",
                            node)
        for name in info.attributes:
            if self._find_attr(info.superclass, name) is not None:
                self._error(f"O atributo '{name}' já existe na superclasse de '{info.name}'", node)

    # ==================================================================
    # 2ª passagem: estrutura
    # ==================================================================
    def visit_Program(self, node: Program):
        for stmt in node.body:
            self.visit(stmt)

    def visit_ClassDecl(self, node: ClassDecl):
        info = self._class_of_node.get(node)
        if info is None:
            return
        for member in node.members:
            if isinstance(member, VarDecl):
                self._visit_attribute(member, info)
            elif isinstance(member, FuncDecl):
                sym = self._decl_symbol.get(member)
                if sym is not None:
                    self._visit_function(member, sym, info)

    def _visit_attribute(self, member: VarDecl, info: ClassInfo) -> None:
        attr = info.attributes.get(member.name)
        if attr is None or member.init is None:
            return
        saved = self.cls_ctx
        self.cls_ctx = None
        t = self._value(member.init)
        self.cls_ctx = saved
        declared = normalize_declared(member.type_name) if member.type_name else None
        if declared is not None:
            if not self._assignable(declared, t):
                self._error(f"O atributo '{member.name}' foi declarado como {declared}, mas "
                            f"recebe um valor do tipo {t}", member)
        elif attr.type == UNKNOWN and t not in (NULL, VOID):
            attr.type = t

    def visit_FuncDecl(self, node: FuncDecl):
        sym = self._decl_symbol.get(node)
        if sym is not None:
            self._visit_function(node, sym, None)

    def _visit_function(self, node: FuncDecl, sym: Symbol, owner: Optional[ClassInfo]) -> None:
        label = f"{owner.name}.{node.name}" if owner else node.name
        self.table.enter_scope(label)
        seen = set()
        for p in node.params:
            if p.name in seen:
                self._error(f"O parâmetro '{p.name}' está repetido", p)
                continue
            seen.add(p.name)
            ptype = normalize_declared(p.type_name)
            psym = Symbol(p.name, PARAMETER, ptype, p.line, p.col, declared_type=p.type_name)
            self.table.define(psym)
            self.resolved[p] = psym

        saved = (self.loop_depth, self.func_ctx, self.cls_ctx, self.in_method, self.in_task)
        ctx = _FuncCtx(node.name)
        self.loop_depth = 0
        self.func_ctx = ctx
        self.cls_ctx = owner
        self.in_method = owner is not None
        self.in_task = False
        for stmt in node.body.statements:
            self.visit(stmt)
        (self.loop_depth, self.func_ctx, self.cls_ctx, self.in_method, self.in_task) = saved
        self.table.exit_scope()
        sym.return_type = self._infer_return(ctx, node)

    def _infer_return(self, ctx: _FuncCtx, node: FuncDecl) -> str:
        types = [t for t, _ in ctx.returns]
        if not types:
            return VOID
        concrete = {t for t in types if t not in (UNKNOWN, VOID, NULL)}
        if VOID in types and (concrete or UNKNOWN in types):
            self._error(f"A função '{node.name}' tem retornos com valor e retornos sem valor",
                        node)
            return UNKNOWN
        if VOID in types:
            return VOID
        if len(concrete) > 1:
            self._error(f"A função '{node.name}' retorna tipos diferentes: "
                        f"{', '.join(sorted(concrete))}", node)
            return UNKNOWN
        if len(concrete) == 1:
            return next(iter(concrete))
        return UNKNOWN

    def visit_ChannelDecl(self, node: ChannelDecl):
        if node.endpoint_a == node.endpoint_b:
            self._error("Os dois computadores do canal devem ter nomes diferentes", node)
        sym = Symbol(node.name, CHANNEL_SYM, CHANNEL, node.line, node.col,
                     endpoints=(node.endpoint_a, node.endpoint_b))
        dup = self.table.define(sym)
        if dup is not None:
            self._error(f"O nome '{node.name}' já foi declarado na linha {dup.line}", node)
        else:
            self.resolved[node] = sym

    def visit_Block(self, node: Block):
        self.table.enter_scope("bloco")
        for stmt in node.statements:
            self.visit(stmt)
        self.table.exit_scope()

    def _visit_body(self, stmt: Node) -> None:
        """Corpo de if/while/for: sempre em escopo próprio."""
        if isinstance(stmt, Block):
            self.visit(stmt)
        else:
            self.table.enter_scope("bloco")
            self.visit(stmt)
            self.table.exit_scope()

    # ------------------------- PAR / FORK / JOIN ----------------------
    def _enter_task(self):
        saved = (self.loop_depth, self.func_ctx, self.in_task)
        self.loop_depth = 0
        self.func_ctx = None
        self.in_task = True
        return saved

    def _exit_task(self, saved) -> None:
        self.loop_depth, self.func_ctx, self.in_task = saved

    def visit_ParBlock(self, node: ParBlock):
        for i, stmt in enumerate(node.statements):
            self.table.enter_scope(f"par[{i}]", isolated=True)
            saved = self._enter_task()
            self.visit(stmt)
            self._exit_task(saved)
            self.table.exit_scope()

    def visit_Fork(self, node: Fork):
        alloc = node.allocation
        if alloc is not None:
            t = self._value(alloc.target)
            if alloc.kind == "core" and t not in (NUMBER, UNKNOWN):
                self._error(f"O número do núcleo deve ser number, mas é {t}", alloc)
            if alloc.kind == "host":
                if t not in (STRING, UNKNOWN):
                    self._error(f"O endereço do computador deve ser string, mas é {t}", alloc)
                if alloc.port is not None:
                    pt = self._value(alloc.port)
                    if pt not in (NUMBER, UNKNOWN):
                        self._error(f"A porta deve ser number, mas é {pt}", alloc)
        sym = Symbol(node.name, TASK, "task", node.line, node.col)
        dup = self.table.define(sym)
        if dup is not None:
            self._error(f"O nome '{node.name}' já foi declarado na linha {dup.line}", node)
        else:
            self.resolved[node] = sym
        self.table.enter_scope(f"fork {node.name}", isolated=True)
        saved = self._enter_task()
        for stmt in node.body.statements:
            self.visit(stmt)
        self._exit_task(saved)
        self.table.exit_scope()

    def visit_Join(self, node: Join):
        for name in node.names:
            sym = self.table.resolve(name)
            if sym is None or sym.kind != TASK:
                self._error(f"'{name}' não é uma subtarefa criada com 'fork'", node)

    # ==================================================================
    # Comandos
    # ==================================================================
    def visit_VarDecl(self, node: VarDecl):
        declared = normalize_declared(node.type_name) if node.type_name else None
        itype: Optional[str] = None
        if node.init is not None:
            itype = self._value(node.init)
        if declared == VOID:
            self._error(f"A variável '{node.name}' não pode ter tipo void", node)
            declared = UNKNOWN
        if declared is not None:
            if itype is not None and not self._assignable(declared, itype):
                self._error(f"Tipo incompatível: '{node.name}' foi declarada como {declared}, "
                            f"mas recebe um valor do tipo {itype}", node)
            vtype = declared
        else:
            vtype = itype if itype not in (None, NULL, VOID) else UNKNOWN
        sym = Symbol(node.name, VARIABLE, vtype, node.line, node.col,
                     declared_type=node.type_name)
        dup = self.table.define(sym)
        if dup is not None:
            self._error(f"A variável '{node.name}' já foi declarada neste escopo "
                        f"(linha {dup.line})", node)
        else:
            self.resolved[node] = sym

    def _root_identifier(self, node: Expr) -> Optional[Identifier]:
        while isinstance(node, (Member, Index)):
            node = node.obj
        return node if isinstance(node, Identifier) else None

    def _check_isolation(self, target: Expr) -> None:
        root = self._root_identifier(target)
        if root is None:
            return
        found = self.table.resolve_with_scope(root.name)
        if found is None:
            return
        sym, scope = found
        if self.table.crosses_isolation(scope):
            self._error(f"A subtarefa (fork/par) não compartilha memória: '{root.name}' foi "
                        f"declarada fora dela e não pode ser alterada aqui. Use um canal "
                        f"(send/receive) para comunicar resultados", target)

    def visit_Assign(self, node: Assign):
        target = node.target
        vtype = self._value(node.value)
        ttype = UNKNOWN
        sym: Optional[Symbol] = None

        if isinstance(target, Identifier):
            sym = self.table.resolve(target.name)
            if sym is None:
                self._error(f"Variável '{target.name}' não declarada", target)
            elif sym.kind not in (VARIABLE, PARAMETER):
                self._error(f"'{target.name}' é {self._kind_name(sym)} e não pode receber "
                            f"atribuição", target)
                sym = None
            else:
                ttype = sym.type
                self.resolved[target] = sym
            self.types[target] = ttype
        elif isinstance(target, Member):
            ttype = self.visit(target)
            attr = self._member_symbol(target)
            sym = attr
        elif isinstance(target, Index):
            ttype = self.visit(target)
            obj_t = self.types.get(target.obj, UNKNOWN)
            if obj_t == STRING:
                self._error("Strings são imutáveis: não é possível atribuir a um caractere",
                            target)
        else:
            self.visit(target)

        self._check_isolation(target)

        if node.op == "=":
            if not self._assignable(ttype, vtype):
                self._error(f"Tipo incompatível na atribuição: o destino é {ttype} e o valor é "
                            f"{vtype}", node)
            elif sym is not None and ttype == UNKNOWN and vtype not in (UNKNOWN, NULL, VOID):
                sym.type = vtype            # inferência tardia
        else:
            base_op = node.op[0]
            self._check_compound(node, base_op, ttype, vtype)

    def _check_compound(self, node: Assign, op: str, ttype: str, vtype: str) -> None:
        if UNKNOWN in (ttype, vtype):
            ok_known = ttype if vtype == UNKNOWN else vtype
            if ok_known not in (UNKNOWN, NUMBER) and not (op == "+" and ok_known in (STRING, LIST)):
                self._error(f"O operador '{op}=' não se aplica ao tipo {ok_known}", node)
            return
        if op == "+" and ttype == vtype and ttype in (NUMBER, STRING, LIST):
            return
        if op != "+" and ttype == NUMBER and vtype == NUMBER:
            return
        self._error(f"O operador '{op}=' não se aplica a {ttype} e {vtype}", node)

    @staticmethod
    def _kind_name(sym: Symbol) -> str:
        return {
            FUNCTION: "uma função", METHOD: "um método", CLASS: "uma classe",
            TASK: "uma subtarefa (fork)", CHANNEL_SYM: "um canal",
        }.get(sym.kind, "uma variável")

    def _condition(self, expr: Expr, what: str) -> None:
        t = self._value(expr)
        if t not in (BOOL, UNKNOWN):
            self._error(f"A condição do '{what}' deve ser booleana, mas é do tipo {t}", expr)

    def visit_If(self, node: If):
        self._condition(node.cond, "if")
        self._visit_body(node.then_branch)
        if node.else_branch is not None:
            self._visit_body(node.else_branch)

    def visit_While(self, node: While):
        self._condition(node.cond, "while")
        self.loop_depth += 1
        self._visit_body(node.body)
        self.loop_depth -= 1

    def visit_DoWhile(self, node: DoWhile):
        self.loop_depth += 1
        self._visit_body(node.body)
        self.loop_depth -= 1
        self._condition(node.cond, "do-while")

    def visit_For(self, node: For):
        self.table.enter_scope("for")
        if node.init is not None:
            self.visit(node.init)
        if node.cond is not None:
            self._condition(node.cond, "for")
        if node.update is not None:
            self.visit(node.update)
        self.loop_depth += 1
        self._visit_body(node.body)
        self.loop_depth -= 1
        self.table.exit_scope()

    def visit_ForIn(self, node: ForIn):
        t = self._value(node.iterable)
        if t not in (LIST, STRING, MATRIX, UNKNOWN):
            self._error(f"O 'for ... in' exige uma lista ou string, mas recebeu {t}",
                        node.iterable)
        self.table.enter_scope("for")
        var_type = STRING if t == STRING else UNKNOWN
        sym = Symbol(node.var_name, VARIABLE, var_type, node.line, node.col)
        self.table.define(sym)
        self.resolved[node] = sym
        self.loop_depth += 1
        self._visit_body(node.body)
        self.loop_depth -= 1
        self.table.exit_scope()

    def visit_Print(self, node: Print):
        for a in node.args:
            self._value(a)

    def visit_Send(self, node: Send):
        if not node.args:
            return
        ct = self._value(node.args[0])
        if ct not in (CHANNEL, UNKNOWN):
            self._error(f"O primeiro argumento de 'send' deve ser um canal (c_channel), mas "
                        f"é {ct}", node)
        for a in node.args[1:]:
            self._value(a)

    def visit_Return(self, node: Return):
        t = VOID if node.value is None else self._value(node.value)
        if self.func_ctx is None:
            if self.in_task:
                self._error("'return' não é permitido dentro de fork/par", node)
            else:
                self._error("'return' só pode ser usado dentro de uma função ou método", node)
            return
        self.func_ctx.returns.append((t, node))

    def visit_Break(self, node: Break):
        if self.loop_depth == 0:
            self._error("'break' usado fora de um laço de repetição", node)

    def visit_Continue(self, node: Continue):
        if self.loop_depth == 0:
            self._error("'continue' usado fora de um laço de repetição", node)

    def visit_ExprStmt(self, node: ExprStmt):
        self.visit(node.expr)

    # ==================================================================
    # Expressões (cada método devolve o tipo da expressão)
    # ==================================================================
    def visit_Literal(self, node: Literal):
        return {"number": NUMBER, "string": STRING, "bool": BOOL, "null": NULL}[node.kind]

    def visit_Identifier(self, node: Identifier):
        sym = self.table.resolve(node.name)
        if sym is None:
            if node.name in FUNCTIONS:
                self._error(f"'{node.name}' é uma função nativa; para usá-la, chame "
                            f"{node.name}(...)", node)
            else:
                self._error(f"Variável '{node.name}' não declarada", node)
            return UNKNOWN
        if sym.kind in (FUNCTION, METHOD):
            self._error(f"'{node.name}' é uma função; para usá-la, chame {node.name}(...)", node)
            return UNKNOWN
        if sym.kind == CLASS:
            self._error(f"'{node.name}' é uma classe; para criar um objeto use "
                        f"new {node.name}(...)", node)
            return UNKNOWN
        if sym.kind == TASK:
            self._error(f"'{node.name}' é uma subtarefa (fork) e não pode ser usada como valor",
                        node)
            return UNKNOWN
        self.resolved[node] = sym
        return sym.type

    def visit_This(self, node: This):
        if not self.in_method or self.cls_ctx is None:
            self._error("'this' só pode ser usado dentro de métodos de uma classe", node)
            return UNKNOWN
        return self.cls_ctx.name

    def visit_Binary(self, node: Binary):
        lt = self._value(node.left)
        rt = self._value(node.right)
        op = node.op

        if op in ("&&", "||"):
            for t in (lt, rt):
                if t not in (BOOL, UNKNOWN):
                    self._error(f"O operador '{op}' exige operandos booleanos, mas recebeu {t}",
                                node)
                    break
            return BOOL

        if op in ("==", "!="):
            if not self._comparable(lt, rt):
                self._error(f"Não é possível comparar {lt} com {rt} usando '{op}'", node)
            return BOOL

        if op in ("<", ">", "<=", ">="):
            known = {t for t in (lt, rt) if t != UNKNOWN}
            if not (known <= {NUMBER} or known <= {STRING}):
                self._error(f"O operador '{op}' exige dois números ou duas strings, mas "
                            f"recebeu {lt} e {rt}", node)
            return BOOL

        if op == "+":
            if lt == UNKNOWN and rt == UNKNOWN:
                return UNKNOWN
            if lt == UNKNOWN or rt == UNKNOWN:
                known = rt if lt == UNKNOWN else lt
                if known not in (NUMBER, STRING, LIST):
                    self._error(f"O operador '+' não se aplica ao tipo {known}", node)
                    return UNKNOWN
                return known
            if lt == rt and lt in (NUMBER, STRING, LIST):
                return lt
            self._error(f"O operador '+' não se aplica a {lt} e {rt}", node)
            return UNKNOWN

        # - * / %
        for t in (lt, rt):
            if t not in (NUMBER, UNKNOWN):
                self._error(f"O operador '{op}' exige números, mas recebeu {lt} e {rt}", node)
                break
        return NUMBER

    def _comparable(self, lt: str, rt: str) -> bool:
        if UNKNOWN in (lt, rt) or NULL in (lt, rt) or lt == rt:
            return True
        if lt in self.classes and rt in self.classes:
            return self._is_subclass(lt, rt) or self._is_subclass(rt, lt)
        return False

    def visit_Unary(self, node: Unary):
        t = self._value(node.operand)
        if node.op == "!":
            if t not in (BOOL, UNKNOWN):
                self._error(f"O operador '!' exige um booleano, mas recebeu {t}", node)
            return BOOL
        if t not in (NUMBER, UNKNOWN):
            self._error(f"O operador '{node.op}' unário exige um número, mas recebeu {t}", node)
        return NUMBER

    # ---- chamadas ---------------------------------------------------
    def _check_arity(self, what: str, expected_min: int, expected_max: Optional[int],
                     given: int, node: Node) -> bool:
        if given < expected_min or (expected_max is not None and given > expected_max):
            if expected_max is None:
                want = f"ao menos {expected_min}"
            elif expected_min == expected_max:
                want = str(expected_min)
            else:
                want = f"de {expected_min} a {expected_max}"
            self._error(f"{what} espera {want} argumento(s), mas recebeu {given}", node)
            return False
        return True

    def _check_user_args(self, what: str, params: List[ParamInfo], arg_types: List[str],
                         args: List[Expr], node: Node) -> None:
        if not self._check_arity(what, len(params), len(params), len(args), node):
            return
        for i, (p, at) in enumerate(zip(params, arg_types)):
            if not self._assignable(p.type, at):
                self._error(f"O argumento {i + 1} de {what.split(' espera')[0]} deve ser "
                            f"{p.type}, mas é {at}", args[i])

    def visit_Call(self, node: Call):
        arg_types = [self._value(a) for a in node.args]
        sym = self.table.resolve(node.name)
        if sym is not None:
            if sym.kind == FUNCTION:
                self.resolved[node] = sym
                self._check_user_args(f"A função '{node.name}'", sym.params or [],
                                      arg_types, node.args, node)
                return sym.return_type
            if sym.kind == CLASS:
                self._error(f"'{node.name}' é uma classe; para criar um objeto use "
                            f"new {node.name}(...)", node)
            else:
                self._error(f"'{node.name}' é {self._kind_name(sym)}, não uma função", node)
            return UNKNOWN
        spec = FUNCTIONS.get(node.name)
        if spec is None:
            self._error(f"Função '{node.name}' não declarada", node)
            return UNKNOWN
        lo, hi, ret, kinds = spec
        if self._check_arity(f"A função nativa '{node.name}'", lo, hi, len(node.args), node):
            for i, at in enumerate(arg_types):
                allowed = kinds[i] if i < len(kinds) else frozenset()
                if allowed and at != UNKNOWN and at not in allowed:
                    self._error(f"O argumento {i + 1} de '{node.name}' deve ser "
                                f"{_or_join(allowed)}, mas é {at}", node.args[i])
        return ret

    def visit_New(self, node: New):
        arg_types = [self._value(a) for a in node.args]
        if node.class_name not in self.classes:
            self._error(f"Classe '{node.class_name}' não declarada", node)
            return UNKNOWN
        init = self._find_method(node.class_name, "init")
        params = init.params if init and init.params else []
        self._check_user_args(f"O construtor de '{node.class_name}'", params, arg_types,
                              node.args, node)
        return node.class_name

    def visit_MethodCall(self, node: MethodCall):
        ot = self._value(node.obj)
        arg_types = [self._value(a) for a in node.args]
        name = node.name

        if ot == UNKNOWN:
            return UNKNOWN
        if ot in self.classes:
            m = self._find_method(ot, name)
            if m is None:
                if self._find_attr(ot, name) is not None:
                    self._error(f"'{name}' é um atributo de '{ot}', não um método", node)
                else:
                    self._error(f"Método '{name}' não declarado em '{ot}'", node)
                return UNKNOWN
            self._check_user_args(f"O método '{name}'", m.params or [], arg_types,
                                  node.args, node)
            return m.return_type
        table = {LIST: LIST_METHODS, STRING: STRING_METHODS, CHANNEL: CHANNEL_METHODS}.get(ot)
        if table is None:
            if ot == NULL:
                self._error(f"Chamada do método '{name}' em um valor nulo", node)
            else:
                self._error(f"O tipo {ot} não possui o método '{name}'", node)
            return UNKNOWN
        spec = table.get(name)
        if spec is None:
            self._error(f"O tipo {ot} não possui o método '{name}'", node)
            return UNKNOWN
        lo, hi, ret = spec
        self._check_arity(f"O método '{name}'", lo, hi, len(node.args), node)
        return ret

    def _member_symbol(self, node: Member) -> Optional[Symbol]:
        ot = self.types.get(node.obj, UNKNOWN)
        if ot in self.classes:
            return self._find_attr(ot, node.name)
        return None

    def visit_Member(self, node: Member):
        ot = self._value(node.obj)
        if ot == UNKNOWN:
            return UNKNOWN
        if ot in self.classes:
            attr = self._find_attr(ot, node.name)
            if attr is not None:
                self.resolved[node] = attr
                return attr.type
            if self._find_method(ot, node.name) is not None:
                self._error(f"'{node.name}' é um método de '{ot}'; use {node.name}(...)", node)
            else:
                self._error(f"Atributo '{node.name}' não declarado em '{ot}'", node)
            return UNKNOWN
        self._error(f"O tipo {ot} não possui atributos", node)
        return UNKNOWN

    def visit_Index(self, node: Index):
        ot = self._value(node.obj)
        it = self._value(node.index)
        if ot not in (LIST, STRING, MATRIX, DICT, UNKNOWN):
            self._error(f"O tipo {ot} não pode ser indexado com []", node)
            return UNKNOWN
        if ot != DICT and it not in (NUMBER, UNKNOWN):
            self._error(f"O índice deve ser um número, mas é {it}", node.index)
        if ot == STRING:
            return STRING
        if ot == MATRIX:
            return LIST
        return UNKNOWN

    def visit_ChannelExpr(self, node: ChannelExpr):
        ht = self._value(node.host)
        pt = self._value(node.port)
        if ht not in (STRING, UNKNOWN):
            self._error(f"O endereço do canal deve ser string, mas é {ht}", node.host)
        if pt not in (NUMBER, UNKNOWN):
            self._error(f"A porta do canal deve ser number, mas é {pt}", node.port)
        return CHANNEL

    def visit_Receive(self, node: Receive):
        ct = self._value(node.channel)
        if ct not in (CHANNEL, UNKNOWN):
            self._error(f"'receive' exige um canal (c_channel), mas recebeu {ct}", node)
        return LIST

    def visit_Input(self, node: Input):
        if node.prompt is not None:
            self._value(node.prompt)
        return STRING

    def visit_ListLiteral(self, node: ListLiteral):
        for e in node.elements:
            self._value(e)
        return LIST

    def visit_MatrixExpr(self, node: MatrixExpr):
        for part, label in ((node.rows, "linhas"), (node.cols, "colunas")):
            t = self._value(part)
            if t not in (NUMBER, UNKNOWN):
                self._error(f"O número de {label} da matriz deve ser number, mas é {t}", part)
        self._value(node.fill)
        return MATRIX
