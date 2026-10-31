"""Testes dos canais de comunicação (sockets): dois processos reais em localhost."""

import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from minipar.codegen import build_executable  # noqa: E402

EX = os.path.join(os.path.dirname(__file__), "..", "exemplos")
HAS_GXX = bool(os.environ.get("CXX") or shutil.which("g++") or shutil.which("c++"))


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


ECO_SERVIDOR = """
c_channel eco a b;
var ativo = true;
while (ativo) {
    var m = eco.receive();
    if (m[0] == "fim") {
        ativo = false;
    } else {
        eco.send(m[0]);
    }
}
print("servidor terminou");
"""

ECO_CLIENTE = """
c_channel eco a b;
var msgs = [
    [1, 2.5, "oi"],
    [true, false, null],
    [[1, [2, 3]], "ç ã é ✅"],
    [0.1 + 0.2, -7, 1000000000000]
];
for (var m in msgs) {
    eco.send(m);
    var r = eco.receive();
    print(r[0]);
}
var grande = "ab";
for (var i = 0; i < 19; i += 1) { grande = grande + grande; }
eco.send(grande);
var volta = eco.receive();
print(len(volta[0]), volta[0] == grande);
var ultimo = 0;
for (var k = 1; k <= 300; k += 1) {
    eco.send(k);
    ultimo = eco.receive()[0];
}
print("ultimo:", ultimo);
eco.send("fim");
"""

PONTE_SERVIDOR = """
var c = c_channel("0.0.0.0", PORTA);
var m = c.receive();
c.send(m[0] * 2, "dobro");
c.close();
"""

PONTE_CLIENTE = """
var c = c_channel("127.0.0.1", PORTA);
c.send(21);
var r = c.receive();
print(r[0], r[1]);
"""

PAR_SERVIDOR = """
c_channel dupla a b;
var x = dupla.receive();
var y = dupla.receive();
var soma = x[0] + y[0];
dupla.send(soma);
"""

PAR_CLIENTE = """
c_channel dupla a b;
par {
    dupla.send(40);
    dupla.send(2);
}
print("soma:", dupla.receive()[0]);
"""

SEM_PAR = """
c_channel solto a b;
solto.send(1);
"""

OBJETO = """
class A { var x = 1; }
c_channel c a b;
c.send(new A());
"""

CLIENTE_SOZINHO = """
c_channel orfao a b;
orfao.send(1);
"""

PEER_SAI = """
c_channel curto a b;
var m = curto.receive();
print("recebi", m[0]);
"""

PEER_ESPERA = """
c_channel curto a b;
curto.send(1);
var r = curto.receive();
print("nunca");
"""


def compilar(tmp, nome, fonte):
    caminho = os.path.join(tmp, nome + ".mp")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(fonte)
    return str(build_executable(caminho, out_dir=os.path.join(tmp, "out"), opt="0").exe_path)


class BaseCanais(unittest.TestCase):
    PORTA = None
    PROGRAMAS = {}

    @classmethod
    def setUpClass(cls):
        if not HAS_GXX:
            raise unittest.SkipTest("g++ não encontrado")
        cls.tmp = tempfile.mkdtemp()
        cls.PORTA = free_port()
        cls.exe = {nome: compilar(cls.tmp, nome, src.replace("PORTA", str(cls.PORTA)))
                   for nome, src in cls.PROGRAMAS.items()}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(getattr(cls, "tmp", ""), ignore_errors=True)

    def hosts(self, canal):
        """Arquivo de endereços com uma porta livre para o canal."""
        porta = free_port()
        caminho = os.path.join(self.tmp, f"hosts_{canal}_{porta}.txt")
        with open(caminho, "w") as f:
            f.write(f"# teste\ncomputador_1 = 127.0.0.1\nb = localhost\nport.{canal} = {porta}\n")
        return caminho

    def iniciar(self, nome, *args, env=None, stdin=None):
        e = dict(os.environ)
        e.update(env or {})
        return subprocess.Popen([self.exe[nome], *args], stdin=subprocess.PIPE if stdin is not None else None,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                cwd=self.tmp, env=e)

    @staticmethod
    def terminar(p, timeout=30):
        try:
            out, err = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            out, err = p.communicate()
            raise AssertionError(f"processo travou. stdout={out!r} stderr={err!r}")
        return out, err, p.returncode


class TestEco(BaseCanais):
    PROGRAMAS = {"servidor": ECO_SERVIDOR, "cliente": ECO_CLIENTE}

    def executar(self, primeiro="servidor"):
        h = self.hosts("eco")
        srv_args = ["--node", "b", "--hosts", h]
        cli_args = ["--node", "a", "--hosts", h]
        if primeiro == "servidor":
            srv = self.iniciar("servidor", *srv_args)
            time.sleep(0.3)
            cli = self.iniciar("cliente", *cli_args)
        else:
            cli = self.iniciar("cliente", *cli_args)
            time.sleep(1.0)
            srv = self.iniciar("servidor", *srv_args)
        return self.terminar(cli), self.terminar(srv)

    def conferir(self, cli, srv):
        out, err, code = cli
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines(), [
            "[1, 2.5, 'oi']",
            "[true, false, null]",
            "[[1, [2, 3]], 'ç ã é ✅']",
            "[0.30000000000000004, -7, 1000000000000]",
            "1048576 true",
            "ultimo: 300"])
        self.assertEqual(srv[2], 0, srv[1])
        self.assertEqual(srv[0].strip(), "servidor terminou")

    def test_servidor_inicia_primeiro(self):
        cli, srv = self.executar("servidor")
        self.conferir(cli, srv)

    def test_cliente_inicia_primeiro_e_tenta_de_novo(self):
        cli, srv = self.executar("cliente")
        self.conferir(cli, srv)
        self.assertIn("aguardando o outro programa", cli[1])

    def test_node_obrigatorio_e_validado(self):
        p = self.iniciar("cliente", "--hosts", self.hosts("eco"))
        out, err, code = self.terminar(p)
        self.assertEqual(code, 1)
        self.assertIn("Informe qual deles este programa é", err)
        p = self.iniciar("cliente", "--node", "zzz", "--hosts", self.hosts("eco"))
        out, err, code = self.terminar(p)
        self.assertEqual(code, 1)
        self.assertIn("valor atual: 'zzz'", err)

    def test_node_por_variavel_de_ambiente(self):
        h = self.hosts("eco")
        srv = self.iniciar("servidor", "--hosts", h, env={"MINIPAR_NODE": "b"})
        time.sleep(0.3)
        cli = self.iniciar("cliente", "--hosts", h, env={"MINIPAR_NODE": "a"})
        self.conferir(self.terminar(cli), self.terminar(srv))

    def test_arquivo_de_hosts_inexistente(self):
        p = self.iniciar("cliente", "--node", "a", "--hosts", "/nao/existe.txt")
        out, err, code = self.terminar(p)
        self.assertEqual(code, 1)
        self.assertIn("Não foi possível abrir o arquivo de computadores", err)

    def test_cliente_sem_servidor_desiste_depois_do_tempo_limite(self):
        t0 = time.time()
        p = self.iniciar("cliente", "--node", "a", "--hosts", self.hosts("eco"),
                         env={"MINIPAR_TIMEOUT": "1"})
        out, err, code = self.terminar(p)
        self.assertEqual(code, 1)
        self.assertIn("Não foi possível conectar", err)
        self.assertLess(time.time() - t0, 10)

    def test_servidor_sem_cliente_desiste_depois_do_tempo_limite(self):
        p = self.iniciar("servidor", "--node", "b", "--hosts", self.hosts("eco"),
                         env={"MINIPAR_TIMEOUT": "1"})
        out, err, code = self.terminar(p)
        self.assertEqual(code, 1)
        self.assertIn("Tempo esgotado", err)

    def test_ajuda(self):
        out, err, code = self.terminar(self.iniciar("cliente", "--help"))
        self.assertEqual(code, 0)
        self.assertIn("--node", out)


class TestCanalPorExpressao(BaseCanais):
    PROGRAMAS = {"servidor": PONTE_SERVIDOR, "cliente": PONTE_CLIENTE}

    def test_c_channel_com_endereco_e_porta(self):
        srv = self.iniciar("servidor")
        time.sleep(0.3)
        cli = self.iniciar("cliente")
        out, err, code = self.terminar(cli)
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "42 dobro")
        self.assertEqual(self.terminar(srv)[2], 0)


class TestParalelismoNoCanal(BaseCanais):
    PROGRAMAS = {"servidor": PAR_SERVIDOR, "cliente": PAR_CLIENTE}

    def test_threads_enviam_pelo_mesmo_canal(self):
        h = self.hosts("dupla")
        srv = self.iniciar("servidor", "--node", "b", "--hosts", h)
        time.sleep(0.3)
        cli = self.iniciar("cliente", "--node", "a", "--hosts", h)
        out, err, code = self.terminar(cli)
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "soma: 42")
        self.assertEqual(self.terminar(srv)[2], 0)


class TestErrosDeCanal(BaseCanais):
    PROGRAMAS = {"objeto": OBJETO, "recebe": PEER_SAI, "espera": PEER_ESPERA}

    def test_objeto_nao_pode_ser_enviado(self):
        out, err, code = self.terminar(self.iniciar("objeto", "--node", "a"))
        self.assertEqual(code, 1)
        self.assertIn("não pode ser enviado por um canal", err)

    def test_conexao_encerrada_pelo_outro_programa(self):
        h = self.hosts("curto")
        a = self.iniciar("recebe", "--node", "b", "--hosts", h)       # recebe 1 mensagem e termina
        time.sleep(0.3)
        b = self.iniciar("espera", "--node", "a", "--hosts", h)       # envia e espera resposta
        out_b, err_b, code_b = self.terminar(b)
        out_a, err_a, code_a = self.terminar(a)
        self.assertEqual(code_a, 0, err_a)
        self.assertEqual(out_a.strip(), "recebi 1")
        self.assertEqual(code_b, 1)
        self.assertIn("Conexão encerrada pelo outro programa", err_b)


@unittest.skipUnless(HAS_GXX, "g++ não encontrado")
class TestProgramaDoTeste1(unittest.TestCase):
    """Os programas reais do Teste 1 (calculadora cliente/servidor)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.srv_exe = str(build_executable(os.path.join(EX, "teste01_servidor.mp"),
                                           out_dir=cls.tmp, opt="0").exe_path)
        cls.cli_exe = str(build_executable(os.path.join(EX, "teste01_cliente.mp"),
                                           out_dir=cls.tmp, opt="0").exe_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_calculadora(self):
        hosts = os.path.join(self.tmp, "minipar.hosts")
        with open(hosts, "w") as f:
            f.write(f"port.calculadora = {free_port()}\n")
        srv = subprocess.Popen([self.srv_exe, "--node", "computador_2", "--hosts", hosts],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(0.3)
        entrada = "+\n3\n4\n*\n6\n7\n/\n10\n4\n/\n1\n0\n^\n1\n1\nsair\n"
        cli = subprocess.run([self.cli_exe, "--node", "computador_1", "--hosts", hosts],
                             input=entrada, capture_output=True, text=True, timeout=30)
        srv_out, srv_err = srv.communicate(timeout=30)
        self.assertEqual(cli.returncode, 0, cli.stderr)
        resultados = [l.split("Resultado: ")[-1] for l in cli.stdout.splitlines() if "Resultado:" in l]
        self.assertEqual(resultados, ["7", "42", "2.5", "erro: divisão por zero",
                                      "erro: operação inválida"])
        self.assertEqual(srv.returncode, 0, srv_err)
        self.assertIn("Pedido recebido: 3 + 4", srv_out)
        self.assertIn("Pedido recebido: 10 / 4", srv_out)
        self.assertIn("Cliente encerrou a conversa.", srv_out)


class TestPortaPadrao(unittest.TestCase):
    def test_porta_derivada_do_nome_esta_na_faixa_e_e_estavel(self):
        # mesma função FNV-1a do runtime, reproduzida aqui para conferir a faixa
        def porta(nome):
            h = 2166136261
            for c in nome.encode("utf-8"):
                h = ((h ^ c) * 16777619) & 0xFFFFFFFF
            return 20000 + h % 20000
        for nome in ("calculadora", "eco", "dupla"):
            self.assertTrue(20000 <= porta(nome) < 40000)
        self.assertEqual(porta("calculadora"), porta("calculadora"))


if __name__ == "__main__":
    unittest.main()
