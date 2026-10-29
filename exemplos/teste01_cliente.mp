# Teste 1 (cliente, computador_1): lê a operação, envia ao servidor e mostra o resultado.
c_channel calculadora computador_1 computador_2;

seq {
    print("=== Calculadora (cliente) ===");
    print("Operações disponíveis: +, -, *, /");
    var operacao = input("Operação: ");
    var valor1 = to_number(input("Operando 1: "));
    var valor2 = to_number(input("Operando 2: "));

    calculadora.send(operacao, valor1, valor2);

    var resposta = calculadora.receive();
    print("Resultado:", resposta[0]);
}
