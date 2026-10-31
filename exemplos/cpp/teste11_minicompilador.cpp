// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----
static mp::Value v_compilador;
static mp::Value v_entrada;
static mp::Value v_lexemas;
static mp::Value v_raiz;
static mp::Value v_tokens;

// ---- protótipos ----
mp::Value fn_eh_operador(mp::Value v_s);
mp::Value fn_eh_espaco(mp::Value v_c);
mp::Value fn_eh_letra(mp::Value v_c);
mp::Value fn_so_digitos(mp::Value v_s);
mp::Value fn_eh_numero(mp::Value v_s);
mp::Value fn_espacos(mp::Value v_n);
mp::Value fn_pad_direita(mp::Value v_s, mp::Value v_n);
mp::Value fn_formatar_double(mp::Value v_x);
mp::Value fn_Token_D___attrs(mp::Value self);
mp::Value fn_Token_D_init(mp::Value self, mp::Value v_t, mp::Value v_l);
mp::Value fn_Token_D_mostrar(mp::Value self);
mp::Value fn_analisar(mp::Value v_entrada_1);
mp::Value fn_ASTNode_D___attrs(mp::Value self);
mp::Value fn_ASTNode_D_init(mp::Value self, mp::Value v_v);
mp::Value fn_MiniCompilador_D___attrs(mp::Value self);
mp::Value fn_MiniCompilador_D_init(mp::Value self, mp::Value v_lexemas_1);
mp::Value fn_MiniCompilador_D_parse_expr(mp::Value self);
mp::Value fn_MiniCompilador_D_parse_term(mp::Value self);
mp::Value fn_MiniCompilador_D_parse_factor(mp::Value self);
mp::Value fn_MiniCompilador_D_registrar_simbolo(mp::Value self, mp::Value v_token);
mp::Value fn_MiniCompilador_D_imprimir_ast(mp::Value self, mp::Value v_node, mp::Value v_nivel);
mp::Value fn_MiniCompilador_D_formatar(mp::Value self, mp::Value v_node);
mp::Value fn_MiniCompilador_D_gerar_tac(mp::Value self, mp::Value v_node);
mp::Value fn_MiniCompilador_D_emitir(mp::Value self, mp::Value v_linha);
mp::Value fn_MiniCompilador_D_emitir_mov(mp::Value self, mp::Value v_reg, mp::Value v_valor);
mp::Value fn_MiniCompilador_D_gerar_assembly(mp::Value self, mp::Value v_node);
mp::Value fn_MiniCompilador_D_simbolo_menor(mp::Value self, mp::Value v_i, mp::Value v_j);
mp::Value fn_MiniCompilador_D_ordenar_simbolos(mp::Value self);
mp::Value fn_MiniCompilador_D_imprimir_simbolos(mp::Value self);
mp::Value fn_MiniCompilador_D_avaliar(mp::Value self, mp::Value v_node);
mp::Value fn_contem(mp::Value v_lista, mp::Value v_item);
mp::Value fn_main();

mp::Value fn_eh_operador(mp::Value v_s) {
    // eh_operador
    mp::Value t0, t1;
    t0 = mp::Value(true);
    if (mp::eq(v_s, mp::Value(std::string("+", 1)))) goto L_endlogic1;
    if (mp::eq(v_s, mp::Value(std::string("-", 1)))) goto L_endlogic1;
    if (mp::eq(v_s, mp::Value(std::string("*", 1)))) goto L_endlogic1;
    t1 = mp::Value(mp::eq(v_s, mp::Value(std::string("/", 1))));
    t0 = t1;
    L_endlogic1: ;
    return t0;
}

mp::Value fn_eh_espaco(mp::Value v_c) {
    // eh_espaco
    mp::Value t0, t1;
    t0 = mp::Value(true);
    if (mp::eq(v_c, mp::Value(std::string(" ", 1)))) goto L_endlogic2;
    if (mp::eq(v_c, mp::Value(std::string("\t", 1)))) goto L_endlogic2;
    if (mp::eq(v_c, mp::Value(std::string("\r", 1)))) goto L_endlogic2;
    t1 = mp::Value(mp::eq(v_c, mp::Value(std::string("\n", 1))));
    t0 = t1;
    L_endlogic2: ;
    return t0;
}

mp::Value fn_eh_letra(mp::Value v_c) {
    // eh_letra
    mp::Value t0, t1, t2;
    t0 = mp::Value(true);
    t1 = mp::bi_is_alpha(v_c);
    if ((t1).truthy()) goto L_endlogic3;
    t2 = mp::Value(mp::eq(v_c, mp::Value(std::string("_", 1))));
    t0 = t2;
    L_endlogic3: ;
    return t0;
}

mp::Value fn_so_digitos(mp::Value v_s) {
    // so_digitos
    mp::Value t0, t1, t2, t3, v_i;
    t0 = mp::bi_len(v_s);
    if (mp::ne(t0, mp::Value(0.0))) goto L_endif4;
    return mp::Value(false);
    L_endif4: ;
    v_i = mp::Value(0.0);
    L_for5: ;
    t1 = mp::bi_len(v_s);
    if (mp::ge(v_i, t1)) goto L_endfor7;
    t2 = mp::get_index(v_s, v_i);
    t3 = mp::bi_is_digit(t2);
    if ((t3).truthy()) goto L_endif8;
    return mp::Value(false);
    L_endif8: ;
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for5;
    L_endfor7: ;
    return mp::Value(true);
}

mp::Value fn_eh_numero(mp::Value v_s) {
    // eh_numero
    mp::Value t0, t1, t2, t3, t4, t5, t6, t7;
    mp::Value t8, v_partes;
    v_partes = mp::bi_split(v_s, mp::Value(std::string(".", 1)));
    t0 = mp::bi_len(v_partes);
    if (mp::ne(t0, mp::Value(1.0))) goto L_endif9;
    t1 = mp::get_index(v_partes, mp::Value(0.0));
    t2 = fn_so_digitos(t1);
    return t2;
    L_endif9: ;
    t3 = mp::Value(false);
    t4 = mp::bi_len(v_partes);
    if (mp::ne(t4, mp::Value(2.0))) goto L_endlogic10;
    t5 = mp::get_index(v_partes, mp::Value(0.0));
    t6 = fn_so_digitos(t5);
    if (!(t6).truthy()) goto L_endlogic10;
    t7 = mp::get_index(v_partes, mp::Value(1.0));
    t8 = fn_so_digitos(t7);
    t3 = t8;
    L_endlogic10: ;
    return t3;
}

mp::Value fn_espacos(mp::Value v_n) {
    // espacos
    mp::Value v_i, v_s;
    v_s = mp::Value(std::string("", 0));
    v_i = mp::Value(0.0);
    L_for11: ;
    if (mp::ge(v_i, v_n)) goto L_endfor13;
    v_s = mp::add(v_s, mp::Value(std::string("  ", 2)));
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for11;
    L_endfor13: ;
    return v_s;
}

mp::Value fn_pad_direita(mp::Value v_s, mp::Value v_n) {
    // pad_direita
    mp::Value t0, v_r;
    v_r = v_s;
    L_while14: ;
    t0 = mp::bi_len(v_r);
    if (mp::ge(t0, v_n)) goto L_endwhile15;
    v_r = mp::add(v_r, mp::Value(std::string(" ", 1)));
    goto L_while14;
    L_endwhile15: ;
    return v_r;
}

mp::Value fn_formatar_double(mp::Value v_x) {
    // formatar_double
    mp::Value t0, t1, t2;
    t0 = mp::bi_floor(v_x);
    if (mp::ne(v_x, t0)) goto L_endif16;
    t1 = mp::bi_fmt(v_x, mp::Value(1.0));
    return t1;
    L_endif16: ;
    t2 = mp::bi_to_string(v_x);
    return t2;
}

mp::Value fn_Token_D___attrs(mp::Value self) {
    // Token.__attrs
    (void)self;
    mp::set_member(self, "tipo", mp::Value(std::string("", 0)));
    mp::set_member(self, "lexema", mp::Value(std::string("", 0)));
    return mp::Value();
}

mp::Value fn_Token_D_init(mp::Value self, mp::Value v_t, mp::Value v_l) {
    // Token.init
    (void)self;
    mp::set_member(self, "tipo", v_t);
    mp::set_member(self, "lexema", v_l);
    return mp::Value();
}

mp::Value fn_Token_D_mostrar(mp::Value self) {
    // Token.mostrar
    mp::Value t0, t1, t2, t3, t4, t5;
    (void)self;
    t0 = mp::get_member(self, "tipo");
    t1 = mp::add(mp::Value(std::string("[", 1)), t0);
    t2 = mp::add(t1, mp::Value(std::string(": '", 3)));
    t3 = mp::get_member(self, "lexema");
    t4 = mp::add(t2, t3);
    t5 = mp::add(t4, mp::Value(std::string("']", 2)));
    mp::print({t5});
    return mp::Value();
}

mp::Value fn_analisar(mp::Value v_entrada_1) {
    // analisar
    mp::Value t0, t1, t10, t11, t12, t13, t14, t15;
    mp::Value t16, t17, t18, t19, t2, t20, t21, t22;
    mp::Value t23, t24, t25, t3, t4, t5, t6, t7;
    mp::Value t8, t9, v_c, v_i, v_j, v_k, v_n, v_tokens_1;
    v_tokens_1 = mp::new_list();
    v_i = mp::Value(0.0);
    v_n = mp::bi_len(v_entrada_1);
    L_while17: ;
    if (mp::ge(v_i, v_n)) goto L_endwhile18;
    v_c = mp::get_index(v_entrada_1, v_i);
    t0 = fn_eh_espaco(v_c);
    if (!(t0).truthy()) goto L_else19;
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_endif20;
    L_else19: ;
    if (mp::ne(v_c, mp::Value(std::string("#", 1)))) goto L_else21;
    v_i = v_n;
    goto L_endif22;
    L_else21: ;
    t1 = mp::bi_is_digit(v_c);
    if (!(t1).truthy()) goto L_else23;
    v_j = v_i;
    L_while25: ;
    if (mp::ge(v_j, v_n)) goto L_endwhile26;
    t2 = mp::get_index(v_entrada_1, v_j);
    t3 = mp::bi_is_digit(t2);
    if (!(t3).truthy()) goto L_endwhile26;
    v_j = mp::add(v_j, mp::Value(1.0));
    goto L_while25;
    L_endwhile26: ;
    t4 = mp::add(v_j, mp::Value(1.0));
    if (mp::ge(t4, v_n)) goto L_endif27;
    t5 = mp::get_index(v_entrada_1, v_j);
    if (mp::ne(t5, mp::Value(std::string(".", 1)))) goto L_endif27;
    t6 = mp::add(v_j, mp::Value(1.0));
    t7 = mp::get_index(v_entrada_1, t6);
    t8 = mp::bi_is_digit(t7);
    if (!(t8).truthy()) goto L_endif27;
    v_j = mp::add(v_j, mp::Value(1.0));
    L_while28: ;
    if (mp::ge(v_j, v_n)) goto L_endwhile29;
    t9 = mp::get_index(v_entrada_1, v_j);
    t10 = mp::bi_is_digit(t9);
    if (!(t10).truthy()) goto L_endwhile29;
    v_j = mp::add(v_j, mp::Value(1.0));
    goto L_while28;
    L_endwhile29: ;
    L_endif27: ;
    t11 = mp::sub(v_j, v_i);
    t12 = mp::bi_substr(v_entrada_1, v_i, t11);
    t13 = mp::new_obj("Token");
    fn_Token_D___attrs(t13);
    fn_Token_D_init(t13, mp::Value(std::string("NUMERO", 6)), t12);
    mp::append(v_tokens_1, t13);
    v_i = v_j;
    goto L_endif24;
    L_else23: ;
    t14 = fn_eh_letra(v_c);
    if (!(t14).truthy()) goto L_else30;
    v_k = v_i;
    L_while32: ;
    if (mp::ge(v_k, v_n)) goto L_endwhile33;
    t15 = mp::get_index(v_entrada_1, v_k);
    t16 = fn_eh_letra(t15);
    if ((t16).truthy()) goto L_skip34;
    t17 = mp::get_index(v_entrada_1, v_k);
    t18 = mp::bi_is_digit(t17);
    if (!(t18).truthy()) goto L_endwhile33;
    L_skip34: ;
    v_k = mp::add(v_k, mp::Value(1.0));
    goto L_while32;
    L_endwhile33: ;
    t19 = mp::sub(v_k, v_i);
    t20 = mp::bi_substr(v_entrada_1, v_i, t19);
    t21 = mp::new_obj("Token");
    fn_Token_D___attrs(t21);
    fn_Token_D_init(t21, mp::Value(std::string("IDENTIFICADOR", 13)), t20);
    mp::append(v_tokens_1, t21);
    v_i = v_k;
    goto L_endif31;
    L_else30: ;
    t22 = fn_eh_operador(v_c);
    if (!(t22).truthy()) goto L_else35;
    t23 = mp::new_obj("Token");
    fn_Token_D___attrs(t23);
    fn_Token_D_init(t23, mp::Value(std::string("OPERADOR", 8)), v_c);
    mp::append(v_tokens_1, t23);
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_endif36;
    L_else35: ;
    if (mp::ne(v_c, mp::Value(std::string("=", 1)))) goto L_else37;
    t24 = mp::new_obj("Token");
    fn_Token_D___attrs(t24);
    fn_Token_D_init(t24, mp::Value(std::string("ATRIBUICAO", 10)), v_c);
    mp::append(v_tokens_1, t24);
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_endif38;
    L_else37: ;
    if (mp::eq(v_c, mp::Value(std::string("(", 1)))) goto L_skip41;
    if (mp::ne(v_c, mp::Value(std::string(")", 1)))) goto L_else39;
    L_skip41: ;
    t25 = mp::new_obj("Token");
    fn_Token_D___attrs(t25);
    fn_Token_D_init(t25, mp::Value(std::string("PARENTESE", 9)), v_c);
    mp::append(v_tokens_1, t25);
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_endif40;
    L_else39: ;
    v_i = mp::add(v_i, mp::Value(1.0));
    L_endif40: ;
    L_endif38: ;
    L_endif36: ;
    L_endif31: ;
    L_endif24: ;
    L_endif22: ;
    L_endif20: ;
    goto L_while17;
    L_endwhile18: ;
    return v_tokens_1;
}

mp::Value fn_ASTNode_D___attrs(mp::Value self) {
    // ASTNode.__attrs
    (void)self;
    mp::set_member(self, "valor", mp::Value(std::string("", 0)));
    mp::set_member(self, "esquerda", mp::Value());
    mp::set_member(self, "direita", mp::Value());
    return mp::Value();
}

mp::Value fn_ASTNode_D_init(mp::Value self, mp::Value v_v) {
    // ASTNode.init
    (void)self;
    mp::set_member(self, "valor", v_v);
    return mp::Value();
}

mp::Value fn_MiniCompilador_D___attrs(mp::Value self) {
    // MiniCompilador.__attrs
    mp::Value t0, t1, t2;
    (void)self;
    t0 = mp::new_list();
    mp::set_member(self, "tokens", t0);
    mp::set_member(self, "pos", mp::Value(0.0));
    mp::set_member(self, "temp_count", mp::Value(1.0));
    mp::set_member(self, "reg_count", mp::Value(0.0));
    t1 = mp::new_list();
    mp::set_member(self, "simbolos", t1);
    t2 = mp::new_list();
    mp::set_member(self, "tipos_simbolos", t2);
    mp::set_member(self, "erro", mp::Value(false));
    mp::set_member(self, "divisao_por_zero", mp::Value(false));
    mp::set_member(self, "asm", mp::Value(std::string("", 0)));
    return mp::Value();
}

mp::Value fn_MiniCompilador_D_init(mp::Value self, mp::Value v_lexemas_1) {
    // MiniCompilador.init
    (void)self;
    mp::set_member(self, "tokens", v_lexemas_1);
    return mp::Value();
}

mp::Value fn_MiniCompilador_D_parse_expr(mp::Value self) {
    // MiniCompilador.parse_expr
    mp::Value t0, t1, t10, t11, t12, t2, t3, t4;
    mp::Value t5, t6, t7, t8, t9, v_direita, v_node, v_op;
    mp::Value v_pai;
    (void)self;
    v_node = mp::call_method(self, "parse_term", {});
    L_while42: ;
    t0 = mp::get_member(self, "pos");
    t1 = mp::get_member(self, "tokens");
    t2 = mp::bi_len(t1);
    if (mp::ge(t0, t2)) goto L_endwhile43;
    t3 = mp::get_member(self, "tokens");
    t4 = mp::get_member(self, "pos");
    t5 = mp::get_index(t3, t4);
    if (mp::eq(t5, mp::Value(std::string("+", 1)))) goto L_skip44;
    t6 = mp::get_member(self, "tokens");
    t7 = mp::get_member(self, "pos");
    t8 = mp::get_index(t6, t7);
    if (mp::ne(t8, mp::Value(std::string("-", 1)))) goto L_endwhile43;
    L_skip44: ;
    t9 = mp::get_member(self, "tokens");
    t10 = mp::get_member(self, "pos");
    v_op = mp::get_index(t9, t10);
    t11 = mp::get_member(self, "pos");
    t12 = mp::add(t11, mp::Value(1.0));
    mp::set_member(self, "pos", t12);
    v_direita = mp::call_method(self, "parse_term", {});
    v_pai = mp::new_obj("ASTNode");
    fn_ASTNode_D___attrs(v_pai);
    fn_ASTNode_D_init(v_pai, v_op);
    mp::set_member(v_pai, "esquerda", v_node);
    mp::set_member(v_pai, "direita", v_direita);
    v_node = v_pai;
    goto L_while42;
    L_endwhile43: ;
    return v_node;
}

mp::Value fn_MiniCompilador_D_parse_term(mp::Value self) {
    // MiniCompilador.parse_term
    mp::Value t0, t1, t10, t11, t12, t2, t3, t4;
    mp::Value t5, t6, t7, t8, t9, v_direita, v_node, v_op;
    mp::Value v_pai;
    (void)self;
    v_node = mp::call_method(self, "parse_factor", {});
    L_while45: ;
    t0 = mp::get_member(self, "pos");
    t1 = mp::get_member(self, "tokens");
    t2 = mp::bi_len(t1);
    if (mp::ge(t0, t2)) goto L_endwhile46;
    t3 = mp::get_member(self, "tokens");
    t4 = mp::get_member(self, "pos");
    t5 = mp::get_index(t3, t4);
    if (mp::eq(t5, mp::Value(std::string("*", 1)))) goto L_skip47;
    t6 = mp::get_member(self, "tokens");
    t7 = mp::get_member(self, "pos");
    t8 = mp::get_index(t6, t7);
    if (mp::ne(t8, mp::Value(std::string("/", 1)))) goto L_endwhile46;
    L_skip47: ;
    t9 = mp::get_member(self, "tokens");
    t10 = mp::get_member(self, "pos");
    v_op = mp::get_index(t9, t10);
    t11 = mp::get_member(self, "pos");
    t12 = mp::add(t11, mp::Value(1.0));
    mp::set_member(self, "pos", t12);
    v_direita = mp::call_method(self, "parse_factor", {});
    v_pai = mp::new_obj("ASTNode");
    fn_ASTNode_D___attrs(v_pai);
    fn_ASTNode_D_init(v_pai, v_op);
    mp::set_member(v_pai, "esquerda", v_node);
    mp::set_member(v_pai, "direita", v_direita);
    v_node = v_pai;
    goto L_while45;
    L_endwhile46: ;
    return v_node;
}

mp::Value fn_MiniCompilador_D_parse_factor(mp::Value self) {
    // MiniCompilador.parse_factor
    mp::Value t0, t1, t10, t11, t12, t13, t14, t15;
    mp::Value t16, t17, t18, t19, t2, t20, t3, t4;
    mp::Value t5, t6, t7, t8, t9, v_node, v_token;
    (void)self;
    t0 = mp::get_member(self, "pos");
    t1 = mp::get_member(self, "tokens");
    t2 = mp::bi_len(t1);
    if (mp::lt(t0, t2)) goto L_endif48;
    mp::set_member(self, "erro", mp::Value(true));
    mp::print({mp::Value(std::string("\342\235\214 Erro de sintaxe: a express\303\243o terminou antes do esperado", 60))});
    t3 = mp::new_obj("ASTNode");
    fn_ASTNode_D___attrs(t3);
    fn_ASTNode_D_init(t3, mp::Value(std::string("0", 1)));
    return t3;
    L_endif48: ;
    t4 = mp::get_member(self, "tokens");
    t5 = mp::get_member(self, "pos");
    v_token = mp::get_index(t4, t5);
    t6 = mp::get_member(self, "pos");
    t7 = mp::add(t6, mp::Value(1.0));
    mp::set_member(self, "pos", t7);
    if (mp::ne(v_token, mp::Value(std::string("(", 1)))) goto L_endif49;
    v_node = mp::call_method(self, "parse_expr", {});
    t8 = mp::get_member(self, "pos");
    t9 = mp::get_member(self, "tokens");
    t10 = mp::bi_len(t9);
    if (mp::ge(t8, t10)) goto L_else50;
    t11 = mp::get_member(self, "tokens");
    t12 = mp::get_member(self, "pos");
    t13 = mp::get_index(t11, t12);
    if (mp::ne(t13, mp::Value(std::string(")", 1)))) goto L_else50;
    t14 = mp::get_member(self, "pos");
    t15 = mp::add(t14, mp::Value(1.0));
    mp::set_member(self, "pos", t15);
    goto L_endif51;
    L_else50: ;
    mp::set_member(self, "erro", mp::Value(true));
    mp::print({mp::Value(std::string("\342\235\214 Erro de sintaxe: esperava ')'", 33))});
    L_endif51: ;
    return v_node;
    L_endif49: ;
    t16 = fn_eh_operador(v_token);
    if ((t16).truthy()) goto L_skip53;
    if (mp::eq(v_token, mp::Value(std::string(")", 1)))) goto L_skip53;
    if (mp::ne(v_token, mp::Value(std::string("=", 1)))) goto L_endif52;
    L_skip53: ;
    mp::set_member(self, "erro", mp::Value(true));
    t17 = mp::add(mp::Value(std::string("\342\235\214 Erro de sintaxe: esperava um operando, mas encontrou '", 58)), v_token);
    t18 = mp::add(t17, mp::Value(std::string("'", 1)));
    mp::print({t18});
    t19 = mp::new_obj("ASTNode");
    fn_ASTNode_D___attrs(t19);
    fn_ASTNode_D_init(t19, mp::Value(std::string("0", 1)));
    return t19;
    L_endif52: ;
    mp::call_method(self, "registrar_simbolo", {v_token});
    t20 = mp::new_obj("ASTNode");
    fn_ASTNode_D___attrs(t20);
    fn_ASTNode_D_init(t20, v_token);
    return t20;
}

mp::Value fn_MiniCompilador_D_registrar_simbolo(mp::Value self, mp::Value v_token) {
    // MiniCompilador.registrar_simbolo
    mp::Value t0, t1, t2, t3, t4, t5;
    (void)self;
    t0 = mp::get_member(self, "simbolos");
    t1 = fn_contem(t0, v_token);
    if (!(t1).truthy()) goto L_endif54;
    return mp::Value();
    L_endif54: ;
    t2 = mp::get_member(self, "simbolos");
    mp::append(t2, v_token);
    t3 = fn_eh_numero(v_token);
    if (!(t3).truthy()) goto L_else55;
    t4 = mp::get_member(self, "tipos_simbolos");
    mp::append(t4, mp::Value(std::string("CONST", 5)));
    goto L_endif56;
    L_else55: ;
    t5 = mp::get_member(self, "tipos_simbolos");
    mp::append(t5, mp::Value(std::string("VAR", 3)));
    L_endif56: ;
    return mp::Value();
}

mp::Value fn_MiniCompilador_D_imprimir_ast(mp::Value self, mp::Value v_node, mp::Value v_nivel) {
    // MiniCompilador.imprimir_ast
    mp::Value t0, t1, t2, t3, t4, t5, t6;
    (void)self;
    if (mp::ne(v_node, mp::Value())) goto L_endif57;
    return mp::Value();
    L_endif57: ;
    t0 = mp::get_member(v_node, "direita");
    t1 = mp::add(v_nivel, mp::Value(1.0));
    mp::call_method(self, "imprimir_ast", {t0, t1});
    t2 = fn_espacos(v_nivel);
    t3 = mp::get_member(v_node, "valor");
    t4 = mp::add(t2, t3);
    mp::print({t4});
    t5 = mp::get_member(v_node, "esquerda");
    t6 = mp::add(v_nivel, mp::Value(1.0));
    mp::call_method(self, "imprimir_ast", {t5, t6});
    return mp::Value();
}

mp::Value fn_MiniCompilador_D_formatar(mp::Value self, mp::Value v_node) {
    // MiniCompilador.formatar
    mp::Value t0, t1, t10, t11, t12, t13, t2, t3;
    mp::Value t4, t5, t6, t7, t8, t9;
    (void)self;
    if (mp::ne(v_node, mp::Value())) goto L_endif58;
    return mp::Value(std::string("", 0));
    L_endif58: ;
    t0 = mp::get_member(v_node, "valor");
    t1 = fn_eh_operador(t0);
    if ((t1).truthy()) goto L_endif59;
    t2 = mp::get_member(v_node, "valor");
    return t2;
    L_endif59: ;
    t3 = mp::get_member(v_node, "esquerda");
    t4 = mp::call_method(self, "formatar", {t3});
    t5 = mp::add(mp::Value(std::string("(", 1)), t4);
    t6 = mp::add(t5, mp::Value(std::string(" ", 1)));
    t7 = mp::get_member(v_node, "valor");
    t8 = mp::add(t6, t7);
    t9 = mp::add(t8, mp::Value(std::string(" ", 1)));
    t10 = mp::get_member(v_node, "direita");
    t11 = mp::call_method(self, "formatar", {t10});
    t12 = mp::add(t9, t11);
    t13 = mp::add(t12, mp::Value(std::string(")", 1)));
    return t13;
}

mp::Value fn_MiniCompilador_D_gerar_tac(mp::Value self, mp::Value v_node) {
    // MiniCompilador.gerar_tac
    mp::Value t0, t1, t10, t11, t12, t13, t14, t15;
    mp::Value t2, t3, t4, t5, t6, t7, t8, t9;
    mp::Value v_a1, v_a2, v_temp;
    (void)self;
    t0 = mp::get_member(v_node, "valor");
    t1 = fn_eh_operador(t0);
    if ((t1).truthy()) goto L_endif60;
    t2 = mp::get_member(v_node, "valor");
    return t2;
    L_endif60: ;
    t3 = mp::get_member(v_node, "esquerda");
    v_a1 = mp::call_method(self, "gerar_tac", {t3});
    t4 = mp::get_member(v_node, "direita");
    v_a2 = mp::call_method(self, "gerar_tac", {t4});
    t5 = mp::get_member(self, "temp_count");
    t6 = mp::bi_to_string(t5);
    v_temp = mp::add(mp::Value(std::string("t", 1)), t6);
    t7 = mp::get_member(self, "temp_count");
    t8 = mp::add(t7, mp::Value(1.0));
    mp::set_member(self, "temp_count", t8);
    t9 = mp::add(v_temp, mp::Value(std::string(" = ", 3)));
    t10 = mp::add(t9, v_a1);
    t11 = mp::add(t10, mp::Value(std::string(" ", 1)));
    t12 = mp::get_member(v_node, "valor");
    t13 = mp::add(t11, t12);
    t14 = mp::add(t13, mp::Value(std::string(" ", 1)));
    t15 = mp::add(t14, v_a2);
    mp::print({t15});
    return v_temp;
}

mp::Value fn_MiniCompilador_D_emitir(mp::Value self, mp::Value v_linha) {
    // MiniCompilador.emitir
    mp::Value t0, t1, t2;
    (void)self;
    mp::print({v_linha});
    t0 = mp::get_member(self, "asm");
    t1 = mp::add(t0, v_linha);
    t2 = mp::add(t1, mp::Value(std::string("\n", 1)));
    mp::set_member(self, "asm", t2);
    return mp::Value();
}

mp::Value fn_MiniCompilador_D_emitir_mov(mp::Value self, mp::Value v_reg, mp::Value v_valor) {
    // MiniCompilador.emitir_mov
    mp::Value t0, t1, t10, t11, t12, t13, t14, t15;
    mp::Value t16, t17, t18, t19, t2, t3, t4, t5;
    mp::Value t6, t7, t8, t9, v_inteiro;
    (void)self;
    t0 = fn_so_digitos(v_valor);
    if (!(t0).truthy()) goto L_else61;
    t1 = mp::bi_to_number(v_valor);
    if (mp::gt(t1, mp::Value(255.0))) goto L_else63;
    t2 = mp::add(mp::Value(std::string("    MOV    ", 11)), v_reg);
    t3 = mp::add(t2, mp::Value(std::string(", #", 3)));
    t4 = mp::add(t3, v_valor);
    mp::call_method(self, "emitir", {t4});
    goto L_endif64;
    L_else63: ;
    t5 = mp::add(mp::Value(std::string("    LDR    ", 11)), v_reg);
    t6 = mp::add(t5, mp::Value(std::string(", =", 3)));
    t7 = mp::add(t6, v_valor);
    mp::call_method(self, "emitir", {t7});
    L_endif64: ;
    goto L_endif62;
    L_else61: ;
    t8 = fn_eh_numero(v_valor);
    if (!(t8).truthy()) goto L_else65;
    t9 = mp::bi_split(v_valor, mp::Value(std::string(".", 1)));
    v_inteiro = mp::get_index(t9, mp::Value(0.0));
    t10 = mp::add(mp::Value(std::string("    LDR    ", 11)), v_reg);
    t11 = mp::add(t10, mp::Value(std::string(", =", 3)));
    t12 = mp::add(t11, v_inteiro);
    t13 = mp::add(t12, mp::Value(std::string("    @ aviso: decimal ", 21)));
    t14 = mp::add(t13, v_valor);
    t15 = mp::add(t14, mp::Value(std::string(" truncado", 9)));
    mp::call_method(self, "emitir", {t15});
    goto L_endif66;
    L_else65: ;
    t16 = mp::add(mp::Value(std::string("    MOV    ", 11)), v_reg);
    t17 = mp::add(t16, mp::Value(std::string(", #0    @ vari\303\241vel '", 21)));
    t18 = mp::add(t17, v_valor);
    t19 = mp::add(t18, mp::Value(std::string("' sem valor (usando 0)", 22)));
    mp::call_method(self, "emitir", {t19});
    L_endif66: ;
    L_endif62: ;
    return mp::Value();
}

mp::Value fn_MiniCompilador_D_gerar_assembly(mp::Value self, mp::Value v_node) {
    // MiniCompilador.gerar_assembly
    mp::Value t0, t1, t10, t11, t12, t13, t14, t15;
    mp::Value t16, t17, t18, t19, t2, t20, t21, t22;
    mp::Value t23, t24, t25, t26, t27, t28, t29, t3;
    mp::Value t30, t31, t32, t33, t4, t5, t6, t7;
    mp::Value t8, t9, v_a1, v_a2, v_expr, v_instr, v_reg, v_reg_folha;
    (void)self;
    t0 = mp::get_member(v_node, "valor");
    t1 = fn_eh_operador(t0);
    if ((t1).truthy()) goto L_endif67;
    t2 = mp::get_member(self, "reg_count");
    t3 = mp::bi_to_string(t2);
    v_reg_folha = mp::add(mp::Value(std::string("r", 1)), t3);
    t4 = mp::get_member(self, "reg_count");
    t5 = mp::add(t4, mp::Value(1.0));
    mp::set_member(self, "reg_count", t5);
    t6 = mp::get_member(v_node, "valor");
    mp::call_method(self, "emitir_mov", {v_reg_folha, t6});
    return v_reg_folha;
    L_endif67: ;
    t7 = mp::get_member(v_node, "esquerda");
    v_a1 = mp::call_method(self, "gerar_assembly", {t7});
    t8 = mp::get_member(v_node, "direita");
    v_a2 = mp::call_method(self, "gerar_assembly", {t8});
    t9 = mp::get_member(self, "reg_count");
    t10 = mp::bi_to_string(t9);
    v_reg = mp::add(mp::Value(std::string("r", 1)), t10);
    t11 = mp::get_member(self, "reg_count");
    t12 = mp::add(t11, mp::Value(1.0));
    mp::set_member(self, "reg_count", t12);
    v_instr = mp::Value(std::string("NOP", 3));
    t13 = mp::get_member(v_node, "valor");
    if (mp::ne(t13, mp::Value(std::string("+", 1)))) goto L_else68;
    v_instr = mp::Value(std::string("ADD", 3));
    goto L_endif69;
    L_else68: ;
    t14 = mp::get_member(v_node, "valor");
    if (mp::ne(t14, mp::Value(std::string("-", 1)))) goto L_else70;
    v_instr = mp::Value(std::string("SUB", 3));
    goto L_endif71;
    L_else70: ;
    t15 = mp::get_member(v_node, "valor");
    if (mp::ne(t15, mp::Value(std::string("*", 1)))) goto L_else72;
    v_instr = mp::Value(std::string("MUL", 3));
    goto L_endif73;
    L_else72: ;
    t16 = mp::get_member(v_node, "valor");
    if (mp::ne(t16, mp::Value(std::string("/", 1)))) goto L_endif74;
    v_instr = mp::Value(std::string("DIV_UNSUPPORTED", 15));
    L_endif74: ;
    L_endif73: ;
    L_endif71: ;
    L_endif69: ;
    v_expr = mp::call_method(self, "formatar", {v_node});
    if (mp::ne(v_instr, mp::Value(std::string("DIV_UNSUPPORTED", 15)))) goto L_else75;
    t17 = mp::add(mp::Value(std::string("    @ divis\303\243o n\303\243o suportada: ", 31)), v_a1);
    t18 = mp::add(t17, mp::Value(std::string(" / ", 3)));
    t19 = mp::add(t18, v_a2);
    t20 = mp::add(t19, mp::Value(std::string("    @ resultado de '", 20)));
    t21 = mp::add(t20, v_expr);
    t22 = mp::add(t21, mp::Value(std::string("'", 1)));
    mp::call_method(self, "emitir", {t22});
    goto L_endif76;
    L_else75: ;
    t23 = fn_pad_direita(v_instr, mp::Value(6.0));
    t24 = mp::add(mp::Value(std::string("    ", 4)), t23);
    t25 = mp::add(t24, mp::Value(std::string(" ", 1)));
    t26 = mp::add(t25, v_reg);
    t27 = mp::add(t26, mp::Value(std::string(", ", 2)));
    t28 = mp::add(t27, v_a1);
    t29 = mp::add(t28, mp::Value(std::string(", ", 2)));
    t30 = mp::add(t29, v_a2);
    t31 = mp::add(t30, mp::Value(std::string("    @ resultado de '", 20)));
    t32 = mp::add(t31, v_expr);
    t33 = mp::add(t32, mp::Value(std::string("'", 1)));
    mp::call_method(self, "emitir", {t33});
    L_endif76: ;
    return v_reg;
}

mp::Value fn_MiniCompilador_D_simbolo_menor(mp::Value self, mp::Value v_i, mp::Value v_j) {
    // MiniCompilador.simbolo_menor
    mp::Value t0, t1, t2, t3, t4, t5, t6, t7;
    mp::Value v_a, v_b, v_ta, v_tb;
    (void)self;
    t0 = mp::get_member(self, "simbolos");
    v_a = mp::get_index(t0, v_i);
    t1 = mp::get_member(self, "simbolos");
    v_b = mp::get_index(t1, v_j);
    t2 = mp::get_member(self, "tipos_simbolos");
    v_ta = mp::get_index(t2, v_i);
    t3 = mp::get_member(self, "tipos_simbolos");
    v_tb = mp::get_index(t3, v_j);
    if (mp::ne(v_ta, mp::Value(std::string("CONST", 5)))) goto L_endif77;
    if (mp::ne(v_tb, mp::Value(std::string("CONST", 5)))) goto L_endif77;
    t4 = mp::bi_to_number(v_a);
    t5 = mp::bi_to_number(v_b);
    t6 = mp::Value(mp::lt(t4, t5));
    return t6;
    L_endif77: ;
    if (mp::ne(v_ta, mp::Value(std::string("CONST", 5)))) goto L_endif78;
    return mp::Value(true);
    L_endif78: ;
    if (mp::ne(v_tb, mp::Value(std::string("CONST", 5)))) goto L_endif79;
    return mp::Value(false);
    L_endif79: ;
    t7 = mp::Value(mp::lt(v_a, v_b));
    return t7;
}

mp::Value fn_MiniCompilador_D_ordenar_simbolos(mp::Value self) {
    // MiniCompilador.ordenar_simbolos
    mp::Value t0, t1, t10, t11, t12, t13, t14, t15;
    mp::Value t16, t17, t18, t2, t3, t4, t5, t6;
    mp::Value t7, t8, t9, v_i, v_j, v_n, v_troca, v_troca_tipo;
    (void)self;
    t0 = mp::get_member(self, "simbolos");
    v_n = mp::bi_len(t0);
    v_i = mp::Value(0.0);
    L_for80: ;
    if (mp::ge(v_i, v_n)) goto L_endfor82;
    v_j = mp::Value(0.0);
    L_for83: ;
    t1 = mp::sub(v_n, mp::Value(1.0));
    t2 = mp::sub(t1, v_i);
    if (mp::ge(v_j, t2)) goto L_endfor85;
    t3 = mp::add(v_j, mp::Value(1.0));
    t4 = mp::call_method(self, "simbolo_menor", {t3, v_j});
    if (!(t4).truthy()) goto L_endif86;
    t5 = mp::get_member(self, "simbolos");
    v_troca = mp::get_index(t5, v_j);
    t6 = mp::get_member(self, "simbolos");
    t7 = mp::get_member(self, "simbolos");
    t8 = mp::add(v_j, mp::Value(1.0));
    t9 = mp::get_index(t7, t8);
    mp::set_index(t6, v_j, t9);
    t10 = mp::get_member(self, "simbolos");
    t11 = mp::add(v_j, mp::Value(1.0));
    mp::set_index(t10, t11, v_troca);
    t12 = mp::get_member(self, "tipos_simbolos");
    v_troca_tipo = mp::get_index(t12, v_j);
    t13 = mp::get_member(self, "tipos_simbolos");
    t14 = mp::get_member(self, "tipos_simbolos");
    t15 = mp::add(v_j, mp::Value(1.0));
    t16 = mp::get_index(t14, t15);
    mp::set_index(t13, v_j, t16);
    t17 = mp::get_member(self, "tipos_simbolos");
    t18 = mp::add(v_j, mp::Value(1.0));
    mp::set_index(t17, t18, v_troca_tipo);
    L_endif86: ;
    v_j = mp::add(v_j, mp::Value(1.0));
    goto L_for83;
    L_endfor85: ;
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for80;
    L_endfor82: ;
    return mp::Value();
}

mp::Value fn_MiniCompilador_D_imprimir_simbolos(mp::Value self) {
    // MiniCompilador.imprimir_simbolos
    mp::Value t0, t1, t2, t3, t4, t5, t6, t7;
    mp::Value t8, v_i;
    (void)self;
    mp::call_method(self, "ordenar_simbolos", {});
    v_i = mp::Value(0.0);
    L_for87: ;
    t0 = mp::get_member(self, "simbolos");
    t1 = mp::bi_len(t0);
    if (mp::ge(v_i, t1)) goto L_endfor89;
    t2 = mp::get_member(self, "simbolos");
    t3 = mp::get_index(t2, v_i);
    t4 = mp::add(mp::Value(std::string("\360\237\224\271 ", 5)), t3);
    t5 = mp::add(t4, mp::Value(std::string(" \342\206\222 ", 5)));
    t6 = mp::get_member(self, "tipos_simbolos");
    t7 = mp::get_index(t6, v_i);
    t8 = mp::add(t5, t7);
    mp::print({t8});
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for87;
    L_endfor89: ;
    return mp::Value();
}

mp::Value fn_MiniCompilador_D_avaliar(mp::Value self, mp::Value v_node) {
    // MiniCompilador.avaliar
    mp::Value t0, t1, t10, t11, t12, t13, t14, t15;
    mp::Value t16, t17, t2, t3, t4, t5, t6, t7;
    mp::Value t8, t9, v_dir, v_esq;
    (void)self;
    t0 = mp::get_member(v_node, "valor");
    t1 = fn_eh_operador(t0);
    if ((t1).truthy()) goto L_endif90;
    t2 = mp::get_member(v_node, "valor");
    t3 = fn_eh_numero(t2);
    if (!(t3).truthy()) goto L_endif91;
    t4 = mp::get_member(v_node, "valor");
    t5 = mp::bi_to_number(t4);
    return t5;
    L_endif91: ;
    t6 = mp::get_member(v_node, "valor");
    t7 = mp::add(mp::Value(std::string("\342\232\240\357\270\217 Vari\303\241vel '", 18)), t6);
    t8 = mp::add(t7, mp::Value(std::string("' n\303\243o tem valor atribu\303\255do. Usando 0.", 38)));
    mp::print({t8});
    return mp::Value(0.0);
    L_endif90: ;
    t9 = mp::get_member(v_node, "esquerda");
    v_esq = mp::call_method(self, "avaliar", {t9});
    t10 = mp::get_member(v_node, "direita");
    v_dir = mp::call_method(self, "avaliar", {t10});
    t11 = mp::get_member(v_node, "valor");
    if (mp::ne(t11, mp::Value(std::string("+", 1)))) goto L_endif92;
    t12 = mp::add(v_esq, v_dir);
    return t12;
    L_endif92: ;
    t13 = mp::get_member(v_node, "valor");
    if (mp::ne(t13, mp::Value(std::string("-", 1)))) goto L_endif93;
    t14 = mp::sub(v_esq, v_dir);
    return t14;
    L_endif93: ;
    t15 = mp::get_member(v_node, "valor");
    if (mp::ne(t15, mp::Value(std::string("*", 1)))) goto L_endif94;
    t16 = mp::mul(v_esq, v_dir);
    return t16;
    L_endif94: ;
    if (mp::ne(v_dir, mp::Value(0.0))) goto L_endif95;
    mp::set_member(self, "divisao_por_zero", mp::Value(true));
    return mp::Value(0.0);
    L_endif95: ;
    t17 = mp::div(v_esq, v_dir);
    return t17;
}

mp::Value fn_contem(mp::Value v_lista, mp::Value v_item) {
    // contem
    mp::Value t0, t1, t2, v_x;
    t0 = v_lista;
    t1 = mp::size_of(t0);
    t2 = mp::Value(0.0);
    L_foreach96: ;
    if (mp::ge(t2, t1)) goto L_endforeach98;
    v_x = mp::get_index(t0, t2);
    if (mp::ne(v_x, v_item)) goto L_endif99;
    return mp::Value(true);
    L_endif99: ;
    t2 = mp::add(t2, mp::Value(1.0));
    goto L_foreach96;
    L_endforeach98: ;
    return mp::Value(false);
}

mp::Value fn_main() {
    // main
    mp::Value t0, t1, t10, t11, t12, t13, t14, t15;
    mp::Value t2, t3, t4, t5, t6, t7, t8, t9;
    mp::Value v_resultado, v_t;
    v_entrada = mp::input(mp::Value(std::string("Digite uma express\303\243o infixada: ", 32)));
    v_tokens = fn_analisar(v_entrada);
    mp::print({mp::Value(std::string("\n\360\237\224\215 Tokens gerados pelo analisador l\303\251xico:", 45))});
    v_lexemas = mp::new_list();
    t0 = v_tokens;
    t1 = mp::size_of(t0);
    t2 = mp::Value(0.0);
    L_foreach100: ;
    if (mp::ge(t2, t1)) goto L_endforeach102;
    v_t = mp::get_index(t0, t2);
    mp::call_method(v_t, "mostrar", {});
    t3 = mp::get_member(v_t, "lexema");
    mp::append(v_lexemas, t3);
    t2 = mp::add(t2, mp::Value(1.0));
    goto L_foreach100;
    L_endforeach102: ;
    v_compilador = mp::new_obj("MiniCompilador");
    fn_MiniCompilador_D___attrs(v_compilador);
    fn_MiniCompilador_D_init(v_compilador, v_lexemas);
    v_raiz = mp::call_method(v_compilador, "parse_expr", {});
    t4 = mp::get_member(v_compilador, "pos");
    t5 = mp::bi_len(v_lexemas);
    if (mp::ge(t4, t5)) goto L_endif103;
    t6 = mp::get_member(v_compilador, "erro");
    if ((t6).truthy()) goto L_endif103;
    mp::set_member(v_compilador, "erro", mp::Value(true));
    t7 = mp::get_member(v_compilador, "pos");
    t8 = mp::get_index(v_lexemas, t7);
    t9 = mp::add(mp::Value(std::string("\342\235\214 Erro de sintaxe: s\303\255mbolos sobrando depois da express\303\243o: '", 63)), t8);
    t10 = mp::add(t9, mp::Value(std::string("'", 1)));
    mp::print({t10});
    L_endif103: ;
    t11 = mp::get_member(v_compilador, "erro");
    if (!(t11).truthy()) goto L_else104;
    mp::print({mp::Value(std::string("\n\360\237\232\253 Compila\303\247\303\243o interrompida por erro de sintaxe.", 52))});
    goto L_endif105;
    L_else104: ;
    mp::print({mp::Value(std::string("\n\360\237\214\263 \303\201rvore Sint\303\241tica Abstrata (AST):", 40))});
    mp::call_method(v_compilador, "imprimir_ast", {v_raiz, mp::Value(0.0)});
    mp::print({mp::Value(std::string("\n\360\237\223\246 C\303\263digo de Tr\303\252s Endere\303\247os (TAC):", 40))});
    mp::call_method(v_compilador, "gerar_tac", {v_raiz});
    mp::print({mp::Value(std::string("\n\342\232\231\357\270\217 Assembly ARMv7 (CPUlator):", 34))});
    mp::call_method(v_compilador, "emitir", {mp::Value(std::string(".global _start", 14))});
    mp::call_method(v_compilador, "emitir", {mp::Value(std::string(".text", 5))});
    mp::call_method(v_compilador, "emitir", {mp::Value(std::string("_start:", 7))});
    mp::call_method(v_compilador, "gerar_assembly", {v_raiz});
    mp::call_method(v_compilador, "emitir", {mp::Value(std::string("    b .    @ loop infinito para parar o programa", 48))});
    mp::print({mp::Value(std::string("\n\360\237\223\232 Tabela de S\303\255mbolos:", 26))});
    mp::call_method(v_compilador, "imprimir_simbolos", {});
    mp::print({mp::Value(std::string("\n\360\237\247\256 Resultado final da express\303\243o:", 36))});
    v_resultado = mp::call_method(v_compilador, "avaliar", {v_raiz});
    t12 = mp::get_member(v_compilador, "divisao_por_zero");
    if (!(t12).truthy()) goto L_else106;
    mp::print({mp::Value(std::string("\342\236\241\357\270\217  NaN (divis\303\243o por zero)", 31))});
    goto L_endif107;
    L_else106: ;
    t13 = fn_formatar_double(v_resultado);
    t14 = mp::add(mp::Value(std::string("\342\236\241\357\270\217  ", 8)), t13);
    mp::print({t14});
    L_endif107: ;
    t15 = mp::get_member(v_compilador, "asm");
    mp::bi_write_file(mp::Value(std::string("Codigo-Assembly-ARMV7.arm", 25)), t15);
    mp::print({mp::Value(std::string("\n\360\237\222\276 Assembly salvo em Codigo-Assembly-ARMV7.arm", 49))});
    L_endif105: ;
    return mp::Value();
}

static void register_classes() {
    mp::register_class("Token", "", {
        {"init", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Token.init", a, 2); return fn_Token_D_init(self, a[0], a[1]); }},
        {"mostrar", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("Token.mostrar", a, 0); return fn_Token_D_mostrar(self); }},
    });
    mp::register_class("ASTNode", "", {
        {"init", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("ASTNode.init", a, 1); return fn_ASTNode_D_init(self, a[0]); }},
    });
    mp::register_class("MiniCompilador", "", {
        {"init", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.init", a, 1); return fn_MiniCompilador_D_init(self, a[0]); }},
        {"parse_expr", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.parse_expr", a, 0); return fn_MiniCompilador_D_parse_expr(self); }},
        {"parse_term", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.parse_term", a, 0); return fn_MiniCompilador_D_parse_term(self); }},
        {"parse_factor", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.parse_factor", a, 0); return fn_MiniCompilador_D_parse_factor(self); }},
        {"registrar_simbolo", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.registrar_simbolo", a, 1); return fn_MiniCompilador_D_registrar_simbolo(self, a[0]); }},
        {"imprimir_ast", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.imprimir_ast", a, 2); return fn_MiniCompilador_D_imprimir_ast(self, a[0], a[1]); }},
        {"formatar", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.formatar", a, 1); return fn_MiniCompilador_D_formatar(self, a[0]); }},
        {"gerar_tac", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.gerar_tac", a, 1); return fn_MiniCompilador_D_gerar_tac(self, a[0]); }},
        {"emitir", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.emitir", a, 1); return fn_MiniCompilador_D_emitir(self, a[0]); }},
        {"emitir_mov", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.emitir_mov", a, 2); return fn_MiniCompilador_D_emitir_mov(self, a[0], a[1]); }},
        {"gerar_assembly", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.gerar_assembly", a, 1); return fn_MiniCompilador_D_gerar_assembly(self, a[0]); }},
        {"simbolo_menor", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.simbolo_menor", a, 2); return fn_MiniCompilador_D_simbolo_menor(self, a[0], a[1]); }},
        {"ordenar_simbolos", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.ordenar_simbolos", a, 0); return fn_MiniCompilador_D_ordenar_simbolos(self); }},
        {"imprimir_simbolos", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.imprimir_simbolos", a, 0); return fn_MiniCompilador_D_imprimir_simbolos(self); }},
        {"avaliar", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("MiniCompilador.avaliar", a, 1); return fn_MiniCompilador_D_avaliar(self, a[0]); }},
    });
}

int main(int argc, char** argv) {
    return mp::run_program(argc, argv, []() {
        register_classes();
    }, []() { fn_main(); });
}
