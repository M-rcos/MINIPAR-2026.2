# fork em OUTRO COMPUTADOR (aqui, em localhost para teste).
#
# 1) No computador que vai executar a tarefa remota, inicie o trabalhador (o mesmo
#    programa compilado, em modo --worker):
#        ./fork_remoto --worker 9000
# 2) No computador principal, execute normalmente:
#        ./fork_remoto
#
# A tarefa remota recebe cópias das variáveis locais que usa e devolve o resultado
# pelo "return"; o programa principal o recebe com "join".
func fibonacci(n) {
    var lista = [];
    var a = 0;
    var b = 1;
    for (var i = 0; i < n; i += 1) {
        lista.append(a);
        var proximo = a + b;
        a = b;
        b = proximo;
    }
    return lista;
}

func fatorial(n) {
    var r = 1;
    for (var i = 2; i <= n; i += 1) {
        r *= i;
    }
    return r;
}

func principal() {
    var quantos = 12;
    var numero = 10;

    # Fibonacci roda no outro computador; o fatorial, em um núcleo local.
    fork fib on host "127.0.0.1", 9000 {
        return fibonacci(quantos);
    }
    fork fat on core 0 {
        return fatorial(numero);
    }

    var f = join fat;
    var serie = join fib;
    print("Fatorial de", numero, "=", f);
    print("Fibonacci:", serie);
}

principal();
