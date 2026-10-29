# Exemplo de fork/join com alocação em núcleos e em outro computador.
func avaliar(nome, quantidade) {
    var i = 0;
    while (i < quantidade) {
        i += 1;
    }
    print(nome, "concluiu", quantidade, "atividades");
}

fork professor on core 0 {
    avaliar("Professor", 40);
}
fork monitor1 on core 1 {
    avaliar("Monitor 1", 40);
}
fork remoto on host "192.168.0.20", 9000 {
    avaliar("Monitor remoto", 40);
}
fork local {
    avaliar("Tarefa local", 10);
}

join;
print("Todas as subtarefas terminaram");
