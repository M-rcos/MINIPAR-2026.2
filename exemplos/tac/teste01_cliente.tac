channel calculadora computador_1 computador_2

func main():
    print "=== Calculadora (cliente) ==="
    continuar = true
  while1:
    ifFalse continuar goto endwhile2
    print "Operações disponíveis: +, -, *, /  (digite 'sair' para terminar)"
    t0 = input "Operação: "
    param t0
    operacao = call trim, 1
    if operacao != "sair" goto else3
    send calculadora, "sair", 0, 0
    continuar = false
    goto endif4
  else3:
    t1 = input "Operando 1: "
    param t1
    t2 = call trim, 1
    param t2
    valor1 = call to_number, 1
    t3 = input "Operando 2: "
    param t3
    t4 = call trim, 1
    param t4
    valor2 = call to_number, 1
    send calculadora, operacao, valor1, valor2
    resposta = receive calculadora
    t5 = resposta[0]
    print "Resultado:", t5
  endif4:
    goto while1
  endwhile2:
    return
endfunc
