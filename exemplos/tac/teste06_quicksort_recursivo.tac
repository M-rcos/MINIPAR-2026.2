class Quicksort:
    field array
    method init
    method ordenar
    method quicksort_rec
endclass

class InterfaceOrdenacao:
    method iniciar
endclass

global interface_ordenacao

func eh_inteiro(tok):
    param tok
    t0 = call len, 1
    if t0 != 0 goto endif1
    return false
  endif1:
    inicio = 0
    t1 = tok[0]
    if t1 != "-" goto endif2
    inicio = 1
  endif2:
    param tok
    t2 = call len, 1
    if inicio != t2 goto endif3
    return false
  endif3:
    i = inicio
  for4:
    param tok
    t3 = call len, 1
    if i >= t3 goto endfor6
    t4 = tok[i]
    param t4
    t5 = call is_digit, 1
    if t5 goto endif7
    return false
  endif7:
  forstep5:
    i = i + 1
    goto for4
  endfor6:
    return true
endfunc

func Quicksort.__attrs(this):
    t0 = new_list
    this.array = t0
    return
endfunc

func Quicksort.init(this, a):
    this.array = a
    return
endfunc

func Quicksort.ordenar(this):
    t0 = this.array
    param t0
    t1 = callm this.quicksort_rec, 1
    return t1
endfunc

func Quicksort.quicksort_rec(this, array):
    param array
    t0 = call len, 1
    if t0 > 1 goto endif8
    return array
  endif8:
    pivot = array[0]
    menores = new_list
    maiores = new_list
    i = 1
  for9:
    param array
    t1 = call len, 1
    if i >= t1 goto endfor11
    x = array[i]
    if x > pivot goto else12
    append menores, x
    goto endif13
  else12:
    append maiores, x
  endif13:
  forstep10:
    i = i + 1
    goto for9
  endfor11:
    param menores
    t2 = callm this.quicksort_rec, 1
    t3 = new_list
    append t3, pivot
    t4 = t2 + t3
    param maiores
    t5 = callm this.quicksort_rec, 1
    t6 = t4 + t5
    return t6
endfunc

func InterfaceOrdenacao.__attrs(this):
    return
endfunc

func InterfaceOrdenacao.iniciar(this):
    print "==== Ordenação com Quicksort ===="
    print "Insira os elementos do vetor separados por espaço:"
    t0 = input
    param t0
    entrada = call trim, 1
    valido = true
    param entrada
    param " "
    t1 = call split, 2
    t2 = size t1
    t3 = 0
  foreach14:
    if t3 >= t2 goto endforeach16
    tok = t1[t3]
    if tok == "" goto endif17
    param tok
    t4 = call eh_inteiro, 1
    if t4 goto endif17
    valido = false
  endif17:
  foreachstep15:
    t3 = t3 + 1
    goto foreach14
  endforeach16:
    if valido goto endif18
    print "Por favor, insira apenas números separados por espaço."
    callm this.iniciar, 0
    return
  endif18:
    param entrada
    array = call parse_ints, 1
    print "Vetor original:", array
    algoritmo = new Quicksort
    param algoritmo
    call Quicksort.__attrs, 1
    param algoritmo
    param array
    call Quicksort.init, 2
    vetor_ordenado = callm algoritmo.ordenar, 0
    print "Vetor ordenado:", vetor_ordenado
    return
endfunc

func main():
    interface_ordenacao = new InterfaceOrdenacao
    param interface_ordenacao
    call InterfaceOrdenacao.__attrs, 1
    callm interface_ordenacao.iniciar, 0
    return
endfunc
