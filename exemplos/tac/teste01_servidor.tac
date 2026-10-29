channel calculadora computador_1 computador_2

func main():
    pedido = receive calculadora
    operacao = pedido[0]
    valor1 = pedido[1]
    valor2 = pedido[2]
    resultado = 0
    if operacao != "+" goto else1
    resultado = valor1 + valor2
    goto endif2
  else1:
    if operacao != "-" goto else3
    resultado = valor1 - valor2
    goto endif4
  else3:
    if operacao != "*" goto else5
    resultado = valor1 * valor2
    goto endif6
  else5:
    if operacao != "/" goto endif7
    if valor2 != 0 goto else8
    resultado = 0
    goto endif9
  else8:
    resultado = valor1 / valor2
  endif9:
  endif7:
  endif6:
  endif4:
  endif2:
    send calculadora, resultado
    return
endfunc
