// ============================================================================
// Runtime da linguagem MiniPar 2026.2 (C++17, apenas cabeçalho).
//
// O código C++ gerado pelo compilador usa este arquivo para dar semântica
// dinâmica aos valores (número, string, bool, lista, objeto, canal), às
// funções nativas e às subtarefas (par/fork) executadas em threads.
// ============================================================================
#pragma once

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <mutex>
#include <random>
#include <stdexcept>
#include <string>
#include <thread>
#include <type_traits>
#include <unordered_map>
#include <vector>

#ifdef _WIN32
#  ifndef NOMINMAX
#    define NOMINMAX
#  endif
#  include <windows.h>
#elif defined(__linux__)
#  include <pthread.h>
#  include <sched.h>
#endif

namespace mp {

// ----------------------------------------------------------------------------
// Erros de execução
// ----------------------------------------------------------------------------
struct RuntimeError : std::runtime_error {
    using std::runtime_error::runtime_error;
};

[[noreturn]] inline void fail(const std::string& msg) { throw RuntimeError(msg); }

inline std::atomic<bool>& failed_flag() {
    static std::atomic<bool> f{false};
    return f;
}

struct List;
struct Obj;
struct Channel;
class Value;

// ----------------------------------------------------------------------------
// Value: valor dinâmico (nulo, bool, número, string, lista, objeto, canal)
// ----------------------------------------------------------------------------
class Value {
public:
    enum Tag : uint8_t { NIL, BOOL, NUM, STR, LIST, OBJ, CHAN };

    Tag tag = NIL;
    union { bool b; double n; };
    std::shared_ptr<void> p;   // string, lista, objeto ou canal

    Value() : n(0) {}
    Value(bool v) : tag(BOOL), n(0) { b = v; }
    Value(double v) : tag(NUM), n(v) {}
    template <class T, typename std::enable_if<std::is_integral<T>::value &&
                                               !std::is_same<T, bool>::value, int>::type = 0>
    Value(T v) : tag(NUM), n(static_cast<double>(v)) {}
    Value(const char* s) : tag(STR), n(0), p(std::make_shared<std::string>(s)) {}
    Value(const std::string& s) : tag(STR), n(0), p(std::make_shared<std::string>(s)) {}
    Value(std::string&& s) : tag(STR), n(0), p(std::make_shared<std::string>(std::move(s))) {}

    static Value make_list();
    static Value make_obj(const struct ClassInfo* cls);
    static Value make_channel(std::shared_ptr<Channel> c);

    bool is_nil() const { return tag == NIL; }
    bool is_num() const { return tag == NUM; }
    bool is_str() const { return tag == STR; }
    bool is_list() const { return tag == LIST; }
    bool is_obj() const { return tag == OBJ; }

    const std::string& str() const { return *static_cast<const std::string*>(p.get()); }
    List& list() const { return *static_cast<List*>(p.get()); }
    Obj& obj() const { return *static_cast<Obj*>(p.get()); }
    Channel& chan() const { return *static_cast<Channel*>(p.get()); }

    bool truthy() const {
        switch (tag) {
            case NIL: return false;
            case BOOL: return b;
            case NUM: return n != 0;
            case STR: return !str().empty();
            default: return true;
        }
    }
};

struct List {
    std::vector<Value> v;
};

using Args = std::vector<Value>;
using Method = std::function<Value(const Value& self, Args& args)>;

struct ClassInfo {
    std::string name;
    std::string super;
    std::map<std::string, Method> methods;
};

struct Obj {
    const ClassInfo* cls;
    std::unordered_map<std::string, Value> fields;
};

inline Value Value::make_list() {
    Value v;
    v.tag = LIST;
    v.p = std::make_shared<List>();
    return v;
}

inline Value Value::make_obj(const ClassInfo* cls) {
    Value v;
    v.tag = OBJ;
    auto o = std::make_shared<Obj>();
    o->cls = cls;
    v.p = o;
    return v;
}

inline Value Value::make_channel(std::shared_ptr<Channel> c) {
    Value v;
    v.tag = CHAN;
    v.p = std::move(c);
    return v;
}

// ----------------------------------------------------------------------------
// Nomes de tipo e conversão para texto
// ----------------------------------------------------------------------------
inline const char* type_name(const Value& v) {
    switch (v.tag) {
        case Value::NIL: return "null";
        case Value::BOOL: return "bool";
        case Value::NUM: return "number";
        case Value::STR: return "string";
        case Value::LIST: return "list";
        case Value::OBJ: return "objeto";
        case Value::CHAN: return "c_channel";
    }
    return "?";
}

inline std::string num_to_str(double d) {
    if (std::isnan(d)) return "nan";
    if (std::isinf(d)) return d > 0 ? "inf" : "-inf";
    if (d == 0) return "0";
    char buf[64];
    if (d == std::floor(d) && std::fabs(d) < 1e18) {
        std::snprintf(buf, sizeof buf, "%.0f", d);
        return buf;
    }
    // menor precisão que reproduz exatamente o número (como o repr do Python)
    for (int prec = 1; prec <= 17; ++prec) {
        std::snprintf(buf, sizeof buf, "%.*g", prec, d);
        if (std::strtod(buf, nullptr) == d) break;
    }
    return buf;
}

inline std::string to_str(const Value& v, bool quote_strings = false);

inline std::string to_str(const Value& v, bool quote_strings) {
    switch (v.tag) {
        case Value::NIL: return "null";
        case Value::BOOL: return v.b ? "true" : "false";
        case Value::NUM: return num_to_str(v.n);
        case Value::STR: return quote_strings ? "'" + v.str() + "'" : v.str();
        case Value::LIST: {
            std::string s = "[";
            const auto& items = v.list().v;
            for (size_t i = 0; i < items.size(); ++i) {
                if (i) s += ", ";
                s += to_str(items[i], true);
            }
            return s + "]";
        }
        case Value::OBJ: return "<objeto " + v.obj().cls->name + ">";
        case Value::CHAN: return "<canal>";
    }
    return "?";
}

// ----------------------------------------------------------------------------
// Operadores
// ----------------------------------------------------------------------------
[[noreturn]] inline void bad_operands(const char* op, const Value& a, const Value& b) {
    fail(std::string("Operador '") + op + "' não se aplica a " + type_name(a) + " e " +
         type_name(b));
}

inline Value add(const Value& a, const Value& b) {
    if (a.tag == Value::NUM && b.tag == Value::NUM) return Value(a.n + b.n);
    if (a.tag == Value::STR && b.tag == Value::STR) return Value(a.str() + b.str());
    if (a.tag == Value::LIST && b.tag == Value::LIST) {
        Value r = Value::make_list();
        r.list().v = a.list().v;
        r.list().v.insert(r.list().v.end(), b.list().v.begin(), b.list().v.end());
        return r;
    }
    bad_operands("+", a, b);
}

inline Value sub(const Value& a, const Value& b) {
    if (a.tag == Value::NUM && b.tag == Value::NUM) return Value(a.n - b.n);
    bad_operands("-", a, b);
}

inline Value mul(const Value& a, const Value& b) {
    if (a.tag == Value::NUM && b.tag == Value::NUM) return Value(a.n * b.n);
    bad_operands("*", a, b);
}

inline Value div(const Value& a, const Value& b) {
    if (a.tag == Value::NUM && b.tag == Value::NUM) {
        if (b.n == 0) fail("Divisão por zero");
        return Value(a.n / b.n);
    }
    bad_operands("/", a, b);
}

inline Value mod(const Value& a, const Value& b) {
    if (a.tag == Value::NUM && b.tag == Value::NUM) {
        if (b.n == 0) fail("Divisão por zero (operador %)");
        double r = std::fmod(a.n, b.n);
        if (r != 0 && ((r < 0) != (b.n < 0))) r += b.n;   // resto com o sinal do divisor
        return Value(r);
    }
    bad_operands("%", a, b);
}

inline Value neg(const Value& a) {
    if (a.tag == Value::NUM) return Value(-a.n);
    fail(std::string("Operador '-' unário não se aplica a ") + type_name(a));
}

inline bool eq(const Value& a, const Value& b) {
    if (a.tag != b.tag) return false;
    switch (a.tag) {
        case Value::NIL: return true;
        case Value::BOOL: return a.b == b.b;
        case Value::NUM: return a.n == b.n;
        case Value::STR: return a.str() == b.str();
        case Value::LIST: {
            const auto& x = a.list().v;
            const auto& y = b.list().v;
            if (x.size() != y.size()) return false;
            for (size_t i = 0; i < x.size(); ++i)
                if (!eq(x[i], y[i])) return false;
            return true;
        }
        default: return a.p == b.p;
    }
}

inline bool ne(const Value& a, const Value& b) { return !eq(a, b); }

inline bool lt(const Value& a, const Value& b) {
    if (a.tag == Value::NUM && b.tag == Value::NUM) return a.n < b.n;
    if (a.tag == Value::STR && b.tag == Value::STR) return a.str() < b.str();
    bad_operands("<", a, b);
}
inline bool gt(const Value& a, const Value& b) {
    if (a.tag == Value::NUM && b.tag == Value::NUM) return a.n > b.n;
    if (a.tag == Value::STR && b.tag == Value::STR) return a.str() > b.str();
    bad_operands(">", a, b);
}
inline bool le(const Value& a, const Value& b) {
    if (a.tag == Value::NUM && b.tag == Value::NUM) return a.n <= b.n;
    if (a.tag == Value::STR && b.tag == Value::STR) return a.str() <= b.str();
    bad_operands("<=", a, b);
}
inline bool ge(const Value& a, const Value& b) {
    if (a.tag == Value::NUM && b.tag == Value::NUM) return a.n >= b.n;
    if (a.tag == Value::STR && b.tag == Value::STR) return a.str() >= b.str();
    bad_operands(">=", a, b);
}

// ----------------------------------------------------------------------------
// Listas, strings e matrizes
// ----------------------------------------------------------------------------
inline size_t to_index(const Value& i, size_t size, const char* what) {
    if (i.tag != Value::NUM) fail(std::string("O índice de ") + what + " deve ser um número");
    double d = i.n;
    if (d != std::floor(d)) fail("O índice deve ser um número inteiro");
    long long k = static_cast<long long>(d);
    if (k < 0) k += static_cast<long long>(size);       // índices negativos, como no Python
    if (k < 0 || k >= static_cast<long long>(size))
        fail("Índice fora dos limites: " + num_to_str(d) + " (tamanho " +
             std::to_string(size) + ")");
    return static_cast<size_t>(k);
}

inline Value get_index(const Value& c, const Value& i) {
    if (c.tag == Value::LIST) return c.list().v[to_index(i, c.list().v.size(), "lista")];
    if (c.tag == Value::STR) {
        const std::string& s = c.str();
        return Value(std::string(1, s[to_index(i, s.size(), "string")]));
    }
    fail(std::string("O tipo ") + type_name(c) + " não pode ser indexado");
}

inline void set_index(const Value& c, const Value& i, const Value& v) {
    if (c.tag == Value::LIST) {
        c.list().v[to_index(i, c.list().v.size(), "lista")] = v;
        return;
    }
    if (c.tag == Value::STR) fail("Strings são imutáveis");
    fail(std::string("O tipo ") + type_name(c) + " não aceita atribuição por índice");
}

inline Value size_of(const Value& c) {
    if (c.tag == Value::LIST) return Value(c.list().v.size());
    if (c.tag == Value::STR) return Value(c.str().size());
    fail(std::string("O tipo ") + type_name(c) + " não possui tamanho");
}

inline void append(const Value& l, const Value& v) {
    if (l.tag != Value::LIST) fail(std::string("append exige uma lista, mas recebeu ") + type_name(l));
    l.list().v.push_back(v);
}

inline Value pop(const Value& l) {
    if (l.tag != Value::LIST) fail(std::string("pop exige uma lista, mas recebeu ") + type_name(l));
    auto& v = l.list().v;
    if (v.empty()) fail("pop em lista vazia");
    Value r = v.back();
    v.pop_back();
    return r;
}

inline Value new_list() { return Value::make_list(); }

inline Value new_matrix(const Value& rows, const Value& cols, const Value& fill) {
    if (rows.tag != Value::NUM || cols.tag != Value::NUM)
        fail("matrix exige números de linhas e colunas");
    Value m = Value::make_list();
    for (long long r = 0; r < static_cast<long long>(rows.n); ++r) {
        Value row = Value::make_list();
        row.list().v.assign(static_cast<size_t>(cols.n), fill);
        m.list().v.push_back(row);
    }
    return m;
}

// ----------------------------------------------------------------------------
// Classes e objetos
// ----------------------------------------------------------------------------
inline std::map<std::string, ClassInfo>& class_registry() {
    static std::map<std::string, ClassInfo> r;
    return r;
}

inline void register_class(const std::string& name, const std::string& super,
                           std::map<std::string, Method> methods) {
    ClassInfo ci;
    ci.name = name;
    ci.super = super;
    ci.methods = std::move(methods);
    class_registry()[name] = std::move(ci);
}

inline Value new_obj(const char* cls) {
    auto it = class_registry().find(cls);
    if (it == class_registry().end()) fail(std::string("Classe não registrada: ") + cls);
    return Value::make_obj(&it->second);
}

inline const Method* find_method(const ClassInfo* ci, const std::string& name) {
    while (ci != nullptr) {
        auto it = ci->methods.find(name);
        if (it != ci->methods.end()) return &it->second;
        if (ci->super.empty()) return nullptr;
        auto sup = class_registry().find(ci->super);
        ci = sup == class_registry().end() ? nullptr : &sup->second;
    }
    return nullptr;
}

inline Value get_member(const Value& o, const char* name) {
    if (o.tag != Value::OBJ) fail(std::string("O tipo ") + type_name(o) + " não possui atributos");
    auto& f = o.obj().fields;
    auto it = f.find(name);
    if (it == f.end())
        fail(std::string("Atributo '") + name + "' não existe em '" + o.obj().cls->name + "'");
    return it->second;
}

inline void set_member(const Value& o, const char* name, const Value& v) {
    if (o.tag != Value::OBJ) fail(std::string("O tipo ") + type_name(o) + " não possui atributos");
    o.obj().fields[name] = v;
}

inline void check_arity(const char* what, const Args& a, size_t expected) {
    if (a.size() != expected)
        fail(std::string(what) + " espera " + std::to_string(expected) +
             " argumento(s), mas recebeu " + std::to_string(a.size()));
}

// ----------------------------------------------------------------------------
// Canais de comunicação (implementação real com sockets: Etapa 7)
// ----------------------------------------------------------------------------
struct Channel {
    std::string name, a, b, host;
    int port = 0;
};

inline Value make_channel(const char* name, const char* a, const char* b) {
    auto c = std::make_shared<Channel>();
    c->name = name; c->a = a; c->b = b;
    return Value::make_channel(c);
}

inline Value new_channel(const Value& host, const Value& port) {
    if (host.tag != Value::STR || port.tag != Value::NUM)
        fail("c_channel(endereço, porta) exige uma string e um número");
    auto c = std::make_shared<Channel>();
    c->host = host.str();
    c->port = static_cast<int>(port.n);
    return Value::make_channel(c);
}

[[noreturn]] inline void channels_unavailable() {
    fail("Canais de comunicação ainda não estão disponíveis nesta versão do runtime");
}
inline void chan_send(const Value&, const Args&) { channels_unavailable(); }
inline Value chan_receive(const Value&) { channels_unavailable(); }
inline void chan_close(const Value&) { channels_unavailable(); }

// ----------------------------------------------------------------------------
// Chamada dinâmica de método (objetos e métodos nativos de lista/string/canal)
// ----------------------------------------------------------------------------
inline Value call_method(const Value& o, const char* name, Args args) {
    const std::string m = name;
    if (o.tag == Value::OBJ) {
        const Method* fn = find_method(o.obj().cls, m);
        if (fn == nullptr)
            fail("Método '" + m + "' não declarado em '" + o.obj().cls->name + "'");
        return (*fn)(o, args);
    }
    if (o.tag == Value::LIST) {
        if (m == "append" || m == "push_back") { check_arity(name, args, 1); append(o, args[0]); return Value(); }
        if (m == "pop") { check_arity(name, args, 0); return pop(o); }
        if (m == "size") { check_arity(name, args, 0); return size_of(o); }
    }
    if (o.tag == Value::STR && m == "size") { check_arity(name, args, 0); return size_of(o); }
    if (o.tag == Value::CHAN) {
        if (m == "send") { chan_send(o, args); return Value(); }
        if (m == "receive") { check_arity(name, args, 0); return chan_receive(o); }
        if (m == "close") { check_arity(name, args, 0); chan_close(o); return Value(); }
    }
    fail(std::string("O tipo ") + type_name(o) + " não possui o método '" + m + "'");
}

// ----------------------------------------------------------------------------
// Entrada e saída
// ----------------------------------------------------------------------------
inline std::mutex& io_mutex() {
    static std::mutex m;
    return m;
}

inline void print(std::initializer_list<Value> items) {
    std::string line;
    bool first = true;
    for (const auto& v : items) {
        if (!first) line += ' ';
        first = false;
        line += to_str(v);
    }
    line += '\n';
    std::lock_guard<std::mutex> lock(io_mutex());
    std::fwrite(line.data(), 1, line.size(), stdout);
}

inline Value input() {
    std::fflush(stdout);
    std::string line;
    if (!std::getline(std::cin, line)) return Value(std::string());
    if (!line.empty() && line.back() == '\r') line.pop_back();
    return Value(line);
}

inline Value input(const Value& prompt) {
    {
        std::lock_guard<std::mutex> lock(io_mutex());
        std::string s = to_str(prompt);
        std::fwrite(s.data(), 1, s.size(), stdout);
    }
    return input();
}

// ----------------------------------------------------------------------------
// Funções nativas
// ----------------------------------------------------------------------------
inline double need_num(const Value& v, const char* fn) {
    if (v.tag != Value::NUM) fail(std::string(fn) + " exige um número, mas recebeu " + type_name(v));
    return v.n;
}
inline const std::string& need_str(const Value& v, const char* fn) {
    if (v.tag != Value::STR) fail(std::string(fn) + " exige uma string, mas recebeu " + type_name(v));
    return v.str();
}

inline Value bi_len(const Value& v) { return size_of(v); }

inline Value bi_range(const Value& n) {
    Value r = Value::make_list();
    for (long long i = 0; i < static_cast<long long>(need_num(n, "range")); ++i) r.list().v.push_back(Value(i));
    return r;
}
inline Value bi_range(const Value& a, const Value& b) {
    Value r = Value::make_list();
    for (long long i = static_cast<long long>(need_num(a, "range"));
         i < static_cast<long long>(need_num(b, "range")); ++i)
        r.list().v.push_back(Value(i));
    return r;
}

inline Value bi_to_number(const Value& v) {
    if (v.tag == Value::NUM) return v;
    if (v.tag == Value::BOOL) return Value(v.b ? 1.0 : 0.0);
    const std::string& s = need_str(v, "to_number");
    char* end = nullptr;
    double d = std::strtod(s.c_str(), &end);
    while (end && *end == ' ') ++end;
    if (s.empty() || end == s.c_str() || *end != '\0')
        fail("Não foi possível converter '" + s + "' para número");
    return Value(d);
}
inline Value bi_to_int(const Value& v) { return Value(std::trunc(bi_to_number(v).n)); }
inline Value bi_to_string(const Value& v) { return Value(to_str(v)); }

inline Value bi_parse_ints(const Value& v) {
    const std::string& s = need_str(v, "parse_ints");
    Value r = Value::make_list();
    size_t i = 0;
    while (i < s.size()) {
        while (i < s.size() && std::isspace(static_cast<unsigned char>(s[i]))) ++i;
        if (i >= s.size()) break;
        size_t j = i;
        while (j < s.size() && !std::isspace(static_cast<unsigned char>(s[j]))) ++j;
        std::string tok = s.substr(i, j - i);
        char* end = nullptr;
        long long k = std::strtoll(tok.c_str(), &end, 10);
        if (*end != '\0') fail("'" + tok + "' não é um inteiro válido");
        r.list().v.push_back(Value(k));
        i = j;
    }
    return r;
}

inline Value bi_exp(const Value& x) { return Value(std::exp(need_num(x, "exp"))); }
inline Value bi_sqrt(const Value& x) {
    double d = need_num(x, "sqrt");
    if (d < 0) fail("sqrt de número negativo");
    return Value(std::sqrt(d));
}
inline Value bi_abs(const Value& x) { return Value(std::fabs(need_num(x, "abs"))); }
inline Value bi_floor(const Value& x) { return Value(std::floor(need_num(x, "floor"))); }
inline Value bi_pow(const Value& a, const Value& b) {
    return Value(std::pow(need_num(a, "pow"), need_num(b, "pow")));
}
inline Value bi_max(const Value& a, const Value& b) {
    return Value(std::max(need_num(a, "max"), need_num(b, "max")));
}
inline Value bi_min(const Value& a, const Value& b) {
    return Value(std::min(need_num(a, "min"), need_num(b, "min")));
}

inline Value bi_random() {
    static std::mutex m;
    static std::mt19937_64 gen{std::random_device{}()};
    std::lock_guard<std::mutex> lock(m);
    return Value(std::uniform_real_distribution<double>(0.0, 1.0)(gen));
}

inline Value bi_fmt(const Value& x, const Value& digits) {
    char buf[512];
    std::snprintf(buf, sizeof buf, "%.*f", static_cast<int>(need_num(digits, "fmt")),
                  need_num(x, "fmt"));
    return Value(std::string(buf));
}

inline Value bi_is_digit(const Value& v) {
    const std::string& s = need_str(v, "is_digit");
    if (s.empty()) return Value(false);
    for (unsigned char c : s)
        if (!std::isdigit(c)) return Value(false);
    return Value(true);
}
inline Value bi_is_alpha(const Value& v) {
    const std::string& s = need_str(v, "is_alpha");
    if (s.empty()) return Value(false);
    for (unsigned char c : s)
        if (!std::isalpha(c)) return Value(false);
    return Value(true);
}

inline Value bi_substr(const Value& v, const Value& start, const Value& len) {
    const std::string& s = need_str(v, "substr");
    long long a = static_cast<long long>(need_num(start, "substr"));
    long long n = static_cast<long long>(need_num(len, "substr"));
    if (a < 0 || n < 0 || a > static_cast<long long>(s.size())) return Value(std::string());
    return Value(s.substr(static_cast<size_t>(a), static_cast<size_t>(n)));
}

inline Value bi_split(const Value& v, const Value& sep) {
    const std::string& s = need_str(v, "split");
    const std::string& d = need_str(sep, "split");
    Value r = Value::make_list();
    if (d.empty()) {
        for (char c : s) r.list().v.push_back(Value(std::string(1, c)));
        return r;
    }
    size_t pos = 0;
    while (true) {
        size_t k = s.find(d, pos);
        if (k == std::string::npos) {
            r.list().v.push_back(Value(s.substr(pos)));
            break;
        }
        r.list().v.push_back(Value(s.substr(pos, k - pos)));
        pos = k + d.size();
    }
    return r;
}

inline std::chrono::steady_clock::time_point start_time() {
    static const auto t0 = std::chrono::steady_clock::now();
    return t0;
}
inline Value bi_clock() {
    return Value(std::chrono::duration<double>(std::chrono::steady_clock::now() - start_time()).count());
}
inline Value bi_sleep(const Value& s) {
    std::this_thread::sleep_for(std::chrono::duration<double>(need_num(s, "sleep")));
    return Value();
}

// ----------------------------------------------------------------------------
// Subtarefas: par (um grupo de threads) e fork (threads nomeadas, com núcleo)
// ----------------------------------------------------------------------------
inline void report_task_error(const std::string& name, const std::exception& e) {
    std::lock_guard<std::mutex> lock(io_mutex());
    std::fflush(stdout);
    std::fprintf(stderr, "Erro de execução na subtarefa '%s': %s\n", name.c_str(), e.what());
    failed_flag() = true;
}

// Fixa a thread atual em um núcleo da CPU (quando o sistema permite).
inline void pin_to_core(int core, const std::string& task) {
    unsigned ncores = std::thread::hardware_concurrency();
    if (core < 0) return;
    if (ncores != 0 && static_cast<unsigned>(core) >= ncores) {
        std::lock_guard<std::mutex> lock(io_mutex());
        std::fprintf(stderr, "Aviso: a subtarefa '%s' pediu o núcleo %d, mas a máquina tem %u; "
                             "sem fixação de núcleo\n", task.c_str(), core, ncores);
        return;
    }
#ifdef _WIN32
    SetThreadAffinityMask(GetCurrentThread(), static_cast<DWORD_PTR>(1) << core);
#elif defined(__linux__)
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(core, &set);
    pthread_setaffinity_np(pthread_self(), sizeof(set), &set);
#else
    (void)task;
#endif
}

inline void run_task(const std::string& name, int core, const std::function<void()>& fn) {
    try {
        pin_to_core(core, name);
        fn();
    } catch (const std::exception& e) {
        report_task_error(name, e);
    }
}

class TaskGroup {
    std::vector<std::thread> threads_;
public:
    void spawn(const std::string& name, int core, std::function<void()> fn) {
        threads_.emplace_back([name, core, fn]() { run_task(name, core, fn); });
    }
    void join() {
        for (auto& t : threads_)
            if (t.joinable()) t.join();
        threads_.clear();
    }
    ~TaskGroup() { join(); }
};

class ForkTable {
    std::map<std::string, std::thread> threads_;
    void reap(const std::string& name) {
        auto it = threads_.find(name);
        if (it != threads_.end() && it->second.joinable()) it->second.join();
    }
public:
    void spawn(const std::string& name, const Value& core, std::function<void()> fn) {
        int c = -1;
        if (core.tag == Value::NUM) c = static_cast<int>(core.n);
        reap(name);
        threads_[name] = std::thread([name, c, fn]() { run_task(name, c, fn); });
    }
    void spawn_local(const std::string& name, std::function<void()> fn) {
        spawn(name, Value(), std::move(fn));
    }
    // Execução em outro computador: implementada na Etapa 8 (por enquanto, local).
    void spawn_host(const std::string& name, const Value& host, const Value& port,
                    std::function<void()> fn) {
        {
            std::lock_guard<std::mutex> lock(io_mutex());
            std::fprintf(stderr, "Aviso: 'fork %s on host %s' ainda executa localmente "
                                 "(execução remota na Etapa 8)\n",
                         name.c_str(), to_str(host).c_str());
        }
        (void)port;
        spawn(name, Value(), std::move(fn));
    }
    void join(std::initializer_list<const char*> names) {
        for (const char* n : names) {
            auto it = threads_.find(n);
            if (it == threads_.end()) fail(std::string("join de subtarefa desconhecida: ") + n);
            if (it->second.joinable()) it->second.join();
        }
    }
    void join_all() {
        for (auto& kv : threads_)
            if (kv.second.joinable()) kv.second.join();
    }
    ~ForkTable() { join_all(); }
};

// ----------------------------------------------------------------------------
// Execução do programa
// ----------------------------------------------------------------------------
inline int run_program(const std::function<void()>& init, const std::function<void()>& entry) {
    start_time();
    std::ios::sync_with_stdio(true);
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
#endif
    int code = 0;
    try {
        init();
        entry();
    } catch (const std::exception& e) {
        std::fflush(stdout);
        std::fprintf(stderr, "Erro de execução: %s\n", e.what());
        code = 1;
    }
    std::fflush(stdout);
    if (failed_flag()) code = 1;
    return code;
}

}  // namespace mp
