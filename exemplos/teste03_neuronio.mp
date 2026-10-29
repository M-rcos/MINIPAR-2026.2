# Teste 3: neurônio com aprendizado, usando classe e objeto.
class Neuronio {
    var input_val = 0;
    var output_desejado = 0;
    var peso = 0.5;
    var bias = 1;
    var peso_bias = 0.5;
    var taxa_aprendizado = 0.01;
    var erro = 1000000.0;
    var iteracao = 0;

    func init(entrada, desejado) {
        this.input_val = entrada;
        this.output_desejado = desejado;
    }

    func ativacao(soma) {
        if (soma >= 0) {
            return 1;
        }
        return 0;
    }

    func treinar() {
        print("Entrada:", this.input_val, "| Saída desejada:", this.output_desejado);
        while (this.erro != 0) {
            this.iteracao += 1;
            print("\n#### Iteração:", this.iteracao);
            print("Peso:", fmt(this.peso, 4));
            var soma = (this.input_val * this.peso) + (this.bias * this.peso_bias);
            var saida = this.ativacao(soma);
            print("Saída:", saida);
            this.erro = this.output_desejado - saida;
            print("Erro:", this.erro);
            if (this.erro != 0) {
                this.peso += this.taxa_aprendizado * this.input_val * this.erro;
                print("Peso do bias:", fmt(this.peso_bias, 4));
                this.peso_bias += this.taxa_aprendizado * this.bias * this.erro;
            }
        }
        print("\n✅ Parabéns! O neurônio aprendeu.");
        print("Valor desejado:", this.output_desejado);
    }
}

var neuronio = new Neuronio(1, 0);
neuronio.treinar();
