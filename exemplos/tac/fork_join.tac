func avaliar(nome, quantidade):
    i = 0
  while1:
    if i >= quantidade goto endwhile2
    i = i + 1
    goto while1
  endwhile2:
    t0 = nome + " concluiu "
    param quantidade
    t1 = call to_string, 1
    t2 = t0 + t1
    t3 = t2 + " atividades"
    return t3
endfunc

func executar():
    fork professor on core 0 -> executar$professor()
    fork monitor1 on core 1 -> executar$monitor1()
    fork local -> executar$local()
    t3 = join professor
    print t3
    t4 = join monitor1
    print t4
    t5 = join local
    print t5
    print "Todas as subtarefas terminaram"
    return
endfunc

task executar$professor():
    param "Professor"
    param 40
    t0 = call avaliar, 2
    return t0
endfunc

task executar$monitor1():
    param "Monitor 1"
    param 40
    t1 = call avaliar, 2
    return t1
endfunc

task executar$local():
    param "Tarefa local"
    param 10
    t2 = call avaliar, 2
    return t2
endfunc

func main():
    call executar, 0
    return
endfunc
