// Código gerado automaticamente pelo compilador MiniPar 2026.2
#include "minipar_runtime.hpp"

// ---- variáveis globais ----
static mp::Value v_ATIVIDADES_POR_ALUNO;
static mp::Value v_AVALIADORES;
static mp::Value v_NUM_ALUNOS;
static mp::Value v_TOTAL_ATIVIDADES;
static mp::Value v_reducao_pct;
static mp::Value v_resultado_par;
static mp::Value v_resultado_seq;
static mp::Value v_speedup;
static mp::Value v_tarefas;
static mp::Value v_tempo_par;
static mp::Value v_tempo_seq;

// ---- protótipos ----
mp::Value fn_GeradorLCG_D___attrs(mp::Value self);
mp::Value fn_GeradorLCG_D_init(mp::Value self, mp::Value v_semente);
mp::Value fn_GeradorLCG_D_mult_mod(mp::Value self, mp::Value v_a, mp::Value v_b);
mp::Value fn_GeradorLCG_D_proximo(mp::Value self);
mp::Value fn_GeradorLCG_D_uniforme(mp::Value self, mp::Value v_minimo, mp::Value v_maximo);
mp::Value fn_simular_atraso(mp::Value v_segundos);
mp::Value fn_avaliar_atividade(mp::Value v_tarefa, mp::Value v_avaliador, mp::Value v_gerador);
mp::Value fn_avaliar_lote(mp::Value v_avaliador, mp::Value v_lote);
mp::Value fn_fatiar(mp::Value v_lista, mp::Value v_inicio, mp::Value v_fim);
mp::Value fn_execucao_sequencial();
mp::Value fn_execucao_paralela();
mp::Value fn_execucao_paralela_T_professor(mp::Value v_nome0, mp::Value v_lote0);
mp::Value fn_execucao_paralela_T_monitor1(mp::Value v_nome1, mp::Value v_lote1);
mp::Value fn_execucao_paralela_T_monitor2(mp::Value v_nome2, mp::Value v_lote2);
mp::Value fn_execucao_paralela_T_monitor3(mp::Value v_nome3, mp::Value v_lote3);
mp::Value fn_main();

mp::Value fn_GeradorLCG_D___attrs(mp::Value self) {
    // GeradorLCG.__attrs
    (void)self;
    mp::set_member(self, "estado", mp::Value(0.0));
    return mp::Value();
}

mp::Value fn_GeradorLCG_D_init(mp::Value self, mp::Value v_semente) {
    // GeradorLCG.init
    (void)self;
    mp::set_member(self, "estado", v_semente);
    return mp::Value();
}

mp::Value fn_GeradorLCG_D_mult_mod(mp::Value self, mp::Value v_a, mp::Value v_b) {
    // GeradorLCG.mult_mod
    mp::Value t0, t1, t2, t3, t4, t5, t6, t7;
    mp::Value v_alto, v_baixo;
    (void)self;
    t0 = mp::div(v_a, mp::Value(65536.0));
    v_alto = mp::bi_floor(t0);
    t1 = mp::mul(v_alto, mp::Value(65536.0));
    v_baixo = mp::sub(v_a, t1);
    t2 = mp::mul(v_alto, v_b);
    t3 = mp::mod(t2, mp::Value(32768.0));
    t4 = mp::mul(t3, mp::Value(65536.0));
    t5 = mp::mul(v_baixo, v_b);
    t6 = mp::add(t4, t5);
    t7 = mp::mod(t6, mp::Value(2147483648.0));
    return t7;
}

mp::Value fn_GeradorLCG_D_proximo(mp::Value self) {
    // GeradorLCG.proximo
    mp::Value t0, t1, t2, t3, t4;
    (void)self;
    t0 = mp::get_member(self, "estado");
    t1 = mp::call_method(self, "mult_mod", {t0, mp::Value(1103515245.0)});
    t2 = mp::add(t1, mp::Value(12345.0));
    t3 = mp::mod(t2, mp::Value(2147483648.0));
    mp::set_member(self, "estado", t3);
    t4 = mp::get_member(self, "estado");
    return t4;
}

mp::Value fn_GeradorLCG_D_uniforme(mp::Value self, mp::Value v_minimo, mp::Value v_maximo) {
    // GeradorLCG.uniforme
    mp::Value t0, t1, t2, t3, v_fracao;
    (void)self;
    t0 = mp::call_method(self, "proximo", {});
    v_fracao = mp::div(t0, mp::Value(2147483647.0));
    t1 = mp::sub(v_maximo, v_minimo);
    t2 = mp::mul(t1, v_fracao);
    t3 = mp::add(v_minimo, t2);
    return t3;
}

mp::Value fn_simular_atraso(mp::Value v_segundos) {
    // simular_atraso
    mp::Value t0, v_i, v_iteracoes, v_soma;
    t0 = mp::mul(v_segundos, mp::Value(1500000.0));
    v_iteracoes = mp::bi_floor(t0);
    v_soma = mp::Value(0.0);
    v_i = mp::Value(0.0);
    L_for1: ;
    if (mp::ge(v_i, v_iteracoes)) goto L_endfor3;
    v_soma = mp::add(v_soma, v_i);
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for1;
    L_endfor3: ;
    return v_soma;
}

mp::Value fn_avaliar_atividade(mp::Value v_tarefa, mp::Value v_avaliador, mp::Value v_gerador) {
    // avaliar_atividade
    mp::Value t0, t1, t2, v_tempo_correcao;
    v_tempo_correcao = mp::call_method(v_gerador, "uniforme", {mp::Value(0.05), mp::Value(0.15)});
    fn_simular_atraso(v_tempo_correcao);
    t0 = mp::add(mp::Value(std::string("[", 1)), v_avaliador);
    t1 = mp::add(t0, mp::Value(std::string("] Concluiu: ", 12)));
    t2 = mp::add(t1, v_tarefa);
    return t2;
}

mp::Value fn_avaliar_lote(mp::Value v_avaliador, mp::Value v_lote) {
    // avaliar_lote
    mp::Value t0, t1, t2, t3, v_gerador, v_resultados, v_tarefa;
    v_gerador = mp::new_obj("GeradorLCG");
    fn_GeradorLCG_D___attrs(v_gerador);
    fn_GeradorLCG_D_init(v_gerador, mp::Value(123456789.0));
    v_resultados = mp::new_list();
    t0 = v_lote;
    t1 = mp::size_of(t0);
    t2 = mp::Value(0.0);
    L_foreach4: ;
    if (mp::ge(t2, t1)) goto L_endforeach6;
    v_tarefa = mp::get_index(t0, t2);
    t3 = fn_avaliar_atividade(v_tarefa, v_avaliador, v_gerador);
    mp::append(v_resultados, t3);
    t2 = mp::add(t2, mp::Value(1.0));
    goto L_foreach4;
    L_endforeach6: ;
    return v_resultados;
}

mp::Value fn_fatiar(mp::Value v_lista, mp::Value v_inicio, mp::Value v_fim) {
    // fatiar
    mp::Value t0, v_i, v_parte;
    v_parte = mp::new_list();
    v_i = v_inicio;
    L_for7: ;
    if (mp::ge(v_i, v_fim)) goto L_endfor9;
    t0 = mp::get_index(v_lista, v_i);
    mp::append(v_parte, t0);
    v_i = mp::add(v_i, mp::Value(1.0));
    goto L_for7;
    L_endfor9: ;
    return v_parte;
}

mp::Value fn_execucao_sequencial() {
    // execucao_sequencial
    mp::Value t0, t1, t2, v_fim, v_inicio, v_resultados;
    mp::print({mp::Value(std::string("--- 1. Executando Modo Sequencial (Apenas 1 N\303\272cleo / Professor) ---", 68))});
    v_inicio = mp::bi_clock();
    v_resultados = fn_avaliar_lote(mp::Value(std::string("Professor", 9)), v_tarefas);
    v_fim = mp::bi_clock();
    t0 = mp::new_list();
    t1 = mp::sub(v_fim, v_inicio);
    mp::append(t0, t1);
    t2 = mp::bi_len(v_resultados);
    mp::append(t0, t2);
    return t0;
}

mp::Value fn_execucao_paralela() {
    // execucao_paralela
    mp::Value t0, t1, t12, t13, t14, t15, t16, t17;
    mp::Value t18, t19, t2, t20, t3, t4, t5, t6;
    mp::Value t7, v_fim, v_inicio, v_lote0, v_lote1, v_lote2, v_lote3, v_nome0;
    mp::Value v_nome1, v_nome2, v_nome3, v_r0, v_r1, v_r2, v_r3, v_tamanho_fatia;
    mp::ForkTable __forks;
    mp::print({mp::Value(std::string("--- 2. Executando Modo Paralelo (4 N\303\272cleos Dedicados: Professor + 3 Monitores) ---", 83))});
    t0 = mp::bi_len(v_tarefas);
    t1 = mp::bi_len(v_AVALIADORES);
    t2 = mp::div(t0, t1);
    v_tamanho_fatia = mp::bi_floor(t2);
    v_lote0 = fn_fatiar(v_tarefas, mp::Value(0.0), v_tamanho_fatia);
    t3 = mp::mul(mp::Value(2.0), v_tamanho_fatia);
    v_lote1 = fn_fatiar(v_tarefas, v_tamanho_fatia, t3);
    t4 = mp::mul(mp::Value(2.0), v_tamanho_fatia);
    t5 = mp::mul(mp::Value(3.0), v_tamanho_fatia);
    v_lote2 = fn_fatiar(v_tarefas, t4, t5);
    t6 = mp::mul(mp::Value(3.0), v_tamanho_fatia);
    t7 = mp::mul(mp::Value(4.0), v_tamanho_fatia);
    v_lote3 = fn_fatiar(v_tarefas, t6, t7);
    v_nome0 = mp::get_index(v_AVALIADORES, mp::Value(0.0));
    v_nome1 = mp::get_index(v_AVALIADORES, mp::Value(1.0));
    v_nome2 = mp::get_index(v_AVALIADORES, mp::Value(2.0));
    v_nome3 = mp::get_index(v_AVALIADORES, mp::Value(3.0));
    v_inicio = mp::bi_clock();
    __forks.spawn("professor", mp::Value(0.0), "execucao_paralela$professor", {mp::copy_for_task(v_nome0), mp::copy_for_task(v_lote0)});
    __forks.spawn("monitor1", mp::Value(1.0), "execucao_paralela$monitor1", {mp::copy_for_task(v_nome1), mp::copy_for_task(v_lote1)});
    __forks.spawn("monitor2", mp::Value(2.0), "execucao_paralela$monitor2", {mp::copy_for_task(v_nome2), mp::copy_for_task(v_lote2)});
    __forks.spawn("monitor3", mp::Value(3.0), "execucao_paralela$monitor3", {mp::copy_for_task(v_nome3), mp::copy_for_task(v_lote3)});
    v_r0 = __forks.join_value("professor");
    v_r1 = __forks.join_value("monitor1");
    v_r2 = __forks.join_value("monitor2");
    v_r3 = __forks.join_value("monitor3");
    v_fim = mp::bi_clock();
    t12 = mp::new_list();
    t13 = mp::sub(v_fim, v_inicio);
    mp::append(t12, t13);
    t14 = mp::bi_len(v_r0);
    t15 = mp::bi_len(v_r1);
    t16 = mp::add(t14, t15);
    t17 = mp::bi_len(v_r2);
    t18 = mp::add(t16, t17);
    t19 = mp::bi_len(v_r3);
    t20 = mp::add(t18, t19);
    mp::append(t12, t20);
    return t12;
}

mp::Value fn_execucao_paralela_T_professor(mp::Value v_nome0, mp::Value v_lote0) {
    // execucao_paralela$professor
    mp::Value t8;
    t8 = fn_avaliar_lote(v_nome0, v_lote0);
    return t8;
}

mp::Value fn_execucao_paralela_T_monitor1(mp::Value v_nome1, mp::Value v_lote1) {
    // execucao_paralela$monitor1
    mp::Value t9;
    t9 = fn_avaliar_lote(v_nome1, v_lote1);
    return t9;
}

mp::Value fn_execucao_paralela_T_monitor2(mp::Value v_nome2, mp::Value v_lote2) {
    // execucao_paralela$monitor2
    mp::Value t10;
    t10 = fn_avaliar_lote(v_nome2, v_lote2);
    return t10;
}

mp::Value fn_execucao_paralela_T_monitor3(mp::Value v_nome3, mp::Value v_lote3) {
    // execucao_paralela$monitor3
    mp::Value t11;
    t11 = fn_avaliar_lote(v_nome3, v_lote3);
    return t11;
}

mp::Value fn_main() {
    // main
    mp::Value t0, t1, t10, t11, t12, t13, t14, t15;
    mp::Value t16, t17, t18, t19, t2, t20, t21, t22;
    mp::Value t23, t24, t25, t26, t27, t28, t29, t3;
    mp::Value t30, t31, t32, t33, t34, t35, t36, t37;
    mp::Value t4, t5, t6, t7, t8, t9, v_aluno_id, v_atividade_id;
    v_NUM_ALUNOS = mp::Value(40.0);
    v_ATIVIDADES_POR_ALUNO = mp::Value(4.0);
    v_TOTAL_ATIVIDADES = mp::mul(v_NUM_ALUNOS, v_ATIVIDADES_POR_ALUNO);
    v_AVALIADORES = mp::new_list();
    mp::append(v_AVALIADORES, mp::Value(std::string("Professor", 9)));
    mp::append(v_AVALIADORES, mp::Value(std::string("Monitor 1", 9)));
    mp::append(v_AVALIADORES, mp::Value(std::string("Monitor 2", 9)));
    mp::append(v_AVALIADORES, mp::Value(std::string("Monitor 3", 9)));
    v_tarefas = mp::new_list();
    v_aluno_id = mp::Value(0.0);
    L_for10: ;
    if (mp::ge(v_aluno_id, v_NUM_ALUNOS)) goto L_endfor12;
    v_atividade_id = mp::Value(0.0);
    L_for13: ;
    if (mp::ge(v_atividade_id, v_ATIVIDADES_POR_ALUNO)) goto L_endfor15;
    t0 = mp::add(v_aluno_id, mp::Value(1.0));
    t1 = mp::bi_to_string(t0);
    t2 = mp::add(mp::Value(std::string("Aluno ", 6)), t1);
    t3 = mp::add(t2, mp::Value(std::string(" - Atividade ", 13)));
    t4 = mp::add(v_atividade_id, mp::Value(1.0));
    t5 = mp::bi_to_string(t4);
    t6 = mp::add(t3, t5);
    mp::append(v_tarefas, t6);
    v_atividade_id = mp::add(v_atividade_id, mp::Value(1.0));
    goto L_for13;
    L_endfor15: ;
    v_aluno_id = mp::add(v_aluno_id, mp::Value(1.0));
    goto L_for10;
    L_endfor12: ;
    t7 = mp::bi_to_string(v_TOTAL_ATIVIDADES);
    t8 = mp::add(mp::Value(std::string("Total de Atividades a Avaliar: ", 31)), t7);
    t9 = mp::add(t8, mp::Value(std::string(" (40 alunos x 4 atividades)\n", 28)));
    mp::print({t9});
    v_resultado_seq = fn_execucao_sequencial();
    v_tempo_seq = mp::get_index(v_resultado_seq, mp::Value(0.0));
    t10 = mp::bi_fmt(v_tempo_seq, mp::Value(2.0));
    t11 = mp::add(mp::Value(std::string("Tempo Sequencial Conclu\303\255do em: ", 32)), t10);
    t12 = mp::add(t11, mp::Value(std::string(" segundos\n", 10)));
    mp::print({t12});
    v_resultado_par = fn_execucao_paralela();
    v_tempo_par = mp::get_index(v_resultado_par, mp::Value(0.0));
    t13 = mp::bi_fmt(v_tempo_par, mp::Value(2.0));
    t14 = mp::add(mp::Value(std::string("Tempo Paralelo Conclu\303\255do em:   ", 32)), t13);
    t15 = mp::add(t14, mp::Value(std::string(" segundos\n", 10)));
    mp::print({t15});
    v_speedup = mp::Value(0.0);
    v_reducao_pct = mp::Value(0.0);
    if (mp::le(v_tempo_par, mp::Value(0.0))) goto L_endif16;
    v_speedup = mp::div(v_tempo_seq, v_tempo_par);
    t16 = mp::sub(v_tempo_seq, v_tempo_par);
    t17 = mp::div(t16, v_tempo_seq);
    v_reducao_pct = mp::mul(t17, mp::Value(100.0));
    L_endif16: ;
    mp::print({mp::Value(std::string("==========================================", 42))});
    mp::print({mp::Value(std::string("         BENCHMARK DE DESEMPENHO          ", 42))});
    mp::print({mp::Value(std::string("==========================================", 42))});
    t18 = mp::bi_fmt(v_tempo_seq, mp::Value(2.0));
    t19 = mp::add(mp::Value(std::string("Tempo Sequencial : ", 19)), t18);
    t20 = mp::add(t19, mp::Value(std::string(" s", 2)));
    mp::print({t20});
    t21 = mp::bi_fmt(v_tempo_par, mp::Value(2.0));
    t22 = mp::add(mp::Value(std::string("Tempo Paralelo   : ", 19)), t21);
    t23 = mp::add(t22, mp::Value(std::string(" s", 2)));
    mp::print({t23});
    t24 = mp::bi_fmt(v_speedup, mp::Value(2.0));
    t25 = mp::add(mp::Value(std::string("Acelera\303\247\303\243o       : ", 21)), t24);
    t26 = mp::add(t25, mp::Value(std::string("x mais r\303\241pido!", 15)));
    mp::print({t26});
    t27 = mp::bi_fmt(v_reducao_pct, mp::Value(1.0));
    t28 = mp::add(mp::Value(std::string("Redu\303\247\303\243o no tempo : ", 21)), t27);
    t29 = mp::add(t28, mp::Value(std::string("% de economia", 13)));
    mp::print({t29});
    mp::print({mp::Value(std::string("==========================================", 42))});
    t30 = mp::get_index(v_resultado_seq, mp::Value(1.0));
    t31 = mp::bi_to_string(t30);
    t32 = mp::add(mp::Value(std::string("Atividades corrigidas: ", 23)), t31);
    t33 = mp::add(t32, mp::Value(std::string(" (sequencial) e ", 16)));
    t34 = mp::get_index(v_resultado_par, mp::Value(1.0));
    t35 = mp::bi_to_string(t34);
    t36 = mp::add(t33, t35);
    t37 = mp::add(t36, mp::Value(std::string(" (paralelo)", 11)));
    mp::print({t37});
    return mp::Value();
}

static void register_all() {
    mp::register_class("GeradorLCG", "", {
        {"init", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("GeradorLCG.init", a, 1); return fn_GeradorLCG_D_init(self, a[0]); }},
        {"mult_mod", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("GeradorLCG.mult_mod", a, 2); return fn_GeradorLCG_D_mult_mod(self, a[0], a[1]); }},
        {"proximo", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("GeradorLCG.proximo", a, 0); return fn_GeradorLCG_D_proximo(self); }},
        {"uniforme", [](const mp::Value& self, mp::Args& a) -> mp::Value { mp::check_arity("GeradorLCG.uniforme", a, 2); return fn_GeradorLCG_D_uniforme(self, a[0], a[1]); }},
    });
    mp::register_task("execucao_paralela$professor", [](mp::Args& a) -> mp::Value { mp::check_arity("tarefa execucao_paralela$professor", a, 2); return fn_execucao_paralela_T_professor(a[0], a[1]); });
    mp::register_task("execucao_paralela$monitor1", [](mp::Args& a) -> mp::Value { mp::check_arity("tarefa execucao_paralela$monitor1", a, 2); return fn_execucao_paralela_T_monitor1(a[0], a[1]); });
    mp::register_task("execucao_paralela$monitor2", [](mp::Args& a) -> mp::Value { mp::check_arity("tarefa execucao_paralela$monitor2", a, 2); return fn_execucao_paralela_T_monitor2(a[0], a[1]); });
    mp::register_task("execucao_paralela$monitor3", [](mp::Args& a) -> mp::Value { mp::check_arity("tarefa execucao_paralela$monitor3", a, 2); return fn_execucao_paralela_T_monitor3(a[0], a[1]); });
}

int main(int argc, char** argv) {
    return mp::run_program(argc, argv, []() {
        register_all();
    }, []() { fn_main(); });
}
