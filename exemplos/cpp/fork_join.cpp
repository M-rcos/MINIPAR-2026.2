// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----

// ---- protótipos ----
mp::Value fn_avaliar(mp::Value v_nome, mp::Value v_quantidade);
mp::Value fn_main();

mp::Value fn_avaliar(mp::Value v_nome, mp::Value v_quantidade) {
    // avaliar
    mp::Value v_i;
    v_i = mp::Value(0.0);
    L_while1: ;
    if (mp::ge(v_i, v_quantidade)) goto L_endwhile2;
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_while1;
    L_endwhile2: ;
    mp::print({v_nome, mp::Value(std::string("concluiu", 8)), v_quantidade, mp::Value(std::string("atividades", 10))});
    return mp::Value();
}

mp::Value fn_main() {
    // main
    mp::ForkTable __forks;
    __forks.spawn("professor", mp::Value(0.0), [=]() mutable {
        fn_avaliar(mp::Value(std::string("Professor", 9)), mp::Value(40.0));
    });
    __forks.spawn("monitor1", mp::Value(1.0), [=]() mutable {
        fn_avaliar(mp::Value(std::string("Monitor 1", 9)), mp::Value(40.0));
    });
    __forks.spawn_host("remoto", mp::Value(std::string("192.168.0.20", 12)), mp::Value(9000.0), [=]() mutable {
        fn_avaliar(mp::Value(std::string("Monitor remoto", 14)), mp::Value(40.0));
    });
    __forks.spawn_local("local", [=]() mutable {
        fn_avaliar(mp::Value(std::string("Tarefa local", 12)), mp::Value(10.0));
    });
    __forks.join_all();
    mp::print({mp::Value(std::string("Todas as subtarefas terminaram", 30))});
    return mp::Value();
}

static void register_classes() {
}

int main(int argc, char** argv) {
    return mp::run_program(argc, argv, []() {
        register_classes();
    }, []() { fn_main(); });
}
