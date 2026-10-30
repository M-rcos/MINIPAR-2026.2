// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----
static mp::Value v_categorias;
static mp::Value v_recomendacoes;
static mp::Value v_recomendador;
static mp::Value v_usuario;

// ---- protótipos ----
mp::Value fn_contem(mp::Value v_lista, mp::Value v_item);
mp::Value fn_Produto_D___attrs(mp::Value self);
mp::Value fn_Produto_D_init(mp::Value self, mp::Value v_n);
mp::Value fn_Categoria_D___attrs(mp::Value self);
mp::Value fn_Categoria_D_init(mp::Value self, mp::Value v_n, mp::Value v_lista_produtos);
mp::Value fn_Usuario_D___attrs(mp::Value self);
mp::Value fn_Usuario_D_init(mp::Value self, mp::Value v_historico);
mp::Value fn_Usuario_D_codificar_historico(mp::Value self, mp::Value v_todos_produtos);
mp::Value fn_RedeNeural_D___attrs(mp::Value self);
mp::Value fn_RedeNeural_D_init(mp::Value self, mp::Value v_input_size, mp::Value v_hidden_size, mp::Value v_output_size);
mp::Value fn_RedeNeural_D_relu(mp::Value self, mp::Value v_x);
mp::Value fn_RedeNeural_D_sigmoid(mp::Value self, mp::Value v_x);
mp::Value fn_RedeNeural_D_forward(mp::Value self, mp::Value v_X);
mp::Value fn_Recomendador_D___attrs(mp::Value self);
mp::Value fn_Recomendador_D_init(mp::Value self, mp::Value v_u, mp::Value v_cats);
mp::Value fn_Recomendador_D_recomendar(mp::Value self);
mp::Value fn_main();

mp::Value fn_contem(mp::Value v_lista, mp::Value v_item) {
    // contem
    mp::Value t0, t1, t2, v_x;
    t0 = v_lista;
    t1 = mp::size_of(t0);
    t2 = mp::Value(0.0);
    L_foreach1: ;
    if (mp::ge(t2, t1)) goto L_endforeach3;
    v_x = mp::get_index(t0, t2);
    if (mp::ne(v_x, v_item)) goto L_endif4;
    return mp::Value(true);
    L_endif4: ;
    t2 = mp::add(t2, mp::Value(1.0));
    goto L_foreach1;
    L_endforeach3: ;
    return mp::Value(false);
}

mp::Value fn_Produto_D___attrs(mp::Value self) {
    // Produto.__attrs
    (void)self;
    mp::set_member(self, "nome", mp::Value(std::string("", 0)));
    return mp::Value();
}

mp::Value fn_Produto_D_init(mp::Value self, mp::Value v_n) {
    // Produto.init
    (void)self;
    mp::set_member(self, "nome", v_n);
    return mp::Value();
}

mp::Value fn_Categoria_D___attrs(mp::Value self) {
    // Categoria.__attrs
    mp::Value t0;
    (void)self;
    mp::set_member(self, "nome", mp::Value(std::string("", 0)));
    t0 = mp::new_list();
    mp::set_member(self, "produtos", t0);
    return mp::Value();
}

mp::Value fn_Categoria_D_init(mp::Value self, mp::Value v_n, mp::Value v_lista_produtos) {
    // Categoria.init
    mp::Value t0, t1, t2, t3, t4, v_p;
    (void)self;
    mp::set_member(self, "nome", v_n);
    t0 = v_lista_produtos;
    t1 = mp::size_of(t0);
    t2 = mp::Value(0.0);
    L_foreach5: ;
    if (mp::ge(t2, t1)) goto L_endforeach7;
    v_p = mp::get_index(t0, t2);
    t3 = mp::get_member(self, "produtos");
    t4 = mp::new_obj("Produto");
    fn_Produto_D___attrs(t4);
    fn_Produto_D_init(t4, v_p);
    mp::append(t3, t4);
    t2 = mp::add(t2, mp::Value(1.0));
    goto L_foreach5;
    L_endforeach7: ;
    return mp::Value();
}

mp::Value fn_Usuario_D___attrs(mp::Value self) {
    // Usuario.__attrs
    mp::Value t0;
    (void)self;
    t0 = mp::new_list();
    mp::set_member(self, "historico_compras", t0);
    return mp::Value();
}

mp::Value fn_Usuario_D_init(mp::Value self, mp::Value v_historico) {
    // Usuario.init
    (void)self;
    mp::set_member(self, "historico_compras", v_historico);
    return mp::Value();
}

mp::Value fn_Usuario_D_codificar_historico(mp::Value self, mp::Value v_todos_produtos) {
    // Usuario.codificar_historico
    mp::Value t0, t1, t2, t3, t4, v_codificacao, v_produto;
    (void)self;
    v_codificacao = mp::new_list();
    t0 = v_todos_produtos;
    t1 = mp::size_of(t0);
    t2 = mp::Value(0.0);
    L_foreach8: ;
    if (mp::ge(t2, t1)) goto L_endforeach10;
    v_produto = mp::get_index(t0, t2);
    t3 = mp::get_member(self, "historico_compras");
    t4 = fn_contem(t3, v_produto);
    if (!(t4).truthy()) goto L_else11;
    mp::append(v_codificacao, mp::Value(1.0));
    goto L_endif12;
    L_else11: ;
    mp::append(v_codificacao, mp::Value(0.0));
    L_endif12: ;
    t2 = mp::add(t2, mp::Value(1.0));
    goto L_foreach8;
    L_endforeach10: ;
    return v_codificacao;
}

mp::Value fn_RedeNeural_D___attrs(mp::Value self) {
    // RedeNeural.__attrs
    mp::Value t0, t1;
    (void)self;
    mp::set_member(self, "W1", mp::Value());
    t0 = mp::new_list();
    mp::set_member(self, "b1", t0);
    mp::set_member(self, "W2", mp::Value());
    t1 = mp::new_list();
    mp::set_member(self, "b2", t1);
    return mp::Value();
}

mp::Value fn_RedeNeural_D_init(mp::Value self, mp::Value v_input_size, mp::Value v_hidden_size, mp::Value v_output_size) {
    // RedeNeural.init
    mp::Value t0, t1, t2, t3, v_i, v_i_1;
    (void)self;
    t0 = mp::new_matrix(v_input_size, v_hidden_size, mp::Value(0.5));
    mp::set_member(self, "W1", t0);
    v_i = mp::Value(0.0);
    L_for13: ;
    if (mp::ge(v_i, v_hidden_size)) goto L_endfor15;
    t1 = mp::get_member(self, "b1");
    mp::append(t1, mp::Value(0.5));
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for13;
    L_endfor15: ;
    t2 = mp::new_matrix(v_hidden_size, v_output_size, mp::Value(0.5));
    mp::set_member(self, "W2", t2);
    v_i_1 = mp::Value(0.0);
    L_for16: ;
    if (mp::ge(v_i_1, v_output_size)) goto L_endfor18;
    t3 = mp::get_member(self, "b2");
    mp::append(t3, mp::Value(0.5));
    v_i_1 = mp::add(v_i_1, mp::Value(1.0));
    goto L_for16;
    L_endfor18: ;
    return mp::Value();
}

mp::Value fn_RedeNeural_D_relu(mp::Value self, mp::Value v_x) {
    // RedeNeural.relu
    mp::Value t0, t1, t2, t3, v_r, v_v;
    (void)self;
    v_r = mp::new_list();
    t0 = v_x;
    t1 = mp::size_of(t0);
    t2 = mp::Value(0.0);
    L_foreach19: ;
    if (mp::ge(t2, t1)) goto L_endforeach21;
    v_v = mp::get_index(t0, t2);
    t3 = mp::bi_max(mp::Value(0.0), v_v);
    mp::append(v_r, t3);
    t2 = mp::add(t2, mp::Value(1.0));
    goto L_foreach19;
    L_endforeach21: ;
    return v_r;
}

mp::Value fn_RedeNeural_D_sigmoid(mp::Value self, mp::Value v_x) {
    // RedeNeural.sigmoid
    mp::Value t0, t1, t2, t3, t4, t5, t6, v_r;
    mp::Value v_v;
    (void)self;
    v_r = mp::new_list();
    t0 = v_x;
    t1 = mp::size_of(t0);
    t2 = mp::Value(0.0);
    L_foreach22: ;
    if (mp::ge(t2, t1)) goto L_endforeach24;
    v_v = mp::get_index(t0, t2);
    t3 = mp::neg(v_v);
    t4 = mp::bi_exp(t3);
    t5 = mp::add(mp::Value(1.0), t4);
    t6 = mp::div(mp::Value(1.0), t5);
    mp::append(v_r, t6);
    t2 = mp::add(t2, mp::Value(1.0));
    goto L_foreach22;
    L_endforeach24: ;
    return v_r;
}

mp::Value fn_RedeNeural_D_forward(mp::Value self, mp::Value v_X) {
    // RedeNeural.forward
    mp::Value t0, t1, t10, t11, t12, t13, t14, t15;
    mp::Value t16, t17, t18, t19, t2, t20, t21, t22;
    mp::Value t3, t4, t5, t6, t7, t8, t9, v_A1;
    mp::Value v_Z1, v_Z2, v_i, v_i_1, v_j, v_j_1, v_soma, v_soma2;
    (void)self;
    v_Z1 = mp::new_list();
    v_i = mp::Value(0.0);
    L_for25: ;
    t0 = mp::get_member(self, "b1");
    t1 = mp::bi_len(t0);
    if (mp::ge(v_i, t1)) goto L_endfor27;
    v_soma = mp::Value(0.0);
    v_j = mp::Value(0.0);
    L_for28: ;
    t2 = mp::bi_len(v_X);
    if (mp::ge(v_j, t2)) goto L_endfor30;
    t3 = mp::get_index(v_X, v_j);
    t4 = mp::get_member(self, "W1");
    t5 = mp::get_index(t4, v_j);
    t6 = mp::get_index(t5, v_i);
    t7 = mp::mul(t3, t6);
    v_soma = mp::add(v_soma, t7);
    v_j = mp::add(v_j, mp::Value(1.0));
    goto L_for28;
    L_endfor30: ;
    t8 = mp::get_member(self, "b1");
    t9 = mp::get_index(t8, v_i);
    t10 = mp::add(v_soma, t9);
    mp::append(v_Z1, t10);
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for25;
    L_endfor27: ;
    v_A1 = mp::call_method(self, "relu", {v_Z1});
    v_Z2 = mp::new_list();
    v_i_1 = mp::Value(0.0);
    L_for31: ;
    t11 = mp::get_member(self, "b2");
    t12 = mp::bi_len(t11);
    if (mp::ge(v_i_1, t12)) goto L_endfor33;
    v_soma2 = mp::Value(0.0);
    v_j_1 = mp::Value(0.0);
    L_for34: ;
    t13 = mp::bi_len(v_A1);
    if (mp::ge(v_j_1, t13)) goto L_endfor36;
    t14 = mp::get_index(v_A1, v_j_1);
    t15 = mp::get_member(self, "W2");
    t16 = mp::get_index(t15, v_j_1);
    t17 = mp::get_index(t16, v_i_1);
    t18 = mp::mul(t14, t17);
    v_soma2 = mp::add(v_soma2, t18);
    v_j_1 = mp::add(v_j_1, mp::Value(1.0));
    goto L_for34;
    L_endfor36: ;
    t19 = mp::get_member(self, "b2");
    t20 = mp::get_index(t19, v_i_1);
    t21 = mp::add(v_soma2, t20);
    mp::append(v_Z2, t21);
    v_i_1 = mp::add(v_i_1, mp::Value(1.0));
    goto L_for31;
    L_endfor33: ;
    t22 = mp::call_method(self, "sigmoid", {v_Z2});
    return t22;
}

mp::Value fn_Recomendador_D___attrs(mp::Value self) {
    // Recomendador.__attrs
    mp::Value t0, t1;
    (void)self;
    mp::set_member(self, "usuario", mp::Value());
    t0 = mp::new_list();
    mp::set_member(self, "categorias", t0);
    t1 = mp::new_list();
    mp::set_member(self, "todos_produtos", t1);
    return mp::Value();
}

mp::Value fn_Recomendador_D_init(mp::Value self, mp::Value v_u, mp::Value v_cats) {
    // Recomendador.init
    mp::Value t0, t1, t2, t3, t4, t5, t6, t7;
    mp::Value v_c, v_p;
    (void)self;
    mp::set_member(self, "usuario", v_u);
    mp::set_member(self, "categorias", v_cats);
    t0 = v_cats;
    t1 = mp::size_of(t0);
    t2 = mp::Value(0.0);
    L_foreach37: ;
    if (mp::ge(t2, t1)) goto L_endforeach39;
    v_c = mp::get_index(t0, t2);
    t3 = mp::get_member(v_c, "produtos");
    t4 = mp::size_of(t3);
    t5 = mp::Value(0.0);
    L_foreach40: ;
    if (mp::ge(t5, t4)) goto L_endforeach42;
    v_p = mp::get_index(t3, t5);
    t6 = mp::get_member(self, "todos_produtos");
    t7 = mp::get_member(v_p, "nome");
    mp::append(t6, t7);
    t5 = mp::add(t5, mp::Value(1.0));
    goto L_foreach40;
    L_endforeach42: ;
    t2 = mp::add(t2, mp::Value(1.0));
    goto L_foreach37;
    L_endforeach39: ;
    return mp::Value();
}

mp::Value fn_Recomendador_D_recomendar(mp::Value self) {
    // Recomendador.recomendar
    mp::Value t0, t1, t10, t2, t3, t4, t5, t6;
    mp::Value t7, t8, t9, v_entrada_codificada, v_hidden_size, v_i, v_input_size, v_output_size;
    mp::Value v_recomendacoes_1, v_rede, v_saida;
    (void)self;
    t0 = mp::get_member(self, "usuario");
    t1 = mp::get_member(self, "todos_produtos");
    v_entrada_codificada = mp::call_method(t0, "codificar_historico", {t1});
    v_input_size = mp::bi_len(v_entrada_codificada);
    v_hidden_size = mp::Value(10.0);
    v_output_size = mp::bi_len(v_entrada_codificada);
    v_rede = mp::new_obj("RedeNeural");
    fn_RedeNeural_D___attrs(v_rede);
    fn_RedeNeural_D_init(v_rede, v_input_size, v_hidden_size, v_output_size);
    v_saida = mp::call_method(v_rede, "forward", {v_entrada_codificada});
    v_recomendacoes_1 = mp::new_list();
    v_i = mp::Value(0.0);
    L_for43: ;
    t2 = mp::bi_len(v_saida);
    if (mp::ge(v_i, t2)) goto L_endfor45;
    t3 = mp::get_index(v_saida, v_i);
    if (mp::le(t3, mp::Value(0.5))) goto L_endif46;
    t4 = mp::get_member(self, "usuario");
    t5 = mp::get_member(t4, "historico_compras");
    t6 = mp::get_member(self, "todos_produtos");
    t7 = mp::get_index(t6, v_i);
    t8 = fn_contem(t5, t7);
    if ((t8).truthy()) goto L_endif46;
    t9 = mp::get_member(self, "todos_produtos");
    t10 = mp::get_index(t9, v_i);
    mp::append(v_recomendacoes_1, t10);
    L_endif46: ;
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for43;
    L_endfor45: ;
    return v_recomendacoes_1;
}

mp::Value fn_main() {
    // main
    mp::Value t0, t1, t10, t11, t2, t3, t4, t5;
    mp::Value t6, t7, t8, t9, v_produto;
    v_categorias = mp::new_list();
    t0 = mp::new_list();
    mp::append(t0, mp::Value(std::string("Smartphone", 10)));
    mp::append(t0, mp::Value(std::string("Laptop", 6)));
    mp::append(t0, mp::Value(std::string("Tablet", 6)));
    mp::append(t0, mp::Value(std::string("Fones de ouvido", 15)));
    t1 = mp::new_obj("Categoria");
    fn_Categoria_D___attrs(t1);
    fn_Categoria_D_init(t1, mp::Value(std::string("Eletr\303\264nicos", 12)), t0);
    mp::append(v_categorias, t1);
    t2 = mp::new_list();
    mp::append(t2, mp::Value(std::string("Camisa", 6)));
    mp::append(t2, mp::Value(std::string("Jeans", 5)));
    mp::append(t2, mp::Value(std::string("Jaqueta", 7)));
    mp::append(t2, mp::Value(std::string("Sapatos", 7)));
    t3 = mp::new_obj("Categoria");
    fn_Categoria_D___attrs(t3);
    fn_Categoria_D_init(t3, mp::Value(std::string("Roupas", 6)), t2);
    mp::append(v_categorias, t3);
    t4 = mp::new_list();
    mp::append(t4, mp::Value(std::string("Geladeira", 9)));
    mp::append(t4, mp::Value(std::string("Micro-ondas", 11)));
    mp::append(t4, mp::Value(std::string("M\303\241quina de lavar", 17)));
    mp::append(t4, mp::Value(std::string("Ar condicionado", 15)));
    t5 = mp::new_obj("Categoria");
    fn_Categoria_D___attrs(t5);
    fn_Categoria_D_init(t5, mp::Value(std::string("Eletrodom\303\251sticos", 17)), t4);
    mp::append(v_categorias, t5);
    t6 = mp::new_list();
    mp::append(t6, mp::Value(std::string("Fic\303\247\303\243o", 8)));
    mp::append(t6, mp::Value(std::string("N\303\243o-fic\303\247\303\243o", 13)));
    mp::append(t6, mp::Value(std::string("Fic\303\247\303\243o cient\303\255fica", 20)));
    mp::append(t6, mp::Value(std::string("Fantasia", 8)));
    t7 = mp::new_obj("Categoria");
    fn_Categoria_D___attrs(t7);
    fn_Categoria_D_init(t7, mp::Value(std::string("Livros", 6)), t6);
    mp::append(v_categorias, t7);
    t8 = mp::new_list();
    mp::append(t8, mp::Value(std::string("Smartphone", 10)));
    mp::append(t8, mp::Value(std::string("Jeans", 5)));
    mp::append(t8, mp::Value(std::string("Micro-ondas", 11)));
    mp::append(t8, mp::Value(std::string("Fic\303\247\303\243o", 8)));
    v_usuario = mp::new_obj("Usuario");
    fn_Usuario_D___attrs(v_usuario);
    fn_Usuario_D_init(v_usuario, t8);
    v_recomendador = mp::new_obj("Recomendador");
    fn_Recomendador_D___attrs(v_recomendador);
    fn_Recomendador_D_init(v_recomendador, v_usuario, v_categorias);
    v_recomendacoes = mp::call_method(v_recomendador, "recomendar", {});
    mp::print({mp::Value(std::string("Produtos recomendados para voc\303\252:", 33))});
    t9 = v_recomendacoes;
    t10 = mp::size_of(t9);
    t11 = mp::Value(0.0);
    L_foreach47: ;
    if (mp::ge(t11, t10)) goto L_endforeach49;
    v_produto = mp::get_index(t9, t11);
    mp::print({v_produto});
    t11 = mp::add(t11, mp::Value(1.0));
    goto L_foreach47;
    L_endforeach49: ;
    return mp::Value();
}

static void register_classes() {
    mp::register_class("Produto", "", {
        {"init", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Produto.init", a, 1); return fn_Produto_D_init(self, a[0]); }},
    });
    mp::register_class("Categoria", "", {
        {"init", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Categoria.init", a, 2); return fn_Categoria_D_init(self, a[0], a[1]); }},
    });
    mp::register_class("Usuario", "", {
        {"init", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Usuario.init", a, 1); return fn_Usuario_D_init(self, a[0]); }},
        {"codificar_historico", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Usuario.codificar_historico", a, 1); return fn_Usuario_D_codificar_historico(self, a[0]); }},
    });
    mp::register_class("RedeNeural", "", {
        {"init", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("RedeNeural.init", a, 3); return fn_RedeNeural_D_init(self, a[0], a[1], a[2]); }},
        {"relu", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("RedeNeural.relu", a, 1); return fn_RedeNeural_D_relu(self, a[0]); }},
        {"sigmoid", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("RedeNeural.sigmoid", a, 1); return fn_RedeNeural_D_sigmoid(self, a[0]); }},
        {"forward", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("RedeNeural.forward", a, 1); return fn_RedeNeural_D_forward(self, a[0]); }},
    });
    mp::register_class("Recomendador", "", {
        {"init", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Recomendador.init", a, 2); return fn_Recomendador_D_init(self, a[0], a[1]); }},
        {"recomendar", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Recomendador.recomendar", a, 0); return fn_Recomendador_D_recomendar(self); }},
    });
}

int main() {
    return mp::run_program([]() {
        register_classes();
    }, []() { fn_main(); });
}
