// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----
static mp::Value v_array;

// ---- protótipos ----
mp::Value fn_quicksort_iterativo(mp::Value v_arr);
mp::Value fn_main();

mp::Value fn_quicksort_iterativo(mp::Value v_arr) {
    // quicksort_iterativo
    mp::Value t0, t1, t2, t3, t4, t5, t6, t7;
    mp::Value v_fim, v_i, v_inicio, v_j, v_pilha, v_pivo, v_troca, v_troca_pivo;
    v_pilha = mp::new_list();
    mp::append(v_pilha, mp::Value(0.0));
    t0 = mp::bi_len(v_arr);
    t1 = mp::sub(t0, mp::Value(1.0));
    mp::append(v_pilha, t1);
    L_while1: ;
    t2 = mp::bi_len(v_pilha);
    if (mp::le(t2, mp::Value(0.0))) goto L_endwhile2;
    v_fim = mp::pop(v_pilha);
    v_inicio = mp::pop(v_pilha);
    if (mp::ge(v_inicio, v_fim)) goto L_endif3;
    v_pivo = mp::get_index(v_arr, v_fim);
    v_i = mp::sub(v_inicio, mp::Value(1.0));
    v_j = v_inicio;
    L_for4: ;
    if (mp::ge(v_j, v_fim)) goto L_endfor6;
    t3 = mp::get_index(v_arr, v_j);
    if (mp::gt(t3, v_pivo)) goto L_endif7;
    v_i = mp::add(v_i, mp::Value(1.0));
    v_troca = mp::get_index(v_arr, v_i);
    t4 = mp::get_index(v_arr, v_j);
    mp::set_index(v_arr, v_i, t4);
    mp::set_index(v_arr, v_j, v_troca);
    L_endif7: ;
    v_j = mp::add(v_j, mp::Value(1.0));
    goto L_for4;
    L_endfor6: ;
    v_i = mp::add(v_i, mp::Value(1.0));
    v_troca_pivo = mp::get_index(v_arr, v_i);
    t5 = mp::get_index(v_arr, v_fim);
    mp::set_index(v_arr, v_i, t5);
    mp::set_index(v_arr, v_fim, v_troca_pivo);
    mp::append(v_pilha, v_inicio);
    t6 = mp::sub(v_i, mp::Value(1.0));
    mp::append(v_pilha, t6);
    t7 = mp::add(v_i, mp::Value(1.0));
    mp::append(v_pilha, t7);
    mp::append(v_pilha, v_fim);
    L_endif3: ;
    goto L_while1;
    L_endwhile2: ;
    return mp::Value();
}

mp::Value fn_main() {
    // main
    v_array = mp::new_list();
    mp::append(v_array, mp::Value(33.0));
    mp::append(v_array, mp::Value(12.0));
    mp::append(v_array, mp::Value(98.0));
    mp::append(v_array, mp::Value(5.0));
    mp::append(v_array, mp::Value(61.0));
    fn_quicksort_iterativo(v_array);
    mp::print({mp::Value(std::string("Array ordenado:", 15)), v_array});
    return mp::Value();
}

static void register_classes() {
}

int main() {
    return mp::run_program([]() {
        register_classes();
    }, []() { fn_main(); });
}
