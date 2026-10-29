"""Testes unitários do Analisador Sintático (rodar com: make test)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from minipar.lexer import Lexer  # noqa: E402
from minipar.parser import (  # noqa: E402
    Parser, format_tree, to_dict, NodeVisitor,
    Assign, Binary, Block, Call, ChannelDecl, ClassDecl, DoWhile, ExprStmt, For,
    ForIn, Fork, FuncDecl, Identifier, If, Index, Join, ListLiteral, Literal,
    Member, MethodCall, New, ParBlock, Print, Receive, Return, Unary, VarDecl, While,
)

EX = os.path.join(os.path.dirname(__file__), "..", "exemplos")


def parse(src):
    lx = Lexer(src)
    p = Parser(lx.tokenize())
    tree = p.parse()
    return tree, p.errors


def parse_ok(src):
    tree, errs = parse(src)
    assert not errs, [e.message for e in errs]
    return tree


def expr_of(src):
    """Parseia 'var _ = <src>;' e devolve a expressão."""
    return parse_ok(f"var _ = {src};").body[0].init


def sig(node):
    """Forma compacta de uma expressão, para comparar estruturas."""
    if isinstance(node, Binary):
        return f"({sig(node.left)} {node.op} {sig(node.right)})"
    if isinstance(node, Unary):
        return f"({node.op}{sig(node.operand)})"
    if isinstance(node, Literal):
        return repr(node.value)
    if isinstance(node, Identifier):
        return node.name
    if isinstance(node, Member):
        return f"{sig(node.obj)}.{node.name}"
    if isinstance(node, Index):
        return f"{sig(node.obj)}[{sig(node.index)}]"
    if isinstance(node, Call):
        return f"{node.name}({', '.join(sig(a) for a in node.args)})"
    if isinstance(node, MethodCall):
        return f"{sig(node.obj)}.{node.name}({', '.join(sig(a) for a in node.args)})"
    return type(node).__name__


class TestExpressoes(unittest.TestCase):
    def test_precedencia_mult_sobre_soma(self):
        self.assertEqual(sig(expr_of("1 + 2 * 3")), "(1 + (2 * 3))")

    def test_parenteses_alteram_precedencia(self):
        self.assertEqual(sig(expr_of("(1 + 2) * 3")), "((1 + 2) * 3)")

    def test_associatividade_a_esquerda(self):
        self.assertEqual(sig(expr_of("10 - 4 - 3")), "((10 - 4) - 3)")
        self.assertEqual(sig(expr_of("100 / 10 / 5")), "((100 / 10) / 5)")

    def test_logicos_e_comparacao(self):
        self.assertEqual(sig(expr_of("a < b && c > d || e")), "(((a < b) && (c > d)) || e)")

    def test_unarios(self):
        self.assertEqual(sig(expr_of("-a * !b")), "((-a) * (!b))")
        self.assertEqual(sig(expr_of("- - 3")), "(-(-3))")

    def test_modulo(self):
        self.assertEqual(sig(expr_of("a % 2 == 0")), "((a % 2) == 0)")

    def test_expressao_do_teste11(self):
        self.assertEqual(sig(expr_of("((2+4)*7)-(5*4)")), "(((2 + 4) * 7) - (5 * 4))")

    def test_pos_fixo_encadeado(self):
        self.assertEqual(sig(expr_of("a.b.c(1, 2)[0]")), "a.b.c(1, 2)[0]")

    def test_this_e_new(self):
        e = expr_of("new Rede(0.5, 3)")
        self.assertIsInstance(e, New)
        self.assertEqual(e.class_name, "Rede")
        self.assertEqual(len(e.args), 2)
        self.assertEqual(sig(expr_of("this.peso")), "This.peso")

    def test_receive_funcional_e_metodo(self):
        self.assertIsInstance(expr_of("receive(canal)"), Receive)
        e = expr_of("canal.receive()")
        self.assertIsInstance(e, MethodCall)
        self.assertEqual(e.name, "receive")

    def test_lista_vazia_e_literais(self):
        self.assertEqual(expr_of("[]").elements, [])
        self.assertEqual([x.value for x in expr_of("[1, 2.5, \"a\"]").elements], [1, 2.5, "a"])
        self.assertIsNone(expr_of("null").value)
        self.assertTrue(expr_of("true").value)


class TestComandos(unittest.TestCase):
    def test_var_com_e_sem_tipo(self):
        t = parse_ok("var x = 1; number y = 2; float z; string s = \"a\";")
        self.assertEqual([(d.name, d.type_name) for d in t.body],
                         [("x", None), ("y", "number"), ("z", "float"), ("s", "string")])
        self.assertIsNone(t.body[2].init)

    def test_atribuicoes(self):
        t = parse_ok("x = 1; x += 2; this.a = 3; v[0] = 4; o.p.q -= 5;")
        self.assertEqual([a.op for a in t.body], ["=", "+=", "=", "=", "-="])
        self.assertIsInstance(t.body[3].target, Index)
        self.assertIsInstance(t.body[2].target, Member)

    def test_if_else_if(self):
        t = parse_ok("if (a) { x = 1; } else if (b) { x = 2; } else { x = 3; }")
        node = t.body[0]
        self.assertIsInstance(node, If)
        self.assertIsInstance(node.else_branch, If)
        self.assertIsInstance(node.else_branch.else_branch, Block)

    def test_else_pendente_liga_ao_if_mais_proximo(self):
        t = parse_ok("if (a) if (b) x = 1; else x = 2;")
        externo = t.body[0]
        self.assertIsNone(externo.else_branch)
        self.assertIsNotNone(externo.then_branch.else_branch)

    def test_while_do_while(self):
        t = parse_ok("while (i < 3) i += 1; do { i -= 1; } while (i > 0);")
        self.assertIsInstance(t.body[0], While)
        self.assertIsInstance(t.body[1], DoWhile)

    def test_for_classico_e_iterador(self):
        t = parse_ok("for (var i = 0; i < 10; i += 1) { } for (var x in lista) print(x);")
        self.assertIsInstance(t.body[0], For)
        self.assertIsInstance(t.body[0].init, VarDecl)
        self.assertIsInstance(t.body[0].update, Assign)
        self.assertIsInstance(t.body[1], ForIn)
        self.assertEqual(t.body[1].var_name, "x")

    def test_for_com_partes_vazias(self):
        t = parse_ok("for (;;) { break; }")
        f = t.body[0]
        self.assertIsNone(f.init)
        self.assertIsNone(f.cond)
        self.assertIsNone(f.update)

    def test_print_return_break_continue(self):
        t = parse_ok("func f() { print(); print(1, \"a\"); return; return 1; break; continue; }")
        stmts = t.body[0].body.statements
        self.assertIsInstance(stmts[0], Print)
        self.assertEqual(len(stmts[1].args), 2)
        self.assertIsNone(stmts[2].value)
        self.assertIsNotNone(stmts[3].value)

    def test_chamada_como_comando(self):
        t = parse_ok("f(1); obj.m(2); canal.send(1, 2);")
        self.assertTrue(all(isinstance(s, ExprStmt) for s in t.body))

    def test_send_como_comando(self):
        t = parse_ok("send(canal, 10, 20);")
        self.assertEqual(len(t.body[0].args), 3)


class TestEstruturas(unittest.TestCase):
    def test_funcao_com_tipos_nos_parametros(self):
        t = parse_ok("func soma(number a, b) { return a + b; }")
        f = t.body[0]
        self.assertIsInstance(f, FuncDecl)
        self.assertEqual([(p.name, p.type_name) for p in f.params], [("a", "number"), ("b", None)])

    def test_classe_com_heranca_e_membros(self):
        t = parse_ok("class B extends A { var x = 1; func init(a) { this.x = a; } func m() { } }")
        c = t.body[0]
        self.assertIsInstance(c, ClassDecl)
        self.assertEqual(c.superclass, "A")
        self.assertEqual(len(c.members), 3)

    def test_canal_declaracao(self):
        t = parse_ok("c_channel calc computador_1 computador_2;")
        self.assertIsInstance(t.body[0], ChannelDecl)
        self.assertEqual((t.body[0].name, t.body[0].endpoint_a, t.body[0].endpoint_b),
                         ("calc", "computador_1", "computador_2"))

    def test_canal_como_expressao(self):
        t = parse_ok('var c = c_channel("127.0.0.1", 5000);')
        self.assertEqual(type(t.body[0].init).__name__, "ChannelExpr")

    def test_seq_e_par(self):
        t = parse_ok("seq { a(); } par { seq { b(); } seq { c(); } }")
        self.assertTrue(t.body[0].explicit_seq)
        self.assertIsInstance(t.body[1], ParBlock)
        self.assertEqual(len(t.body[1].statements), 2)

    def test_fork_core_host_e_local(self):
        t = parse_ok('fork a on core 2 { x(); } fork b on host "10.0.0.2", 9000 { y(); } '
                     'fork c { z(); } join a, b; join;')
        a, b, c, j1, j2 = t.body
        self.assertEqual((a.allocation.kind, a.allocation.target.value), ("core", 2))
        self.assertEqual((b.allocation.kind, b.allocation.port.value), ("host", 9000))
        self.assertIsNone(c.allocation)
        self.assertEqual(j1.names, ["a", "b"])
        self.assertEqual(j2.names, [])

    def test_on_core_host_continuam_sendo_nomes_de_variavel(self):
        t = parse_ok("var core = 1; var host = 2; var on = core + host;")
        self.assertEqual(len(t.body), 3)

    def test_nomes_de_metodo_send_receive(self):
        t = parse_ok("c.send(1); var r = c.receive();")
        self.assertEqual(t.body[0].expr.name, "send")


class TestErros(unittest.TestCase):
    def msgs(self, src):
        _, errs = parse(src)
        return [e.message for e in errs]

    def test_falta_ponto_e_virgula_aponta_fim_da_linha_anterior(self):
        _, errs = parse("var a = 10\nvar b = 2;")
        self.assertEqual(len(errs), 1)
        self.assertIn("';'", errs[0].message)
        self.assertEqual((errs[0].line, errs[0].col), (1, 11))

    def test_falta_parentese(self):
        m = self.msgs("if (a > b { x = 1; }")
        self.assertEqual(len(m), 1)
        self.assertIn("')'", m[0])

    def test_expressao_faltando(self):
        m = self.msgs("a = 1 + ;")
        self.assertEqual(len(m), 1)
        self.assertIn("expressão", m[0])

    def test_bloco_nao_fechado(self):
        m = self.msgs("func f() {\n  var x = 1;\n")
        self.assertTrue(any("não foi fechado" in x for x in m))

    def test_chave_sobrando(self):
        m = self.msgs("var a = 1; }")
        self.assertTrue(any("inesperado" in x for x in m))

    def test_alvo_de_atribuicao_invalido(self):
        m = self.msgs("1 = a;")
        self.assertTrue(any("lado esquerdo" in x for x in m))

    def test_expressao_solta_nao_e_comando(self):
        m = self.msgs("a + 1;")
        self.assertTrue(any("não pode ser usada como comando" in x for x in m))

    def test_funcao_aninhada_proibida(self):
        m = self.msgs("func f() { func g() { } }")
        self.assertTrue(any("nível global" in x for x in m))

    def test_else_solto(self):
        m = self.msgs("else { }")
        self.assertEqual(len(m), 1)

    def test_fork_on_invalido(self):
        m = self.msgs("fork t on gpu { }")
        self.assertTrue(any("'core' ou 'host'" in x for x in m))

    def test_canal_expressao_com_aridade_errada(self):
        m = self.msgs('var c = c_channel("ip");')
        self.assertTrue(any("2 argumentos" in x for x in m))

    def test_membro_invalido_na_classe(self):
        m = self.msgs("class A { x = 1; }")
        self.assertTrue(any("atributo" in x for x in m))

    def test_recuperacao_encontra_varios_erros(self):
        with open(os.path.join(EX, "erros_sintaticos.mp"), encoding="utf-8") as f:
            _, errs = parse(f.read())
        self.assertEqual(len(errs), 8)

    def test_nunca_trava_com_entrada_aleatoria(self):
        lixo = ["{{{{", "}}}}", "((((", "var", "class", "fork", "if", "for (", "a.", "a[",
                "func (", "c_channel", "else else else", "= = =", "@", "\"abc"]
        for src in lixo:
            parse(src)  # só não pode lançar exceção nem entrar em laço infinito


class TestExemplos(unittest.TestCase):
    ARQUIVOS = [
        "teste01_cliente.mp", "teste01_servidor.mp",
        "teste02_par_fatorial_fibonacci.mp", "teste03_neuronio.mp",
        "teste07_quicksort_iterativo.mp", "fork_join.mp",
    ]

    def test_exemplos_sem_erros(self):
        for nome in self.ARQUIVOS:
            with self.subTest(nome):
                with open(os.path.join(EX, nome), encoding="utf-8") as f:
                    lx = Lexer(f.read())
                    p = Parser(lx.tokenize())
                    p.parse()
                self.assertEqual(lx.errors, [])
                self.assertEqual([e.message for e in p.errors], [])


class TestFerramentas(unittest.TestCase):
    def test_format_tree_e_to_dict(self):
        t = parse_ok("var x = 1 + 2;")
        txt = format_tree(t)
        self.assertIn("VarDecl name='x'", txt)
        self.assertIn("Binary op='+'", txt)
        d = to_dict(t)
        self.assertEqual(d["type"], "Program")
        self.assertEqual(d["body"][0]["init"]["op"], "+")
        self.assertEqual(d["body"][0]["line"], 1)

    def test_visitor_conta_nos(self):
        class Contador(NodeVisitor):
            def __init__(self):
                self.binarios = 0

            def visit_Binary(self, node):
                self.binarios += 1
                self.generic_visit(node)

        c = Contador()
        c.visit(parse_ok("var x = 1 + 2 * 3 - 4;"))
        self.assertEqual(c.binarios, 3)


if __name__ == "__main__":
    unittest.main()
