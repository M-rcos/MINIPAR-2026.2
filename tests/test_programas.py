"""Testes dos Programas de Teste 4, 5, 6 e 11 (compilados com o g++ e executados)."""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from minipar.codegen import build_executable  # noqa: E402

EX = os.path.join(os.path.dirname(__file__), "..", "exemplos")
HAS_GXX = bool(os.environ.get("CXX") or shutil.which("g++") or shutil.which("c++"))


class ProgramaCompilado(unittest.TestCase):
    """Compila um exemplo uma única vez e permite executá-lo várias vezes."""

    ARQUIVO = ""
    PREFIXO = ""        # código MiniPar acrescentado antes do programa (ex.: seed)
    OPT = "0"

    @classmethod
    def setUpClass(cls):
        if not HAS_GXX or not cls.ARQUIVO:
            raise unittest.SkipTest("g++ não encontrado")
        cls.tmp = tempfile.mkdtemp()
        with open(os.path.join(EX, cls.ARQUIVO), encoding="utf-8") as f:
            src = cls.PREFIXO + f.read()
        path = os.path.join(cls.tmp, "prog.mp")
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        cls.exe = str(build_executable(path, out_dir=os.path.join(cls.tmp, "out"),
                                       opt=cls.OPT).exe_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(getattr(cls, "tmp", ""), ignore_errors=True)

    def executar(self, stdin=""):
        p = subprocess.run([self.exe], input=stdin, capture_output=True, text=True,
                           cwd=self.tmp, timeout=120)
        return p.stdout, p.stderr, p.returncode


# ----------------------------------------------------------------------------
class TestTeste04RedeXOR(ProgramaCompilado):
    ARQUIVO = "teste04_rede_xor.mp"
    PREFIXO = "seed(3);\n"
    OPT = "2"

    def valores(self, out):
        return [float(v) for v in re.findall(r"Predicted Output: ([0-9.]+)", out)]

    def test_aprende_xor(self):
        out, err, code = self.executar()
        self.assertEqual(code, 0, err)
        linhas = out.splitlines()
        self.assertEqual(len(linhas), 4)
        for entrada, linha in zip(("[0, 0]", "[0, 1]", "[1, 0]", "[1, 1]"), linhas):
            self.assertTrue(linha.startswith(f"Input: {entrada}, Predicted Output: "), linha)
        v = self.valores(out)
        self.assertLess(v[0], 0.1)
        self.assertGreater(v[1], 0.9)
        self.assertGreater(v[2], 0.9)
        self.assertLess(v[3], 0.1)

    def test_semente_torna_a_execucao_reproduzivel(self):
        self.assertEqual(self.executar()[0], self.executar()[0])


class TestTeste04SemSemente(unittest.TestCase):
    @unittest.skipUnless(HAS_GXX, "g++ não encontrado")
    def test_programa_original_converge_sem_semente(self):
        with tempfile.TemporaryDirectory() as d:
            exe = build_executable(os.path.join(EX, "teste04_rede_xor.mp"), out_dir=d,
                                   opt="2").exe_path
            ok = 0
            for _ in range(3):
                out = subprocess.run([str(exe)], capture_output=True, text=True).stdout
                v = [float(x) for x in re.findall(r"Predicted Output: ([0-9.]+)", out)]
                ok += v[0] < 0.1 and v[1] > 0.9 and v[2] > 0.9 and v[3] < 0.1
            self.assertGreaterEqual(ok, 2)   # a inicialização é aleatória: tolera 1 falha em 3


# ----------------------------------------------------------------------------
class TestTeste05Recomendacao(ProgramaCompilado):
    ARQUIVO = "teste05_recomendacao.mp"

    def test_saida_igual_ao_enunciado(self):
        out, err, code = self.executar()
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines(), [
            "Produtos recomendados para você:",
            "Laptop", "Tablet", "Fones de ouvido", "Camisa", "Jaqueta", "Sapatos",
            "Geladeira", "Máquina de lavar", "Ar condicionado",
            "Não-ficção", "Ficção científica", "Fantasia"])


# ----------------------------------------------------------------------------
class TestTeste06Quicksort(ProgramaCompilado):
    ARQUIVO = "teste06_quicksort_recursivo.mp"

    def test_saida_igual_ao_enunciado(self):
        out, err, code = self.executar("10 -3 -40 80 70 -100\n")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines(), [
            "==== Ordenação com Quicksort ====",
            "Insira os elementos do vetor separados por espaço:",
            "Vetor original: [10, -3, -40, 80, 70, -100]",
            "Vetor ordenado: [-100, -40, -3, 10, 70, 80]"])

    def test_entrada_invalida_reinicia_a_interface(self):
        out, err, code = self.executar("abc 3\n3 x\n  5   1  4  \n")
        self.assertEqual(code, 0, err)
        linhas = out.splitlines()
        self.assertEqual(linhas.count("Por favor, insira apenas números separados por espaço."), 2)
        self.assertEqual(linhas.count("==== Ordenação com Quicksort ===="), 3)
        self.assertEqual(linhas[-2:], ["Vetor original: [5, 1, 4]", "Vetor ordenado: [1, 4, 5]"])

    def test_casos_de_borda(self):
        for entrada, esperado in (("7\n", "[7]"), ("\n", "[]"), ("3 3 1 3\n", "[1, 3, 3, 3]"),
                                  ("-5 -9 -1\n", "[-9, -5, -1]")):
            with self.subTest(entrada):
                out, _, code = self.executar(entrada)
                self.assertEqual(code, 0)
                self.assertEqual(out.splitlines()[-1], f"Vetor ordenado: {esperado}")


# ----------------------------------------------------------------------------
SAIDA_ESPERADA_11 = """\
🔍 Tokens gerados pelo analisador léxico:
[PARENTESE: '(']
[PARENTESE: '(']
[NUMERO: '2']
[OPERADOR: '+']
[NUMERO: '4']
[PARENTESE: ')']
[OPERADOR: '*']
[NUMERO: '7']
[PARENTESE: ')']
[OPERADOR: '-']
[PARENTESE: '(']
[NUMERO: '5']
[OPERADOR: '*']
[NUMERO: '4']
[PARENTESE: ')']

🌳 Árvore Sintática Abstrata (AST):
    4
  *
    5
-
    7
  *
      4
    +
      2

📦 Código de Três Endereços (TAC):
t1 = 2 + 4
t2 = t1 * 7
t3 = 5 * 4
t4 = t2 - t3

⚙️ Assembly ARMv7 (CPUlator):
.global _start
.text
_start:
    MOV    r0, #2
    MOV    r1, #4
    ADD    r2, r0, r1    @ resultado de '(2 + 4)'
    MOV    r3, #7
    MUL    r4, r2, r3    @ resultado de '((2 + 4) * 7)'
    MOV    r5, #5
    MOV    r6, #4
    MUL    r7, r5, r6    @ resultado de '(5 * 4)'
    SUB    r8, r4, r7    @ resultado de '(((2 + 4) * 7) - (5 * 4))'
    b .    @ loop infinito para parar o programa

📚 Tabela de Símbolos:
🔹 2 → CONST
🔹 4 → CONST
🔹 5 → CONST
🔹 7 → CONST

🧮 Resultado final da expressão:
➡️  22.0"""

ASM_VALIDO = [
    r"^\.global _start$", r"^\.text$", r"^_start:$",
    r"^    MOV    r(?:\d|1[0-2]), #(?:\d|\d\d|1\d\d|2[0-4]\d|25[0-5])(?:    @ .*)?$",
    r"^    LDR    r(?:\d|1[0-2]), =\d+(?:    @ .*)?$",
    r"^    (?:ADD|SUB|MUL)    r(?:\d|1[0-2]), r(?:\d|1[0-2]), r(?:\d|1[0-2])    @ resultado de '.*'$",
    r"^    @ .*$",
    r"^    b \.    @ .*$",
]


class TestTeste11MiniCompilador(ProgramaCompilado):
    ARQUIVO = "teste11_minicompilador.mp"

    def rodar(self, expr):
        out, err, code = self.executar(expr + "\n")
        self.assertEqual(code, 0, err)
        arm = os.path.join(self.tmp, "Codigo-Assembly-ARMV7.arm")
        with open(arm, encoding="utf-8") as f:
            return out, f.read()

    def test_expressao_1_igual_ao_enunciado(self):
        out, arm = self.rodar("((2+4)*7)-(5*4)")
        linhas = out.splitlines()
        self.assertEqual(linhas[0], "Digite uma expressão infixada: ")
        fim = linhas.index("➡️  22.0")
        self.assertEqual("\n".join(linhas[1:fim + 1]), SAIDA_ESPERADA_11)
        self.assertEqual(linhas[-1], "💾 Assembly salvo em Codigo-Assembly-ARMV7.arm")

    def test_arquivo_arm_igual_ao_do_enunciado(self):
        _, arm = self.rodar("((2+4)*7)-(5*4)")
        self.assertEqual(arm, (
            ".global _start\n.text\n_start:\n"
            "    MOV    r0, #2\n    MOV    r1, #4\n"
            "    ADD    r2, r0, r1    @ resultado de '(2 + 4)'\n"
            "    MOV    r3, #7\n"
            "    MUL    r4, r2, r3    @ resultado de '((2 + 4) * 7)'\n"
            "    MOV    r5, #5\n    MOV    r6, #4\n"
            "    MUL    r7, r5, r6    @ resultado de '(5 * 4)'\n"
            "    SUB    r8, r4, r7    @ resultado de '(((2 + 4) * 7) - (5 * 4))'\n"
            "    b .    @ loop infinito para parar o programa\n"))

    def test_expressao_2(self):
        out, arm = self.rodar("((10 -8*7)+4)*2")
        self.assertIn("➡️  -84.0", out)
        self.assertIn("t1 = 8 * 7\nt2 = 10 - t1\nt3 = t2 + 4\nt4 = t3 * 2", out)
        linhas = arm.splitlines()
        self.assertEqual(linhas[3:7], [
            "    MOV    r0, #10", "    MOV    r1, #8", "    MOV    r2, #7",
            "    MUL    r3, r1, r2    @ resultado de '(8 * 7)'"])
        self.assertIn("🔹 10 → CONST", out)

    def test_assembly_gerado_tem_apenas_instrucoes_validas(self):
        for expr in ("((2+4)*7)-(5*4)", "((10 -8*7)+4)*2", "1000+1", "2*3*4*5", "(1+2)*(3+4)"):
            with self.subTest(expr):
                _, arm = self.rodar(expr)
                for linha in arm.splitlines():
                    self.assertTrue(any(re.match(p, linha) for p in ASM_VALIDO), linha)
                # nenhuma operação escreve no mesmo registrador que lê como 1º operando (MUL em ARMv5)
                for m in re.finditer(r"MUL    (r\d+), (r\d+), (r\d+)", arm):
                    self.assertNotEqual(m.group(1), m.group(2))

    def test_precedencia_e_associatividade(self):
        casos = {"2+3*4": "14.0", "(2+3)*4": "20.0", "10-4-3": "3.0", "100/10/5": "2.0",
                 "10/4": "2.5", "2*3+4*5": "26.0", "7": "7.0"}
        for expr, resultado in casos.items():
            with self.subTest(expr):
                out, _ = self.rodar(expr)
                self.assertIn("➡️  " + resultado, out)

    def test_decimais_variaveis_e_numeros_grandes(self):
        out, arm = self.rodar("x+1*2.5")
        self.assertIn("🔹 x → VAR", out)
        self.assertIn("⚠️ Variável 'x' não tem valor atribuído. Usando 0.", out)
        self.assertIn("➡️  2.5", out)
        self.assertIn("LDR    r2, =2    @ aviso: decimal 2.5 truncado", arm)
        out, arm = self.rodar("1000+1")
        self.assertIn("    LDR    r0, =1000", arm)
        self.assertIn("➡️  1001.0", out)

    def test_divisao_e_divisao_por_zero(self):
        out, arm = self.rodar("10/4")
        self.assertIn("@ divisão não suportada: r0 / r1", arm)
        out, _ = self.rodar("5/0")
        self.assertIn("➡️  NaN (divisão por zero)", out)

    def test_erros_de_sintaxe_interrompem_a_compilacao(self):
        casos = {"(2+": "esperava ')'", "2 3": "símbolos sobrando", "+3": "esperava um operando",
                 "": "terminou antes do esperado"}
        for expr, trecho in casos.items():
            with self.subTest(expr):
                out, err, code = self.executar(expr + "\n")
                self.assertEqual(code, 0, err)
                self.assertIn("❌ Erro de sintaxe", out)
                self.assertIn(trecho, out)
                self.assertIn("Compilação interrompida", out)
                self.assertNotIn("Assembly ARMv7", out)

    def test_comentario_e_espacos_na_expressao(self):
        out, _ = self.rodar("  ( 1 + 2 ) * 3   # comentário ignorado")
        self.assertIn("➡️  9.0", out)


if __name__ == "__main__":
    unittest.main()
