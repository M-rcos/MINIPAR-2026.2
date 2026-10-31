// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----
static mp::Value v_interface_ordenacao;

// ---- protótipos ----
mp::Value fn_eh_inteiro(mp::Value v_tok);
mp::Value fn_Quicksort_D___attrs(mp::Value self);
mp::Value fn_Quicksort_D_init(mp::Value self, mp::Value v_a);
mp::Value fn_Quicksort_D_ordenar(mp::Value self);
mp::Value fn_Quicksort_D_quicksort_rec(mp::Value self, mp::Value v_array);
mp::Value fn_InterfaceOrdenacao_D___attrs(mp::Value self);
mp::Value fn_InterfaceOrdenacao_D_iniciar(mp::Value self);
mp::Value fn_main();

mp::Value fn_eh_inteiro(mp::Value v_tok) {
    // eh_inteiro
    mp::Value t0, t1, t2, t3, t4, t5, v_i, v_inicio;
    t0 = mp::bi_len(v_tok);
    if (mp::ne(t0, mp::Value(0.0))) goto L_endif1;
    return mp::Value(false);
    L_endif1: ;
    v_inicio = mp::Value(0.0);
    t1 = mp::get_index(v_tok, mp::Value(0.0));
    if (mp::ne(t1, mp::Value(std::string("-", 1)))) goto L_endif2;
    v_inicio = mp::Value(1.0);
    L_endif2: ;
    t2 = mp::bi_len(v_tok);
    if (mp::ne(v_inicio, t2)) goto L_endif3;
    return mp::Value(false);
    L_endif3: ;
    v_i = v_inicio;
    L_for4: ;
    t3 = mp::bi_len(v_tok);
    if (mp::ge(v_i, t3)) goto L_endfor6;
    t4 = mp::get_index(v_tok, v_i);
    t5 = mp::bi_is_digit(t4);
    if ((t5).truthy()) goto L_endif7;
    return mp::Value(false);
    L_endif7: ;
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for4;
    L_endfor6: ;
    return mp::Value(true);
}

mp::Value fn_Quicksort_D___attrs(mp::Value self) {
    // Quicksort.__attrs
    mp::Value t0;
    (void)self;
    t0 = mp::new_list();
    mp::set_member(self, "array", t0);
    return mp::Value();
}

mp::Value fn_Quicksort_D_init(mp::Value self, mp::Value v_a) {
    // Quicksort.init
    (void)self;
    mp::set_member(self, "array", v_a);
    return mp::Value();
}

mp::Value fn_Quicksort_D_ordenar(mp::Value self) {
    // Quicksort.ordenar
    mp::Value t0, t1;
    (void)self;
    t0 = mp::get_member(self, "array");
    t1 = mp::call_method(self, "quicksort_rec", {t0});
    return t1;
}

mp::Value fn_Quicksort_D_quicksort_rec(mp::Value self, mp::Value v_array) {
    // Quicksort.quicksort_rec
    mp::Value t0, t1, t2, t3, t4, t5, t6, v_i;
    mp::Value v_maiores, v_menores, v_pivot, v_x;
    (void)self;
    t0 = mp::bi_len(v_array);
    if (mp::gt(t0, mp::Value(1.0))) goto L_endif8;
    return v_array;
    L_endif8: ;
    v_pivot = mp::get_index(v_array, mp::Value(0.0));
    v_menores = mp::new_list();
    v_maiores = mp::new_list();
    v_i = mp::Value(1.0);
    L_for9: ;
    t1 = mp::bi_len(v_array);
    if (mp::ge(v_i, t1)) goto L_endfor11;
    v_x = mp::get_index(v_array, v_i);
    if (mp::gt(v_x, v_pivot)) goto L_else12;
    mp::append(v_menores, v_x);
    goto L_endif13;
    L_else12: ;
    mp::append(v_maiores, v_x);
    L_endif13: ;
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for9;
    L_endfor11: ;
    t2 = mp::call_method(self, "quicksort_rec", {v_menores});
    t3 = mp::new_list();
    mp::append(t3, v_pivot);
    t4 = mp::add(t2, t3);
    t5 = mp::call_method(self, "quicksort_rec", {v_maiores});
    t6 = mp::add(t4, t5);
    return t6;
}

mp::Value fn_InterfaceOrdenacao_D___attrs(mp::Value self) {
    // InterfaceOrdenacao.__attrs
    (void)self;
    return mp::Value();
}

mp::Value fn_InterfaceOrdenacao_D_iniciar(mp::Value self) {
    // InterfaceOrdenacao.iniciar
    mp::Value t0, t1, t2, t3, t4, v_algoritmo, v_array, v_entrada;
    mp::Value v_tok, v_valido, v_vetor_ordenado;
    (void)self;
    mp::print({mp::Value(std::string("==== Ordena\303\247\303\243o com Quicksort ====", 35))});
    mp::print({mp::Value(std::string("Insira os elementos do vetor separados por espa\303\247o:", 51))});
    t0 = mp::input();
    v_entrada = mp::bi_trim(t0);
    v_valido = mp::Value(true);
    t1 = mp::bi_split(v_entrada, mp::Value(std::string(" ", 1)));
    t2 = mp::size_of(t1);
    t3 = mp::Value(0.0);
    L_foreach14: ;
    if (mp::ge(t3, t2)) goto L_endforeach16;
    v_tok = mp::get_index(t1, t3);
    if (mp::eq(v_tok, mp::Value(std::string("", 0)))) goto L_endif17;
    t4 = fn_eh_inteiro(v_tok);
    if ((t4).truthy()) goto L_endif17;
    v_valido = mp::Value(false);
    L_endif17: ;
    t3 = mp::add(t3, mp::Value(1.0));
    goto L_foreach14;
    L_endforeach16: ;
    if ((v_valido).truthy()) goto L_endif18;
    mp::print({mp::Value(std::string("Por favor, insira apenas n\303\272meros separados por espa\303\247o.", 56))});
    mp::call_method(self, "iniciar", {});
    return mp::Value();
    L_endif18: ;
    v_array = mp::bi_parse_ints(v_entrada);
    mp::print({mp::Value(std::string("Vetor original:", 15)), v_array});
    v_algoritmo = mp::new_obj("Quicksort");
    fn_Quicksort_D___attrs(v_algoritmo);
    fn_Quicksort_D_init(v_algoritmo, v_array);
    v_vetor_ordenado = mp::call_method(v_algoritmo, "ordenar", {});
    mp::print({mp::Value(std::string("Vetor ordenado:", 15)), v_vetor_ordenado});
    return mp::Value();
}

mp::Value fn_main() {
    // main
    v_interface_ordenacao = mp::new_obj("InterfaceOrdenacao");
    fn_InterfaceOrdenacao_D___attrs(v_interface_ordenacao);
    mp::call_method(v_interface_ordenacao, "iniciar", {});
    return mp::Value();
}

static void register_classes() {
    mp::register_class("Quicksort", "", {
        {"init", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Quicksort.init", a, 1); return fn_Quicksort_D_init(self, a[0]); }},
        {"ordenar", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Quicksort.ordenar", a, 0); return fn_Quicksort_D_ordenar(self); }},
        {"quicksort_rec", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Quicksort.quicksort_rec", a, 1); return fn_Quicksort_D_quicksort_rec(self, a[0]); }},
    });
    mp::register_class("InterfaceOrdenacao", "", {
        {"iniciar", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("InterfaceOrdenacao.iniciar", a, 0); return fn_InterfaceOrdenacao_D_iniciar(self); }},
    });
}

int main(int argc, char** argv) {
    return mp::run_program(argc, argv, []() {
        register_classes();
    }, []() { fn_main(); });
}
