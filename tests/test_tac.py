"""Testes do Gerador de Código de Três Endereços (TAC)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from minipar.lexer import Lexer  # noqa: E402
from minipar.parser import Parser  # noqa: E402
from minipar.semantic import SemanticAnalyzer  # noqa: E402
from minipar.tac import TACGenerator  # noqa: E402
from tac_runner import TACRunner  # noqa: E402

EX = os.path.join(os.path.dirname(__file__), "..", "exemplos")


def gen(src):
    lx = Lexer(src)
    p = Parser(lx.tokenize())
    tree = p.parse()
    assert not lx.errors and not p.errors, [e.message for e in lx.errors + p.errors]
    a = SemanticAnalyzer()
    a.analyze(tree)
    assert not a.errors, [e.message for e in a.errors]
    return TACGenerator(a).generate(tree)


def lines(src, fn="main"):
    """Instruções de uma função como lista de textos (sem o 'return' final)."""
    prog = gen(src)
    out = [str(i) for i in prog.function(fn).instrs]
    if out and out[-1] == "return":
        out.pop()
    return out


def run(src, stdin=()):
    return TACRunner(gen(src), stdin).run()


class TestExpressoes(unittest.TestCase):
    def test_precedencia_gera_temporarios_na_ordem_certa(self):
        self.assertEqual(lines("var x = 1 + 2 * 3;"), ["t0 = 2 * 3", "x = 1 + t0"])

    def test_expressao_do_teste11(self):
        self.assertEqual(
            lines("var r = ((2+4)*7)-(5*4);"),
            ["t0 = 2 + 4", "t1 = t0 * 7", "t2 = 5 * 4", "r = t1 - t2"])

    def test_atribuicao_grava_direto_no_destino(self):
        self.assertEqual(lines("var a = 1; var b = 2; a = a + b;"),
                         ["a = 1", "b = 2", "a = a + b"])

    def test_unario_e_literal_negativo(self):
        self.assertEqual(lines("var a = -3; var b = 4; var c = -b;"),
                         ["a = -3", "b = 4", "c = -b"])
        self.assertEqual(lines("var a = true; var b = !a;"), ["a = true", "b = !a"])

    def test_compostos(self):
        self.assertEqual(lines("var x = 1; x += 2; x *= x;"),
                         ["x = 1", "x = x + 2", "x = x * x"])

    def test_listas_e_indices(self):
        self.assertEqual(
            lines("var l = [1, 2]; var a = l[0]; l[1] = a;"),
            ["l = new_list", "append l, 1", "append l, 2", "a = l[0]", "l[1] = a"])

    def test_composto_em_indice_avalia_uma_vez(self):
        self.assertEqual(
            lines("var l = [5]; l[0] += 2;"),
            ["l = new_list", "append l, 5", "t0 = l[0]", "t1 = t0 + 2", "l[0] = t1"])

    def test_logico_como_valor(self):
        out = lines("var a = true; var b = false; var c = a && b;")
        self.assertEqual(out[2:], ["c = false", "ifFalse a goto endlogic1", "c = b",
                                   "endlogic1:"])

    def test_logico_em_atribuicao_comum_usa_temporario(self):
        out = lines("var a = true; var c = false; c = a && c;")
        self.assertEqual(out[2:], ["t0 = false", "ifFalse a goto endlogic1", "t0 = c",
                                   "endlogic1:", "c = t0"])

    def test_chamadas_e_params(self):
        out = lines("func f(a, b) { return a + b; } var r = f(1, 2); f(3, 4);")
        self.assertEqual(out, ["param 1", "param 2", "r = call f, 2",
                               "param 3", "param 4", "call f, 2"])

    def test_funcao_void_nao_tem_destino(self):
        out = lines("func g() { print(1); } g();")
        self.assertEqual(out, ["call g, 0"])

    def test_string_literal_e_print(self):
        self.assertEqual(lines('print("a\\nb", 1);'), ['print "a\\nb", 1'])


class TestControle(unittest.TestCase):
    def test_if_inverte_comparacao(self):
        out = lines("var a = 1; var b = 2; if (a < b) { a = 3; }")
        self.assertEqual(out[2:], ["if a >= b goto endif1", "a = 3", "endif1:"])

    def test_if_else(self):
        out = lines("var a = 1; if (a == 1) { a = 2; } else { a = 3; }")
        self.assertEqual(out[1:], ["if a != 1 goto else1", "a = 2", "goto endif2",
                                   "else1:", "a = 3", "endif2:"])

    def test_curto_circuito_and_or(self):
        out = lines("var a = 1; var b = 2; if (a < 5 && b > 1) { a = 0; }")
        self.assertEqual(out[2:], ["if a >= 5 goto endif1", "if b <= 1 goto endif1",
                                   "a = 0", "endif1:"])
        out = lines("var a = 1; var b = 2; if (a < 5 || b > 1) { a = 0; }")
        self.assertEqual(out[2:], ["if a < 5 goto skip2", "if b <= 1 goto endif1",
                                   "skip2:", "a = 0", "endif1:"])

    def test_while(self):
        out = lines("var i = 0; while (i < 3) { i += 1; }")
        self.assertEqual(out[1:], ["while1:", "if i >= 3 goto endwhile2", "i = i + 1",
                                   "goto while1", "endwhile2:"])

    def test_for_classico(self):
        out = lines("for (var i = 0; i < 3; i += 1) { print(i); }")
        self.assertEqual(out, ["i = 0", "for1:", "if i >= 3 goto endfor3", "print i",
                               "forstep2:", "i = i + 1", "goto for1", "endfor3:"])

    def test_break_e_continue(self):
        out = lines("var i = 0; while (true) { i += 1; if (i > 5) { break; } continue; }")
        self.assertIn("goto endwhile2", out)
        self.assertIn("goto while1", out)

    def test_nomes_unicos_em_escopos_diferentes(self):
        out = lines("var x = 1; { var x = 2; print(x); } print(x);")
        self.assertEqual(out, ["x = 1", "x_1 = 2", "print x_1", "print x"])

    def test_variavel_com_nome_de_temporario_e_renomeada(self):
        out = lines("var t0 = 5; var y = t0 + 1;")
        self.assertEqual(out, ["t0_v = 5", "y = t0_v + 1"])


class TestOO(unittest.TestCase):
    SRC = """
    class A { var v = 1; func init(n) { this.v = n; } func get() { return this.v; } }
    class B extends A { var w = 2; func soma() { return this.get() + this.w; } }
    var b = new B(10);
    print(b.soma());
    """

    def test_estrutura_de_classes_e_funcoes(self):
        prog = gen(self.SRC)
        self.assertEqual([c.name for c in prog.classes], ["A", "B"])
        self.assertEqual(prog.classes[1].superclass, "A")
        nomes = [f.name for f in prog.functions]
        for esperado in ("A.__attrs", "A.init", "A.get", "B.__attrs", "B.soma", "main"):
            self.assertIn(esperado, nomes)
        self.assertEqual(prog.function("B.__attrs").instrs[0].a, "this")

    def test_new_inicializa_atributos_e_chama_construtor(self):
        out = lines(self.SRC)
        self.assertEqual(out[:6], ["b = new B", "param b", "call B.__attrs, 1",
                                  "param b", "param 10", "call A.init, 2"])

    def test_execucao_com_heranca(self):
        self.assertEqual(run(self.SRC), "12")

    def test_polimorfismo(self):
        src = """
        class Animal { func falar() { print("..."); } }
        class Cao extends Animal { func falar() { print("Au"); } }
        func fala(a) { a.falar(); }
        fala(new Animal()); fala(new Cao());
        """
        self.assertEqual(run(src), "...\nAu")

    def test_atributo_composto_e_this(self):
        src = """
        class C { var n = 0; func inc() { this.n += 5; } }
        var c = new C(); c.inc(); c.inc(); print(c.n);
        """
        self.assertEqual(run(src), "10")


class TestParalelismoECanais(unittest.TestCase):
    def test_par(self):
        out = lines("par { print(1); print(2); }")
        self.assertEqual(out, ["par_begin", "task par1_t1", "print 1", "end_task",
                               "task par1_t2", "print 2", "end_task", "par_end"])

    def test_fork_join(self):
        out = lines('fork a on core 1 { print(1); } fork b on host "10.0.0.2", 9000 { print(2); }'
                    "fork c { print(3); } join a, b; join;")
        self.assertEqual(out, [
            "fork a on core 1", "print 1", "end_task",
            'fork b on host "10.0.0.2", 9000', "print 2", "end_task",
            "fork c", "print 3", "end_task", "join a, b", "join"])

    def test_canal(self):
        prog = gen("c_channel calc c1 c2; calc.send(1, 2); var r = calc.receive(); calc.close();"
                   "var ch = c_channel(\"127.0.0.1\", 5000); send(ch, \"x\"); var m = receive(ch);")
        self.assertEqual(prog.channels, [("calc", "c1", "c2")])
        out = [str(i) for i in prog.function("main").instrs][:-1]
        self.assertEqual(out, ["send calc, 1, 2", "r = receive calc", "close calc",
                               'ch = new_channel "127.0.0.1", 5000', 'send ch, "x"',
                               "m = receive ch"])

    def test_texto_formatado_tem_secoes(self):
        txt = gen("c_channel c a b; var g = 1; func f() { } fork t { f(); } join;").format()
        self.assertIn("channel c a b", txt)
        self.assertIn("global g", txt)
        self.assertIn("func f():", txt)
        self.assertIn("endfunc", txt)


class TestExecucao(unittest.TestCase):
    """Executa o TAC gerado e compara com o resultado esperado."""

    def test_fatorial_recursivo(self):
        src = "func f(n) { if (n <= 1) { return 1; } return n * f(n - 1); } print(f(10));"
        self.assertEqual(run(src), "3628800")

    def test_fibonacci_recursivo(self):
        src = ("func fib(n) { if (n == 0) { return 0; } if (n == 1) { return 1; } "
               "return fib(n - 1) + fib(n - 2); } print(fib(10));")
        self.assertEqual(run(src), "55")

    def test_laco_com_break_e_continue(self):
        src = """
        var soma = 0;
        for (var i = 0; i < 20; i += 1) {
            if (i % 2 == 0) { continue; }
            if (i > 11) { break; }
            soma += i;
        }
        print(soma);
        """
        self.assertEqual(run(src), "36")

    def test_do_while_e_while(self):
        src = "var i = 0; do { i += 3; } while (i < 10); var j = 10; while (j > 0) { j -= 4; } print(i, j);"
        self.assertEqual(run(src), "12 -2")

    def test_curto_circuito_nao_avalia_lado_direito(self):
        src = """
        var cont = 0;
        func efeito() { cont += 1; return true; }
        if (false && efeito()) { print("x"); }
        if (true || efeito()) { print("y"); }
        var v = false && efeito();
        print(cont, v);
        """
        self.assertEqual(run(src), "y\n0 false")

    def test_logicos_compostos(self):
        src = ("var a = 3; var b = 7; if ((a < 5 && b > 5) || a == 0) { print(1); } "
               "if (!(a < 5) || b < 5) { print(2); } else { print(3); } "
               "var r = (a > 1 && b > 1) || false; print(r);")
        self.assertEqual(run(src), "1\n3\ntrue")

    def test_foreach_em_lista_e_string(self):
        src = 'var s = 0; for (var x in [1, 2, 3]) { s += x; } for (var c in "ab") { print(c); } print(s);'
        self.assertEqual(run(src), "a\nb\n6")

    def test_variavel_global_em_funcao(self):
        src = "var g = 10; func inc() { g += 1; } inc(); inc(); print(g);"
        self.assertEqual(run(src), "12")

    def test_escopos_sombreados(self):
        src = "var x = 1; { var x = 2; x += 1; print(x); } print(x);"
        self.assertEqual(run(src), "3\n1")

    def test_entrada(self):
        src = 'var n = to_number(input("n: ")); print(n * 2);'
        self.assertEqual(run(src, ["21"]), "42")

    def test_teste07_quicksort_iterativo(self):
        with open(os.path.join(EX, "teste07_quicksort_iterativo.mp"), encoding="utf-8") as f:
            self.assertEqual(run(f.read()), "Array ordenado: [5, 12, 33, 61, 98]")

    def test_teste03_neuronio(self):
        with open(os.path.join(EX, "teste03_neuronio.mp"), encoding="utf-8") as f:
            saida = run(f.read()).split("\n")
        self.assertEqual(saida[0], "Entrada: 1 | Saída desejada: 0")
        self.assertIn("#### Iteração: 1", saida)
        self.assertIn("#### Iteração: 51", saida)
        self.assertNotIn("#### Iteração: 52", saida)
        i51 = saida.index("#### Iteração: 51")
        self.assertEqual(saida[i51 + 1:i51 + 4], ["Peso: -0.0000", "Saída: 0", "Erro: 0"])
        self.assertEqual(saida[-1], "Valor desejado: 0")

    def test_teste02_sequencial(self):
        with open(os.path.join(EX, "teste02_par_fatorial_fibonacci.mp"), encoding="utf-8") as f:
            saida = run(f.read()).split("\n")
        self.assertIn("Fatorial de 5 = 120", saida)
        self.assertIn("Fib: 34", saida)


class TestExemplos(unittest.TestCase):
    def test_todos_os_exemplos_validos_geram_tac(self):
        for nome in ["teste01_cliente.mp", "teste01_servidor.mp",
                     "teste02_par_fatorial_fibonacci.mp", "teste03_neuronio.mp",
                     "teste07_quicksort_iterativo.mp", "fork_join.mp"]:
            with self.subTest(nome):
                with open(os.path.join(EX, nome), encoding="utf-8") as f:
                    prog = gen(f.read())
                self.assertIsNotNone(prog.function("main"))
                self.assertTrue(prog.format().strip())
                self.assertIsInstance(prog.to_dict(), dict)

    def test_toda_funcao_termina_com_return(self):
        with open(os.path.join(EX, "teste03_neuronio.mp"), encoding="utf-8") as f:
            prog = gen(f.read())
        for fn in prog.functions:
            self.assertEqual(fn.instrs[-1].op, "return", fn.name)

    def test_rotulos_usados_existem(self):
        with open(os.path.join(EX, "teste03_neuronio.mp"), encoding="utf-8") as f:
            prog = gen(f.read())
        for fn in prog.functions:
            definidos = {i.dst for i in fn.instrs if i.op == "label"}
            usados = {i.dst for i in fn.instrs if i.op in ("goto", "if_rel", "if_true", "if_false")}
            self.assertLessEqual(usados, definidos, fn.name)


if __name__ == "__main__":
    unittest.main()
