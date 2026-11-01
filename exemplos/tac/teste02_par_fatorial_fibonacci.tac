func fatorial(n):
    r = 1
    i = 2
  while1:
    if i > n goto endwhile2
    r = r * i
    i = i + 1
    goto while1
  endwhile2:
    return r
endfunc

func fibonacci(n):
    a = 0
    b = 1
    cont = 0
  while3:
    if cont >= n goto endwhile4
    print "Fib:", a
    aux = a + b
    a = b
    b = aux
    cont = cont + 1
    goto while3
  endwhile4:
    return
endfunc

func main():
    par_begin
      task par1_t1 -> main$par1_t1()
      task par1_t2 -> main$par1_t2()
    par_end
    return
endfunc

task main$par1_t1():
    k = 2
  while5:
    if k > 5 goto endwhile6
    param k
    t0 = call fatorial, 1
    print "Fatorial de", k, "=", t0
    k = k + 1
    goto while5
  endwhile6:
    return
endfunc

task main$par1_t2():
    param 10
    call fibonacci, 1
    return
endfunc
