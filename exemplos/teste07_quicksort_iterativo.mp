# Teste 7: quicksort não recursivo de um array de 5 elementos, só com funções.
func quicksort_iterativo(arr) {
    var pilha = [];
    pilha.append(0);
    pilha.append(len(arr) - 1);

    while (len(pilha) > 0) {
        var fim = pilha.pop();
        var inicio = pilha.pop();

        if (inicio < fim) {
            var pivo = arr[fim];
            var i = inicio - 1;

            for (var j = inicio; j < fim; j += 1) {
                if (arr[j] <= pivo) {
                    i += 1;
                    var troca = arr[i];
                    arr[i] = arr[j];
                    arr[j] = troca;
                }
            }

            i += 1;
            var troca_pivo = arr[i];
            arr[i] = arr[fim];
            arr[fim] = troca_pivo;

            pilha.append(inicio);
            pilha.append(i - 1);
            pilha.append(i + 1);
            pilha.append(fim);
        }
    }
}

var array = [33, 12, 98, 5, 61];
quicksort_iterativo(array);
print("Array ordenado:", array);
