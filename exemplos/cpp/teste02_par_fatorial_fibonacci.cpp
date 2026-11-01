// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----

// ---- protótipos ----
mp::Value fn_fatorial(mp::Value v_n);
mp::Value fn_fibonacci(mp::Value v_n);
mp::Value fn_main();
mp::Value fn_main_T_par1_t1();
mp::Value fn_main_T_par1_t2();

mp::Value fn_fatorial(mp::Value v_n) {
    // fatorial
    mp::Value v_i, v_r;
    v_r = mp::Value(1.0);
    v_i = mp::Value(2.0);
    L_while1: ;
    if (mp::gt(v_i, v_n)) goto L_endwhile2;
    v_r = mp::mul(v_r, v_i);
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_while1;
    L_endwhile2: ;
    return v_r;
}

mp::Value fn_fibonacci(mp::Value v_n) {
    // fibonacci
    mp::Value v_a, v_aux, v_b, v_cont;
    v_a = mp::Value(0.0);
    v_b = mp::Value(1.0);
    v_cont = mp::Value(0.0);
    L_while3: ;
    if (mp::ge(v_cont, v_n)) goto L_endwhile4;
    mp::print({mp::Value(std::string("Fib:", 4)), v_a});
    v_aux = mp::add(v_a, v_b);
    v_a = v_b;
    v_b = v_aux;
    v_cont = mp::add(v_cont, mp::Value(1.0));
    goto L_while3;
    L_endwhile4: ;
    return mp::Value();
}

mp::Value fn_main() {
    // main
    {
        mp::TaskGroup __g1;
        __g1.spawn("par1_t1", -1, "main$par1_t1", {});
        __g1.spawn("par1_t2", -1, "main$par1_t2", {});
        __g1.join();
    }
    return mp::Value();
}

mp::Value fn_main_T_par1_t1() {
    // main$par1_t1
    mp::Value t0, v_k;
    v_k = mp::Value(2.0);
    L_while5: ;
    if (mp::gt(v_k, mp::Value(5.0))) goto L_endwhile6;
    t0 = fn_fatorial(v_k);
    mp::print({mp::Value(std::string("Fatorial de", 11)), v_k, mp::Value(std::string("=", 1)), t0});
    v_k = mp::add(v_k, mp::Value(1.0));
    goto L_while5;
    L_endwhile6: ;
    return mp::Value();
}

mp::Value fn_main_T_par1_t2() {
    // main$par1_t2
    fn_fibonacci(mp::Value(10.0));
    return mp::Value();
}

static void register_all() {
    mp::register_task("main$par1_t1", [](mp::Args& a) -> mp::Value { mp::check_arity("tarefa main$par1_t1", a, 0); return fn_main_T_par1_t1(); });
    mp::register_task("main$par1_t2", [](mp::Args& a) -> mp::Value { mp::check_arity("tarefa main$par1_t2", a, 0); return fn_main_T_par1_t2(); });
}

int main(int argc, char** argv) {
    return mp::run_program(argc, argv, []() {
        register_all();
    }, []() { fn_main(); });
}
