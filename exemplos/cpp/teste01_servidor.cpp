// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----
static mp::Value v_calculadora;

// ---- protótipos ----
mp::Value fn_main();

mp::Value fn_main() {
    // main
    mp::Value v_operacao, v_pedido, v_resultado, v_valor1, v_valor2;
    v_pedido = mp::chan_receive(v_calculadora);
    v_operacao = mp::get_index(v_pedido, mp::Value(0.0));
    v_valor1 = mp::get_index(v_pedido, mp::Value(1.0));
    v_valor2 = mp::get_index(v_pedido, mp::Value(2.0));
    v_resultado = mp::Value(0.0);
    if (mp::ne(v_operacao, mp::Value(std::string("+", 1)))) goto L_else1;
    v_resultado = mp::add(v_valor1, v_valor2);
    goto L_endif2;
    L_else1: ;
    if (mp::ne(v_operacao, mp::Value(std::string("-", 1)))) goto L_else3;
    v_resultado = mp::sub(v_valor1, v_valor2);
    goto L_endif4;
    L_else3: ;
    if (mp::ne(v_operacao, mp::Value(std::string("*", 1)))) goto L_else5;
    v_resultado = mp::mul(v_valor1, v_valor2);
    goto L_endif6;
    L_else5: ;
    if (mp::ne(v_operacao, mp::Value(std::string("/", 1)))) goto L_endif7;
    if (mp::ne(v_valor2, mp::Value(0.0))) goto L_else8;
    v_resultado = mp::Value(0.0);
    goto L_endif9;
    L_else8: ;
    v_resultado = mp::div(v_valor1, v_valor2);
    L_endif9: ;
    L_endif7: ;
    L_endif6: ;
    L_endif4: ;
    L_endif2: ;
    mp::chan_send(v_calculadora, {v_resultado});
    return mp::Value();
}

static void register_classes() {
}

int main() {
    return mp::run_program([]() {
        register_classes();
        v_calculadora = mp::make_channel("calculadora", "computador_1", "computador_2");
    }, []() { fn_main(); });
}
