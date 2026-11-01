// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----

// ---- protótipos ----
mp::Value fn_avaliar(mp::Value v_nome, mp::Value v_quantidade);
mp::Value fn_executar();
mp::Value fn_executar_T_professor();
mp::Value fn_executar_T_monitor1();
mp::Value fn_executar_T_local();
mp::Value fn_main();

mp::Value fn_avaliar(mp::Value v_nome, mp::Value v_quantidade) {
    // avaliar
    mp::Value t0, t1, t2, t3, v_i;
    v_i = mp::Value(0.0);
    L_while1: ;
    if (mp::ge(v_i, v_quantidade)) goto L_endwhile2;
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_while1;
    L_endwhile2: ;
    t0 = mp::add(v_nome, mp::Value(std::string(" concluiu ", 10)));
    t1 = mp::bi_to_string(v_quantidade);
    t2 = mp::add(t0, t1);
    t3 = mp::add(t2, mp::Value(std::string(" atividades", 11)));
    return t3;
}

mp::Value fn_executar() {
    // executar
    mp::Value t3, t4, t5;
    mp::ForkTable __forks;
    __forks.spawn("professor", mp::Value(0.0), "executar$professor", {});
    __forks.spawn("monitor1", mp::Value(1.0), "executar$monitor1", {});
    __forks.spawn("local", mp::Value(), "executar$local", {});
    t3 = __forks.join_value("professor");
    mp::print({t3});
    t4 = __forks.join_value("monitor1");
    mp::print({t4});
    t5 = __forks.join_value("local");
    mp::print({t5});
    mp::print({mp::Value(std::string("Todas as subtarefas terminaram", 30))});
    return mp::Value();
}

mp::Value fn_executar_T_professor() {
    // executar$professor
    mp::Value t0;
    t0 = fn_avaliar(mp::Value(std::string("Professor", 9)), mp::Value(40.0));
    return t0;
}

mp::Value fn_executar_T_monitor1() {
    // executar$monitor1
    mp::Value t1;
    t1 = fn_avaliar(mp::Value(std::string("Monitor 1", 9)), mp::Value(40.0));
    return t1;
}

mp::Value fn_executar_T_local() {
    // executar$local
    mp::Value t2;
    t2 = fn_avaliar(mp::Value(std::string("Tarefa local", 12)), mp::Value(10.0));
    return t2;
}

mp::Value fn_main() {
    // main
    fn_executar();
    return mp::Value();
}

static void register_all() {
    mp::register_task("executar$professor", [](mp::Args& a) -> mp::Value { mp::check_arity("tarefa executar$professor", a, 0); return fn_executar_T_professor(); });
    mp::register_task("executar$monitor1", [](mp::Args& a) -> mp::Value { mp::check_arity("tarefa executar$monitor1", a, 0); return fn_executar_T_monitor1(); });
    mp::register_task("executar$local", [](mp::Args& a) -> mp::Value { mp::check_arity("tarefa executar$local", a, 0); return fn_executar_T_local(); });
}

int main(int argc, char** argv) {
    return mp::run_program(argc, argv, []() {
        register_all();
    }, []() { fn_main(); });
}
