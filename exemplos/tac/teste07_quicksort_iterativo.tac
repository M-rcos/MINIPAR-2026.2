global array

func quicksort_iterativo(arr):
    pilha = new_list
    append pilha, 0
    param arr
    t0 = call len, 1
    t1 = t0 - 1
    append pilha, t1
  while1:
    param pilha
    t2 = call len, 1
    if t2 <= 0 goto endwhile2
    fim = pop pilha
    inicio = pop pilha
    if inicio >= fim goto endif3
    pivo = arr[fim]
    i = inicio - 1
    j = inicio
  for4:
    if j >= fim goto endfor6
    t3 = arr[j]
    if t3 > pivo goto endif7
    i = i + 1
    troca = arr[i]
    t4 = arr[j]
    arr[i] = t4
    arr[j] = troca
  endif7:
  forstep5:
    j = j + 1
    goto for4
  endfor6:
    i = i + 1
    troca_pivo = arr[i]
    t5 = arr[fim]
    arr[i] = t5
    arr[fim] = troca_pivo
    append pilha, inicio
    t6 = i - 1
    append pilha, t6
    t7 = i + 1
    append pilha, t7
    append pilha, fim
  endif3:
    goto while1
  endwhile2:
    return
endfunc

func main():
    array = new_list
    append array, 33
    append array, 12
    append array, 98
    append array, 5
    append array, 61
    param array
    call quicksort_iterativo, 1
    print "Array ordenado:", array
    return
endfunc
