"""Testes unitários do Analisador Léxico (rodar com: make test)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from minipar.lexer import Lexer  # noqa: E402


def lex(src):
    lx = Lexer(src)
    toks = lx.tokenize()
    return toks, lx.errors


def types(src):
    toks, _ = lex(src)
    return [t.type for t in toks]


class TestLexer(unittest.TestCase):
    def test_vazio_gera_apenas_eof(self):
        toks, errs = lex("")
        self.assertEqual([t.type for t in toks], ["EOF"])
        self.assertEqual(errs, [])

    def test_declaracao_simples(self):
        self.assertEqual(
            types("var x = 42;"),
            ["var", "IDENTIFIER", "=", "NUMBER", ";", "EOF"],
        )

    def test_numeros_int_e_float(self):
        toks, errs = lex("42 3.14 0.5")
        self.assertEqual(errs, [])
        self.assertEqual([t.value for t in toks[:3]], [42, 3.14, 0.5])
        self.assertIsInstance(toks[0].value, int)
        self.assertIsInstance(toks[1].value, float)

    def test_ponto_apos_numero_sem_digito_nao_e_float(self):
        self.assertEqual(types("3.x"), ["NUMBER", ".", "IDENTIFIER", "EOF"])

    def test_palavras_reservadas_e_tipos(self):
        self.assertEqual(
            types("class extends fork join par seq float number"),
            ["class", "extends", "fork", "join", "par", "seq", "float", "number", "EOF"],
        )

    def test_on_core_host_sao_identificadores(self):
        self.assertEqual(types("on core host"), ["IDENTIFIER"] * 3 + ["EOF"])

    def test_operadores_compostos(self):
        self.assertEqual(
            types("== != <= >= && || += -= *= /="),
            ["==", "!=", "<=", ">=", "&&", "||", "+=", "-=", "*=", "/=", "EOF"],
        )

    def test_operadores_simples_e_delimitadores(self):
        self.assertEqual(
            types("+ - * / % < > = ! ( ) { } [ ] . ; , :"),
            ["+", "-", "*", "/", "%", "<", ">", "=", "!",
             "(", ")", "{", "}", "[", "]", ".", ";", ",", ":", "EOF"],
        )

    def test_comentario_e_descartado(self):
        self.assertEqual(
            types("# comentario\nvar x; # outro\n"),
            ["var", "IDENTIFIER", ";", "EOF"],
        )

    def test_string_com_escapes(self):
        toks, errs = lex(r'"a\nb\t\"c\\"')
        self.assertEqual(errs, [])
        self.assertEqual(toks[0].value, 'a\nb\t"c\\')

    def test_hashtag_dentro_de_string_nao_e_comentario(self):
        toks, errs = lex('print("#### Iteracao");')
        self.assertEqual(errs, [])
        self.assertEqual(toks[2].value, "#### Iteracao")

    def test_literais_booleanos_e_null(self):
        toks, _ = lex("true false null")
        self.assertEqual([t.value for t in toks[:3]], [True, False, None])

    def test_send_receive_input_print_reservadas(self):
        self.assertEqual(
            types("send receive input print matrix c_channel"),
            ["send", "receive", "input", "print", "matrix", "c_channel", "EOF"],
        )

    def test_linhas_e_colunas(self):
        toks, _ = lex("var x;\n  y = 1;")
        y = toks[3]
        self.assertEqual((y.type, y.line, y.col), ("IDENTIFIER", 2, 3))

    def test_metodo_encadeado(self):
        self.assertEqual(
            types("a.b(1)[2]"),
            ["IDENTIFIER", ".", "IDENTIFIER", "(", "NUMBER", ")", "[", "NUMBER", "]", "EOF"],
        )

    # ------------------------- erros -------------------------
    def test_caractere_invalido(self):
        _, errs = lex("var x = 1 @ 2;")
        self.assertEqual(len(errs), 1)
        self.assertIn("inválido", errs[0].message)
        self.assertEqual((errs[0].line, errs[0].col), (1, 11))

    def test_string_nao_terminada(self):
        _, errs = lex('var s = "abc;\nvar y = 1;')
        self.assertEqual(len(errs), 1)
        self.assertIn("não terminada", errs[0].message)
        self.assertEqual(errs[0].line, 1)

    def test_numero_malformado(self):
        _, errs = lex("var y = 12abc;")
        self.assertEqual(len(errs), 1)
        self.assertIn("malformado", errs[0].message)

    def test_operador_incompleto(self):
        _, errs = lex("a & b")
        self.assertEqual(len(errs), 1)
        self.assertIn("&&", errs[0].message)

    def test_escape_invalido(self):
        _, errs = lex(r'"x\qy"')
        self.assertEqual(len(errs), 1)
        self.assertIn("escape", errs[0].message)

    def test_recuperacao_varios_erros(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "exemplos",
                               "erros_lexicos.mp"), encoding="utf-8") as f:
            _, errs = lex(f.read())
        self.assertEqual(len(errs), 5)

    def test_mensagem_formatada_tem_apontador(self):
        src = "var x = 1 @ 2;"
        _, errs = lex(src)
        msg = errs[0].format(src)
        self.assertIn("^", msg)
        self.assertIn(src, msg)

    def test_exemplo_teste2_sem_erros(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "exemplos",
                               "teste02_par_fatorial_fibonacci.mp"), encoding="utf-8") as f:
            toks, errs = lex(f.read())
        self.assertEqual(errs, [])
        self.assertGreater(len(toks), 100)


if __name__ == "__main__":
    unittest.main()
