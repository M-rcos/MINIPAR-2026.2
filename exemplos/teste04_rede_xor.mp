# Teste 4: rede neural que aprende a função XOR.
# Camada oculta com 3 neurônios e 1 neurônio de saída, ativação sigmoide,
# treino por feedforward e backpropagation. Todos os cálculos são manuais.

# Funções auxiliares
func sigmoid(x) {
    return 1 / (1 + exp(-x));
}

func sigmoid_derivative(x) {
    return x * (1 - x);
}

class Neuronio {
    var pesos = [];
    var bias = 0;
    var saida = 0;

    func init(num_inputs) {
        for (var i = 0; i < num_inputs; i += 1) {
            this.pesos.append(random());
        }
        this.bias = random();
    }

    func feedforward(entradas) {
        var soma = 0;
        for (var i = 0; i < len(entradas); i += 1) {
            soma += entradas[i] * this.pesos[i];
        }
        soma += this.bias;
        this.saida = sigmoid(soma);
        return this.saida;
    }

    func calcular_derivada() {
        return sigmoid_derivative(this.saida);
    }
}

class RedeNeural {
    var taxa_aprendizado = 0.2;
    var camada_oculta = [];
    var neuronio_saida = null;

    func init() {
        for (var i = 0; i < 3; i += 1) {
            this.camada_oculta.append(new Neuronio(2));
        }
        this.neuronio_saida = new Neuronio(3);
    }

    # devolve [saidas_ocultas, saida_final]
    func feedforward(entradas) {
        var saidas_ocultas = [];
        for (var n in this.camada_oculta) {
            saidas_ocultas.append(n.feedforward(entradas));
        }
        var saida_final = this.neuronio_saida.feedforward(saidas_ocultas);
        return [saidas_ocultas, saida_final];
    }

    func backpropagation(entradas, saida_desejada, saidas_ocultas, saida_final) {
        var erro = saida_desejada - saida_final;
        var delta_saida = erro * this.neuronio_saida.calcular_derivada();

        # Atualiza pesos da camada de saída
        for (var i = 0; i < len(this.neuronio_saida.pesos); i += 1) {
            this.neuronio_saida.pesos[i] += saidas_ocultas[i] * delta_saida * this.taxa_aprendizado;
        }
        this.neuronio_saida.bias += delta_saida * this.taxa_aprendizado;

        # Atualiza pesos da camada oculta
        for (var i = 0; i < len(this.camada_oculta); i += 1) {
            var neuronio = this.camada_oculta[i];
            var delta_oculto = delta_saida * this.neuronio_saida.pesos[i] * neuronio.calcular_derivada();
            for (var j = 0; j < len(neuronio.pesos); j += 1) {
                neuronio.pesos[j] += entradas[j] * delta_oculto * this.taxa_aprendizado;
            }
            neuronio.bias += delta_oculto * this.taxa_aprendizado;
        }
    }

    func treinar(entradas, saidas_desejadas, epocas) {
        for (var e = 0; e < epocas; e += 1) {
            for (var k = 0; k < len(entradas); k += 1) {
                var r = this.feedforward(entradas[k]);
                this.backpropagation(entradas[k], saidas_desejadas[k], r[0], r[1]);
            }
        }
    }

    func testar(entradas) {
        for (var k = 0; k < len(entradas); k += 1) {
            var r = this.feedforward(entradas[k]);
            print("Input: " + to_string(entradas[k]) + ", Predicted Output: " + fmt(r[1], 4));
        }
    }
}

# Dados XOR
var entradas = [[0, 0], [0, 1], [1, 0], [1, 1]];
var saidas_desejadas = [0, 1, 1, 0];

# Execução
var rede = new RedeNeural();
rede.treinar(entradas, saidas_desejadas, 20000);
rede.testar(entradas);
