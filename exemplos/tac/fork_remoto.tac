func fibonacci(n):
    lista = new_list
    a = 0
    b = 1
    i = 0
  for1:
    if i >= n goto endfor3
    append lista, a
    proximo = a + b
    a = b
    b = proximo
  forstep2:
    i = i + 1
    goto for1
  endfor3:
    return lista
endfunc

func fatorial(n):
    r = 1
    i = 2
  for4:
    if i > n goto endfor6
    r = r * i
  forstep5:
    i = i + 1
    goto for4
  endfor6:
    return r
endfunc

func principal():
    quantos = 12
    numero = 10
    fork fib on host "127.0.0.1", 9000 -> principal$fib(quantos)
    fork fat on core 0 -> principal$fat(numero)
    f = join fat
    serie = join fib
    print "Fatorial de", numero, "=", f
    print "Fibonacci:", serie
    return
endfunc

task principal$fib(quantos):
    param quantos
    t0 = call fibonacci, 1
    return t0
endfunc

task principal$fat(numero):
    param numero
    t1 = call fatorial, 1
    return t1
endfunc

func main():
    call principal, 0
    return
endfunc
