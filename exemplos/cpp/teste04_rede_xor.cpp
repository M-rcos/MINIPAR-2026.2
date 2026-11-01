// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----
static mp::Value v_entradas;
static mp::Value v_rede;
static mp::Value v_saidas_desejadas;

// ---- protótipos ----
mp::Value fn_sigmoid(mp::Value v_x);
mp::Value fn_sigmoid_derivative(mp::Value v_x);
mp::Value fn_Neuronio_D___attrs(mp::Value self);
mp::Value fn_Neuronio_D_init(mp::Value self, mp::Value v_num_inputs);
mp::Value fn_Neuronio_D_feedforward(mp::Value self, mp::Value v_entradas_1);
mp::Value fn_Neuronio_D_calcular_derivada(mp::Value self);
mp::Value fn_RedeNeural_D___attrs(mp::Value self);
mp::Value fn_RedeNeural_D_init(mp::Value self);
mp::Value fn_RedeNeural_D_feedforward(mp::Value self, mp::Value v_entradas_1);
mp::Value fn_RedeNeural_D_backpropagation(mp::Value self, mp::Value v_entradas_1, mp::Value v_saida_desejada, mp::Value v_saidas_ocultas, mp::Value v_saida_final);
mp::Value fn_RedeNeural_D_treinar(mp::Value self, mp::Value v_entradas_1, mp::Value v_saidas_desejadas_1, mp::Value v_epocas);
mp::Value fn_RedeNeural_D_testar(mp::Value self, mp::Value v_entradas_1);
mp::Value fn_main();

mp::Value fn_sigmoid(mp::Value v_x) {
    // sigmoid
    mp::Value t0, t1, t2, t3;
    t0 = mp::neg(v_x);
    t1 = mp::bi_exp(t0);
    t2 = mp::add(mp::Value(1.0), t1);
    t3 = mp::div(mp::Value(1.0), t2);
    return t3;
}

mp::Value fn_sigmoid_derivative(mp::Value v_x) {
    // sigmoid_derivative
    mp::Value t0, t1;
    t0 = mp::sub(mp::Value(1.0), v_x);
    t1 = mp::mul(v_x, t0);
    return t1;
}

mp::Value fn_Neuronio_D___attrs(mp::Value self) {
    // Neuronio.__attrs
    mp::Value t0;
    (void)self;
    t0 = mp::new_list();
    mp::set_member(self, "pesos", t0);
    mp::set_member(self, "bias", mp::Value(0.0));
    mp::set_member(self, "saida", mp::Value(0.0));
    return mp::Value();
}

mp::Value fn_Neuronio_D_init(mp::Value self, mp::Value v_num_inputs) {
    // Neuronio.init
    mp::Value t0, t1, t2, v_i;
    (void)self;
    v_i = mp::Value(0.0);
    L_for1: ;
    if (mp::ge(v_i, v_num_inputs)) goto L_endfor3;
    t0 = mp::get_member(self, "pesos");
    t1 = mp::bi_random();
    mp::append(t0, t1);
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for1;
    L_endfor3: ;
    t2 = mp::bi_random();
    mp::set_member(self, "bias", t2);
    return mp::Value();
}

mp::Value fn_Neuronio_D_feedforward(mp::Value self, mp::Value v_entradas_1) {
    // Neuronio.feedforward
    mp::Value t0, t1, t2, t3, t4, t5, t6, t7;
    mp::Value v_i, v_soma;
    (void)self;
    v_soma = mp::Value(0.0);
    v_i = mp::Value(0.0);
    L_for4: ;
    t0 = mp::bi_len(v_entradas_1);
    if (mp::ge(v_i, t0)) goto L_endfor6;
    t1 = mp::get_index(v_entradas_1, v_i);
    t2 = mp::get_member(self, "pesos");
    t3 = mp::get_index(t2, v_i);
    t4 = mp::mul(t1, t3);
    v_soma = mp::add(v_soma, t4);
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for4;
    L_endfor6: ;
    t5 = mp::get_member(self, "bias");
    v_soma = mp::add(v_soma, t5);
    t6 = fn_sigmoid(v_soma);
    mp::set_member(self, "saida", t6);
    t7 = mp::get_member(self, "saida");
    return t7;
}

mp::Value fn_Neuronio_D_calcular_derivada(mp::Value self) {
    // Neuronio.calcular_derivada
    mp::Value t0, t1;
    (void)self;
    t0 = mp::get_member(self, "saida");
    t1 = fn_sigmoid_derivative(t0);
    return t1;
}

mp::Value fn_RedeNeural_D___attrs(mp::Value self) {
    // RedeNeural.__attrs
    mp::Value t0;
    (void)self;
    mp::set_member(self, "taxa_aprendizado", mp::Value(0.2));
    t0 = mp::new_list();
    mp::set_member(self, "camada_oculta", t0);
    mp::set_member(self, "neuronio_saida", mp::Value());
    return mp::Value();
}

mp::Value fn_RedeNeural_D_init(mp::Value self) {
    // RedeNeural.init
    mp::Value t0, t1, t2, v_i;
    (void)self;
    v_i = mp::Value(0.0);
    L_for7: ;
    if (mp::ge(v_i, mp::Value(3.0))) goto L_endfor9;
    t0 = mp::get_member(self, "camada_oculta");
    t1 = mp::new_obj("Neuronio");
    fn_Neuronio_D___attrs(t1);
    fn_Neuronio_D_init(t1, mp::Value(2.0));
    mp::append(t0, t1);
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for7;
    L_endfor9: ;
    t2 = mp::new_obj("Neuronio");
    fn_Neuronio_D___attrs(t2);
    fn_Neuronio_D_init(t2, mp::Value(3.0));
    mp::set_member(self, "neuronio_saida", t2);
    return mp::Value();
}

mp::Value fn_RedeNeural_D_feedforward(mp::Value self, mp::Value v_entradas_1) {
    // RedeNeural.feedforward
    mp::Value t0, t1, t2, t3, t4, t5, v_n, v_saida_final;
    mp::Value v_saidas_ocultas;
    (void)self;
    v_saidas_ocultas = mp::new_list();
    t0 = mp::get_member(self, "camada_oculta");
    t1 = mp::size_of(t0);
    t2 = mp::Value(0.0);
    L_foreach10: ;
    if (mp::ge(t2, t1)) goto L_endforeach12;
    v_n = mp::get_index(t0, t2);
    t3 = mp::call_method(v_n, "feedforward", {v_entradas_1});
    mp::append(v_saidas_ocultas, t3);
    t2 = mp::add(t2, mp::Value(1.0));
    goto L_foreach10;
    L_endforeach12: ;
    t4 = mp::get_member(self, "neuronio_saida");
    v_saida_final = mp::call_method(t4, "feedforward", {v_saidas_ocultas});
    t5 = mp::new_list();
    mp::append(t5, v_saidas_ocultas);
    mp::append(t5, v_saida_final);
    return t5;
}

mp::Value fn_RedeNeural_D_backpropagation(mp::Value self, mp::Value v_entradas_1, mp::Value v_saida_desejada, mp::Value v_saidas_ocultas, mp::Value v_saida_final) {
    // RedeNeural.backpropagation
    mp::Value t0, t1, t10, t11, t12, t13, t14, t15;
    mp::Value t16, t17, t18, t19, t2, t20, t21, t22;
    mp::Value t23, t24, t25, t26, t27, t28, t29, t3;
    mp::Value t30, t31, t32, t33, t34, t35, t36, t37;
    mp::Value t38, t4, t5, t6, t7, t8, t9, v_delta_oculto;
    mp::Value v_delta_saida, v_erro, v_i, v_i_1, v_j, v_neuronio;
    (void)self;
    v_erro = mp::sub(v_saida_desejada, v_saida_final);
    t0 = mp::get_member(self, "neuronio_saida");
    t1 = mp::call_method(t0, "calcular_derivada", {});
    v_delta_saida = mp::mul(v_erro, t1);
    v_i = mp::Value(0.0);
    L_for13: ;
    t2 = mp::get_member(self, "neuronio_saida");
    t3 = mp::get_member(t2, "pesos");
    t4 = mp::bi_len(t3);
    if (mp::ge(v_i, t4)) goto L_endfor15;
    t5 = mp::get_member(self, "neuronio_saida");
    t6 = mp::get_member(t5, "pesos");
    t7 = mp::get_index(t6, v_i);
    t8 = mp::get_index(v_saidas_ocultas, v_i);
    t9 = mp::mul(t8, v_delta_saida);
    t10 = mp::get_member(self, "taxa_aprendizado");
    t11 = mp::mul(t9, t10);
    t12 = mp::add(t7, t11);
    mp::set_index(t6, v_i, t12);
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for13;
    L_endfor15: ;
    t13 = mp::get_member(self, "neuronio_saida");
    t14 = mp::get_member(t13, "bias");
    t15 = mp::get_member(self, "taxa_aprendizado");
    t16 = mp::mul(v_delta_saida, t15);
    t17 = mp::add(t14, t16);
    mp::set_member(t13, "bias", t17);
    v_i_1 = mp::Value(0.0);
    L_for16: ;
    t18 = mp::get_member(self, "camada_oculta");
    t19 = mp::bi_len(t18);
    if (mp::ge(v_i_1, t19)) goto L_endfor18;
    t20 = mp::get_member(self, "camada_oculta");
    v_neuronio = mp::get_index(t20, v_i_1);
    t21 = mp::get_member(self, "neuronio_saida");
    t22 = mp::get_member(t21, "pesos");
    t23 = mp::get_index(t22, v_i_1);
    t24 = mp::mul(v_delta_saida, t23);
    t25 = mp::call_method(v_neuronio, "calcular_derivada", {});
    v_delta_oculto = mp::mul(t24, t25);
    v_j = mp::Value(0.0);
    L_for19: ;
    t26 = mp::get_member(v_neuronio, "pesos");
    t27 = mp::bi_len(t26);
    if (mp::ge(v_j, t27)) goto L_endfor21;
    t28 = mp::get_member(v_neuronio, "pesos");
    t29 = mp::get_index(t28, v_j);
    t30 = mp::get_index(v_entradas_1, v_j);
    t31 = mp::mul(t30, v_delta_oculto);
    t32 = mp::get_member(self, "taxa_aprendizado");
    t33 = mp::mul(t31, t32);
    t34 = mp::add(t29, t33);
    mp::set_index(t28, v_j, t34);
    v_j = mp::add(v_j, mp::Value(1.0));
    goto L_for19;
    L_endfor21: ;
    t35 = mp::get_member(v_neuronio, "bias");
    t36 = mp::get_member(self, "taxa_aprendizado");
    t37 = mp::mul(v_delta_oculto, t36);
    t38 = mp::add(t35, t37);
    mp::set_member(v_neuronio, "bias", t38);
    v_i_1 = mp::add(v_i_1, mp::Value(1.0));
    goto L_for16;
    L_endfor18: ;
    return mp::Value();
}

mp::Value fn_RedeNeural_D_treinar(mp::Value self, mp::Value v_entradas_1, mp::Value v_saidas_desejadas_1, mp::Value v_epocas) {
    // RedeNeural.treinar
    mp::Value t0, t1, t2, t3, t4, t5, v_e, v_k;
    mp::Value v_r;
    (void)self;
    v_e = mp::Value(0.0);
    L_for22: ;
    if (mp::ge(v_e, v_epocas)) goto L_endfor24;
    v_k = mp::Value(0.0);
    L_for25: ;
    t0 = mp::bi_len(v_entradas_1);
    if (mp::ge(v_k, t0)) goto L_endfor27;
    t1 = mp::get_index(v_entradas_1, v_k);
    v_r = mp::call_method(self, "feedforward", {t1});
    t2 = mp::get_index(v_entradas_1, v_k);
    t3 = mp::get_index(v_saidas_desejadas_1, v_k);
    t4 = mp::get_index(v_r, mp::Value(0.0));
    t5 = mp::get_index(v_r, mp::Value(1.0));
    mp::call_method(self, "backpropagation", {t2, t3, t4, t5});
    v_k = mp::add(v_k, mp::Value(1.0));
    goto L_for25;
    L_endfor27: ;
    v_e = mp::add(v_e, mp::Value(1.0));
    goto L_for22;
    L_endfor24: ;
    return mp::Value();
}

mp::Value fn_RedeNeural_D_testar(mp::Value self, mp::Value v_entradas_1) {
    // RedeNeural.testar
    mp::Value t0, t1, t2, t3, t4, t5, t6, t7;
    mp::Value t8, v_k, v_r;
    (void)self;
    v_k = mp::Value(0.0);
    L_for28: ;
    t0 = mp::bi_len(v_entradas_1);
    if (mp::ge(v_k, t0)) goto L_endfor30;
    t1 = mp::get_index(v_entradas_1, v_k);
    v_r = mp::call_method(self, "feedforward", {t1});
    t2 = mp::get_index(v_entradas_1, v_k);
    t3 = mp::bi_to_string(t2);
    t4 = mp::add(mp::Value(std::string("Input: ", 7)), t3);
    t5 = mp::add(t4, mp::Value(std::string(", Predicted Output: ", 20)));
    t6 = mp::get_index(v_r, mp::Value(1.0));
    t7 = mp::bi_fmt(t6, mp::Value(4.0));
    t8 = mp::add(t5, t7);
    mp::print({t8});
    v_k = mp::add(v_k, mp::Value(1.0));
    goto L_for28;
    L_endfor30: ;
    return mp::Value();
}

mp::Value fn_main() {
    // main
    mp::Value t0, t1, t2, t3;
    v_entradas = mp::new_list();
    t0 = mp::new_list();
    mp::append(t0, mp::Value(0.0));
    mp::append(t0, mp::Value(0.0));
    mp::append(v_entradas, t0);
    t1 = mp::new_list();
    mp::append(t1, mp::Value(0.0));
    mp::append(t1, mp::Value(1.0));
    mp::append(v_entradas, t1);
    t2 = mp::new_list();
    mp::append(t2, mp::Value(1.0));
    mp::append(t2, mp::Value(0.0));
    mp::append(v_entradas, t2);
    t3 = mp::new_list();
    mp::append(t3, mp::Value(1.0));
    mp::append(t3, mp::Value(1.0));
    mp::append(v_entradas, t3);
    v_saidas_desejadas = mp::new_list();
    mp::append(v_saidas_desejadas, mp::Value(0.0));
    mp::append(v_saidas_desejadas, mp::Value(1.0));
    mp::append(v_saidas_desejadas, mp::Value(1.0));
    mp::append(v_saidas_desejadas, mp::Value(0.0));
    v_rede = mp::new_obj("RedeNeural");
    fn_RedeNeural_D___attrs(v_rede);
    fn_RedeNeural_D_init(v_rede);
    mp::call_method(v_rede, "treinar", {v_entradas, v_saidas_desejadas, mp::Value(20000.0)});
    mp::call_method(v_rede, "testar", {v_entradas});
    return mp::Value();
}

static void register_all() {
    mp::register_class("Neuronio", "", {
        {"init", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Neuronio.init", a, 1); return fn_Neuronio_D_init(self, a[0]); }},
        {"feedforward", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Neuronio.feedforward", a, 1); return fn_Neuronio_D_feedforward(self, a[0]); }},
        {"calcular_derivada", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Neuronio.calcular_derivada", a, 0); return fn_Neuronio_D_calcular_derivada(self); }},
    });
    mp::register_class("RedeNeural", "", {
        {"init", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("RedeNeural.init", a, 0); return fn_RedeNeural_D_init(self); }},
        {"feedforward", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("RedeNeural.feedforward", a, 1); return fn_RedeNeural_D_feedforward(self, a[0]); }},
        {"backpropagation", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("RedeNeural.backpropagation", a, 4); return fn_RedeNeural_D_backpropagation(self, a[0], a[1], a[2], a[3]); }},
        {"treinar", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("RedeNeural.treinar", a, 3); return fn_RedeNeural_D_treinar(self, a[0], a[1], a[2]); }},
        {"testar", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("RedeNeural.testar", a, 1); return fn_RedeNeural_D_testar(self, a[0]); }},
    });
}

int main(int argc, char** argv) {
    return mp::run_program(argc, argv, []() {
        register_all();
    }, []() { fn_main(); });
}
