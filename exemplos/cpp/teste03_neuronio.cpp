// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----
static mp::Value v_neuronio;

// ---- protótipos ----
mp::Value fn_Neuronio_D___attrs(mp::Value self);
mp::Value fn_Neuronio_D_init(mp::Value self, mp::Value v_entrada, mp::Value v_desejado);
mp::Value fn_Neuronio_D_ativacao(mp::Value self, mp::Value v_soma);
mp::Value fn_Neuronio_D_treinar(mp::Value self);
mp::Value fn_main();

mp::Value fn_Neuronio_D___attrs(mp::Value self) {
    // Neuronio.__attrs
    (void)self;
    mp::set_member(self, "input_val", mp::Value(0.0));
    mp::set_member(self, "output_desejado", mp::Value(0.0));
    mp::set_member(self, "peso", mp::Value(0.5));
    mp::set_member(self, "bias", mp::Value(1.0));
    mp::set_member(self, "peso_bias", mp::Value(0.5));
    mp::set_member(self, "taxa_aprendizado", mp::Value(0.01));
    mp::set_member(self, "erro", mp::Value(1000000.0));
    mp::set_member(self, "iteracao", mp::Value(0.0));
    return mp::Value();
}

mp::Value fn_Neuronio_D_init(mp::Value self, mp::Value v_entrada, mp::Value v_desejado) {
    // Neuronio.init
    (void)self;
    mp::set_member(self, "input_val", v_entrada);
    mp::set_member(self, "output_desejado", v_desejado);
    return mp::Value();
}

mp::Value fn_Neuronio_D_ativacao(mp::Value self, mp::Value v_soma) {
    // Neuronio.ativacao
    (void)self;
    if (mp::lt(v_soma, mp::Value(0.0))) goto L_endif1;
    return mp::Value(1.0);
    L_endif1: ;
    return mp::Value(0.0);
}

mp::Value fn_Neuronio_D_treinar(mp::Value self) {
    // Neuronio.treinar
    mp::Value t0, t1, t10, t11, t12, t13, t14, t15;
    mp::Value t16, t17, t18, t19, t2, t20, t21, t22;
    mp::Value t23, t24, t25, t26, t27, t28, t29, t3;
    mp::Value t30, t31, t32, t33, t34, t4, t5, t6;
    mp::Value t7, t8, t9, v_saida, v_soma;
    (void)self;
    t0 = mp::get_member(self, "input_val");
    t1 = mp::get_member(self, "output_desejado");
    mp::print({mp::Value(std::string("Entrada:", 8)), t0, mp::Value(std::string("| Sa\303\255da desejada:", 18)), t1});
    L_while2: ;
    t2 = mp::get_member(self, "erro");
    if (mp::eq(t2, mp::Value(0.0))) goto L_endwhile3;
    t3 = mp::get_member(self, "iteracao");
    t4 = mp::add(t3, mp::Value(1.0));
    mp::set_member(self, "iteracao", t4);
    t5 = mp::get_member(self, "iteracao");
    mp::print({mp::Value(std::string("\n#### Itera\303\247\303\243o:", 17)), t5});
    t6 = mp::get_member(self, "peso");
    t7 = mp::bi_fmt(t6, mp::Value(4.0));
    mp::print({mp::Value(std::string("Peso:", 5)), t7});
    t8 = mp::get_member(self, "input_val");
    t9 = mp::get_member(self, "peso");
    t10 = mp::mul(t8, t9);
    t11 = mp::get_member(self, "bias");
    t12 = mp::get_member(self, "peso_bias");
    t13 = mp::mul(t11, t12);
    v_soma = mp::add(t10, t13);
    v_saida = mp::call_method(self, "ativacao", {v_soma});
    mp::print({mp::Value(std::string("Sa\303\255da:", 7)), v_saida});
    t14 = mp::get_member(self, "output_desejado");
    t15 = mp::sub(t14, v_saida);
    mp::set_member(self, "erro", t15);
    t16 = mp::get_member(self, "erro");
    mp::print({mp::Value(std::string("Erro:", 5)), t16});
    t17 = mp::get_member(self, "erro");
    if (mp::eq(t17, mp::Value(0.0))) goto L_endif4;
    t18 = mp::get_member(self, "peso");
    t19 = mp::get_member(self, "taxa_aprendizado");
    t20 = mp::get_member(self, "input_val");
    t21 = mp::mul(t19, t20);
    t22 = mp::get_member(self, "erro");
    t23 = mp::mul(t21, t22);
    t24 = mp::add(t18, t23);
    mp::set_member(self, "peso", t24);
    t25 = mp::get_member(self, "peso_bias");
    t26 = mp::bi_fmt(t25, mp::Value(4.0));
    mp::print({mp::Value(std::string("Peso do bias:", 13)), t26});
    t27 = mp::get_member(self, "peso_bias");
    t28 = mp::get_member(self, "taxa_aprendizado");
    t29 = mp::get_member(self, "bias");
    t30 = mp::mul(t28, t29);
    t31 = mp::get_member(self, "erro");
    t32 = mp::mul(t30, t31);
    t33 = mp::add(t27, t32);
    mp::set_member(self, "peso_bias", t33);
    L_endif4: ;
    goto L_while2;
    L_endwhile3: ;
    mp::print({mp::Value(std::string("\n\342\234\205 Parab\303\251ns! O neur\303\264nio aprendeu.", 37))});
    t34 = mp::get_member(self, "output_desejado");
    mp::print({mp::Value(std::string("Valor desejado:", 15)), t34});
    return mp::Value();
}

mp::Value fn_main() {
    // main
    v_neuronio = mp::new_obj("Neuronio");
    fn_Neuronio_D___attrs(v_neuronio);
    fn_Neuronio_D_init(v_neuronio, mp::Value(1.0), mp::Value(0.0));
    mp::call_method(v_neuronio, "treinar", {});
    return mp::Value();
}

static void register_all() {
    mp::register_class("Neuronio", "", {
        {"init", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Neuronio.init", a, 2); return fn_Neuronio_D_init(self, a[0], a[1]); }},
        {"ativacao", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Neuronio.ativacao", a, 1); return fn_Neuronio_D_ativacao(self, a[0]); }},
        {"treinar", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Neuronio.treinar", a, 0); return fn_Neuronio_D_treinar(self); }},
    });
}

int main(int argc, char** argv) {
    return mp::run_program(argc, argv, []() {
        register_all();
    }, []() { fn_main(); });
}
