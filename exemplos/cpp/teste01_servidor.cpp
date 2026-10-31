// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----
static mp::Value v_calculadora;

// ---- protótipos ----
mp::Value fn_main();

mp::Value fn_main() {
    // main
    mp::Value t0, t1, t2, t3, v_atendendo, v_operacao, v_pedido, v_valor1;
    mp::Value v_valor2;
    mp::print({mp::Value(std::string("=== Calculadora (servidor) ===", 30))});
    v_atendendo = mp::Value(true);
    L_while1: ;
    if (!(v_atendendo).truthy()) goto L_endwhile2;
    v_pedido = mp::chan_receive(v_calculadora);
    v_operacao = mp::get_index(v_pedido, mp::Value(0.0));
    if (mp::ne(v_operacao, mp::Value(std::string("sair", 4)))) goto L_else3;
    mp::print({mp::Value(std::string("Cliente encerrou a conversa.", 28))});
    v_atendendo = mp::Value(false);
    goto L_endif4;
    L_else3: ;
    v_valor1 = mp::get_index(v_pedido, mp::Value(1.0));
    v_valor2 = mp::get_index(v_pedido, mp::Value(2.0));
    mp::print({mp::Value(std::string("Pedido recebido:", 16)), v_valor1, v_operacao, v_valor2});
    if (mp::ne(v_operacao, mp::Value(std::string("+", 1)))) goto L_else5;
    t0 = mp::add(v_valor1, v_valor2);
    mp::chan_send(v_calculadora, {t0});
    goto L_endif6;
    L_else5: ;
    if (mp::ne(v_operacao, mp::Value(std::string("-", 1)))) goto L_else7;
    t1 = mp::sub(v_valor1, v_valor2);
    mp::chan_send(v_calculadora, {t1});
    goto L_endif8;
    L_else7: ;
    if (mp::ne(v_operacao, mp::Value(std::string("*", 1)))) goto L_else9;
    t2 = mp::mul(v_valor1, v_valor2);
    mp::chan_send(v_calculadora, {t2});
    goto L_endif10;
    L_else9: ;
    if (mp::ne(v_operacao, mp::Value(std::string("/", 1)))) goto L_else11;
    if (mp::ne(v_valor2, mp::Value(0.0))) goto L_else13;
    mp::chan_send(v_calculadora, {mp::Value(std::string("erro: divis\303\243o por zero", 23))});
    goto L_endif14;
    L_else13: ;
    t3 = mp::div(v_valor1, v_valor2);
    mp::chan_send(v_calculadora, {t3});
    L_endif14: ;
    goto L_endif12;
    L_else11: ;
    mp::chan_send(v_calculadora, {mp::Value(std::string("erro: opera\303\247\303\243o inv\303\241lida", 26))});
    L_endif12: ;
    L_endif10: ;
    L_endif8: ;
    L_endif6: ;
    L_endif4: ;
    goto L_while1;
    L_endwhile2: ;
    return mp::Value();
}

static void register_classes() {
}

int main(int argc, char** argv) {
    return mp::run_program(argc, argv, []() {
        register_classes();
        v_calculadora = mp::make_channel("calculadora", "computador_1", "computador_2");
    }, []() { fn_main(); });
}
