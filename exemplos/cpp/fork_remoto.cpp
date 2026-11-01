// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----

// ---- protótipos ----
mp::Value fn_fibonacci(mp::Value v_n);
mp::Value fn_fatorial(mp::Value v_n);
mp::Value fn_principal();
mp::Value fn_principal_T_fib(mp::Value v_quantos);
mp::Value fn_principal_T_fat(mp::Value v_numero);
mp::Value fn_main();

mp::Value fn_fibonacci(mp::Value v_n) {
    // fibonacci
    mp::Value v_a, v_b, v_i, v_lista, v_proximo;
    v_lista = mp::new_list();
    v_a = mp::Value(0.0);
    v_b = mp::Value(1.0);
    v_i = mp::Value(0.0);
    L_for1: ;
    if (mp::ge(v_i, v_n)) goto L_endfor3;
    mp::append(v_lista, v_a);
    v_proximo = mp::add(v_a, v_b);
    v_a = v_b;
    v_b = v_proximo;
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for1;
    L_endfor3: ;
    return v_lista;
}

mp::Value fn_fatorial(mp::Value v_n) {
    // fatorial
    mp::Value v_i, v_r;
    v_r = mp::Value(1.0);
    v_i = mp::Value(2.0);
    L_for4: ;
    if (mp::gt(v_i, v_n)) goto L_endfor6;
    v_r = mp::mul(v_r, v_i);
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for4;
    L_endfor6: ;
    return v_r;
}

mp::Value fn_principal() {
    // principal
    mp::Value v_f, v_numero, v_quantos, v_serie;
    mp::ForkTable __forks;
    v_quantos = mp::Value(12.0);
    v_numero = mp::Value(10.0);
    __forks.spawn_host("fib", mp::Value(std::string("127.0.0.1", 9)), mp::Value(9000.0), "principal$fib", {mp::copy_for_task(v_quantos)});
    __forks.spawn("fat", mp::Value(0.0), "principal$fat", {mp::copy_for_task(v_numero)});
    v_f = __forks.join_value("fat");
    v_serie = __forks.join_value("fib");
    mp::print({mp::Value(std::string("Fatorial de", 11)), v_numero, mp::Value(std::string("=", 1)), v_f});
    mp::print({mp::Value(std::string("Fibonacci:", 10)), v_serie});
    return mp::Value();
}

mp::Value fn_principal_T_fib(mp::Value v_quantos) {
    // principal$fib
    mp::Value t0;
    t0 = fn_fibonacci(v_quantos);
    return t0;
}

mp::Value fn_principal_T_fat(mp::Value v_numero) {
    // principal$fat
    mp::Value t1;
    t1 = fn_fatorial(v_numero);
    return t1;
}

mp::Value fn_main() {
    // main
    fn_principal();
    return mp::Value();
}

static void register_all() {
    mp::register_task("principal$fib", [](mp::Args& a) -> mp::Value { mp::check_arity("tarefa principal$fib", a, 1); return fn_principal_T_fib(a[0]); });
    mp::register_task("principal$fat", [](mp::Args& a) -> mp::Value { mp::check_arity("tarefa principal$fat", a, 1); return fn_principal_T_fat(a[0]); });
}

int main(int argc, char** argv) {
    return mp::run_program(argc, argv, []() {
        register_all();
    }, []() { fn_main(); });
}
