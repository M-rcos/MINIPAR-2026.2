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
global desenho
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

func retangulo(x, y, tamanho, cor):
    t0 = tamanho / 2
    canto_x = x - t0
    t1 = tamanho / 2
    t2 = y + t1
    topo_y = -t2
    param canto_x
    param 3
    t3 = call fmt, 2
    t4 = "<rect x=\"" + t3
    t5 = t4 + "\" y=\""
    param topo_y
    param 3
    t6 = call fmt, 2
    t7 = t5 + t6
    t8 = t7 + "\" width=\""
    param tamanho
    param 3
    t9 = call fmt, 2
    t10 = t8 + t9
    t11 = t10 + "\" height=\""
    param tamanho
    param 3
    t12 = call fmt, 2
    t13 = t11 + t12
    t14 = t13 + "\" fill=\""
    t15 = t14 + cor
    t16 = t15 + "\"/>"
    return t16
endfunc

func desenhar_tapete(x, y, lado, grau, retangulos):
    if grau > 0 goto endif18
    return
  endif18:
    t0 = lado / 3
    param x
    param y
    param t0
    param "white"
    t1 = call retangulo, 4
    param t1
    callm retangulos.append, 1
    novo_lado = lado / 3
    novo_grau = grau - 1
    t2 = x - novo_lado
    t3 = y + novo_lado
    param t2
    param t3
    param novo_lado
    param novo_grau
    param retangulos
    call desenhar_tapete, 5
    t4 = y + novo_lado
    param x
    param t4
    param novo_lado
    param novo_grau
    param retangulos
    call desenhar_tapete, 5
    t5 = x + novo_lado
    t6 = y + novo_lado
    param t5
    param t6
    param novo_lado
    param novo_grau
    param retangulos
    call desenhar_tapete, 5
    t7 = x - novo_lado
    param t7
    param y
    param novo_lado
    param novo_grau
    param retangulos
    call desenhar_tapete, 5
    t8 = x + novo_lado
    param t8
    param y
    param novo_lado
    param novo_grau
    param retangulos
    call desenhar_tapete, 5
    t9 = x - novo_lado
    t10 = y - novo_lado
    param t9
    param t10
    param novo_lado
    param novo_grau
    param retangulos
    call desenhar_tapete, 5
    t11 = y - novo_lado
    param x
    param t11
    param novo_lado
    param novo_grau
    param retangulos
    call desenhar_tapete, 5
    t12 = x + novo_lado
    t13 = y - novo_lado
    param t12
    param t13
    param novo_lado
    param novo_grau
    param retangulos
    call desenhar_tapete, 5
    return
endfunc

func gerar_sierpinski(lado_inicial, grau):
    inicio = call clock, 0
    retangulos = new_list
    param 0
    param 0
    param lado_inicial
    param "navy"
    t0 = call retangulo, 4
    append retangulos, t0
    param 0
    param 0
    param lado_inicial
    param grau
    param retangulos
    call desenhar_tapete, 5
    t1 = lado_inicial / 2
    meio = t1 + 10
    t2 = -meio
    param t2
    param 1
    t3 = call fmt, 2
    t4 = "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"" + t3
    t5 = t4 + " "
    t6 = -meio
    param t6
    param 1
    t7 = call fmt, 2
    t8 = t5 + t7
    t9 = t8 + " "
    t10 = 2 * meio
    param t10
    param 1
    t11 = call fmt, 2
    t12 = t9 + t11
    t13 = t12 + " "
    t14 = 2 * meio
    param t14
    param 1
    t15 = call fmt, 2
    t16 = t13 + t15
    svg = t16 + "\">\n"
    t17 = -meio
    param t17
    param 1
    t18 = call fmt, 2
    t19 = "<rect x=\"" + t18
    t20 = t19 + "\" y=\""
    t21 = -meio
    param t21
    param 1
    t22 = call fmt, 2
    t23 = t20 + t22
    t24 = t23 + "\" width=\""
    t25 = 2 * meio
    param t25
    param 1
    t26 = call fmt, 2
    t27 = t24 + t26
    t28 = t27 + "\" height=\""
    t29 = 2 * meio
    param t29
    param 1
    t30 = call fmt, 2
    t31 = t28 + t30
    t32 = t31 + "\" fill=\"black\"/>\n"
    svg = svg + t32
    t33 = retangulos
    t34 = size t33
    t35 = 0
  foreach19:
    if t35 >= t34 goto endforeach21
    r = t33[t35]
    t36 = r + "\n"
    svg = svg + t36
  foreachstep20:
    t35 = t35 + 1
    goto foreach19
  endforeach21:
    svg = svg + "</svg>\n"
    t37 = new_list
    append t37, svg
    t38 = call clock, 0
    t39 = t38 - inicio
    append t37, t39
    param retangulos
    t40 = call len, 1
    append t37, t40
    return t37
endfunc

func execucao_sequencial():
    print "--- 1. Executando Modo Sequencial (Apenas 1 Núcleo) ---"
    inicio = call clock, 0
    param "Professor"
    param tarefas
    resultados = call avaliar_lote, 2
    fractal = call gerar_mandelbrot, 0
    param 300
    param 4
    sierpinski = call gerar_sierpinski, 2
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
    print "--- 2. Executando Modo Paralelo (6 Núcleos Dedicados) ---"
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
    fork mandelbrot on core 4 -> execucao_paralela$mandelbrot()
    fork sierpinski on core 5 -> execucao_paralela$sierpinski()
    r0 = join professor
    r1 = join monitor1
    r2 = join monitor2
    r3 = join monitor3
    texto_mandelbrot = join mandelbrot
    desenho_1 = join sierpinski
    fim = call clock, 0
    t14 = new_list
    t15 = fim - inicio
    append t14, t15
    append t14, texto_mandelbrot
    param r0
    t16 = call len, 1
    param r1
    t17 = call len, 1
    t18 = t16 + t17
    param r2
    t19 = call len, 1
    t20 = t18 + t19
    param r3
    t21 = call len, 1
    t22 = t20 + t21
    append t14, t22
    append t14, desenho_1
    return t14
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

task execucao_paralela$mandelbrot():
    t12 = call gerar_mandelbrot, 0
    return t12
endfunc

task execucao_paralela$sierpinski():
    param 300
    param 4
    t13 = call gerar_sierpinski, 2
    return t13
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
  for22:
    if aluno_id >= NUM_ALUNOS goto endfor24
    atividade_id = 0
  for25:
    if atividade_id >= ATIVIDADES_POR_ALUNO goto endfor27
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
  forstep26:
    atividade_id = atividade_id + 1
    goto for25
  endfor27:
  forstep23:
    aluno_id = aluno_id + 1
    goto for22
  endfor24:
    param TOTAL_ATIVIDADES
    t7 = call to_string, 1
    t8 = "Carga de Trabalho: " + t7
    t9 = t8 + " atividades + Mandelbrot (ASCII) + Sierpinski (SVG)\n"
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
    desenho = resultado_par[3]
    t13 = desenho[0]
    param "sierpinski.svg"
    param t13
    call write_file, 2
    t14 = desenho[2]
    param t14
    t15 = call to_string, 1
    t16 = "-> [Núcleo 6] Tapete de Sierpinski gerado em sierpinski.svg (" + t15
    t17 = t16 + " quadrados)"
    print t17
    param tempo_par
    param 2
    t18 = call fmt, 2
    t19 = "Tempo Paralelo Concluído em:   " + t18
    t20 = t19 + " segundos\n"
    print t20
    t21 = resultado_par[1]
    print t21
    speedup = 0
    reducao_pct = 0
    if tempo_par <= 0 goto endif28
    speedup = tempo_seq / tempo_par
    t22 = tempo_seq - tempo_par
    t23 = t22 / tempo_seq
    reducao_pct = t23 * 100
  endif28:
    print "=========================================="
    print "         BENCHMARK DE DESEMPENHO          "
    print "=========================================="
    print "Núcleos Utilizados (Paralelo) : 6"
    param tempo_seq
    param 2
    t24 = call fmt, 2
    t25 = "Tempo Sequencial             : " + t24
    t26 = t25 + " s"
    print t26
    param tempo_par
    param 2
    t27 = call fmt, 2
    t28 = "Tempo Paralelo               : " + t27
    t29 = t28 + " s"
    print t29
    param speedup
    param 2
    t30 = call fmt, 2
    t31 = "Aceleração (Speedup)         : " + t30
    t32 = t31 + "x mais rápido!"
    print t32
    param reducao_pct
    param 1
    t33 = call fmt, 2
    t34 = "Redução de Tempo             : " + t33
    t35 = t34 + "%"
    print t35
    t36 = desenho[1]
    param t36
    param 4
    t37 = call fmt, 2
    t38 = "Tempo para gerar o desenho   : " + t37
    t39 = t38 + " s (medido à parte, dentro da subtarefa)"
    print t39
    print "=========================================="
    t40 = resultado_seq[2]
    param t40
    t41 = call to_string, 1
    t42 = "Atividades corrigidas: " + t41
    t43 = t42 + " (sequencial) e "
    t44 = resultado_par[2]
    param t44
    t45 = call to_string, 1
    t46 = t43 + t45
    t47 = t46 + " (paralelo)"
    print t47
    return
endfunc
