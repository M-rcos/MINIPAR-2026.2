class Neuronio:
    field pesos
    field bias
    field saida
    method init
    method feedforward
    method calcular_derivada
endclass

class RedeNeural:
    field taxa_aprendizado
    field camada_oculta
    field neuronio_saida
    method init
    method feedforward
    method backpropagation
    method treinar
    method testar
endclass

global entradas
global saidas_desejadas
global rede

func sigmoid(x):
    t0 = -x
    param t0
    t1 = call exp, 1
    t2 = 1 + t1
    t3 = 1 / t2
    return t3
endfunc

func sigmoid_derivative(x):
    t0 = 1 - x
    t1 = x * t0
    return t1
endfunc

func Neuronio.__attrs(this):
    t0 = new_list
    this.pesos = t0
    this.bias = 0
    this.saida = 0
    return
endfunc

func Neuronio.init(this, num_inputs):
    i = 0
  for1:
    if i >= num_inputs goto endfor3
    t0 = this.pesos
    t1 = call random, 0
    append t0, t1
  forstep2:
    i = i + 1
    goto for1
  endfor3:
    t2 = call random, 0
    this.bias = t2
    return
endfunc

func Neuronio.feedforward(this, entradas_1):
    soma = 0
    i = 0
  for4:
    param entradas_1
    t0 = call len, 1
    if i >= t0 goto endfor6
    t1 = entradas_1[i]
    t2 = this.pesos
    t3 = t2[i]
    t4 = t1 * t3
    soma = soma + t4
  forstep5:
    i = i + 1
    goto for4
  endfor6:
    t5 = this.bias
    soma = soma + t5
    param soma
    t6 = call sigmoid, 1
    this.saida = t6
    t7 = this.saida
    return t7
endfunc

func Neuronio.calcular_derivada(this):
    t0 = this.saida
    param t0
    t1 = call sigmoid_derivative, 1
    return t1
endfunc

func RedeNeural.__attrs(this):
    this.taxa_aprendizado = 0.2
    t0 = new_list
    this.camada_oculta = t0
    this.neuronio_saida = null
    return
endfunc

func RedeNeural.init(this):
    i = 0
  for7:
    if i >= 3 goto endfor9
    t0 = this.camada_oculta
    t1 = new Neuronio
    param t1
    call Neuronio.__attrs, 1
    param t1
    param 2
    call Neuronio.init, 2
    append t0, t1
  forstep8:
    i = i + 1
    goto for7
  endfor9:
    t2 = new Neuronio
    param t2
    call Neuronio.__attrs, 1
    param t2
    param 3
    call Neuronio.init, 2
    this.neuronio_saida = t2
    return
endfunc

func RedeNeural.feedforward(this, entradas_1):
    saidas_ocultas = new_list
    t0 = this.camada_oculta
    t1 = size t0
    t2 = 0
  foreach10:
    if t2 >= t1 goto endforeach12
    n = t0[t2]
    param entradas_1
    t3 = callm n.feedforward, 1
    append saidas_ocultas, t3
  foreachstep11:
    t2 = t2 + 1
    goto foreach10
  endforeach12:
    t4 = this.neuronio_saida
    param saidas_ocultas
    saida_final = callm t4.feedforward, 1
    t5 = new_list
    append t5, saidas_ocultas
    append t5, saida_final
    return t5
endfunc

func RedeNeural.backpropagation(this, entradas_1, saida_desejada, saidas_ocultas, saida_final):
    erro = saida_desejada - saida_final
    t0 = this.neuronio_saida
    t1 = callm t0.calcular_derivada, 0
    delta_saida = erro * t1
    i = 0
  for13:
    t2 = this.neuronio_saida
    t3 = t2.pesos
    param t3
    t4 = call len, 1
    if i >= t4 goto endfor15
    t5 = this.neuronio_saida
    t6 = t5.pesos
    t7 = t6[i]
    t8 = saidas_ocultas[i]
    t9 = t8 * delta_saida
    t10 = this.taxa_aprendizado
    t11 = t9 * t10
    t12 = t7 + t11
    t6[i] = t12
  forstep14:
    i = i + 1
    goto for13
  endfor15:
    t13 = this.neuronio_saida
    t14 = t13.bias
    t15 = this.taxa_aprendizado
    t16 = delta_saida * t15
    t17 = t14 + t16
    t13.bias = t17
    i_1 = 0
  for16:
    t18 = this.camada_oculta
    param t18
    t19 = call len, 1
    if i_1 >= t19 goto endfor18
    t20 = this.camada_oculta
    neuronio = t20[i_1]
    t21 = this.neuronio_saida
    t22 = t21.pesos
    t23 = t22[i_1]
    t24 = delta_saida * t23
    t25 = callm neuronio.calcular_derivada, 0
    delta_oculto = t24 * t25
    j = 0
  for19:
    t26 = neuronio.pesos
    param t26
    t27 = call len, 1
    if j >= t27 goto endfor21
    t28 = neuronio.pesos
    t29 = t28[j]
    t30 = entradas_1[j]
    t31 = t30 * delta_oculto
    t32 = this.taxa_aprendizado
    t33 = t31 * t32
    t34 = t29 + t33
    t28[j] = t34
  forstep20:
    j = j + 1
    goto for19
  endfor21:
    t35 = neuronio.bias
    t36 = this.taxa_aprendizado
    t37 = delta_oculto * t36
    t38 = t35 + t37
    neuronio.bias = t38
  forstep17:
    i_1 = i_1 + 1
    goto for16
  endfor18:
    return
endfunc

func RedeNeural.treinar(this, entradas_1, saidas_desejadas_1, epocas):
    e = 0
  for22:
    if e >= epocas goto endfor24
    k = 0
  for25:
    param entradas_1
    t0 = call len, 1
    if k >= t0 goto endfor27
    t1 = entradas_1[k]
    param t1
    r = callm this.feedforward, 1
    t2 = entradas_1[k]
    t3 = saidas_desejadas_1[k]
    t4 = r[0]
    t5 = r[1]
    param t2
    param t3
    param t4
    param t5
    callm this.backpropagation, 4
  forstep26:
    k = k + 1
    goto for25
  endfor27:
  forstep23:
    e = e + 1
    goto for22
  endfor24:
    return
endfunc

func RedeNeural.testar(this, entradas_1):
    k = 0
  for28:
    param entradas_1
    t0 = call len, 1
    if k >= t0 goto endfor30
    t1 = entradas_1[k]
    param t1
    r = callm this.feedforward, 1
    t2 = entradas_1[k]
    param t2
    t3 = call to_string, 1
    t4 = "Input: " + t3
    t5 = t4 + ", Predicted Output: "
    t6 = r[1]
    param t6
    param 4
    t7 = call fmt, 2
    t8 = t5 + t7
    print t8
  forstep29:
    k = k + 1
    goto for28
  endfor30:
    return
endfunc

func main():
    entradas = new_list
    t0 = new_list
    append t0, 0
    append t0, 0
    append entradas, t0
    t1 = new_list
    append t1, 0
    append t1, 1
    append entradas, t1
    t2 = new_list
    append t2, 1
    append t2, 0
    append entradas, t2
    t3 = new_list
    append t3, 1
    append t3, 1
    append entradas, t3
    saidas_desejadas = new_list
    append saidas_desejadas, 0
    append saidas_desejadas, 1
    append saidas_desejadas, 1
    append saidas_desejadas, 0
    rede = new RedeNeural
    param rede
    call RedeNeural.__attrs, 1
    param rede
    call RedeNeural.init, 1
    param entradas
    param saidas_desejadas
    param 20000
    callm rede.treinar, 3
    param entradas
    callm rede.testar, 1
    return
endfunc
