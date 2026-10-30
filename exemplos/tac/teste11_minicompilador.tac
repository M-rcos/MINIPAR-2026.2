class Token:
    field tipo
    field lexema
    method init
    method mostrar
endclass

class ASTNode:
    field valor
    field esquerda
    field direita
    method init
endclass

class MiniCompilador:
    field tokens
    field pos
    field temp_count
    field reg_count
    field simbolos
    field tipos_simbolos
    field erro
    field divisao_por_zero
    field asm
    method init
    method parse_expr
    method parse_term
    method parse_factor
    method registrar_simbolo
    method imprimir_ast
    method formatar
    method gerar_tac
    method emitir
    method emitir_mov
    method gerar_assembly
    method simbolo_menor
    method ordenar_simbolos
    method imprimir_simbolos
    method avaliar
endclass

global entrada
global tokens
global lexemas
global compilador
global raiz

func eh_operador(s):
    t0 = true
    if s == "+" goto endlogic1
    if s == "-" goto endlogic1
    if s == "*" goto endlogic1
    t1 = s == "/"
    t0 = t1
  endlogic1:
    return t0
endfunc

func eh_espaco(c):
    t0 = true
    if c == " " goto endlogic2
    if c == "\t" goto endlogic2
    if c == "\r" goto endlogic2
    t1 = c == "\n"
    t0 = t1
  endlogic2:
    return t0
endfunc

func eh_letra(c):
    t0 = true
    param c
    t1 = call is_alpha, 1
    if t1 goto endlogic3
    t2 = c == "_"
    t0 = t2
  endlogic3:
    return t0
endfunc

func so_digitos(s):
    param s
    t0 = call len, 1
    if t0 != 0 goto endif4
    return false
  endif4:
    i = 0
  for5:
    param s
    t1 = call len, 1
    if i >= t1 goto endfor7
    t2 = s[i]
    param t2
    t3 = call is_digit, 1
    if t3 goto endif8
    return false
  endif8:
  forstep6:
    i = i + 1
    goto for5
  endfor7:
    return true
endfunc

func eh_numero(s):
    param s
    param "."
    partes = call split, 2
    param partes
    t0 = call len, 1
    if t0 != 1 goto endif9
    t1 = partes[0]
    param t1
    t2 = call so_digitos, 1
    return t2
  endif9:
    t3 = false
    param partes
    t4 = call len, 1
    if t4 != 2 goto endlogic10
    t5 = partes[0]
    param t5
    t6 = call so_digitos, 1
    ifFalse t6 goto endlogic10
    t7 = partes[1]
    param t7
    t8 = call so_digitos, 1
    t3 = t8
  endlogic10:
    return t3
endfunc

func espacos(n):
    s = ""
    i = 0
  for11:
    if i >= n goto endfor13
    s = s + "  "
  forstep12:
    i = i + 1
    goto for11
  endfor13:
    return s
endfunc

func pad_direita(s, n):
    r = s
  while14:
    param r
    t0 = call len, 1
    if t0 >= n goto endwhile15
    r = r + " "
    goto while14
  endwhile15:
    return r
endfunc

func formatar_double(x):
    param x
    t0 = call floor, 1
    if x != t0 goto endif16
    param x
    param 1
    t1 = call fmt, 2
    return t1
  endif16:
    param x
    t2 = call to_string, 1
    return t2
endfunc

func Token.__attrs(this):
    this.tipo = ""
    this.lexema = ""
    return
endfunc

func Token.init(this, t, l):
    this.tipo = t
    this.lexema = l
    return
endfunc

func Token.mostrar(this):
    t0 = this.tipo
    t1 = "[" + t0
    t2 = t1 + ": '"
    t3 = this.lexema
    t4 = t2 + t3
    t5 = t4 + "']"
    print t5
    return
endfunc

func analisar(entrada_1):
    tokens_1 = new_list
    i = 0
    param entrada_1
    n = call len, 1
  while17:
    if i >= n goto endwhile18
    c = entrada_1[i]
    param c
    t0 = call eh_espaco, 1
    ifFalse t0 goto else19
    i = i + 1
    goto endif20
  else19:
    if c != "#" goto else21
    i = n
    goto endif22
  else21:
    param c
    t1 = call is_digit, 1
    ifFalse t1 goto else23
    j = i
  while25:
    if j >= n goto endwhile26
    t2 = entrada_1[j]
    param t2
    t3 = call is_digit, 1
    ifFalse t3 goto endwhile26
    j = j + 1
    goto while25
  endwhile26:
    t4 = j + 1
    if t4 >= n goto endif27
    t5 = entrada_1[j]
    if t5 != "." goto endif27
    t6 = j + 1
    t7 = entrada_1[t6]
    param t7
    t8 = call is_digit, 1
    ifFalse t8 goto endif27
    j = j + 1
  while28:
    if j >= n goto endwhile29
    t9 = entrada_1[j]
    param t9
    t10 = call is_digit, 1
    ifFalse t10 goto endwhile29
    j = j + 1
    goto while28
  endwhile29:
  endif27:
    t11 = j - i
    param entrada_1
    param i
    param t11
    t12 = call substr, 3
    t13 = new Token
    param t13
    call Token.__attrs, 1
    param t13
    param "NUMERO"
    param t12
    call Token.init, 3
    append tokens_1, t13
    i = j
    goto endif24
  else23:
    param c
    t14 = call eh_letra, 1
    ifFalse t14 goto else30
    k = i
  while32:
    if k >= n goto endwhile33
    t15 = entrada_1[k]
    param t15
    t16 = call eh_letra, 1
    if t16 goto skip34
    t17 = entrada_1[k]
    param t17
    t18 = call is_digit, 1
    ifFalse t18 goto endwhile33
  skip34:
    k = k + 1
    goto while32
  endwhile33:
    t19 = k - i
    param entrada_1
    param i
    param t19
    t20 = call substr, 3
    t21 = new Token
    param t21
    call Token.__attrs, 1
    param t21
    param "IDENTIFICADOR"
    param t20
    call Token.init, 3
    append tokens_1, t21
    i = k
    goto endif31
  else30:
    param c
    t22 = call eh_operador, 1
    ifFalse t22 goto else35
    t23 = new Token
    param t23
    call Token.__attrs, 1
    param t23
    param "OPERADOR"
    param c
    call Token.init, 3
    append tokens_1, t23
    i = i + 1
    goto endif36
  else35:
    if c != "=" goto else37
    t24 = new Token
    param t24
    call Token.__attrs, 1
    param t24
    param "ATRIBUICAO"
    param c
    call Token.init, 3
    append tokens_1, t24
    i = i + 1
    goto endif38
  else37:
    if c == "(" goto skip41
    if c != ")" goto else39
  skip41:
    t25 = new Token
    param t25
    call Token.__attrs, 1
    param t25
    param "PARENTESE"
    param c
    call Token.init, 3
    append tokens_1, t25
    i = i + 1
    goto endif40
  else39:
    i = i + 1
  endif40:
  endif38:
  endif36:
  endif31:
  endif24:
  endif22:
  endif20:
    goto while17
  endwhile18:
    return tokens_1
endfunc

func ASTNode.__attrs(this):
    this.valor = ""
    this.esquerda = null
    this.direita = null
    return
endfunc

func ASTNode.init(this, v):
    this.valor = v
    return
endfunc

func MiniCompilador.__attrs(this):
    t0 = new_list
    this.tokens = t0
    this.pos = 0
    this.temp_count = 1
    this.reg_count = 0
    t1 = new_list
    this.simbolos = t1
    t2 = new_list
    this.tipos_simbolos = t2
    this.erro = false
    this.divisao_por_zero = false
    this.asm = ""
    return
endfunc

func MiniCompilador.init(this, lexemas_1):
    this.tokens = lexemas_1
    return
endfunc

func MiniCompilador.parse_expr(this):
    node = callm this.parse_term, 0
  while42:
    t0 = this.pos
    t1 = this.tokens
    param t1
    t2 = call len, 1
    if t0 >= t2 goto endwhile43
    t3 = this.tokens
    t4 = this.pos
    t5 = t3[t4]
    if t5 == "+" goto skip44
    t6 = this.tokens
    t7 = this.pos
    t8 = t6[t7]
    if t8 != "-" goto endwhile43
  skip44:
    t9 = this.tokens
    t10 = this.pos
    op = t9[t10]
    t11 = this.pos
    t12 = t11 + 1
    this.pos = t12
    direita = callm this.parse_term, 0
    pai = new ASTNode
    param pai
    call ASTNode.__attrs, 1
    param pai
    param op
    call ASTNode.init, 2
    pai.esquerda = node
    pai.direita = direita
    node = pai
    goto while42
  endwhile43:
    return node
endfunc

func MiniCompilador.parse_term(this):
    node = callm this.parse_factor, 0
  while45:
    t0 = this.pos
    t1 = this.tokens
    param t1
    t2 = call len, 1
    if t0 >= t2 goto endwhile46
    t3 = this.tokens
    t4 = this.pos
    t5 = t3[t4]
    if t5 == "*" goto skip47
    t6 = this.tokens
    t7 = this.pos
    t8 = t6[t7]
    if t8 != "/" goto endwhile46
  skip47:
    t9 = this.tokens
    t10 = this.pos
    op = t9[t10]
    t11 = this.pos
    t12 = t11 + 1
    this.pos = t12
    direita = callm this.parse_factor, 0
    pai = new ASTNode
    param pai
    call ASTNode.__attrs, 1
    param pai
    param op
    call ASTNode.init, 2
    pai.esquerda = node
    pai.direita = direita
    node = pai
    goto while45
  endwhile46:
    return node
endfunc

func MiniCompilador.parse_factor(this):
    t0 = this.pos
    t1 = this.tokens
    param t1
    t2 = call len, 1
    if t0 < t2 goto endif48
    this.erro = true
    print "❌ Erro de sintaxe: a expressão terminou antes do esperado"
    t3 = new ASTNode
    param t3
    call ASTNode.__attrs, 1
    param t3
    param "0"
    call ASTNode.init, 2
    return t3
  endif48:
    t4 = this.tokens
    t5 = this.pos
    token = t4[t5]
    t6 = this.pos
    t7 = t6 + 1
    this.pos = t7
    if token != "(" goto endif49
    node = callm this.parse_expr, 0
    t8 = this.pos
    t9 = this.tokens
    param t9
    t10 = call len, 1
    if t8 >= t10 goto else50
    t11 = this.tokens
    t12 = this.pos
    t13 = t11[t12]
    if t13 != ")" goto else50
    t14 = this.pos
    t15 = t14 + 1
    this.pos = t15
    goto endif51
  else50:
    this.erro = true
    print "❌ Erro de sintaxe: esperava ')'"
  endif51:
    return node
  endif49:
    param token
    t16 = call eh_operador, 1
    if t16 goto skip53
    if token == ")" goto skip53
    if token != "=" goto endif52
  skip53:
    this.erro = true
    t17 = "❌ Erro de sintaxe: esperava um operando, mas encontrou '" + token
    t18 = t17 + "'"
    print t18
    t19 = new ASTNode
    param t19
    call ASTNode.__attrs, 1
    param t19
    param "0"
    call ASTNode.init, 2
    return t19
  endif52:
    param token
    callm this.registrar_simbolo, 1
    t20 = new ASTNode
    param t20
    call ASTNode.__attrs, 1
    param t20
    param token
    call ASTNode.init, 2
    return t20
endfunc

func MiniCompilador.registrar_simbolo(this, token):
    t0 = this.simbolos
    param t0
    param token
    t1 = call contem, 2
    ifFalse t1 goto endif54
    return
  endif54:
    t2 = this.simbolos
    append t2, token
    param token
    t3 = call eh_numero, 1
    ifFalse t3 goto else55
    t4 = this.tipos_simbolos
    append t4, "CONST"
    goto endif56
  else55:
    t5 = this.tipos_simbolos
    append t5, "VAR"
  endif56:
    return
endfunc

func MiniCompilador.imprimir_ast(this, node, nivel):
    if node != null goto endif57
    return
  endif57:
    t0 = node.direita
    t1 = nivel + 1
    param t0
    param t1
    callm this.imprimir_ast, 2
    param nivel
    t2 = call espacos, 1
    t3 = node.valor
    t4 = t2 + t3
    print t4
    t5 = node.esquerda
    t6 = nivel + 1
    param t5
    param t6
    callm this.imprimir_ast, 2
    return
endfunc

func MiniCompilador.formatar(this, node):
    if node != null goto endif58
    return ""
  endif58:
    t0 = node.valor
    param t0
    t1 = call eh_operador, 1
    if t1 goto endif59
    t2 = node.valor
    return t2
  endif59:
    t3 = node.esquerda
    param t3
    t4 = callm this.formatar, 1
    t5 = "(" + t4
    t6 = t5 + " "
    t7 = node.valor
    t8 = t6 + t7
    t9 = t8 + " "
    t10 = node.direita
    param t10
    t11 = callm this.formatar, 1
    t12 = t9 + t11
    t13 = t12 + ")"
    return t13
endfunc

func MiniCompilador.gerar_tac(this, node):
    t0 = node.valor
    param t0
    t1 = call eh_operador, 1
    if t1 goto endif60
    t2 = node.valor
    return t2
  endif60:
    t3 = node.esquerda
    param t3
    a1 = callm this.gerar_tac, 1
    t4 = node.direita
    param t4
    a2 = callm this.gerar_tac, 1
    t5 = this.temp_count
    param t5
    t6 = call to_string, 1
    temp = "t" + t6
    t7 = this.temp_count
    t8 = t7 + 1
    this.temp_count = t8
    t9 = temp + " = "
    t10 = t9 + a1
    t11 = t10 + " "
    t12 = node.valor
    t13 = t11 + t12
    t14 = t13 + " "
    t15 = t14 + a2
    print t15
    return temp
endfunc

func MiniCompilador.emitir(this, linha):
    print linha
    t0 = this.asm
    t1 = t0 + linha
    t2 = t1 + "\n"
    this.asm = t2
    return
endfunc

func MiniCompilador.emitir_mov(this, reg, valor):
    param valor
    t0 = call so_digitos, 1
    ifFalse t0 goto else61
    param valor
    t1 = call to_number, 1
    if t1 > 255 goto else63
    t2 = "    MOV    " + reg
    t3 = t2 + ", #"
    t4 = t3 + valor
    param t4
    callm this.emitir, 1
    goto endif64
  else63:
    t5 = "    LDR    " + reg
    t6 = t5 + ", ="
    t7 = t6 + valor
    param t7
    callm this.emitir, 1
  endif64:
    goto endif62
  else61:
    param valor
    t8 = call eh_numero, 1
    ifFalse t8 goto else65
    param valor
    param "."
    t9 = call split, 2
    inteiro = t9[0]
    t10 = "    LDR    " + reg
    t11 = t10 + ", ="
    t12 = t11 + inteiro
    t13 = t12 + "    @ aviso: decimal "
    t14 = t13 + valor
    t15 = t14 + " truncado"
    param t15
    callm this.emitir, 1
    goto endif66
  else65:
    t16 = "    MOV    " + reg
    t17 = t16 + ", #0    @ variável '"
    t18 = t17 + valor
    t19 = t18 + "' sem valor (usando 0)"
    param t19
    callm this.emitir, 1
  endif66:
  endif62:
    return
endfunc

func MiniCompilador.gerar_assembly(this, node):
    t0 = node.valor
    param t0
    t1 = call eh_operador, 1
    if t1 goto endif67
    t2 = this.reg_count
    param t2
    t3 = call to_string, 1
    reg_folha = "r" + t3
    t4 = this.reg_count
    t5 = t4 + 1
    this.reg_count = t5
    t6 = node.valor
    param reg_folha
    param t6
    callm this.emitir_mov, 2
    return reg_folha
  endif67:
    t7 = node.esquerda
    param t7
    a1 = callm this.gerar_assembly, 1
    t8 = node.direita
    param t8
    a2 = callm this.gerar_assembly, 1
    t9 = this.reg_count
    param t9
    t10 = call to_string, 1
    reg = "r" + t10
    t11 = this.reg_count
    t12 = t11 + 1
    this.reg_count = t12
    instr = "NOP"
    t13 = node.valor
    if t13 != "+" goto else68
    instr = "ADD"
    goto endif69
  else68:
    t14 = node.valor
    if t14 != "-" goto else70
    instr = "SUB"
    goto endif71
  else70:
    t15 = node.valor
    if t15 != "*" goto else72
    instr = "MUL"
    goto endif73
  else72:
    t16 = node.valor
    if t16 != "/" goto endif74
    instr = "DIV_UNSUPPORTED"
  endif74:
  endif73:
  endif71:
  endif69:
    param node
    expr = callm this.formatar, 1
    if instr != "DIV_UNSUPPORTED" goto else75
    t17 = "    @ divisão não suportada: " + a1
    t18 = t17 + " / "
    t19 = t18 + a2
    t20 = t19 + "    @ resultado de '"
    t21 = t20 + expr
    t22 = t21 + "'"
    param t22
    callm this.emitir, 1
    goto endif76
  else75:
    param instr
    param 6
    t23 = call pad_direita, 2
    t24 = "    " + t23
    t25 = t24 + " "
    t26 = t25 + reg
    t27 = t26 + ", "
    t28 = t27 + a1
    t29 = t28 + ", "
    t30 = t29 + a2
    t31 = t30 + "    @ resultado de '"
    t32 = t31 + expr
    t33 = t32 + "'"
    param t33
    callm this.emitir, 1
  endif76:
    return reg
endfunc

func MiniCompilador.simbolo_menor(this, i, j):
    t0 = this.simbolos
    a = t0[i]
    t1 = this.simbolos
    b = t1[j]
    t2 = this.tipos_simbolos
    ta = t2[i]
    t3 = this.tipos_simbolos
    tb = t3[j]
    if ta != "CONST" goto endif77
    if tb != "CONST" goto endif77
    param a
    t4 = call to_number, 1
    param b
    t5 = call to_number, 1
    t6 = t4 < t5
    return t6
  endif77:
    if ta != "CONST" goto endif78
    return true
  endif78:
    if tb != "CONST" goto endif79
    return false
  endif79:
    t7 = a < b
    return t7
endfunc

func MiniCompilador.ordenar_simbolos(this):
    t0 = this.simbolos
    param t0
    n = call len, 1
    i = 0
  for80:
    if i >= n goto endfor82
    j = 0
  for83:
    t1 = n - 1
    t2 = t1 - i
    if j >= t2 goto endfor85
    t3 = j + 1
    param t3
    param j
    t4 = callm this.simbolo_menor, 2
    ifFalse t4 goto endif86
    t5 = this.simbolos
    troca = t5[j]
    t6 = this.simbolos
    t7 = this.simbolos
    t8 = j + 1
    t9 = t7[t8]
    t6[j] = t9
    t10 = this.simbolos
    t11 = j + 1
    t10[t11] = troca
    t12 = this.tipos_simbolos
    troca_tipo = t12[j]
    t13 = this.tipos_simbolos
    t14 = this.tipos_simbolos
    t15 = j + 1
    t16 = t14[t15]
    t13[j] = t16
    t17 = this.tipos_simbolos
    t18 = j + 1
    t17[t18] = troca_tipo
  endif86:
  forstep84:
    j = j + 1
    goto for83
  endfor85:
  forstep81:
    i = i + 1
    goto for80
  endfor82:
    return
endfunc

func MiniCompilador.imprimir_simbolos(this):
    callm this.ordenar_simbolos, 0
    i = 0
  for87:
    t0 = this.simbolos
    param t0
    t1 = call len, 1
    if i >= t1 goto endfor89
    t2 = this.simbolos
    t3 = t2[i]
    t4 = "🔹 " + t3
    t5 = t4 + " → "
    t6 = this.tipos_simbolos
    t7 = t6[i]
    t8 = t5 + t7
    print t8
  forstep88:
    i = i + 1
    goto for87
  endfor89:
    return
endfunc

func MiniCompilador.avaliar(this, node):
    t0 = node.valor
    param t0
    t1 = call eh_operador, 1
    if t1 goto endif90
    t2 = node.valor
    param t2
    t3 = call eh_numero, 1
    ifFalse t3 goto endif91
    t4 = node.valor
    param t4
    t5 = call to_number, 1
    return t5
  endif91:
    t6 = node.valor
    t7 = "⚠️ Variável '" + t6
    t8 = t7 + "' não tem valor atribuído. Usando 0."
    print t8
    return 0
  endif90:
    t9 = node.esquerda
    param t9
    esq = callm this.avaliar, 1
    t10 = node.direita
    param t10
    dir = callm this.avaliar, 1
    t11 = node.valor
    if t11 != "+" goto endif92
    t12 = esq + dir
    return t12
  endif92:
    t13 = node.valor
    if t13 != "-" goto endif93
    t14 = esq - dir
    return t14
  endif93:
    t15 = node.valor
    if t15 != "*" goto endif94
    t16 = esq * dir
    return t16
  endif94:
    if dir != 0 goto endif95
    this.divisao_por_zero = true
    return 0
  endif95:
    t17 = esq / dir
    return t17
endfunc

func contem(lista, item):
    t0 = lista
    t1 = size t0
    t2 = 0
  foreach96:
    if t2 >= t1 goto endforeach98
    x = t0[t2]
    if x != item goto endif99
    return true
  endif99:
  foreachstep97:
    t2 = t2 + 1
    goto foreach96
  endforeach98:
    return false
endfunc

func main():
    entrada = input "Digite uma expressão infixada: "
    param entrada
    tokens = call analisar, 1
    print "\n🔍 Tokens gerados pelo analisador léxico:"
    lexemas = new_list
    t0 = tokens
    t1 = size t0
    t2 = 0
  foreach100:
    if t2 >= t1 goto endforeach102
    t = t0[t2]
    callm t.mostrar, 0
    t3 = t.lexema
    append lexemas, t3
  foreachstep101:
    t2 = t2 + 1
    goto foreach100
  endforeach102:
    compilador = new MiniCompilador
    param compilador
    call MiniCompilador.__attrs, 1
    param compilador
    param lexemas
    call MiniCompilador.init, 2
    raiz = callm compilador.parse_expr, 0
    t4 = compilador.pos
    param lexemas
    t5 = call len, 1
    if t4 >= t5 goto endif103
    t6 = compilador.erro
    if t6 goto endif103
    compilador.erro = true
    t7 = compilador.pos
    t8 = lexemas[t7]
    t9 = "❌ Erro de sintaxe: símbolos sobrando depois da expressão: '" + t8
    t10 = t9 + "'"
    print t10
  endif103:
    t11 = compilador.erro
    ifFalse t11 goto else104
    print "\n🚫 Compilação interrompida por erro de sintaxe."
    goto endif105
  else104:
    print "\n🌳 Árvore Sintática Abstrata (AST):"
    param raiz
    param 0
    callm compilador.imprimir_ast, 2
    print "\n📦 Código de Três Endereços (TAC):"
    param raiz
    callm compilador.gerar_tac, 1
    print "\n⚙️ Assembly ARMv7 (CPUlator):"
    param ".global _start"
    callm compilador.emitir, 1
    param ".text"
    callm compilador.emitir, 1
    param "_start:"
    callm compilador.emitir, 1
    param raiz
    callm compilador.gerar_assembly, 1
    param "    b .    @ loop infinito para parar o programa"
    callm compilador.emitir, 1
    print "\n📚 Tabela de Símbolos:"
    callm compilador.imprimir_simbolos, 0
    print "\n🧮 Resultado final da expressão:"
    param raiz
    resultado = callm compilador.avaliar, 1
    t12 = compilador.divisao_por_zero
    ifFalse t12 goto else106
    print "➡️  NaN (divisão por zero)"
    goto endif107
  else106:
    param resultado
    t13 = call formatar_double, 1
    t14 = "➡️  " + t13
    print t14
  endif107:
    t15 = compilador.asm
    param "Codigo-Assembly-ARMV7.arm"
    param t15
    call write_file, 2
    print "\n💾 Assembly salvo em Codigo-Assembly-ARMV7.arm"
  endif105:
    return
endfunc
