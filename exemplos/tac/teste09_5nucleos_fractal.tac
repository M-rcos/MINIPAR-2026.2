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

func gerar_mandelbrot():
    largura = 50
    altura = 20
    max_iter = 100
    caracteres = " .:-=+#%@"
    texto = "\n=== FRACTAL DE MANDELBROT (Gerado pelo Núcleo 5) ==="
    y = 0
  for7:
    if y >= altura goto endfor9
    linha = ""
    t0 = y / altura
    t1 = t0 * 2.4
    cy = t1 - 1.2
    x = 0
  for10:
    if x >= largura goto endfor12
    t2 = x / largura
    t3 = t2 * 3.0
    cx = t3 - 2.0
    zx = 0.0
    zy = 0.0
    iteracao = 0
  while13:
    t4 = zx * zx
    t5 = zy * zy
    t6 = t4 + t5
    if t6 > 4.0 goto endwhile14
    if iteracao >= max_iter goto endwhile14
    t7 = zx * zx
    t8 = zy * zy
    t9 = t7 - t8
    tmp = t9 + cx
    t10 = 2.0 * zx
    t11 = t10 * zy
    zy = t11 + cy
    zx = tmp
    iteracao = iteracao + 1
    goto while13
  endwhile14:
    t12 = iteracao / max_iter
    param caracteres
    t13 = call len, 1
    t14 = t13 - 1
    t15 = t12 * t14
    param t15
    indice = call floor, 1
    t16 = caracteres[indice]
    linha = linha + t16
  forstep11:
    x = x + 1
    goto for10
  endfor12:
    t17 = "\n" + linha
    texto = texto + t17
  forstep8:
    y = y + 1
    goto for7
  endfor9:
    texto = texto + "\n====================================================\n"
    return texto
endfunc

func fatiar(lista, inicio, fim):
    parte = new_list
    i = inicio
  for15:
    if i >= fim goto endfor17
    t0 = lista[i]
    append parte, t0
  forstep16:
    i = i + 1
    goto for15
  endfor17:
    return parte
endfunc

func execucao_sequencial():
    print "--- 1. Executando Modo Sequencial (Apenas 1 Núcleo) ---"
    inicio = call clock, 0
    param "Professor"
    param tarefas
    resultados = call avaliar_lote, 2
    fractal = call gerar_mandelbrot, 0
    fim = call clock, 0
    t0 = new_list
    t1 = fim - inicio
    append t0, t1
    append t0, fractal
    param resultados
    t2 = call len, 1
    append t0, t2
    return t0
endfunc

func execucao_paralela():
    print "--- 2. Executando Modo Paralelo (5 Núcleos Dedicados) ---"
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
    fork fractal on core 4 -> execucao_paralela$fractal()
    r0 = join professor
    r1 = join monitor1
    r2 = join monitor2
    r3 = join monitor3
    texto_fractal = join fractal
    fim = call clock, 0
    t13 = new_list
    t14 = fim - inicio
    append t13, t14
    append t13, texto_fractal
    param r0
    t15 = call len, 1
    param r1
    t16 = call len, 1
    t17 = t15 + t16
    param r2
    t18 = call len, 1
    t19 = t17 + t18
    param r3
    t20 = call len, 1
    t21 = t19 + t20
    append t13, t21
    return t13
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

task execucao_paralela$fractal():
    t12 = call gerar_mandelbrot, 0
    return t12
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
  for18:
    if aluno_id >= NUM_ALUNOS goto endfor20
    atividade_id = 0
  for21:
    if atividade_id >= ATIVIDADES_POR_ALUNO goto endfor23
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
  forstep22:
    atividade_id = atividade_id + 1
    goto for21
  endfor23:
  forstep19:
    aluno_id = aluno_id + 1
    goto for18
  endfor20:
    param TOTAL_ATIVIDADES
    t7 = call to_string, 1
    t8 = "Carga de Trabalho: " + t7
    t9 = t8 + " atividades + 1 Cálculo de Fractal ASCII\n"
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
    t16 = resultado_par[1]
    print t16
    speedup = 0
    reducao_pct = 0
    if tempo_par <= 0 goto endif24
    speedup = tempo_seq / tempo_par
    t17 = tempo_seq - tempo_par
    t18 = t17 / tempo_seq
    reducao_pct = t18 * 100
  endif24:
    print "=========================================="
    print "         BENCHMARK DE DESEMPENHO          "
    print "=========================================="
    print "Núcleos Utilizados (Paralelo) : 5"
    param tempo_seq
    param 2
    t19 = call fmt, 2
    t20 = "Tempo Sequencial             : " + t19
    t21 = t20 + " s"
    print t21
    param tempo_par
    param 2
    t22 = call fmt, 2
    t23 = "Tempo Paralelo               : " + t22
    t24 = t23 + " s"
    print t24
    param speedup
    param 2
    t25 = call fmt, 2
    t26 = "Aceleração (Speedup)         : " + t25
    t27 = t26 + "x mais rápido!"
    print t27
    param reducao_pct
    param 1
    t28 = call fmt, 2
    t29 = "Redução de Tempo             : " + t28
    t30 = t29 + "%"
    print t30
    print "=========================================="
    t31 = resultado_seq[2]
    param t31
    t32 = call to_string, 1
    t33 = "Atividades corrigidas: " + t32
    t34 = t33 + " (sequencial) e "
    t35 = resultado_par[2]
    param t35
    t36 = call to_string, 1
    t37 = t34 + t36
    t38 = t37 + " (paralelo)"
    print t38
    return
endfunc
