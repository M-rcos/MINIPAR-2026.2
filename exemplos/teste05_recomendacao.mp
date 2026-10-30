# Teste 5: sistema de recomendação de e-commerce com rede neural.
# Entrada: vetor binário do histórico de compras (1 comprou, 0 não comprou).
# Camada oculta: 10 neurônios com ReLU. Saída: um neurônio por produto, com sigmoide.

func contem(lista, item) {
    for (var x in lista) {
        if (x == item) {
            return true;
        }
    }
    return false;
}

class Produto {
    var nome = "";

    func init(n) {
        this.nome = n;
    }
}

class Categoria {
    var nome = "";
    var produtos = [];

    func init(n, lista_produtos) {
        this.nome = n;
        for (var p in lista_produtos) {
            this.produtos.append(new Produto(p));
        }
    }
}

class Usuario {
    var historico_compras = [];

    func init(historico) {
        this.historico_compras = historico;
    }

    func codificar_historico(todos_produtos) {
        var codificacao = [];
        for (var produto in todos_produtos) {
            if (contem(this.historico_compras, produto)) {
                codificacao.append(1);
            } else {
                codificacao.append(0);
            }
        }
        return codificacao;
    }
}

class RedeNeural {
    var W1;
    var b1 = [];
    var W2;
    var b2 = [];

    func init(input_size, hidden_size, output_size) {
        this.W1 = matrix(input_size, hidden_size, 0.5);
        for (var i = 0; i < hidden_size; i += 1) {
            this.b1.append(0.5);
        }
        this.W2 = matrix(hidden_size, output_size, 0.5);
        for (var i = 0; i < output_size; i += 1) {
            this.b2.append(0.5);
        }
    }

    func relu(x) {
        var r = [];
        for (var v in x) {
            r.append(max(0, v));
        }
        return r;
    }

    func sigmoid(x) {
        var r = [];
        for (var v in x) {
            r.append(1 / (1 + exp(-v)));
        }
        return r;
    }

    func forward(X) {
        var Z1 = [];
        for (var i = 0; i < len(this.b1); i += 1) {
            var soma = 0;
            for (var j = 0; j < len(X); j += 1) {
                soma += X[j] * this.W1[j][i];
            }
            Z1.append(soma + this.b1[i]);
        }
        var A1 = this.relu(Z1);

        var Z2 = [];
        for (var i = 0; i < len(this.b2); i += 1) {
            var soma2 = 0;
            for (var j = 0; j < len(A1); j += 1) {
                soma2 += A1[j] * this.W2[j][i];
            }
            Z2.append(soma2 + this.b2[i]);
        }
        return this.sigmoid(Z2);
    }
}

class Recomendador {
    var usuario = null;
    var categorias = [];
    var todos_produtos = [];

    func init(u, cats) {
        this.usuario = u;
        this.categorias = cats;
        for (var c in cats) {
            for (var p in c.produtos) {
                this.todos_produtos.append(p.nome);
            }
        }
    }

    func recomendar() {
        var entrada_codificada = this.usuario.codificar_historico(this.todos_produtos);
        var input_size = len(entrada_codificada);
        var hidden_size = 10;
        var output_size = len(entrada_codificada);

        var rede = new RedeNeural(input_size, hidden_size, output_size);
        var saida = rede.forward(entrada_codificada);

        var recomendacoes = [];
        for (var i = 0; i < len(saida); i += 1) {
            if (saida[i] > 0.5 && !contem(this.usuario.historico_compras, this.todos_produtos[i])) {
                recomendacoes.append(this.todos_produtos[i]);
            }
        }
        return recomendacoes;
    }
}

# ---------- Execução ----------
# Dados de entrada
var categorias = [
    new Categoria("Eletrônicos", ["Smartphone", "Laptop", "Tablet", "Fones de ouvido"]),
    new Categoria("Roupas", ["Camisa", "Jeans", "Jaqueta", "Sapatos"]),
    new Categoria("Eletrodomésticos", ["Geladeira", "Micro-ondas", "Máquina de lavar", "Ar condicionado"]),
    new Categoria("Livros", ["Ficção", "Não-ficção", "Ficção científica", "Fantasia"])
];

var usuario = new Usuario(["Smartphone", "Jeans", "Micro-ondas", "Ficção"]);
var recomendador = new Recomendador(usuario, categorias);
var recomendacoes = recomendador.recomendar();

# Exibir recomendações
print("Produtos recomendados para você:");
for (var produto in recomendacoes) {
    print(produto);
}
