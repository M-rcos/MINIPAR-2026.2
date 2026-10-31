// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----
static mp::Value v_calculadora;

// ---- protótipos ----
mp::Value fn_main();

mp::Value fn_main() {
    // main
    mp::Value t0, t1, t2, t3, t4, t5, v_continuar, v_operacao;
    mp::Value v_resposta, v_valor1, v_valor2;
    mp::print({mp::Value(std::string("=== Calculadora (cliente) ===", 29))});
    v_continuar = mp::Value(true);
    L_while1: ;
    if (!(v_continuar).truthy()) goto L_endwhile2;
    mp::print({mp::Value(std::string("Opera\303\247\303\265es dispon\303\255veis: +, -, *, /  (digite 'sair' para terminar)", 67))});
    t0 = mp::input(mp::Value(std::string("Opera\303\247\303\243o: ", 12)));
    v_operacao = mp::bi_trim(t0);
    if (mp::ne(v_operacao, mp::Value(std::string("sair", 4)))) goto L_else3;
    mp::chan_send(v_calculadora, {mp::Value(std::string("sair", 4)), mp::Value(0.0), mp::Value(0.0)});
    v_continuar = mp::Value(false);
    goto L_endif4;
    L_else3: ;
    t1 = mp::input(mp::Value(std::string("Operando 1: ", 12)));
    t2 = mp::bi_trim(t1);
    v_valor1 = mp::bi_to_number(t2);
    t3 = mp::input(mp::Value(std::string("Operando 2: ", 12)));
    t4 = mp::bi_trim(t3);
    v_valor2 = mp::bi_to_number(t4);
    mp::chan_send(v_calculadora, {v_operacao, v_valor1, v_valor2});
    v_resposta = mp::chan_receive(v_calculadora);
    t5 = mp::get_index(v_resposta, mp::Value(0.0));
    mp::print({mp::Value(std::string("Resultado:", 10)), t5});
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
