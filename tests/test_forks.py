"""Testes de fork/join: threads locais, execução em outro computador (trabalhador) e Testes 8, 9 e 10."""

import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from minipar.codegen import build_executable  # noqa: E402

EX = os.path.join(os.path.dirname(__file__), "..", "exemplos")
HAS_GXX = bool(os.environ.get("CXX") or shutil.which("g++") or shutil.which("c++"))


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class Compilado(unittest.TestCase):
    PROGRAMAS = {}      # nome -> código MiniPar (PORTA é substituída por uma porta livre)
    ARQUIVOS = {}       # nome -> arquivo em exemplos/
    OPT = "0"

    @classmethod
    def setUpClass(cls):
        if not HAS_GXX:
            raise unittest.SkipTest("g++ não encontrado")
        cls.tmp = tempfile.mkdtemp()
        cls.porta = free_port()
        cls.exe = {}
        fontes = dict(cls.PROGRAMAS)
        for nome, arq in cls.ARQUIVOS.items():
            with open(os.path.join(EX, arq), encoding="utf-8") as f:
                fontes[nome] = f.read()
        for nome, src in fontes.items():
            caminho = os.path.join(cls.tmp, nome + ".mp")
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(src.replace("PORTA", str(cls.porta)))
            cls.exe[nome] = str(build_executable(caminho, out_dir=os.path.join(cls.tmp, "out"),
                                                 opt=cls.OPT).exe_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(getattr(cls, "tmp", ""), ignore_errors=True)

    def rodar(self, nome, *args, env=None, timeout=120):
        e = dict(os.environ)
        e.update(env or {})
        p = subprocess.run([self.exe[nome], *args], capture_output=True, text=True,
                           cwd=self.tmp, env=e, timeout=timeout)
        return p.stdout, p.stderr, p.returncode

    def trabalhador(self, nome, tarefas, porta=None):
        return subprocess.Popen([self.exe[nome], "--worker", str(porta or self.porta),
                                 "--worker-tasks", str(tarefas)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                cwd=self.tmp)

    @staticmethod
    def terminar(p, timeout=60):
        try:
            return p.communicate(timeout=timeout) + (p.returncode,)
        except subprocess.TimeoutExpired:
            p.kill()
            raise AssertionError("processo travou")


# ----------------------------------------------------------------------------
LOCAL = """
class Caixa {
    var v = 1;
    func dobro() {
        fork t { this.v = this.v * 2; return this.v; }
        return join t;
    }
}
func soma(l) { var s = 0; for (var x in l) { s += x; } return s; }
func tarefas() {
    var lista = [1, 2, 3];
    fork alterar { lista.append(99); return len(lista); }
    var no_filho = join alterar;
    print("filho viu", no_filho, "pai tem", len(lista));
    par { lista.append(7); lista.append(8); }
    print("depois do par:", len(lista));
    fork a on core 0 { return soma(lista); }
    fork b { return soma([10, 20]) * 2; }
    var ra = join a;
    var rb = join b;
    print(ra, rb, join a);
    fork aninhada { var base = soma(lista); fork interna { return base + 1; } return join interna; }
    print("aninhada:", join aninhada);
}
tarefas();
var c = new Caixa();
print(c.dobro(), c.v);
"""

TAREFA_QUE_FALHA = """
fork t { return 1 / 0; }
var r = join t;
print("resultado:", r);
"""

REMOTO_OK = """
func fib(n) {
    var a = 0; var b = 1; var r = [];
    for (var i = 0; i < n; i += 1) { r.append(a); var t = a + b; a = b; b = t; }
    return r;
}
func ola(nome) { print("olá de dentro da tarefa remota,", nome); return "feito"; }
func principal() {
    var n = 10;
    var nome = "marcos";
    fork f on host "127.0.0.1", PORTA { return fib(n); }
    fork o on host "servidor", PORTA { return ola(nome); }
    var r = join f;
    var s = join o;
    print(r);
    print(s);
}
principal();
"""

REMOTO_ERRO = """
func dividir(a, b) { return a / b; }
func principal() {
    var x = 1;
    fork t on host "127.0.0.1", PORTA { return dividir(x, 0); }
    var r = join t;
    print("não chega aqui?", r);
}
principal();
"""

REMOTO_OBJETO = """
class A { var x = 1; }
func principal() {
    var a = new A();
    fork t on host "127.0.0.1", PORTA { return a; }
    return join t;
}
principal();
"""


@unittest.skipUnless(HAS_GXX, "g++ não encontrado")
class TestForkLocal(Compilado):
    PROGRAMAS = {"local": LOCAL, "falha": TAREFA_QUE_FALHA}

    def test_valores_isolamento_e_aninhamento(self):
        out, err, code = self.rodar("local")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines(), [
            "filho viu 4 pai tem 3",          # o filho alterou a CÓPIA da lista
            "depois do par: 3",               # o par também trabalha com cópias
            "6 60 6",                         # join devolve o valor (e pode ser repetido)
            "aninhada: 7",
            "2 1"])                           # objeto: o filho alterou a cópia de this

    def test_erro_na_subtarefa_termina_com_codigo_1_e_join_devolve_null(self):
        out, err, code = self.rodar("falha")
        self.assertEqual(code, 1)
        self.assertIn("Erro de execução na subtarefa 't'", err)
        self.assertIn("Divisão por zero", err)
        self.assertEqual(out.strip(), "resultado: null")


@unittest.skipUnless(HAS_GXX, "g++ não encontrado")
class TestForkRemoto(Compilado):
    PROGRAMAS = {"ok": REMOTO_OK, "erro": REMOTO_ERRO, "objeto": REMOTO_OBJETO}

    def hosts(self):
        caminho = os.path.join(self.tmp, "minipar.hosts")
        with open(caminho, "w") as f:
            f.write("servidor = 127.0.0.1\n")
        return caminho

    def test_tarefas_executam_no_trabalhador_e_devolvem_resultados(self):
        w = self.trabalhador("ok", 2)
        time.sleep(0.4)
        out, err, code = self.rodar("ok", "--hosts", self.hosts())
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines(), ["[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]", "feito"])
        wout, werr, wcode = self.terminar(w)
        self.assertEqual(wcode, 0, werr)
        # o print da tarefa saiu no trabalhador, não no programa principal
        self.assertIn("olá de dentro da tarefa remota, marcos", wout)
        self.assertNotIn("olá", out)

    def test_erro_na_tarefa_remota_chega_ao_programa_principal(self):
        w = self.trabalhador("erro", 1)
        time.sleep(0.4)
        out, err, code = self.rodar("erro")
        self.assertEqual(code, 1)
        self.assertIn("A tarefa remota 't' falhou em 127.0.0.1", err)
        self.assertIn("Divisão por zero", err)
        wout, werr, wcode = self.terminar(w)
        self.assertEqual(wcode, 0, werr)               # o trabalhador continua saudável

    def test_trabalhador_inexistente(self):
        out, err, code = self.rodar("ok", "--hosts", self.hosts(), env={"MINIPAR_TIMEOUT": "1"})
        self.assertEqual(code, 1)
        self.assertIn("Não foi possível conectar", err)

    def test_valor_nao_serializavel_nao_vai_para_outro_computador(self):
        out, err, code = self.rodar("objeto")
        self.assertEqual(code, 1)
        self.assertIn("não pode ser enviado por um canal", err)

    def test_ajuda_mostra_modo_trabalhador(self):
        out, err, code = self.rodar("ok", "--help")
        self.assertEqual(code, 0)
        self.assertIn("--worker", out)


# ----------------------------------------------------------------------------
def mandelbrot_referencia():
    """O mesmo cálculo do código Python do enunciado."""
    largura, altura, max_iter = 50, 20, 100
    caracteres = " .:-=+#%@"
    linhas = ["\n=== FRACTAL DE MANDELBROT (Gerado pelo Núcleo 5) ==="]
    for y in range(altura):
        linha = ""
        cy = (y / altura) * 2.4 - 1.2
        for x in range(largura):
            cx = (x / largura) * 3.0 - 2.0
            zx, zy, it = 0.0, 0.0, 0
            while zx * zx + zy * zy <= 4.0 and it < max_iter:
                tmp = zx * zx - zy * zy + cx
                zy = 2.0 * zx * zy + cy
                zx = tmp
                it += 1
            linha += caracteres[int((it / max_iter) * (len(caracteres) - 1))]
        linhas.append(linha)
    linhas.append("====================================================\n")
    return "\n".join(linhas)


def benchmark(out):
    def num(rotulo):
        m = re.search(re.escape(rotulo) + r"\s*:\s*(-?[0-9.]+)", out)
        assert m, rotulo
        return float(m.group(1))
    return num


class BenchmarkBase(Compilado):
    OPT = "2"

    def conferir_benchmark(self, out, nucleos):
        num = benchmark(out)
        seq = num("Tempo Sequencial")
        par = num("Tempo Paralelo")
        self.assertGreater(seq, 0)
        self.assertGreater(par, 0)
        self.assertIn("BENCHMARK DE DESEMPENHO", out)
        if nucleos > 4:
            self.assertIn(f"Núcleos Utilizados (Paralelo) : {nucleos}", out)
        self.assertIn("Atividades corrigidas: 160 (sequencial) e 160 (paralelo)", out)
        # aceleração e redução são coerentes com os tempos (que saem arredondados)
        aceleracao = num("Aceleração") if nucleos == 4 else num("Aceleração (Speedup)")
        reducao = num("Redução no tempo") if nucleos == 4 else num("Redução de Tempo")
        self.assertAlmostEqual(aceleracao, seq / par, delta=max(0.4, 0.25 * seq / par))
        self.assertAlmostEqual(reducao, (1 - par / seq) * 100, delta=10)


class TestTeste08(BenchmarkBase):
    ARQUIVOS = {"t8": "teste08_avaliacao_4nucleos.mp"}

    def test_saida(self):
        out, err, code = self.rodar("t8")
        self.assertEqual(code, 0, err)
        self.assertIn("Total de Atividades a Avaliar: 160 (40 alunos x 4 atividades)", out)
        self.assertIn("--- 1. Executando Modo Sequencial (Apenas 1 Núcleo / Professor) ---", out)
        self.assertIn("--- 2. Executando Modo Paralelo (4 Núcleos Dedicados: Professor + 3 Monitores) ---", out)
        self.assertRegex(out, r"Tempo Sequencial Concluído em: [0-9.]+ segundos")
        self.assertRegex(out, r"Tempo Paralelo Concluído em:   [0-9.]+ segundos")
        self.conferir_benchmark(out, 4)

    def test_gerador_congruencial_igual_ao_do_python(self):
        with open(os.path.join(EX, "teste08_avaliacao_4nucleos.mp"), encoding="utf-8") as f:
            fonte = f.read()
        classe = fonte[fonte.index("class GeradorLCG"):fonte.index("# Consome ciclos de CPU")]
        programa = classe + """
        var g = new GeradorLCG(123456789);
        for (var i = 0; i < 6; i += 1) { print(g.proximo()); }
        var h = new GeradorLCG(123456789);
        print(fmt(h.uniforme(0.05, 0.15), 6));
        """
        caminho = os.path.join(self.tmp, "lcg.mp")
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(programa)
        exe = str(build_executable(caminho, out_dir=os.path.join(self.tmp, "lcg"), opt="0").exe_path)
        saida = subprocess.run([exe], capture_output=True, text=True).stdout.split()
        estado, esperado = 123456789, []
        for _ in range(6):
            estado = (estado * 1103515245 + 12345) & 0x7FFFFFFF      # o código Python do enunciado
            esperado.append(str(estado))
        self.assertEqual(saida[:6], esperado)
        primeiro = esperado[0]
        self.assertEqual(saida[6], f"{0.05 + (0.15 - 0.05) * (int(primeiro) / 2147483647.0):.6f}")


class TestTeste09(BenchmarkBase):
    ARQUIVOS = {"t9": "teste09_5nucleos_fractal.mp"}

    def test_saida_e_fractal_igual_ao_do_python(self):
        out, err, code = self.rodar("t9")
        self.assertEqual(code, 0, err)
        self.assertIn("Carga de Trabalho: 160 atividades + 1 Cálculo de Fractal ASCII", out)
        self.assertIn("--- 2. Executando Modo Paralelo (5 Núcleos Dedicados) ---", out)
        self.assertIn(mandelbrot_referencia(), out)
        self.conferir_benchmark(out, 5)


class TestTeste10(BenchmarkBase):
    ARQUIVOS = {"t10": "teste10_6nucleos_2fractais.mp"}

    def test_saida_fractais_e_svg(self):
        out, err, code = self.rodar("t10")
        self.assertEqual(code, 0, err)
        self.assertIn("Carga de Trabalho: 160 atividades + Mandelbrot (ASCII) + Sierpinski (SVG)", out)
        self.assertIn("--- 2. Executando Modo Paralelo (6 Núcleos Dedicados) ---", out)
        self.assertIn("-> [Núcleo 6] Tapete de Sierpinski gerado em sierpinski.svg (586 quadrados)", out)
        self.assertIn(mandelbrot_referencia(), out)
        self.assertRegex(out, r"Tempo para gerar o desenho   : [0-9.]+ s")
        self.conferir_benchmark(out, 6)

        raiz = ET.parse(os.path.join(self.tmp, "sierpinski.svg")).getroot()
        retangulos = [e for e in raiz if e.tag.endswith("rect")]
        self.assertEqual(len(retangulos), 1 + 1 + 585)          # fundo + bloco azul + centros brancos
        self.assertEqual(sum(1 for e in retangulos if e.get("fill") == "white"), 585)
        self.assertEqual(raiz.get("viewBox"), "-160.0 -160.0 320.0 320.0")


if __name__ == "__main__":
    unittest.main()
