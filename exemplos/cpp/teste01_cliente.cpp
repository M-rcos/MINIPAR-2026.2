// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----
static mp::Value v_calculadora;

// ---- protótipos ----
mp::Value fn_main();

mp::Value fn_main() {
    // main
    mp::Value t0, t1, t2, v_operacao, v_resposta, v_valor1, v_valor2;
    mp::print({mp::Value(std::string("=== Calculadora (cliente) ===", 29))});
    mp::print({mp::Value(std::string("Opera\303\247\303\265es dispon\303\255veis: +, -, *, /", 36))});
    v_operacao = mp::input(mp::Value(std::string("Opera\303\247\303\243o: ", 12)));
    t0 = mp::input(mp::Value(std::string("Operando 1: ", 12)));
    v_valor1 = mp::bi_to_number(t0);
    t1 = mp::input(mp::Value(std::string("Operando 2: ", 12)));
    v_valor2 = mp::bi_to_number(t1);
    mp::chan_send(v_calculadora, {v_operacao, v_valor1, v_valor2});
    v_resposta = mp::chan_receive(v_calculadora);
    t2 = mp::get_index(v_resposta, mp::Value(0.0));
    mp::print({mp::Value(std::string("Resultado:", 10)), t2});
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
