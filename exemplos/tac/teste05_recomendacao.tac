class Produto:
    field nome
    method init
endclass

class Categoria:
    field nome
    field produtos
    method init
endclass

class Usuario:
    field historico_compras
    method init
    method codificar_historico
endclass

class RedeNeural:
    field W1
    field b1
    field W2
    field b2
    method init
    method relu
    method sigmoid
    method forward
endclass

class Recomendador:
    field usuario
    field categorias
    field todos_produtos
    method init
    method recomendar
endclass

global categorias
global usuario
global recomendador
global recomendacoes

func contem(lista, item):
    t0 = lista
    t1 = size t0
    t2 = 0
  foreach1:
    if t2 >= t1 goto endforeach3
    x = t0[t2]
    if x != item goto endif4
    return true
  endif4:
  foreachstep2:
    t2 = t2 + 1
    goto foreach1
  endforeach3:
    return false
endfunc

func Produto.__attrs(this):
    this.nome = ""
    return
endfunc

func Produto.init(this, n):
    this.nome = n
    return
endfunc

func Categoria.__attrs(this):
    this.nome = ""
    t0 = new_list
    this.produtos = t0
    return
endfunc

func Categoria.init(this, n, lista_produtos):
    this.nome = n
    t0 = lista_produtos
    t1 = size t0
    t2 = 0
  foreach5:
    if t2 >= t1 goto endforeach7
    p = t0[t2]
    t3 = this.produtos
    t4 = new Produto
    param t4
    call Produto.__attrs, 1
    param t4
    param p
    call Produto.init, 2
    append t3, t4
  foreachstep6:
    t2 = t2 + 1
    goto foreach5
  endforeach7:
    return
endfunc

func Usuario.__attrs(this):
    t0 = new_list
    this.historico_compras = t0
    return
endfunc

func Usuario.init(this, historico):
    this.historico_compras = historico
    return
endfunc

func Usuario.codificar_historico(this, todos_produtos):
    codificacao = new_list
    t0 = todos_produtos
    t1 = size t0
    t2 = 0
  foreach8:
    if t2 >= t1 goto endforeach10
    produto = t0[t2]
    t3 = this.historico_compras
    param t3
    param produto
    t4 = call contem, 2
    ifFalse t4 goto else11
    append codificacao, 1
    goto endif12
  else11:
    append codificacao, 0
  endif12:
  foreachstep9:
    t2 = t2 + 1
    goto foreach8
  endforeach10:
    return codificacao
endfunc

func RedeNeural.__attrs(this):
    this.W1 = null
    t0 = new_list
    this.b1 = t0
    this.W2 = null
    t1 = new_list
    this.b2 = t1
    return
endfunc

func RedeNeural.init(this, input_size, hidden_size, output_size):
    t0 = new_matrix input_size, hidden_size, 0.5
    this.W1 = t0
    i = 0
  for13:
    if i >= hidden_size goto endfor15
    t1 = this.b1
    append t1, 0.5
  forstep14:
    i = i + 1
    goto for13
  endfor15:
    t2 = new_matrix hidden_size, output_size, 0.5
    this.W2 = t2
    i_1 = 0
  for16:
    if i_1 >= output_size goto endfor18
    t3 = this.b2
    append t3, 0.5
  forstep17:
    i_1 = i_1 + 1
    goto for16
  endfor18:
    return
endfunc

func RedeNeural.relu(this, x):
    r = new_list
    t0 = x
    t1 = size t0
    t2 = 0
  foreach19:
    if t2 >= t1 goto endforeach21
    v = t0[t2]
    param 0
    param v
    t3 = call max, 2
    append r, t3
  foreachstep20:
    t2 = t2 + 1
    goto foreach19
  endforeach21:
    return r
endfunc

func RedeNeural.sigmoid(this, x):
    r = new_list
    t0 = x
    t1 = size t0
    t2 = 0
  foreach22:
    if t2 >= t1 goto endforeach24
    v = t0[t2]
    t3 = -v
    param t3
    t4 = call exp, 1
    t5 = 1 + t4
    t6 = 1 / t5
    append r, t6
  foreachstep23:
    t2 = t2 + 1
    goto foreach22
  endforeach24:
    return r
endfunc

func RedeNeural.forward(this, X):
    Z1 = new_list
    i = 0
  for25:
    t0 = this.b1
    param t0
    t1 = call len, 1
    if i >= t1 goto endfor27
    soma = 0
    j = 0
  for28:
    param X
    t2 = call len, 1
    if j >= t2 goto endfor30
    t3 = X[j]
    t4 = this.W1
    t5 = t4[j]
    t6 = t5[i]
    t7 = t3 * t6
    soma = soma + t7
  forstep29:
    j = j + 1
    goto for28
  endfor30:
    t8 = this.b1
    t9 = t8[i]
    t10 = soma + t9
    append Z1, t10
  forstep26:
    i = i + 1
    goto for25
  endfor27:
    param Z1
    A1 = callm this.relu, 1
    Z2 = new_list
    i_1 = 0
  for31:
    t11 = this.b2
    param t11
    t12 = call len, 1
    if i_1 >= t12 goto endfor33
    soma2 = 0
    j_1 = 0
  for34:
    param A1
    t13 = call len, 1
    if j_1 >= t13 goto endfor36
    t14 = A1[j_1]
    t15 = this.W2
    t16 = t15[j_1]
    t17 = t16[i_1]
    t18 = t14 * t17
    soma2 = soma2 + t18
  forstep35:
    j_1 = j_1 + 1
    goto for34
  endfor36:
    t19 = this.b2
    t20 = t19[i_1]
    t21 = soma2 + t20
    append Z2, t21
  forstep32:
    i_1 = i_1 + 1
    goto for31
  endfor33:
    param Z2
    t22 = callm this.sigmoid, 1
    return t22
endfunc

func Recomendador.__attrs(this):
    this.usuario = null
    t0 = new_list
    this.categorias = t0
    t1 = new_list
    this.todos_produtos = t1
    return
endfunc

func Recomendador.init(this, u, cats):
    this.usuario = u
    this.categorias = cats
    t0 = cats
    t1 = size t0
    t2 = 0
  foreach37:
    if t2 >= t1 goto endforeach39
    c = t0[t2]
    t3 = c.produtos
    t4 = size t3
    t5 = 0
  foreach40:
    if t5 >= t4 goto endforeach42
    p = t3[t5]
    t6 = this.todos_produtos
    t7 = p.nome
    append t6, t7
  foreachstep41:
    t5 = t5 + 1
    goto foreach40
  endforeach42:
  foreachstep38:
    t2 = t2 + 1
    goto foreach37
  endforeach39:
    return
endfunc

func Recomendador.recomendar(this):
    t0 = this.usuario
    t1 = this.todos_produtos
    param t1
    entrada_codificada = callm t0.codificar_historico, 1
    param entrada_codificada
    input_size = call len, 1
    hidden_size = 10
    param entrada_codificada
    output_size = call len, 1
    rede = new RedeNeural
    param rede
    call RedeNeural.__attrs, 1
    param rede
    param input_size
    param hidden_size
    param output_size
    call RedeNeural.init, 4
    param entrada_codificada
    saida = callm rede.forward, 1
    recomendacoes_1 = new_list
    i = 0
  for43:
    param saida
    t2 = call len, 1
    if i >= t2 goto endfor45
    t3 = saida[i]
    if t3 <= 0.5 goto endif46
    t4 = this.usuario
    t5 = t4.historico_compras
    t6 = this.todos_produtos
    t7 = t6[i]
    param t5
    param t7
    t8 = call contem, 2
    if t8 goto endif46
    t9 = this.todos_produtos
    t10 = t9[i]
    append recomendacoes_1, t10
  endif46:
  forstep44:
    i = i + 1
    goto for43
  endfor45:
    return recomendacoes_1
endfunc

func main():
    categorias = new_list
    t0 = new_list
    append t0, "Smartphone"
    append t0, "Laptop"
    append t0, "Tablet"
    append t0, "Fones de ouvido"
    t1 = new Categoria
    param t1
    call Categoria.__attrs, 1
    param t1
    param "Eletrônicos"
    param t0
    call Categoria.init, 3
    append categorias, t1
    t2 = new_list
    append t2, "Camisa"
    append t2, "Jeans"
    append t2, "Jaqueta"
    append t2, "Sapatos"
    t3 = new Categoria
    param t3
    call Categoria.__attrs, 1
    param t3
    param "Roupas"
    param t2
    call Categoria.init, 3
    append categorias, t3
    t4 = new_list
    append t4, "Geladeira"
    append t4, "Micro-ondas"
    append t4, "Máquina de lavar"
    append t4, "Ar condicionado"
    t5 = new Categoria
    param t5
    call Categoria.__attrs, 1
    param t5
    param "Eletrodomésticos"
    param t4
    call Categoria.init, 3
    append categorias, t5
    t6 = new_list
    append t6, "Ficção"
    append t6, "Não-ficção"
    append t6, "Ficção científica"
    append t6, "Fantasia"
    t7 = new Categoria
    param t7
    call Categoria.__attrs, 1
    param t7
    param "Livros"
    param t6
    call Categoria.init, 3
    append categorias, t7
    t8 = new_list
    append t8, "Smartphone"
    append t8, "Jeans"
    append t8, "Micro-ondas"
    append t8, "Ficção"
    usuario = new Usuario
    param usuario
    call Usuario.__attrs, 1
    param usuario
    param t8
    call Usuario.init, 2
    recomendador = new Recomendador
    param recomendador
    call Recomendador.__attrs, 1
    param recomendador
    param usuario
    param categorias
    call Recomendador.init, 3
    recomendacoes = callm recomendador.recomendar, 0
    print "Produtos recomendados para você:"
    t9 = recomendacoes
    t10 = size t9
    t11 = 0
  foreach47:
    if t11 >= t10 goto endforeach49
    produto = t9[t11]
    print produto
  foreachstep48:
    t11 = t11 + 1
    goto foreach47
  endforeach49:
    return
endfunc
