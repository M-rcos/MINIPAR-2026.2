channel calculadora computador_1 computador_2

func main():
    print "=== Calculadora (servidor) ==="
    atendendo = true
  while1:
    ifFalse atendendo goto endwhile2
    pedido = receive calculadora
    operacao = pedido[0]
    if operacao != "sair" goto else3
    print "Cliente encerrou a conversa."
    atendendo = false
    goto endif4
  else3:
    valor1 = pedido[1]
    valor2 = pedido[2]
    print "Pedido recebido:", valor1, operacao, valor2
    if operacao != "+" goto else5
    t0 = valor1 + valor2
    send calculadora, t0
    goto endif6
  else5:
    if operacao != "-" goto else7
    t1 = valor1 - valor2
    send calculadora, t1
    goto endif8
  else7:
    if operacao != "*" goto else9
    t2 = valor1 * valor2
    send calculadora, t2
    goto endif10
  else9:
    if operacao != "/" goto else11
    if valor2 != 0 goto else13
    send calculadora, "erro: divisão por zero"
    goto endif14
  else13:
    t3 = valor1 / valor2
    send calculadora, t3
  endif14:
    goto endif12
  else11:
    send calculadora, "erro: operação inválida"
  endif12:
  endif10:
  endif8:
  endif6:
  endif4:
    goto while1
  endwhile2:
    return
endfunc
