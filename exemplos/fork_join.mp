# fork/join com alocação em núcleos da CPU e devolução de resultados.
# Cada subtarefa recebe CÓPIAS das variáveis que usa e devolve um valor com "return";
# o programa principal recebe esse valor com "join nome".
func avaliar(nome, quantidade) {
    var i = 0;
    while (i < quantidade) {
        i += 1;
    }
    return nome + " concluiu " + to_string(quantidade) + " atividades";
}

func executar() {
    fork professor on core 0 {
        return avaliar("Professor", 40);
    }
    fork monitor1 on core 1 {
        return avaliar("Monitor 1", 40);
    }
    fork local {
        return avaliar("Tarefa local", 10);
    }

    # join espera cada subtarefa e entrega o valor devolvido
    print(join professor);
    print(join monitor1);
    print(join local);
    print("Todas as subtarefas terminaram");
}

executar();
