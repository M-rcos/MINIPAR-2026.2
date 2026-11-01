class GeradorLCG:
    field estado
    method init
    method mult_mod
    method proximo
    method uniforme
endclass

global NUM_ALUNOS
global ATIVIDADES_POR_ALUNO
global TOTAL_ATIVIDADES
global AVALIADORES
global tarefas
global resultado_seq
global tempo_seq
global resultado_par
global tempo_par
global speedup
global reducao_pct

func GeradorLCG.__attrs(this):
    this.estado = 0
    return
endfunc

func GeradorLCG.init(this, semente):
    this.estado = semente
    return
endfunc

func GeradorLCG.mult_mod(this, a, b):
    t0 = a / 65536
    param t0
    alto = call floor, 1
    t1 = alto * 65536
    baixo = a - t1
    t2 = alto * b
    t3 = t2 % 32768
    t4 = t3 * 65536
    t5 = baixo * b
    t6 = t4 + t5
    t7 = t6 % 2147483648
    return t7
endfunc

func GeradorLCG.proximo(this):
    t0 = this.estado
    param t0
    param 1103515245
    t1 = callm this.mult_mod, 2
    t2 = t1 + 12345
    t3 = t2 % 2147483648
    this.estado = t3
    t4 = this.estado
    return t4
endfunc

func GeradorLCG.uniforme(this, minimo, maximo):
    t0 = callm this.proximo, 0
    fracao = t0 / 2147483647.0
    t1 = maximo - minimo
    t2 = t1 * fracao
    t3 = minimo + t2
    return t3
endfunc

func simular_atraso(segundos):
    t0 = segundos * 1500000
    param t0
    iteracoes = call floor, 1
    soma = 0
    i = 0
  for1:
    if i >= iteracoes goto endfor3
    soma = soma + i
  forstep2:
    i = i + 1
    goto for1
  endfor3:
    return soma
endfunc

func avaliar_atividade(tarefa, avaliador, gerador):
    param 0.05
    param 0.15
    tempo_correcao = callm gerador.uniforme, 2
    param tempo_correcao
    call simular_atraso, 1
    t0 = "[" + avaliador
    t1 = t0 + "] Concluiu: "
    t2 = t1 + tarefa
    return t2
endfunc

func avaliar_lote(avaliador, lote):
    gerador = new GeradorLCG
    param gerador
    call GeradorLCG.__attrs, 1
    param gerador
    param 123456789
    call GeradorLCG.init, 2
    resultados = new_list
    t0 = lote
    t1 = size t0
    t2 = 0
  foreach4:
    if t2 >= t1 goto endforeach6
    tarefa = t0[t2]
    param tarefa
    param avaliador
    param gerador
    t3 = call avaliar_atividade, 3
    append resultados, t3
  foreachstep5:
    t2 = t2 + 1
    goto foreach4
  endforeach6:
    return resultados
endfunc

func fatiar(lista, inicio, fim):
    parte = new_list
    i = inicio
  for7:
    if i >= fim goto endfor9
    t0 = lista[i]
    append parte, t0
  forstep8:
    i = i + 1
    goto for7
  endfor9:
    return parte
endfunc

func execucao_sequencial():
    print "--- 1. Executando Modo Sequencial (Apenas 1 Núcleo / Professor) ---"
    inicio = call clock, 0
    param "Professor"
    param tarefas
    resultados = call avaliar_lote, 2
    fim = call clock, 0
    t0 = new_list
    t1 = fim - inicio
    append t0, t1
    param resultados
    t2 = call len, 1
    append t0, t2
    return t0
endfunc

func execucao_paralela():
    print "--- 2. Executando Modo Paralelo (4 Núcleos Dedicados: Professor + 3 Monitores) ---"
    param tarefas
    t0 = call len, 1
    param AVALIADORES
    t1 = call len, 1
    t2 = t0 / t1
    param t2
    tamanho_fatia = call floor, 1
    param tarefas
    param 0
    param tamanho_fatia
    lote0 = call fatiar, 3
    t3 = 2 * tamanho_fatia
    param tarefas
    param tamanho_fatia
    param t3
    lote1 = call fatiar, 3
    t4 = 2 * tamanho_fatia
    t5 = 3 * tamanho_fatia
    param tarefas
    param t4
    param t5
    lote2 = call fatiar, 3
    t6 = 3 * tamanho_fatia
    t7 = 4 * tamanho_fatia
    param tarefas
    param t6
    param t7
    lote3 = call fatiar, 3
    nome0 = AVALIADORES[0]
    nome1 = AVALIADORES[1]
    nome2 = AVALIADORES[2]
    nome3 = AVALIADORES[3]
    inicio = call clock, 0
    fork professor on core 0 -> execucao_paralela$professor(nome0, lote0)
    fork monitor1 on core 1 -> execucao_paralela$monitor1(nome1, lote1)
    fork monitor2 on core 2 -> execucao_paralela$monitor2(nome2, lote2)
    fork monitor3 on core 3 -> execucao_paralela$monitor3(nome3, lote3)
    r0 = join professor
    r1 = join monitor1
    r2 = join monitor2
    r3 = join monitor3
    fim = call clock, 0
    t12 = new_list
    t13 = fim - inicio
    append t12, t13
    param r0
    t14 = call len, 1
    param r1
    t15 = call len, 1
    t16 = t14 + t15
    param r2
    t17 = call len, 1
    t18 = t16 + t17
    param r3
    t19 = call len, 1
    t20 = t18 + t19
    append t12, t20
    return t12
endfunc

task execucao_paralela$professor(nome0, lote0):
    param nome0
    param lote0
    t8 = call avaliar_lote, 2
    return t8
endfunc

task execucao_paralela$monitor1(nome1, lote1):
    param nome1
    param lote1
    t9 = call avaliar_lote, 2
    return t9
endfunc

task execucao_paralela$monitor2(nome2, lote2):
    param nome2
    param lote2
    t10 = call avaliar_lote, 2
    return t10
endfunc

task execucao_paralela$monitor3(nome3, lote3):
    param nome3
    param lote3
    t11 = call avaliar_lote, 2
    return t11
endfunc

func main():
    NUM_ALUNOS = 40
    ATIVIDADES_POR_ALUNO = 4
    TOTAL_ATIVIDADES = NUM_ALUNOS * ATIVIDADES_POR_ALUNO
    AVALIADORES = new_list
    append AVALIADORES, "Professor"
    append AVALIADORES, "Monitor 1"
    append AVALIADORES, "Monitor 2"
    append AVALIADORES, "Monitor 3"
    tarefas = new_list
    aluno_id = 0
  for10:
    if aluno_id >= NUM_ALUNOS goto endfor12
    atividade_id = 0
  for13:
    if atividade_id >= ATIVIDADES_POR_ALUNO goto endfor15
    t0 = aluno_id + 1
    param t0
    t1 = call to_string, 1
    t2 = "Aluno " + t1
    t3 = t2 + " - Atividade "
    t4 = atividade_id + 1
    param t4
    t5 = call to_string, 1
    t6 = t3 + t5
    append tarefas, t6
  forstep14:
    atividade_id = atividade_id + 1
    goto for13
  endfor15:
  forstep11:
    aluno_id = aluno_id + 1
    goto for10
  endfor12:
    param TOTAL_ATIVIDADES
    t7 = call to_string, 1
    t8 = "Total de Atividades a Avaliar: " + t7
    t9 = t8 + " (40 alunos x 4 atividades)\n"
    print t9
    resultado_seq = call execucao_sequencial, 0
    tempo_seq = resultado_seq[0]
    param tempo_seq
    param 2
    t10 = call fmt, 2
    t11 = "Tempo Sequencial Concluído em: " + t10
    t12 = t11 + " segundos\n"
    print t12
    resultado_par = call execucao_paralela, 0
    tempo_par = resultado_par[0]
    param tempo_par
    param 2
    t13 = call fmt, 2
    t14 = "Tempo Paralelo Concluído em:   " + t13
    t15 = t14 + " segundos\n"
    print t15
    speedup = 0
    reducao_pct = 0
    if tempo_par <= 0 goto endif16
    speedup = tempo_seq / tempo_par
    t16 = tempo_seq - tempo_par
    t17 = t16 / tempo_seq
    reducao_pct = t17 * 100
  endif16:
    print "=========================================="
    print "         BENCHMARK DE DESEMPENHO          "
    print "=========================================="
    param tempo_seq
    param 2
    t18 = call fmt, 2
    t19 = "Tempo Sequencial : " + t18
    t20 = t19 + " s"
    print t20
    param tempo_par
    param 2
    t21 = call fmt, 2
    t22 = "Tempo Paralelo   : " + t21
    t23 = t22 + " s"
    print t23
    param speedup
    param 2
    t24 = call fmt, 2
    t25 = "Aceleração       : " + t24
    t26 = t25 + "x mais rápido!"
    print t26
    param reducao_pct
    param 1
    t27 = call fmt, 2
    t28 = "Redução no tempo : " + t27
    t29 = t28 + "% de economia"
    print t29
    print "=========================================="
    t30 = resultado_seq[1]
    param t30
    t31 = call to_string, 1
    t32 = "Atividades corrigidas: " + t31
    t33 = t32 + " (sequencial) e "
    t34 = resultado_par[1]
    param t34
    t35 = call to_string, 1
    t36 = t33 + t35
    t37 = t36 + " (paralelo)"
    print t37
    return
endfunc
