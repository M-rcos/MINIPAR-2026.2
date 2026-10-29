channel calculadora computador_1 computador_2

func main():
    print "=== Calculadora (cliente) ==="
    print "Operações disponíveis: +, -, *, /"
    operacao = input "Operação: "
    t0 = input "Operando 1: "
    param t0
    valor1 = call to_number, 1
    t1 = input "Operando 2: "
    param t1
    valor2 = call to_number, 1
    send calculadora, operacao, valor1, valor2
    resposta = receive calculadora
    t2 = resposta[0]
    print "Resultado:", t2
    return
endfunc
