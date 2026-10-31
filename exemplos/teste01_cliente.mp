# Teste 1 (cliente, computador_1): lê a operação e os operandos, envia ao servidor
# pelo canal e mostra o resultado devolvido.
# Executar com:  ./teste01_cliente --node computador_1
c_channel calculadora computador_1 computador_2;

seq {
    print("=== Calculadora (cliente) ===");
    var continuar = true;
    while (continuar) {
        print("Operações disponíveis: +, -, *, /  (digite 'sair' para terminar)");
        var operacao = trim(input("Operação: "));

        if (operacao == "sair") {
            calculadora.send("sair", 0, 0);
            continuar = false;
        } else {
            var valor1 = to_number(trim(input("Operando 1: ")));
            var valor2 = to_number(trim(input("Operando 2: ")));
            calculadora.send(operacao, valor1, valor2);
            var resposta = calculadora.receive();
            print("Resultado:", resposta[0]);
        }
    }
}
