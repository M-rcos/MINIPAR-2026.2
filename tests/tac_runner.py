"""Interpretador mínimo de TAC, usado apenas nos testes.

Executa o código de três endereços gerado, para verificar que o fluxo de
controle e as expressões gerados produzem o resultado correto. Subtarefas
(par/fork) são executadas em sequência; canais não são suportados aqui.
"""

import json
import math
import re

_NUM = re.compile(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$")


class Obj:
    def __init__(self, cls):
        self.cls = cls
        self.fields = {}


class TACRunner:
    MAX_STEPS = 5_000_000

    def __init__(self, prog, stdin=()):
        self.prog = prog
        self.classes = {c.name: c for c in prog.classes}
        self.globals = {}
        self.out = []
        self.stdin = list(stdin)
        self.params = []
        self.steps = 0
        self.task_results = {}

    # ---------------------------------------------------------------
    def run(self):
        self.call("main", [])
        return "\n".join(self.out)

    def find_method(self, cls, name):
        while cls is not None:
            c = self.classes[cls]
            if name in c.methods:
                return f"{cls}.{name}"
            cls = c.superclass
        raise RuntimeError(f"método {name} não encontrado")

    def call(self, name, args):
        fn = self.prog.function(name)
        if fn is None:
            return self.builtin(name, args)
        env = dict(zip(fn.params, args))
        labels = {i.dst: k for k, i in enumerate(fn.instrs) if i.op == "label"}
        pc = 0
        while pc < len(fn.instrs):
            self.steps += 1
            if self.steps > self.MAX_STEPS:
                raise RuntimeError("limite de passos excedido (laço infinito?)")
            ins = fn.instrs[pc]
            pc += 1
            op = ins.op
            if op == "assign":
                self.set(env, ins.dst, self.val(env, ins.a))
            elif op == "binop":
                self.set(env, ins.dst, self.binop(ins.extra, self.val(env, ins.a), self.val(env, ins.b)))
            elif op == "unop":
                v = self.val(env, ins.a)
                self.set(env, ins.dst, -v if ins.extra == "-" else (not v))
            elif op == "goto":
                pc = labels[ins.dst]
            elif op == "if_rel":
                if self.binop(ins.extra, self.val(env, ins.a), self.val(env, ins.b)):
                    pc = labels[ins.dst]
            elif op == "if_true":
                if self.val(env, ins.a):
                    pc = labels[ins.dst]
            elif op == "if_false":
                if not self.val(env, ins.a):
                    pc = labels[ins.dst]
            elif op == "param":
                self.params.append(self.val(env, ins.a))
            elif op == "call":
                n = int(ins.b)
                args2 = self.params[len(self.params) - n:] if n else []
                del self.params[len(self.params) - n:]
                r = self.call(ins.a, args2)
                if ins.dst:
                    self.set(env, ins.dst, r)
            elif op == "callm":
                obj = self.val(env, ins.a)
                n = int(ins.extra)
                args2 = self.params[len(self.params) - n:] if n else []
                del self.params[len(self.params) - n:]
                r = self.call(self.find_method(obj.cls, ins.b), [obj] + args2)
                if ins.dst:
                    self.set(env, ins.dst, r)
            elif op == "return":
                return self.val(env, ins.a) if ins.a is not None else None
            elif op == "new_obj":
                self.set(env, ins.dst, Obj(ins.a))
            elif op == "new_list":
                self.set(env, ins.dst, [])
            elif op == "append":
                self.val(env, ins.a).append(self.val(env, ins.b))
            elif op == "pop":
                self.set(env, ins.dst, self.val(env, ins.a).pop())
            elif op == "size":
                self.set(env, ins.dst, len(self.val(env, ins.a)))
            elif op == "load_member":
                self.set(env, ins.dst, self.val(env, ins.a).fields[ins.b])
            elif op == "store_member":
                self.val(env, ins.a).fields[ins.b] = self.val(env, ins.c)
            elif op == "load_index":
                self.set(env, ins.dst, self.val(env, ins.a)[int(self.val(env, ins.b))])
            elif op == "store_index":
                self.val(env, ins.a)[int(self.val(env, ins.b))] = self.val(env, ins.c)
            elif op == "print":
                self.out.append(" ".join(self.show(self.val(env, a)) for a in ins.args))
            elif op == "input":
                self.set(env, ins.dst, self.stdin.pop(0))
            elif op in ("task", "fork"):
                alvo = ins.a if op == "task" else ins.extra
                args2 = [self.val_or_none(env, x) for x in ins.args]
                self.task_results[ins.dst] = self.call(alvo, args2)
            elif op == "join_value":
                self.set(env, ins.dst, self.task_results.get(ins.a))
            elif op in ("label", "par_begin", "par_end", "join"):
                pass
            else:
                raise RuntimeError(f"instrução não suportada no runner: {op}")
        return None

    # ---------------------------------------------------------------
    def set(self, env, name, value):
        if name in self.prog.globals:
            self.globals[name] = value
        else:
            env[name] = value

    def val_or_none(self, env, tok):
        try:
            return self.val(env, tok)
        except RuntimeError:
            return None

    def val(self, env, tok):
        if tok is None:
            return None
        if _NUM.match(tok):
            return float(tok) if ("." in tok or "e" in tok.lower()) else int(tok)
        if tok.startswith('"'):
            return json.loads(tok)
        if tok == "true":
            return True
        if tok == "false":
            return False
        if tok == "null":
            return None
        if tok in env:
            return env[tok]
        if tok in self.globals:
            return self.globals[tok]
        if tok in self.prog.globals:
            return None
        raise RuntimeError(f"variável sem valor: {tok}")

    @staticmethod
    def binop(op, a, b):
        return {
            "+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b,
            "/": lambda: a / b, "%": lambda: a % b,
            "==": lambda: a == b, "!=": lambda: a != b,
            "<": lambda: a < b, ">": lambda: a > b,
            "<=": lambda: a <= b, ">=": lambda: a >= b,
        }[op]()

    def show(self, v):
        if v is True:
            return "true"
        if v is False:
            return "false"
        if v is None:
            return "null"
        if isinstance(v, float) and v == int(v) and abs(v) < 1e15:
            return str(int(v))
        if isinstance(v, list):
            return "[" + ", ".join(self.show(x) for x in v) + "]"
        return str(v)

    def builtin(self, name, a):
        f = {
            "len": lambda: len(a[0]),
            "fmt": lambda: f"{a[0]:.{int(a[1])}f}",
            "to_number": lambda: float(a[0]) if "." in str(a[0]) else int(a[0]),
            "to_string": lambda: self.show(a[0]),
            "range": lambda: list(range(int(a[0]))) if len(a) == 1 else list(range(int(a[0]), int(a[1]))),
            "exp": lambda: math.exp(a[0]), "sqrt": lambda: math.sqrt(a[0]),
            "abs": lambda: abs(a[0]), "floor": lambda: math.floor(a[0]),
            "pow": lambda: a[0] ** a[1], "max": lambda: max(a), "min": lambda: min(a),
            "is_digit": lambda: a[0].isdigit(), "is_alpha": lambda: a[0].isalpha(),
            "substr": lambda: a[0][int(a[1]):int(a[1]) + int(a[2])],
            "split": lambda: a[0].split(a[1]),
            "parse_ints": lambda: [int(x) for x in a[0].split()],
            "trim": lambda: a[0].strip(), "seed": lambda: None,
            "write_file": lambda: None,
            "sleep": lambda: None, "clock": lambda: 0.0, "random": lambda: 0.5,
        }
        if name not in f:
            raise RuntimeError(f"função desconhecida: {name}")
        return f[name]()
