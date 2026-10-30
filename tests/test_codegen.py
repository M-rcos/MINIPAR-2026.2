"""Testes do Gerador de C++ e da integração com o GCC.

Cada teste compila um programa MiniPar com o g++ e executa o binário.
São ignorados automaticamente se o g++ não estiver instalado.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from minipar.codegen import BuildError, build_executable  # noqa: E402
from minipar.pipeline import CompileErrors, to_cpp  # noqa: E402

EX = os.path.join(os.path.dirname(__file__), "..", "exemplos")
HAS_GXX = bool(os.environ.get("CXX") or shutil.which("g++") or shutil.which("c++"))


def run_mp(src, stdin="", opt="0", flags=()):
    """Compila e executa. Devolve (stdout, stderr, código de saída, saída do compilador)."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "prog.mp")
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        res = build_executable(path, out_dir=os.path.join(d, "out"), opt=opt,
                               extra_flags=flags)
        p = subprocess.run([str(res.exe_path)], input=stdin, capture_output=True,
                           text=True, timeout=60)
        return p.stdout, p.stderr, p.returncode, res.compiler_output


def run_file(name, **kw):
    with open(os.path.join(EX, name), encoding="utf-8") as f:
        return run_mp(f.read(), **kw)


class TestGeracaoDeTexto(unittest.TestCase):
    """Não precisam do g++."""

    def test_estrutura_do_cpp(self):
        cpp = to_cpp("var g = 1; func f(a) { return a + g; } print(f(2));")
        self.assertIn('#include "minipar_runtime.hpp"', cpp)
        self.assertIn("static mp::Value v_g;", cpp)
        self.assertIn("mp::Value fn_f(mp::Value v_a)", cpp)
        self.assertIn("mp::print({", cpp)
        self.assertIn("int main()", cpp)

    def test_labels_nao_usados_nao_sao_emitidos(self):
        cpp = to_cpp("var i = 0; while (i < 3) { i += 1; }")
        self.assertIn("L_while1:", cpp)
        self.assertNotIn("L_endif", cpp)

    def test_erro_de_compilacao_levanta_excecao(self):
        with self.assertRaises(CompileErrors) as ctx:
            to_cpp("var x = 1; var x = 2;")
        self.assertIn("já foi declarada", ctx.exception.format())

    def test_strings_com_acentos_e_escapes(self):
        cpp = to_cpp('print("Saída:\\n\\"ok\\" ✅");')
        self.assertNotIn("✅", cpp)         # bytes UTF-8 em octal, sem armadilhas
        self.assertIn("\\n", cpp)


@unittest.skipUnless(HAS_GXX, "g++ não encontrado")
class TestExecucao(unittest.TestCase):
    def test_numeros_e_operadores(self):
        out, err, code, _ = run_mp("""
            print(1 + 2 * 3, 10 / 4, 7 % 3, -7 % 3, 0.1 + 0.2, 1 / 3, 2 - 5);
            print(1000000.0, 3.0, true && false, !true, 5 > 3, "a" < "b", 2 == 2.0);
            print("x" + "y", [1] + [2, 3], null);
        """)
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines(), [
            "7 2.5 1 2 0.30000000000000004 0.3333333333333333 -3",
            "1000000 3 false false true true true",
            "xy [1, 2, 3] null"])

    def test_strings_listas_e_nativas(self):
        out, err, code, _ = run_mp("""
            var s = "abc";
            print(len(s), s[1], substr("abcdef", 2, 3), split("a,b,c", ","));
            var l = [3, 1, 2]; l.append(9); var u = l.pop();
            print(l, u, l.size(), len(l), l[-1]);
            var m = matrix(2, 3, 0); m[1][2] = 7; print(m);
            print(fmt(3.14159, 2), to_number("42") + 1, to_string(7) + "!", is_digit("12"), is_alpha("1a"));
            print(max(3, 8), min(3, 8), abs(-4), floor(2.7), pow(2, 10), sqrt(16), range(4), range(2, 5));
            for (var c in "hi") { print(c); }
            print(parse_ints("10 -3 40"));
        """)
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines(), [
            "3 b cde ['a', 'b', 'c']",
            "[3, 1, 2] 9 3 3 2",
            "[[0, 0, 0], [0, 0, 7]]",
            "3.14 43 7! true false",
            "8 3 4 2 1024 4 [0, 1, 2, 3] [2, 3, 4]",
            "h", "i", "[10, -3, 40]"])

    def test_funcoes_recursao_escopo_e_controle(self):
        out, err, code, _ = run_mp("""
            func fat(n) { if (n <= 1) { return 1; } return n * fat(n - 1); }
            func fib(n) { if (n < 2) { return n; } return fib(n - 1) + fib(n - 2); }
            var g = 10;
            func inc() { g += 1; }
            inc(); inc();
            print(fat(10), fib(15), g);
            var x = 1; { var x = 2; x += 1; print(x); } print(x);
            var soma = 0;
            for (var i = 0; i < 20; i += 1) { if (i % 2 == 0) { continue; } if (i > 11) { break; } soma += i; }
            var j = 0; do { j += 3; } while (j < 10);
            print(soma, j);
            var cont = 0;
            func efeito() { cont += 1; return true; }
            if (false && efeito()) { print("nunca"); }
            if (true || efeito()) { print("curto-circuito"); }
            print(cont);
        """)
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines(), ["3628800 610 12", "3", "1", "36 12",
                                            "curto-circuito", "0"])

    def test_classes_heranca_e_polimorfismo(self):
        out, err, code, _ = run_mp("""
            class Animal {
                var nome = "animal";
                var patas = 4;
                func init(n) { this.nome = n; }
                func falar() { print(this.nome, "faz ...", this.patas); }
                func descrever() { this.falar(); }
            }
            class Cao extends Animal {
                var truques = 0;
                func falar() { print(this.nome, "faz Au"); this.truques += 1; }
            }
            func apresenta(a) { a.descrever(); }
            var a = new Animal("Generico");
            var c = new Cao("Rex");
            apresenta(a); apresenta(c); apresenta(c);
            print(c.truques, c.patas, a.nome);
        """)
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines(), [
            "Generico faz ... 4", "Rex faz Au", "Rex faz Au", "2 4 Generico"])

    def test_entrada_padrao(self):
        out, err, code, _ = run_mp(
            'var nome = input("Nome: "); var n = to_number(input()); print("Oi", nome, n * 2);',
            stdin="Marcos\n21\n")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "Nome: Oi Marcos 42\n")

    def test_erros_de_execucao_terminam_com_codigo_1(self):
        casos = [
            ("var a = 0; print(1 / a);", "Divisão por zero"),
            ("var l = [1, 2]; print(l[5]);", "Índice fora dos limites"),
            ('func f(x) { return x.nada(); } f([1]);', "não possui o método"),
            ('var s = to_number("abc");', "Não foi possível converter"),
            ("var l = []; l.pop();", "pop em lista vazia"),
        ]
        for src, trecho in casos:
            with self.subTest(src):
                out, err, code, _ = run_mp(src)
                self.assertEqual(code, 1)
                self.assertIn("Erro de execução", err)
                self.assertIn(trecho, err)

    def test_par_e_fork_com_threads(self):
        out, err, code, _ = run_mp("""
            func trabalho(nome, n) { var i = 0; var s = 0; while (i < n) { s += i; i += 1; } print(nome, s); }
            par { trabalho("A", 10); trabalho("B", 100); seq { var k = 3; print("C", k * 2); } }
            fork f1 on core 0 { trabalho("F1", 5); }
            fork f2 { trabalho("F2", 6); }
            join f1, f2;
            print("fim");
        """)
        self.assertEqual(code, 0, err)
        linhas = out.splitlines()
        self.assertEqual(sorted(linhas[:3]), ["A 45", "B 4950", "C 6"])
        self.assertEqual(sorted(linhas[3:5]), ["F1 10", "F2 15"])
        self.assertEqual(linhas[5], "fim")

    def test_fork_sem_join_espera_no_fim(self):
        out, err, code, _ = run_mp('fork t { sleep(0.05); print("tarefa terminou"); } print("main");')
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines(), ["main", "tarefa terminou"])

    def test_erro_em_subtarefa_gera_codigo_1(self):
        out, err, code, _ = run_mp("fork t { print(1 / 0); } join;")
        self.assertEqual(code, 1)
        self.assertIn("subtarefa 't'", err)

    def test_otimizacao_O2_e_desempenho(self):
        out, err, code, _ = run_mp("""
            func soma(n) { var s = 0; for (var i = 0; i < n; i += 1) { s += i; } return s; }
            print(soma(3000000));
        """, opt="2")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "4499998500000")


@unittest.skipUnless(HAS_GXX, "g++ não encontrado")
class TestProgramasDeTeste(unittest.TestCase):
    def test_teste07_quicksort_iterativo(self):
        out, err, code, _ = run_file("teste07_quicksort_iterativo.mp")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "Array ordenado: [5, 12, 33, 61, 98]\n")

    def test_teste03_neuronio_igual_ao_enunciado(self):
        out, err, code, _ = run_file("teste03_neuronio.mp")
        self.assertEqual(code, 0, err)
        linhas = out.splitlines()
        # trecho inicial exato do enunciado
        self.assertEqual(linhas[:9], [
            "Entrada: 1 | Saída desejada: 0", "", "#### Iteração: 1", "Peso: 0.5000",
            "Saída: 1", "Erro: -1", "Peso do bias: 0.5000", "", "#### Iteração: 2"])
        self.assertEqual(linhas[9:13], ["Peso: 0.4900", "Saída: 1", "Erro: -1", "Peso do bias: 0.4900"])
        # final exato do enunciado
        self.assertEqual(linhas[-7:], [
            "#### Iteração: 51", "Peso: -0.0000", "Saída: 0", "Erro: 0", "",
            "✅ Parabéns! O neurônio aprendeu.", "Valor desejado: 0"])
        self.assertIn("#### Iteração: 50", linhas)
        self.assertNotIn("#### Iteração: 52", linhas)

    def test_teste02_par_fatorial_fibonacci(self):
        out, err, code, _ = run_file("teste02_par_fatorial_fibonacci.mp")
        self.assertEqual(code, 0, err)
        linhas = out.splitlines()
        for esperado in ("Fatorial de 2 = 2", "Fatorial de 3 = 6", "Fatorial de 4 = 24",
                         "Fatorial de 5 = 120", "Fib: 0", "Fib: 34"):
            self.assertIn(esperado, linhas)
        self.assertEqual(len(linhas), 4 + 10)

    def test_exemplos_compilam_sem_avisos_com_wall_wextra(self):
        for nome in ("teste03_neuronio.mp", "teste07_quicksort_iterativo.mp",
                     "teste02_par_fatorial_fibonacci.mp", "fork_join.mp",
                     "teste01_cliente.mp", "teste01_servidor.mp"):
            with self.subTest(nome):
                with open(os.path.join(EX, nome), encoding="utf-8") as f:
                    src = f.read()
                with tempfile.TemporaryDirectory() as d:
                    path = os.path.join(d, "p.mp")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(src)
                    res = build_executable(path, out_dir=d, opt="0",
                                           extra_flags=["-Wall", "-Wextra"])
                    self.assertEqual(res.compiler_output.strip(), "")


class TestDriver(unittest.TestCase):
    def test_compilador_inexistente(self):
        old = os.environ.get("CXX")
        os.environ["CXX"] = ""
        try:
            with tempfile.TemporaryDirectory() as d:
                path = os.path.join(d, "p.mp")
                with open(path, "w") as f:
                    f.write("print(1);")
                with unittest.mock.patch("shutil.which", return_value=None):
                    with self.assertRaises(BuildError) as ctx:
                        build_executable(path, out_dir=d)
                self.assertIn("Compilador C++ não encontrado", str(ctx.exception))
        finally:
            if old is None:
                os.environ.pop("CXX", None)
            else:
                os.environ["CXX"] = old


if __name__ == "__main__":
    import unittest.mock  # noqa: F401
    unittest.main()
