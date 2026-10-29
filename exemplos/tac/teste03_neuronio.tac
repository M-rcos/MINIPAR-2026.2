class Neuronio:
    field input_val
    field output_desejado
    field peso
    field bias
    field peso_bias
    field taxa_aprendizado
    field erro
    field iteracao
    method init
    method ativacao
    method treinar
endclass

global neuronio

func Neuronio.__attrs(this):
    this.input_val = 0
    this.output_desejado = 0
    this.peso = 0.5
    this.bias = 1
    this.peso_bias = 0.5
    this.taxa_aprendizado = 0.01
    this.erro = 1000000.0
    this.iteracao = 0
    return
endfunc

func Neuronio.init(this, entrada, desejado):
    this.input_val = entrada
    this.output_desejado = desejado
    return
endfunc

func Neuronio.ativacao(this, soma):
    if soma < 0 goto endif1
    return 1
  endif1:
    return 0
endfunc

func Neuronio.treinar(this):
    t0 = this.input_val
    t1 = this.output_desejado
    print "Entrada:", t0, "| Saída desejada:", t1
  while2:
    t2 = this.erro
    if t2 == 0 goto endwhile3
    t3 = this.iteracao
    t4 = t3 + 1
    this.iteracao = t4
    t5 = this.iteracao
    print "\n#### Iteração:", t5
    t6 = this.peso
    param t6
    param 4
    t7 = call fmt, 2
    print "Peso:", t7
    t8 = this.input_val
    t9 = this.peso
    t10 = t8 * t9
    t11 = this.bias
    t12 = this.peso_bias
    t13 = t11 * t12
    soma = t10 + t13
    param soma
    saida = callm this.ativacao, 1
    print "Saída:", saida
    t14 = this.output_desejado
    t15 = t14 - saida
    this.erro = t15
    t16 = this.erro
    print "Erro:", t16
    t17 = this.erro
    if t17 == 0 goto endif4
    t18 = this.peso
    t19 = this.taxa_aprendizado
    t20 = this.input_val
    t21 = t19 * t20
    t22 = this.erro
    t23 = t21 * t22
    t24 = t18 + t23
    this.peso = t24
    t25 = this.peso_bias
    param t25
    param 4
    t26 = call fmt, 2
    print "Peso do bias:", t26
    t27 = this.peso_bias
    t28 = this.taxa_aprendizado
    t29 = this.bias
    t30 = t28 * t29
    t31 = this.erro
    t32 = t30 * t31
    t33 = t27 + t32
    this.peso_bias = t33
  endif4:
    goto while2
  endwhile3:
    print "\n✅ Parabéns! O neurônio aprendeu."
    t34 = this.output_desejado
    print "Valor desejado:", t34
    return
endfunc

func main():
    neuronio = new Neuronio
    param neuronio
    call Neuronio.__attrs, 1
    param neuronio
    param 1
    param 0
    call Neuronio.init, 3
    callm neuronio.treinar, 0
    return
endfunc
