# Teste 1 (servidor, computador_2): recebe a operação, calcula e devolve o resultado.
c_channel calculadora computador_1 computador_2;

seq {
    var pedido = calculadora.receive();
    var operacao = pedido[0];
    var valor1 = pedido[1];
    var valor2 = pedido[2];
    var resultado = 0;

    if (operacao == "+") {
        resultado = valor1 + valor2;
    } else if (operacao == "-") {
        resultado = valor1 - valor2;
    } else if (operacao == "*") {
        resultado = valor1 * valor2;
    } else if (operacao == "/") {
        if (valor2 == 0) {
            resultado = 0;
        } else {
            resultado = valor1 / valor2;
        }
    }

    calculadora.send(resultado);
}
