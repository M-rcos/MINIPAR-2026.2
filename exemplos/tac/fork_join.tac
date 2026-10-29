func avaliar(nome, quantidade):
    i = 0
  while1:
    if i >= quantidade goto endwhile2
    i = i + 1
    goto while1
  endwhile2:
    print nome, "concluiu", quantidade, "atividades"
    return
endfunc

func main():
    fork professor on core 0
      param "Professor"
      param 40
      call avaliar, 2
    end_task
    fork monitor1 on core 1
      param "Monitor 1"
      param 40
      call avaliar, 2
    end_task
    fork remoto on host "192.168.0.20", 9000
      param "Monitor remoto"
      param 40
      call avaliar, 2
    end_task
    fork local
      param "Tarefa local"
      param 10
      call avaliar, 2
    end_task
    join
    print "Todas as subtarefas terminaram"
    return
endfunc
