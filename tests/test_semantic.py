"""Testes unitários da Tabela de Símbolos e do Analisador Semântico."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from minipar.lexer import Lexer  # noqa: E402
from minipar.parser import Parser  # noqa: E402
from minipar.semantic import SemanticAnalyzer  # noqa: E402
from minipar.symtable import FUNCTION, SymbolTable, Symbol, VARIABLE  # noqa: E402

EX = os.path.join(os.path.dirname(__file__), "..", "exemplos")


def analyze(src):
    lx = Lexer(src)
    p = Parser(lx.tokenize())
    tree = p.parse()
    assert not lx.errors and not p.errors, [e.message for e in lx.errors + p.errors]
    a = SemanticAnalyzer()
    a.analyze(tree)
    return a


def msgs(src):
    return [e.message for e in analyze(src).errors]


def ok(src):
    a = analyze(src)
    assert not a.errors, [e.message for e in a.errors]
    return a


class TestTabelaDeSimbolos(unittest.TestCase):
    def test_define_e_resolve_com_escopos(self):
        t = SymbolTable()
        t.define(Symbol("x", VARIABLE, "number"))
        t.enter_scope("f")
        t.define(Symbol("y", VARIABLE, "string"))
        self.assertEqual(t.resolve("x").type, "number")
        self.assertEqual(t.resolve("y").type, "string")
        t.exit_scope()
        self.assertIsNone(t.resolve("y"))

    def test_redeclaracao_devolve_existente(self):
        t = SymbolTable()
        a = Symbol("x", VARIABLE)
        self.assertIsNone(t.define(a))
        self.assertIs(t.define(Symbol("x", VARIABLE)), a)

    def test_sombreamento_em_escopo_interno(self):
        t = SymbolTable()
        t.define(Symbol("x", VARIABLE, "number"))
        t.enter_scope("bloco")
        self.assertIsNone(t.define(Symbol("x", VARIABLE, "string")))
        self.assertEqual(t.resolve("x").type, "string")
        t.exit_scope()
        self.assertEqual(t.resolve("x").type, "number")

    def test_formatacao_nao_quebra(self):
        a = ok("func f(a) { var b = a; } var z = 1;")
        txt = a.symbol_table.format()
        self.assertIn("Escopo: global", txt)
        self.assertIn("FUNCAO", txt)
        self.assertIsInstance(a.symbol_table.to_dict(), dict)


class TestVariaveisETipos(unittest.TestCase):
    def test_inferencia_var(self):
        a = ok('var n = 1; var s = "a"; var b = true; var l = [1]; var u;')
        t = {s.name: s.type for s in a.symbol_table.global_scope.symbols.values()}
        self.assertEqual(t, {"n": "number", "s": "string", "b": "bool", "l": "list",
                             "u": "unknown"})

    def test_tipos_numericos_sao_compativeis(self):
        ok("int a = 1; float b = 2.5; number c = a + b; b = a;")

    def test_inferencia_tardia(self):
        a = ok("var x; x = 5;")
        self.assertEqual(a.symbol_table.resolve("x").type, "number")

    def test_redeclaracao_mesmo_escopo(self):
        self.assertTrue(any("já foi declarada" in m for m in msgs("var x = 1; var x = 2;")))

    def test_redeclaracao_em_escopo_interno_e_permitida(self):
        ok("var x = 1; { var x = 2; }")

    def test_nao_declarada(self):
        self.assertTrue(any("não declarada" in m for m in msgs("y = 1;")))
        self.assertTrue(any("não declarada" in m for m in msgs("print(z);")))

    def test_uso_antes_da_declaracao(self):
        self.assertTrue(any("não declarada" in m for m in msgs("print(a); var a = 1;")))

    def test_inicializador_nao_ve_a_propria_variavel(self):
        self.assertTrue(any("não declarada" in m for m in msgs("var a = a + 1;")))

    def test_tipo_declarado_incompativel(self):
        self.assertTrue(any("incompatível" in m for m in msgs('number n = "x";')))
        self.assertTrue(any("incompatível" in m for m in msgs("bool b = 1;")))

    def test_atribuicao_incompativel(self):
        self.assertTrue(any("incompatível" in m for m in msgs('var x = 1; x = "a";')))

    def test_null_atribuivel_a_nao_primitivos(self):
        ok("var l = [1]; l = null; class A { } var a = new A(); a = null;")
        self.assertTrue(any("incompatível" in m for m in msgs("number n = 1; n = null;")))
        self.assertTrue(any("incompatível" in m for m in msgs('string s = "a"; s = null;')))

    def test_variavel_void_proibida(self):
        self.assertTrue(any("void" in m for m in msgs("void v;")))

    def test_escopo_de_bloco(self):
        self.assertTrue(any("não declarada" in m for m in msgs("{ var a = 1; } print(a);")))

    def test_variavel_do_for_nao_vaza(self):
        self.assertTrue(any("não declarada" in m
                            for m in msgs("for (var i = 0; i < 3; i += 1) { } print(i);")))


class TestOperadores(unittest.TestCase):
    def test_aritmetica_valida(self):
        ok("var a = 1 + 2 * 3 - 4 / 2 % 3;")

    def test_string_mais_numero_e_erro(self):
        self.assertTrue(any("'+'" in m for m in msgs('var a = "x" + 1;')))

    def test_concatenacao_de_strings_e_listas(self):
        a = ok('var s = "a" + "b"; var l = [1] + [2];')
        self.assertEqual(a.symbol_table.resolve("s").type, "string")
        self.assertEqual(a.symbol_table.resolve("l").type, "list")

    def test_comparacoes(self):
        ok('var a = 1 < 2; var b = "a" <= "b"; var c = 1 == 1; var d = "a" != "b";')
        self.assertTrue(any("'<'" in m for m in msgs('var a = 1 < "b";')))
        self.assertTrue(any("comparar" in m for m in msgs('var a = 1 == "b";')))

    def test_logicos_exigem_bool(self):
        ok("var a = true && false || !true;")
        self.assertTrue(any("'&&'" in m for m in msgs("var a = 1 && true;")))
        self.assertTrue(any("'!'" in m for m in msgs("var a = !1;")))

    def test_unario_numerico(self):
        ok("var a = -3; var b = +2;")
        self.assertTrue(any("unário" in m for m in msgs('var a = -"x";')))

    def test_compostos(self):
        ok('var n = 1; n += 2; n -= 1; n *= 3; n /= 2; var s = "a"; s += "b";')
        self.assertTrue(any("'-='" in m for m in msgs('var s = "a"; s -= "b";')))
        self.assertTrue(any("'+='" in m for m in msgs('var n = 1; n += "x";')))

    def test_operando_desconhecido_e_aceito_e_infere(self):
        a = ok("func f(p) { var q = p + 1; return q; }")
        self.assertEqual(a.symbol_table.global_scope.symbols["f"].return_type, "number")

    def test_condicoes_exigem_bool(self):
        for src in ["if (1) { }", "while (1) { }", "do { } while (1);",
                    "for (;1;) { break; }"]:
            with self.subTest(src):
                self.assertTrue(any("booleana" in m for m in msgs(src)))


class TestFuncoes(unittest.TestCase):
    def test_chamada_valida_e_retorno_inferido(self):
        a = ok("func dobro(n) { return n * 2; } var r = dobro(4);")
        self.assertEqual(a.symbol_table.resolve("r").type, "number")

    def test_aridade(self):
        self.assertTrue(any("espera 2" in m for m in msgs("func f(a, b) { } f(1);")))

    def test_funcao_nao_declarada(self):
        self.assertTrue(any("não declarada" in m for m in msgs("g(1);")))

    def test_uso_antes_da_definicao_e_permitido(self):
        ok("f(1); func f(n) { print(n); }")

    def test_recursao(self):
        a = ok("func fat(n) { if (n <= 1) { return 1; } return n * fat(n - 1); }")
        self.assertEqual(a.symbol_table.global_scope.symbols["fat"].return_type, "number")

    def test_recursao_mutua(self):
        ok("func e_par(n) { if (n == 0) { return true; } return e_impar(n - 1); }"
           "func e_impar(n) { if (n == 0) { return false; } return e_par(n - 1); }")

    def test_tipo_do_argumento(self):
        self.assertTrue(any("argumento 1" in m
                            for m in msgs('func f(number n) { } f("x");')))

    def test_void_nao_produz_valor(self):
        self.assertTrue(any("não produz valor" in m
                            for m in msgs("func f() { } var x = f();")))

    def test_return_fora_de_funcao(self):
        self.assertTrue(any("return" in m for m in msgs("return 1;")))

    def test_retornos_de_tipos_diferentes(self):
        self.assertTrue(any("tipos diferentes" in m for m in msgs(
            'func f(a) { if (a) { return 1; } return "x"; }')))

    def test_retorno_com_e_sem_valor(self):
        self.assertTrue(any("com valor e retornos sem valor" in m for m in msgs(
            "func f(a) { if (a) { return 1; } return; }")))

    def test_parametro_repetido(self):
        self.assertTrue(any("repetido" in m for m in msgs("func f(a, a) { }")))

    def test_funcao_duplicada(self):
        self.assertTrue(any("já foi declarado" in m for m in msgs("func f() { } func f() { }")))

    def test_nome_de_funcao_nativa(self):
        self.assertTrue(any("nativa" in m for m in msgs("func len(x) { }")))

    def test_variavel_global_visivel_na_funcao(self):
        ok("var g = 1; func f() { print(g); }")

    def test_usar_funcao_como_valor_e_erro(self):
        self.assertTrue(any("é uma função" in m for m in msgs("func f() { } var a = f;")))

    def test_break_continue_fora_de_laco(self):
        self.assertTrue(any("'break'" in m for m in msgs("break;")))
        self.assertTrue(any("'continue'" in m for m in msgs("continue;")))
        ok("while (true) { break; } for (var x in [1]) { continue; }")


class TestNativas(unittest.TestCase):
    def test_nativas_validas(self):
        ok('var a = len([1]); var b = to_number("3"); var c = fmt(1.5, 2);'
           'var d = range(5); var e = is_digit("1"); var f = exp(1); var g = random();')

    def test_aridade_e_tipo_das_nativas(self):
        self.assertTrue(any("espera 1" in m for m in msgs("var a = len();")))
        self.assertTrue(any("argumento 1" in m for m in msgs("var a = len(5);")))
        self.assertTrue(any("argumento 1" in m for m in msgs("var a = exp(\"x\");")))

    def test_metodos_de_lista(self):
        ok("var l = []; l.append(1); l.push_back(2); var u = l.pop(); var n = l.size();")
        self.assertTrue(any("voar" in m for m in msgs("var l = []; l.voar();")))
        self.assertTrue(any("espera 1" in m for m in msgs("var l = []; l.append();")))

    def test_indexacao(self):
        ok('var l = [1, 2]; var a = l[0]; var s = "abc"; var c = s[1]; l[0] = 5;')
        self.assertTrue(any("índice" in m for m in msgs('var l = [1]; var a = l["x"];')))
        self.assertTrue(any("indexado" in m for m in msgs("var n = 1; var a = n[0];")))
        self.assertTrue(any("imutáveis" in m for m in msgs('var s = "a"; s[0] = "b";')))

    def test_trim_seed_e_write_file(self):
        ok('var a = trim("  oi "); seed(42); write_file("saida.txt", a);')
        self.assertTrue(any("espera 1" in m for m in msgs("var a = trim();")))
        self.assertTrue(any("argumento 1" in m for m in msgs("seed(\"x\");")))
        self.assertTrue(any("espera 2" in m for m in msgs('write_file("a");')))

    def test_input_devolve_string(self):
        a = ok('var s = input("nome: "); var n = to_number(input());')
        self.assertEqual(a.symbol_table.resolve("s").type, "string")


class TestClasses(unittest.TestCase):
    BASE = """
    class Animal {
        var nome = "x";
        func init(n) { this.nome = n; }
        func falar() { print(this.nome); }
    }
    class Cachorro extends Animal {
        var idade = 1;
        func latir(v) { print("Au", v); }
    }
    """

    def test_classe_valida(self):
        a = ok(self.BASE + 'var c = new Cachorro("rex"); c.falar(); c.latir(2); '
                           'print(c.nome, c.idade);')
        self.assertEqual(a.symbol_table.resolve("c").type, "Cachorro")

    def test_construtor_herdado_e_aridade(self):
        self.assertTrue(any("construtor" in m for m in msgs(self.BASE + "var c = new Cachorro();")))

    def test_metodo_e_atributo_inexistentes(self):
        self.assertTrue(any("miar" in m for m in msgs(
            self.BASE + 'var c = new Cachorro("a"); c.miar();')))
        self.assertTrue(any("Atributo 'peso'" in m for m in msgs(
            self.BASE + 'var c = new Cachorro("a"); print(c.peso);')))

    def test_aridade_de_metodo(self):
        self.assertTrue(any("espera 1" in m for m in msgs(
            self.BASE + 'var c = new Cachorro("a"); c.latir();')))

    def test_classe_nao_declarada(self):
        self.assertTrue(any("Classe 'X'" in m for m in msgs("var a = new X();")))

    def test_superclasse_inexistente(self):
        self.assertTrue(any("Superclasse" in m for m in msgs("class A extends B { }")))

    def test_heranca_circular(self):
        self.assertTrue(any("circular" in m for m in msgs(
            "class A extends B { } class B extends A { }")))

    def test_this_so_em_metodo(self):
        self.assertTrue(any("'this'" in m for m in msgs("print(this);")))
        self.assertTrue(any("'this'" in m for m in msgs("func f() { print(this); }")))

    def test_atributo_exige_this_dentro_do_metodo(self):
        self.assertTrue(any("não declarada" in m for m in msgs(
            "class A { var x = 1; func f() { print(x); } }")))

    def test_membros_duplicados(self):
        self.assertTrue(any("já foi declarado" in m for m in msgs(
            "class A { var x = 1; var x = 2; }")))

    def test_sobrescrita_com_parametros_diferentes(self):
        self.assertTrue(any("sobrescreve" in m for m in msgs(
            "class A { func f(a) { } } class B extends A { func f() { } }")))

    def test_atributo_tipado_incompativel(self):
        self.assertTrue(any("declarado como number" in m for m in msgs(
            'class A { number x = "a"; }')))

    def test_polimorfismo_atribuicao_de_subclasse(self):
        ok("class A { } class B extends A { } var a = new A(); a = new B();")
        self.assertTrue(any("incompatível" in m for m in msgs(
            "class A { } class B extends A { } var b = new B(); b = new A();")))

    def test_metodo_sem_chamada_e_erro(self):
        self.assertTrue(any("é um método" in m for m in msgs(
            "class A { func f() { } } var a = new A(); var x = a.f;")))

    def test_retorno_de_metodo_inferido(self):
        a = ok("class A { func dobro(n) { return n * 2; } } var a = new A(); var r = a.dobro(2);")
        self.assertEqual(a.symbol_table.resolve("r").type, "number")


class TestCanaisEParalelismo(unittest.TestCase):
    def test_canal_declarado_e_metodos(self):
        a = ok("c_channel calc c1 c2; calc.send(1, 2); var r = calc.receive(); calc.close();")
        self.assertEqual(a.symbol_table.resolve("r").type, "list")

    def test_canal_como_expressao(self):
        ok('var c = c_channel("127.0.0.1", 5000); send(c, "oi"); var m = receive(c);')
        self.assertTrue(any("porta" in m for m in msgs('var c = c_channel("ip", "x");')))

    def test_canal_com_computadores_iguais(self):
        self.assertTrue(any("nomes diferentes" in m for m in msgs("c_channel a x x;")))

    def test_send_receive_em_nao_canal(self):
        self.assertTrue(any("canal" in m for m in msgs("var x = 1; send(x, 2);")))
        self.assertTrue(any("canal" in m for m in msgs("var x = 1; var r = receive(x);")))

    def test_fork_join_validos(self):
        ok('fork a on core 0 { print(1); } fork b on host "10.0.0.1", 9000 { print(2); }'
           "fork c { print(3); } join a, b; join c; join;")

    def test_join_de_nome_inexistente(self):
        self.assertTrue(any("não é uma subtarefa" in m for m in msgs("join x;")))

    def test_fork_nome_repetido(self):
        self.assertTrue(any("já foi declarado" in m for m in msgs(
            "fork a { } fork a { }")))

    def test_alocacao_com_tipos_errados(self):
        self.assertTrue(any("núcleo" in m for m in msgs('fork a on core "x" { }')))
        self.assertTrue(any("endereço" in m for m in msgs("fork a on host 5, 9000 { }")))

    def test_subtarefa_nao_altera_variavel_externa(self):
        self.assertTrue(any("não compartilha memória" in m for m in msgs(
            "var x = 1; fork t { x = 2; }")))
        self.assertTrue(any("não compartilha memória" in m for m in msgs(
            "var l = [1]; par { l[0] = 2; }")))

    def test_subtarefa_pode_ler_variavel_externa_e_ter_variaveis_proprias(self):
        ok("var x = 1; fork t { var y = x + 1; y = y + 1; print(y); }")

    def test_par_com_seq_e_variaveis_locais(self):
        ok("par { seq { var k = 0; while (k < 3) { k += 1; } } seq { var j = 1; j += 1; } }")

    def test_return_e_break_dentro_de_subtarefa(self):
        self.assertTrue(any("fork/par" in m for m in msgs("func f() { fork t { return 1; } }")))
        self.assertTrue(any("'break'" in m for m in msgs(
            "while (true) { fork t { break; } }")))


class TestExemplos(unittest.TestCase):
    VALIDOS = [
        "teste01_cliente.mp", "teste01_servidor.mp", "teste02_par_fatorial_fibonacci.mp",
        "teste03_neuronio.mp", "teste07_quicksort_iterativo.mp", "fork_join.mp",
    ]

    def test_exemplos_validos_sem_erros(self):
        for nome in self.VALIDOS:
            with self.subTest(nome):
                with open(os.path.join(EX, nome), encoding="utf-8") as f:
                    a = analyze(f.read())
                self.assertEqual([e.message for e in a.errors], [])

    def test_exemplo_de_erros_semanticos(self):
        with open(os.path.join(EX, "erros_semanticos.mp"), encoding="utf-8") as f:
            a = analyze(f.read())
        self.assertEqual(len(a.errors), 24)
        # nenhum erro duplicado na mesma posição
        pos = [(e.line, e.col) for e in a.errors]
        self.assertEqual(len(pos), len(set(pos)))


class TestAnotacoes(unittest.TestCase):
    def test_tipos_das_expressoes_ficam_registrados(self):
        a = ok("var x = 1 + 2;")
        tipos = set(a.types.values())
        self.assertEqual(tipos, {"number"})


if __name__ == "__main__":
    unittest.main()
