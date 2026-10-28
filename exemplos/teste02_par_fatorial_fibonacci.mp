# Teste 2: execução paralela (PAR) de fatorial e Fibonacci
# Cada seq dentro do par vira uma thread independente.

func fatorial(n) {
    var r = 1;
    var i = 2;
    while (i <= n) {
        r = r * i;
        i = i + 1;
    }
    return r;
}

func fibonacci(n) {
    var a = 0;
    var b = 1;
    var cont = 0;
    while (cont < n) {
        print("Fib:", a);
        var aux = a + b;
        a = b;
        b = aux;
        cont += 1;
    }
}

par {
    seq {
        var k = 2;
        while (k <= 5) {
            print("Fatorial de", k, "=", fatorial(k));
            k = k + 1;
        }
    }
    seq {
        fibonacci(10);
    }
}
