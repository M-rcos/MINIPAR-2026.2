# Teste 8: algoritmo paralelo de avaliação de atividades didáticas com 4 avaliadores
# (Professor e três Monitores), cada um em um núcleo da CPU (fork e join).
# Todos os recursos são nativos da linguagem, sem importações.

# ---------------------------------------------------------------------------
# 1. RECURSOS NATIVOS
# ---------------------------------------------------------------------------

# Gerador de números pseudoaleatórios (congruencial linear). Cada avaliador tem o seu,
# como cada processo tinha o seu estado no programa original.
class GeradorLCG {
    var estado = 0;

    func init(semente) {
        this.estado = semente;
    }

    # (a * b) mod 2^31, separando "a" em duas metades de 16 bits para o produto
    # nunca passar de 53 bits (a precisão exata dos números da linguagem).
    func mult_mod(a, b) {
        var alto = floor(a / 65536);
        var baixo = a - alto * 65536;
        return (((alto * b) % 32768) * 65536 + baixo * b) % 2147483648;
    }

    func proximo() {
        this.estado = (this.mult_mod(this.estado, 1103515245) + 12345) % 2147483648;
        return this.estado;
    }

    # decimal aleatório entre "minimo" e "maximo"
    func uniforme(minimo, maximo) {
        var fracao = this.proximo() / 2147483647.0;
        return minimo + (maximo - minimo) * fracao;
    }
}

# Consome ciclos de CPU para simular o tempo de trabalho.
func simular_atraso(segundos) {
    var iteracoes = floor(segundos * 1500000);
    var soma = 0;
    for (var i = 0; i < iteracoes; i += 1) {
        soma += i;
    }
    return soma;
}

# ---------------------------------------------------------------------------
# 2. CONFIGURAÇÃO DO CENÁRIO
# ---------------------------------------------------------------------------
var NUM_ALUNOS = 40;
var ATIVIDADES_POR_ALUNO = 4;
var TOTAL_ATIVIDADES = NUM_ALUNOS * ATIVIDADES_POR_ALUNO;      # 160 atividades
var AVALIADORES = ["Professor", "Monitor 1", "Monitor 2", "Monitor 3"];

# As 160 tarefas a serem corrigidas
var tarefas = [];
for (var aluno_id = 0; aluno_id < NUM_ALUNOS; aluno_id += 1) {
    for (var atividade_id = 0; atividade_id < ATIVIDADES_POR_ALUNO; atividade_id += 1) {
        tarefas.append("Aluno " + to_string(aluno_id + 1) + " - Atividade " + to_string(atividade_id + 1));
    }
}

# ---------------------------------------------------------------------------
# 3. FUNÇÕES DE TRABALHO
# ---------------------------------------------------------------------------

# Simula a correção de uma atividade individual.
func avaliar_atividade(tarefa, avaliador, gerador) {
    var tempo_correcao = gerador.uniforme(0.05, 0.15);
    simular_atraso(tempo_correcao);
    return "[" + avaliador + "] Concluiu: " + tarefa;
}

# Trabalho de um núcleo: corrige o seu lote e devolve a lista de atividades corrigidas.
func avaliar_lote(avaliador, lote) {
    var gerador = new GeradorLCG(123456789);
    var resultados = [];
    for (var tarefa in lote) {
        resultados.append(avaliar_atividade(tarefa, avaliador, gerador));
    }
    return resultados;
}

func fatiar(lista, inicio, fim) {
    var parte = [];
    for (var i = inicio; i < fim; i += 1) {
        parte.append(lista[i]);
    }
    return parte;
}

# Modo sequencial: 1 único núcleo resolve todas as 160 tarefas.
func execucao_sequencial() {
    print("--- 1. Executando Modo Sequencial (Apenas 1 Núcleo / Professor) ---");
    var inicio = clock();
    var resultados = avaliar_lote("Professor", tarefas);
    var fim = clock();
    return [fim - inicio, len(resultados)];
}

# Modo paralelo: aloca manualmente 1 subtarefa (núcleo de CPU) para cada avaliador.
func execucao_paralela() {
    print("--- 2. Executando Modo Paralelo (4 Núcleos Dedicados: Professor + 3 Monitores) ---");
    var tamanho_fatia = floor(len(tarefas) / len(AVALIADORES));    # 4 fatias de 40 tarefas
    var lote0 = fatiar(tarefas, 0, tamanho_fatia);
    var lote1 = fatiar(tarefas, tamanho_fatia, 2 * tamanho_fatia);
    var lote2 = fatiar(tarefas, 2 * tamanho_fatia, 3 * tamanho_fatia);
    var lote3 = fatiar(tarefas, 3 * tamanho_fatia, 4 * tamanho_fatia);
    var nome0 = AVALIADORES[0];
    var nome1 = AVALIADORES[1];
    var nome2 = AVALIADORES[2];
    var nome3 = AVALIADORES[3];

    var inicio = clock();

    # ETAPA 1: FORK (cria e inicia uma subtarefa por avaliador, cada uma em um núcleo)
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

    # ETAPA 2: JOIN (aguarda cada núcleo terminar e recebe as atividades corrigidas)
    var r0 = join professor;
    var r1 = join monitor1;
    var r2 = join monitor2;
    var r3 = join monitor3;

    var fim = clock();
    return [fim - inicio, len(r0) + len(r1) + len(r2) + len(r3)];
}

# ---------------------------------------------------------------------------
# 4. BENCHMARK E EXIBIÇÃO DOS RESULTADOS
# ---------------------------------------------------------------------------
print("Total de Atividades a Avaliar: " + to_string(TOTAL_ATIVIDADES) + " (40 alunos x 4 atividades)\n");

var resultado_seq = execucao_sequencial();
var tempo_seq = resultado_seq[0];
print("Tempo Sequencial Concluído em: " + fmt(tempo_seq, 2) + " segundos\n");

var resultado_par = execucao_paralela();
var tempo_par = resultado_par[0];
print("Tempo Paralelo Concluído em:   " + fmt(tempo_par, 2) + " segundos\n");

# Métricas do benchmark
var speedup = 0;
var reducao_pct = 0;
if (tempo_par > 0) {
    speedup = tempo_seq / tempo_par;
    reducao_pct = ((tempo_seq - tempo_par) / tempo_seq) * 100;
}

print("==========================================");
print("         BENCHMARK DE DESEMPENHO          ");
print("==========================================");
print("Tempo Sequencial : " + fmt(tempo_seq, 2) + " s");
print("Tempo Paralelo   : " + fmt(tempo_par, 2) + " s");
print("Aceleração       : " + fmt(speedup, 2) + "x mais rápido!");
print("Redução no tempo : " + fmt(reducao_pct, 1) + "% de economia");
print("==========================================");
print("Atividades corrigidas: " + to_string(resultado_seq[1]) + " (sequencial) e " + to_string(resultado_par[1]) + " (paralelo)");
