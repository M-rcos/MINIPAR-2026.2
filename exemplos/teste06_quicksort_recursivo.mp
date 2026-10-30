# Teste 6: ordenação com quicksort recursivo, usando classes e objetos.

# Verifica se um texto é um inteiro (com sinal opcional).
func eh_inteiro(tok) {
    if (len(tok) == 0) {
        return false;
    }
    var inicio = 0;
    if (tok[0] == "-") {
        inicio = 1;
    }
    if (inicio == len(tok)) {
        return false;
    }
    for (var i = inicio; i < len(tok); i += 1) {
        if (!is_digit(tok[i])) {
            return false;
        }
    }
    return true;
}

class Quicksort {
    var array = [];

    func init(a) {
        this.array = a;
    }

    func ordenar() {
        return this.quicksort_rec(this.array);
    }

    func quicksort_rec(array) {
        if (len(array) <= 1) {
            return array;
        }
        var pivot = array[0];
        var menores = [];
        var maiores = [];
        for (var i = 1; i < len(array); i += 1) {
            var x = array[i];
            if (x <= pivot) {
                menores.append(x);
            } else {
                maiores.append(x);
            }
        }
        return this.quicksort_rec(menores) + [pivot] + this.quicksort_rec(maiores);
    }
}

class InterfaceOrdenacao {
    func iniciar() {
        print("==== Ordenação com Quicksort ====");
        print("Insira os elementos do vetor separados por espaço:");
        var entrada = trim(input());

        var valido = true;
        for (var tok in split(entrada, " ")) {
            if (tok != "" && !eh_inteiro(tok)) {
                valido = false;
            }
        }
        if (!valido) {
            print("Por favor, insira apenas números separados por espaço.");
            this.iniciar();    # reinicia a interface em caso de erro
            return;
        }

        var array = parse_ints(entrada);
        print("Vetor original:", array);
        var algoritmo = new Quicksort(array);
        var vetor_ordenado = algoritmo.ordenar();
        print("Vetor ordenado:", vetor_ordenado);
    }
}

# Executa o programa
var interface_ordenacao = new InterfaceOrdenacao();
interface_ordenacao.iniciar();
