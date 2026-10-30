# Teste 11: MiniCompilador de expressões infixadas (com parênteses), escrito em MiniPar 2026.2.
# Fases: analisador léxico, analisador sintático (AST), código de três endereços (TAC),
# assembly ARMv7 (para o CPUlator), tabela de símbolos e avaliação da expressão.

# ---------------- funções auxiliares ----------------
func eh_operador(s) {
    return s == "+" || s == "-" || s == "*" || s == "/";
}

func eh_espaco(c) {
    return c == " " || c == "\t" || c == "\r" || c == "\n";
}

func eh_letra(c) {
    return is_alpha(c) || c == "_";
}

# verdadeiro se o texto tem apenas dígitos
func so_digitos(s) {
    if (len(s) == 0) {
        return false;
    }
    for (var i = 0; i < len(s); i += 1) {
        if (!is_digit(s[i])) {
            return false;
        }
    }
    return true;
}

# verdadeiro para inteiros e decimais (ex.: 12 e 3.5)
func eh_numero(s) {
    var partes = split(s, ".");
    if (len(partes) == 1) {
        return so_digitos(partes[0]);
    }
    return len(partes) == 2 && so_digitos(partes[0]) && so_digitos(partes[1]);
}

func espacos(n) {
    var s = "";
    for (var i = 0; i < n; i += 1) {
        s += "  ";
    }
    return s;
}

func pad_direita(s, n) {
    var r = s;
    while (len(r) < n) {
        r += " ";
    }
    return r;
}

# imprime como o Java: 22.0 para inteiros, 3.5 para fracionários
func formatar_double(x) {
    if (x == floor(x)) {
        return fmt(x, 1);
    }
    return to_string(x);
}

# ---------------- analisador léxico ----------------
class Token {
    var tipo = "";
    var lexema = "";

    func init(t, l) {
        this.tipo = t;
        this.lexema = l;
    }

    func mostrar() {
        print("[" + this.tipo + ": '" + this.lexema + "']");
    }
}

func analisar(entrada) {
    var tokens = [];
    var i = 0;
    var n = len(entrada);
    while (i < n) {
        var c = entrada[i];
        if (eh_espaco(c)) {
            i += 1;
        } else if (c == "#") {
            i = n;                      # comentário vai até o fim da linha
        } else if (is_digit(c)) {
            var j = i;
            while (j < n && is_digit(entrada[j])) {
                j += 1;
            }
            if (j + 1 < n && entrada[j] == "." && is_digit(entrada[j + 1])) {
                j += 1;
                while (j < n && is_digit(entrada[j])) {
                    j += 1;
                }
            }
            tokens.append(new Token("NUMERO", substr(entrada, i, j - i)));
            i = j;
        } else if (eh_letra(c)) {
            var k = i;
            while (k < n && (eh_letra(entrada[k]) || is_digit(entrada[k]))) {
                k += 1;
            }
            tokens.append(new Token("IDENTIFICADOR", substr(entrada, i, k - i)));
            i = k;
        } else if (eh_operador(c)) {
            tokens.append(new Token("OPERADOR", c));
            i += 1;
        } else if (c == "=") {
            tokens.append(new Token("ATRIBUICAO", c));
            i += 1;
        } else if (c == "(" || c == ")") {
            tokens.append(new Token("PARENTESE", c));
            i += 1;
        } else {
            i += 1;                     # símbolo desconhecido é ignorado
        }
    }
    return tokens;
}

# ---------------- AST ----------------
class ASTNode {
    var valor = "";
    var esquerda = null;
    var direita = null;

    func init(v) {
        this.valor = v;
    }
}

# ---------------- compilador ----------------
class MiniCompilador {
    var tokens = [];
    var pos = 0;
    var temp_count = 1;
    var reg_count = 0;
    var simbolos = [];
    var tipos_simbolos = [];
    var erro = false;
    var divisao_por_zero = false;
    var asm = "";

    func init(lexemas) {
        this.tokens = lexemas;
    }

    # ----- analisador sintático (descida recursiva) -----
    func parse_expr() {
        var node = this.parse_term();
        while (this.pos < len(this.tokens) && (this.tokens[this.pos] == "+" || this.tokens[this.pos] == "-")) {
            var op = this.tokens[this.pos];
            this.pos += 1;
            var direita = this.parse_term();
            var pai = new ASTNode(op);
            pai.esquerda = node;
            pai.direita = direita;
            node = pai;
        }
        return node;
    }

    func parse_term() {
        var node = this.parse_factor();
        while (this.pos < len(this.tokens) && (this.tokens[this.pos] == "*" || this.tokens[this.pos] == "/")) {
            var op = this.tokens[this.pos];
            this.pos += 1;
            var direita = this.parse_factor();
            var pai = new ASTNode(op);
            pai.esquerda = node;
            pai.direita = direita;
            node = pai;
        }
        return node;
    }

    func parse_factor() {
        if (this.pos >= len(this.tokens)) {
            this.erro = true;
            print("❌ Erro de sintaxe: a expressão terminou antes do esperado");
            return new ASTNode("0");
        }
        var token = this.tokens[this.pos];
        this.pos += 1;
        if (token == "(") {
            var node = this.parse_expr();
            if (this.pos < len(this.tokens) && this.tokens[this.pos] == ")") {
                this.pos += 1;
            } else {
                this.erro = true;
                print("❌ Erro de sintaxe: esperava ')'");
            }
            return node;
        }
        if (eh_operador(token) || token == ")" || token == "=") {
            this.erro = true;
            print("❌ Erro de sintaxe: esperava um operando, mas encontrou '" + token + "'");
            return new ASTNode("0");
        }
        this.registrar_simbolo(token);
        return new ASTNode(token);
    }

    func registrar_simbolo(token) {
        if (contem(this.simbolos, token)) {
            return;
        }
        this.simbolos.append(token);
        if (eh_numero(token)) {
            this.tipos_simbolos.append("CONST");
        } else {
            this.tipos_simbolos.append("VAR");
        }
    }

    # ----- árvore sintática -----
    func imprimir_ast(node, nivel) {
        if (node == null) {
            return;
        }
        this.imprimir_ast(node.direita, nivel + 1);
        print(espacos(nivel) + node.valor);
        this.imprimir_ast(node.esquerda, nivel + 1);
    }

    func formatar(node) {
        if (node == null) {
            return "";
        }
        if (!eh_operador(node.valor)) {
            return node.valor;
        }
        return "(" + this.formatar(node.esquerda) + " " + node.valor + " " + this.formatar(node.direita) + ")";
    }

    # ----- código de três endereços -----
    func gerar_tac(node) {
        if (!eh_operador(node.valor)) {
            return node.valor;
        }
        var a1 = this.gerar_tac(node.esquerda);
        var a2 = this.gerar_tac(node.direita);
        var temp = "t" + to_string(this.temp_count);
        this.temp_count += 1;
        print(temp + " = " + a1 + " " + node.valor + " " + a2);
        return temp;
    }

    # ----- assembly ARMv7 -----
    func emitir(linha) {
        print(linha);
        this.asm = this.asm + linha + "\n";
    }

    func emitir_mov(reg, valor) {
        if (so_digitos(valor)) {
            if (to_number(valor) <= 255) {
                this.emitir("    MOV    " + reg + ", #" + valor);
            } else {
                this.emitir("    LDR    " + reg + ", =" + valor);       # imediato maior que 8 bits
            }
        } else if (eh_numero(valor)) {
            var inteiro = split(valor, ".")[0];
            this.emitir("    LDR    " + reg + ", =" + inteiro + "    @ aviso: decimal " + valor + " truncado");
        } else {
            this.emitir("    MOV    " + reg + ", #0    @ variável '" + valor + "' sem valor (usando 0)");
        }
    }

    func gerar_assembly(node) {
        if (!eh_operador(node.valor)) {
            var reg_folha = "r" + to_string(this.reg_count);
            this.reg_count += 1;
            this.emitir_mov(reg_folha, node.valor);
            return reg_folha;
        }
        var a1 = this.gerar_assembly(node.esquerda);
        var a2 = this.gerar_assembly(node.direita);
        var reg = "r" + to_string(this.reg_count);
        this.reg_count += 1;

        var instr = "NOP";
        if (node.valor == "+") {
            instr = "ADD";
        } else if (node.valor == "-") {
            instr = "SUB";
        } else if (node.valor == "*") {
            instr = "MUL";
        } else if (node.valor == "/") {
            instr = "DIV_UNSUPPORTED";
        }

        var expr = this.formatar(node);
        if (instr == "DIV_UNSUPPORTED") {
            this.emitir("    @ divisão não suportada: " + a1 + " / " + a2 + "    @ resultado de '" + expr + "'");
        } else {
            this.emitir("    " + pad_direita(instr, 6) + " " + reg + ", " + a1 + ", " + a2 + "    @ resultado de '" + expr + "'");
        }
        return reg;
    }

    # ----- tabela de símbolos (constantes por valor, depois variáveis em ordem alfabética) -----
    func simbolo_menor(i, j) {
        var a = this.simbolos[i];
        var b = this.simbolos[j];
        var ta = this.tipos_simbolos[i];
        var tb = this.tipos_simbolos[j];
        if (ta == "CONST" && tb == "CONST") {
            return to_number(a) < to_number(b);
        }
        if (ta == "CONST") {
            return true;
        }
        if (tb == "CONST") {
            return false;
        }
        return a < b;
    }

    func ordenar_simbolos() {
        var n = len(this.simbolos);
        for (var i = 0; i < n; i += 1) {
            for (var j = 0; j < n - 1 - i; j += 1) {
                if (this.simbolo_menor(j + 1, j)) {
                    var troca = this.simbolos[j];
                    this.simbolos[j] = this.simbolos[j + 1];
                    this.simbolos[j + 1] = troca;
                    var troca_tipo = this.tipos_simbolos[j];
                    this.tipos_simbolos[j] = this.tipos_simbolos[j + 1];
                    this.tipos_simbolos[j + 1] = troca_tipo;
                }
            }
        }
    }

    func imprimir_simbolos() {
        this.ordenar_simbolos();
        for (var i = 0; i < len(this.simbolos); i += 1) {
            print("🔹 " + this.simbolos[i] + " → " + this.tipos_simbolos[i]);
        }
    }

    # ----- avaliação -----
    func avaliar(node) {
        if (!eh_operador(node.valor)) {
            if (eh_numero(node.valor)) {
                return to_number(node.valor);
            }
            print("⚠️ Variável '" + node.valor + "' não tem valor atribuído. Usando 0.");
            return 0;
        }
        var esq = this.avaliar(node.esquerda);
        var dir = this.avaliar(node.direita);
        if (node.valor == "+") {
            return esq + dir;
        }
        if (node.valor == "-") {
            return esq - dir;
        }
        if (node.valor == "*") {
            return esq * dir;
        }
        if (dir == 0) {
            this.divisao_por_zero = true;
            return 0;
        }
        return esq / dir;
    }
}

func contem(lista, item) {
    for (var x in lista) {
        if (x == item) {
            return true;
        }
    }
    return false;
}

# ---------------- programa principal ----------------
var entrada = input("Digite uma expressão infixada: ");

var tokens = analisar(entrada);
print("\n🔍 Tokens gerados pelo analisador léxico:");
var lexemas = [];
for (var t in tokens) {
    t.mostrar();
    lexemas.append(t.lexema);
}

var compilador = new MiniCompilador(lexemas);
var raiz = compilador.parse_expr();
if (compilador.pos < len(lexemas) && !compilador.erro) {
    compilador.erro = true;
    print("❌ Erro de sintaxe: símbolos sobrando depois da expressão: '" + lexemas[compilador.pos] + "'");
}

if (compilador.erro) {
    print("\n🚫 Compilação interrompida por erro de sintaxe.");
} else {
    print("\n🌳 Árvore Sintática Abstrata (AST):");
    compilador.imprimir_ast(raiz, 0);

    print("\n📦 Código de Três Endereços (TAC):");
    compilador.gerar_tac(raiz);

    print("\n⚙️ Assembly ARMv7 (CPUlator):");
    compilador.emitir(".global _start");
    compilador.emitir(".text");
    compilador.emitir("_start:");
    compilador.gerar_assembly(raiz);
    compilador.emitir("    b .    @ loop infinito para parar o programa");

    print("\n📚 Tabela de Símbolos:");
    compilador.imprimir_simbolos();

    print("\n🧮 Resultado final da expressão:");
    var resultado = compilador.avaliar(raiz);
    if (compilador.divisao_por_zero) {
        print("➡️  NaN (divisão por zero)");
    } else {
        print("➡️  " + formatar_double(resultado));
    }

    write_file("Codigo-Assembly-ARMV7.arm", compilador.asm);
    print("\n💾 Assembly salvo em Codigo-Assembly-ARMV7.arm");
}
