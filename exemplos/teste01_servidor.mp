# Teste 1 (servidor, computador_2): calculadora aritmética.
# Recebe a operação e os dois operandos do cliente, calcula e devolve o resultado.
# Executar com:  ./teste01_servidor --node computador_2
c_channel calculadora computador_1 computador_2;

seq {
    print("=== Calculadora (servidor) ===");
    var atendendo = true;
    while (atendendo) {
        var pedido = calculadora.receive();
        var operacao = pedido[0];

        if (operacao == "sair") {
            print("Cliente encerrou a conversa.");
            atendendo = false;
        } else {
            var valor1 = pedido[1];
            var valor2 = pedido[2];
            print("Pedido recebido:", valor1, operacao, valor2);

            if (operacao == "+") {
                calculadora.send(valor1 + valor2);
            } else if (operacao == "-") {
                calculadora.send(valor1 - valor2);
            } else if (operacao == "*") {
                calculadora.send(valor1 * valor2);
            } else if (operacao == "/") {
                if (valor2 == 0) {
                    calculadora.send("erro: divisão por zero");
                } else {
                    calculadora.send(valor1 / valor2);
                }
            } else {
                calculadora.send("erro: operação inválida");
            }
        }
    }
}
