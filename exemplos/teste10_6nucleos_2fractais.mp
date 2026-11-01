# Teste 10: algoritmo paralelo em 6 núcleos:
#   núcleos 1 a 4: 160 atividades corrigidas por 4 avaliadores (Professor e três Monitores)
#   núcleo 5:      fractal de Mandelbrot em arte ASCII
#   núcleo 6:      fractal do Tapete de Sierpinski, desenhado como imagem SVG
#
# No programa original o desenho usava a biblioteca "turtle" (uma janela gráfica). Aqui o
# desenho vira o arquivo sierpinski.svg, que se abre no navegador. A GERAÇÃO do desenho
# entra na medição de tempo (nos dois modos, para a comparação ser justa); gravar e abrir
# o arquivo acontece fora da medição.

class GeradorLCG {
    var estado = 0;

    func init(semente) {
        this.estado = semente;
    }

    # (a * b) mod 2^31 sem passar de 53 bits (ver Teste 8)
    func mult_mod(a, b) {
        var alto = floor(a / 65536);
        var baixo = a - alto * 65536;
        return (((alto * b) % 32768) * 65536 + baixo * b) % 2147483648;
    }

    func proximo() {
        this.estado = (this.mult_mod(this.estado, 1103515245) + 12345) % 2147483648;
        return this.estado;
    }

    func uniforme(minimo, maximo) {
        var fracao = this.proximo() / 2147483647.0;
        return minimo + (maximo - minimo) * fracao;
    }
}

func simular_atraso(segundos) {
    var iteracoes = floor(segundos * 1500000);
    var soma = 0;
    for (var i = 0; i < iteracoes; i += 1) {
        soma += i;
    }
    return soma;
}

var NUM_ALUNOS = 40;
var ATIVIDADES_POR_ALUNO = 4;
var TOTAL_ATIVIDADES = NUM_ALUNOS * ATIVIDADES_POR_ALUNO;
var AVALIADORES = ["Professor", "Monitor 1", "Monitor 2", "Monitor 3"];

var tarefas = [];
for (var aluno_id = 0; aluno_id < NUM_ALUNOS; aluno_id += 1) {
    for (var atividade_id = 0; atividade_id < ATIVIDADES_POR_ALUNO; atividade_id += 1) {
        tarefas.append("Aluno " + to_string(aluno_id + 1) + " - Atividade " + to_string(atividade_id + 1));
    }
}

# ---------------- Núcleos 1 a 4: correção das atividades ----------------
func avaliar_atividade(tarefa, avaliador, gerador) {
    var tempo_correcao = gerador.uniforme(0.05, 0.15);
    simular_atraso(tempo_correcao);
    return "[" + avaliador + "] Concluiu: " + tarefa;
}

func avaliar_lote(avaliador, lote) {
    var gerador = new GeradorLCG(123456789);
    var resultados = [];
    for (var tarefa in lote) {
        resultados.append(avaliar_atividade(tarefa, avaliador, gerador));
    }
    return resultados;
}

# ---------------- Núcleo 5: fractal de Mandelbrot (ASCII) ----------------
func gerar_mandelbrot() {
    var largura = 50;
    var altura = 20;
    var max_iter = 100;
    var caracteres = " .:-=+#%@";

    var texto = "\n=== FRACTAL DE MANDELBROT (Gerado pelo Núcleo 5) ===";
    for (var y = 0; y < altura; y += 1) {
        var linha = "";
        # mapeia a coordenada Y para o plano complexo [-1.2, 1.2]
        var cy = (y / altura) * 2.4 - 1.2;
        for (var x = 0; x < largura; x += 1) {
            # mapeia a coordenada X para o plano complexo [-2.0, 1.0]
            var cx = (x / largura) * 3.0 - 2.0;

            # equação complexa do fractal: z = z^2 + c
            var zx = 0.0;
            var zy = 0.0;
            var iteracao = 0;
            while (zx * zx + zy * zy <= 4.0 && iteracao < max_iter) {
                var tmp = zx * zx - zy * zy + cx;
                zy = 2.0 * zx * zy + cy;
                zx = tmp;
                iteracao += 1;
            }

            # mapeia o número de iterações para um caractere
            var indice = floor((iteracao / max_iter) * (len(caracteres) - 1));
            linha += caracteres[indice];
        }
        texto += "\n" + linha;
    }
    texto += "\n====================================================\n";
    return texto;
}

func fatiar(lista, inicio, fim) {
    var parte = [];
    for (var i = inicio; i < fim; i += 1) {
        parte.append(lista[i]);
    }
    return parte;
}

# ---------------- Núcleo 6: Tapete de Sierpinski (SVG) ----------------
# Retângulo SVG de lado "tamanho" centrado em (x, y). No SVG o eixo Y cresce para baixo,
# então o Y do desenho é invertido.
func retangulo(x, y, tamanho, cor) {
    var canto_x = x - tamanho / 2;
    var topo_y = -(y + tamanho / 2);
    return "<rect x=\"" + fmt(canto_x, 3) + "\" y=\"" + fmt(topo_y, 3) + "\" width=\"" + fmt(tamanho, 3) +
           "\" height=\"" + fmt(tamanho, 3) + "\" fill=\"" + cor + "\"/>";
}

# Algoritmo recursivo: desenha o quadrado central "vazio" (branco) e repete nos 8 vizinhos.
func desenhar_tapete(x, y, lado, grau, retangulos) {
    if (grau <= 0) {
        return;
    }
    retangulos.append(retangulo(x, y, lado / 3, "white"));

    var novo_lado = lado / 3;
    var novo_grau = grau - 1;
    desenhar_tapete(x - novo_lado, y + novo_lado, novo_lado, novo_grau, retangulos);
    desenhar_tapete(x, y + novo_lado, novo_lado, novo_grau, retangulos);
    desenhar_tapete(x + novo_lado, y + novo_lado, novo_lado, novo_grau, retangulos);

    desenhar_tapete(x - novo_lado, y, novo_lado, novo_grau, retangulos);
    desenhar_tapete(x + novo_lado, y, novo_lado, novo_grau, retangulos);

    desenhar_tapete(x - novo_lado, y - novo_lado, novo_lado, novo_grau, retangulos);
    desenhar_tapete(x, y - novo_lado, novo_lado, novo_grau, retangulos);
    desenhar_tapete(x + novo_lado, y - novo_lado, novo_lado, novo_grau, retangulos);
}

# Devolve o texto do arquivo SVG e o tempo gasto para gerá-lo (medido à parte).
func gerar_sierpinski(lado_inicial, grau) {
    var inicio = clock();
    var retangulos = [];
    retangulos.append(retangulo(0, 0, lado_inicial, "navy"));          # bloco principal (azul)
    desenhar_tapete(0, 0, lado_inicial, grau, retangulos);             # perfuração recursiva

    var meio = lado_inicial / 2 + 10;
    var svg = "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"" + fmt(-meio, 1) + " " + fmt(-meio, 1) + " " +
              fmt(2 * meio, 1) + " " + fmt(2 * meio, 1) + "\">\n";
    svg += "<rect x=\"" + fmt(-meio, 1) + "\" y=\"" + fmt(-meio, 1) + "\" width=\"" + fmt(2 * meio, 1) +
           "\" height=\"" + fmt(2 * meio, 1) + "\" fill=\"black\"/>\n";
    for (var r in retangulos) {
        svg += r + "\n";
    }
    svg += "</svg>\n";
    return [svg, clock() - inicio, len(retangulos)];
}

# Modo sequencial: 1 único núcleo faz TODO o trabalho (atividades, Mandelbrot e Sierpinski).
func execucao_sequencial() {
    print("--- 1. Executando Modo Sequencial (Apenas 1 Núcleo) ---");
    var inicio = clock();
    var resultados = avaliar_lote("Professor", tarefas);
    var fractal = gerar_mandelbrot();
    var sierpinski = gerar_sierpinski(300, 4);
    var fim = clock();
    return [fim - inicio, fractal, len(resultados)];
}

# Modo paralelo: 6 subtarefas, cada uma em um núcleo.
func execucao_paralela() {
    print("--- 2. Executando Modo Paralelo (6 Núcleos Dedicados) ---");
    var tamanho_fatia = floor(len(tarefas) / len(AVALIADORES));
    var lote0 = fatiar(tarefas, 0, tamanho_fatia);
    var lote1 = fatiar(tarefas, tamanho_fatia, 2 * tamanho_fatia);
    var lote2 = fatiar(tarefas, 2 * tamanho_fatia, 3 * tamanho_fatia);
    var lote3 = fatiar(tarefas, 3 * tamanho_fatia, 4 * tamanho_fatia);
    var nome0 = AVALIADORES[0];
    var nome1 = AVALIADORES[1];
    var nome2 = AVALIADORES[2];
    var nome3 = AVALIADORES[3];

    var inicio = clock();

    # FORK: dispara as 6 subtarefas em núcleos separados
    fork professor on core 0 {
        return avaliar_lote(nome0, lote0);
    }
    fork monitor1 on core 1 {
        return avaliar_lote(nome1, lote1);
    }
    fork monitor2 on core 2 {
        return avaliar_lote(nome2, lote2);
    }
    fork monitor3 on core 3 {
        return avaliar_lote(nome3, lote3);
    }
    fork mandelbrot on core 4 {
        return gerar_mandelbrot();
    }
    fork sierpinski on core 5 {
        return gerar_sierpinski(300, 4);
    }

    # JOIN: aguarda as 6 subtarefas e recebe os resultados
    var r0 = join professor;
    var r1 = join monitor1;
    var r2 = join monitor2;
    var r3 = join monitor3;
    var texto_mandelbrot = join mandelbrot;
    var desenho = join sierpinski;

    var fim = clock();
    return [fim - inicio, texto_mandelbrot, len(r0) + len(r1) + len(r2) + len(r3), desenho];
}

# ---------------- benchmark ----------------
print("Carga de Trabalho: " + to_string(TOTAL_ATIVIDADES) + " atividades + Mandelbrot (ASCII) + Sierpinski (SVG)\n");

var resultado_seq = execucao_sequencial();
var tempo_seq = resultado_seq[0];
print("Tempo Sequencial Concluído em: " + fmt(tempo_seq, 2) + " segundos\n");

var resultado_par = execucao_paralela();
var tempo_par = resultado_par[0];

# Fora da medição: grava o desenho para ser aberto no navegador.
var desenho = resultado_par[3];
write_file("sierpinski.svg", desenho[0]);
print("-> [Núcleo 6] Tapete de Sierpinski gerado em sierpinski.svg (" + to_string(desenho[2]) + " quadrados)");
print("Tempo Paralelo Concluído em:   " + fmt(tempo_par, 2) + " segundos\n");

# fractal de Mandelbrot gerado no processamento paralelo
print(resultado_par[1]);

var speedup = 0;
var reducao_pct = 0;
if (tempo_par > 0) {
    speedup = tempo_seq / tempo_par;
    reducao_pct = ((tempo_seq - tempo_par) / tempo_seq) * 100;
}

print("==========================================");
print("         BENCHMARK DE DESEMPENHO          ");
print("==========================================");
print("Núcleos Utilizados (Paralelo) : 6");
print("Tempo Sequencial             : " + fmt(tempo_seq, 2) + " s");
print("Tempo Paralelo               : " + fmt(tempo_par, 2) + " s");
print("Aceleração (Speedup)         : " + fmt(speedup, 2) + "x mais rápido!");
print("Redução de Tempo             : " + fmt(reducao_pct, 1) + "%");
print("Tempo para gerar o desenho   : " + fmt(desenho[1], 4) + " s (medido à parte, dentro da subtarefa)");
print("==========================================");
print("Atividades corrigidas: " + to_string(resultado_seq[2]) + " (sequencial) e " + to_string(resultado_par[2]) + " (paralelo)");
