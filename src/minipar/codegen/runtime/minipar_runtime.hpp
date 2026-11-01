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

#include <cctype>
#include <cerrno>
#include <cstring>
#include <fstream>

#ifdef _WIN32
#  ifndef NOMINMAX
#    define NOMINMAX
#  endif
#  include <winsock2.h>
#  include <ws2tcpip.h>
#  include <windows.h>
#else
#  include <arpa/inet.h>
#  include <netdb.h>
#  include <netinet/in.h>
#  include <netinet/tcp.h>
#  include <signal.h>
#  include <sys/select.h>
#  include <sys/socket.h>
#  include <sys/types.h>
#  include <unistd.h>
#  ifdef __linux__
#    include <pthread.h>
#    include <sched.h>
#  endif
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

inline std::mutex& io_mutex() {
    static std::mutex m;
    return m;
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
// Configuração de execução (--node, --hosts) e endereços dos computadores
// ----------------------------------------------------------------------------
struct Config {
    std::string node;                                // quem é este programa (ex.: computador_1)
    std::map<std::string, std::string> hosts;        // computador -> endereço
    std::map<std::string, int> ports;                // canal -> porta
    double timeout = 120.0;                          // segundos para conectar/aguardar
    int worker_port = 0;                             // > 0: executa como trabalhador remoto
    int worker_tasks = 0;                            // trabalhador encerra após N tarefas (0 = sempre)
};

inline Config& config() {
    static Config c;
    return c;
}

inline std::string trim_str(const std::string& s) {
    size_t a = 0, b = s.size();
    while (a < b && std::isspace(static_cast<unsigned char>(s[a]))) ++a;
    while (b > a && std::isspace(static_cast<unsigned char>(s[b - 1]))) --b;
    return s.substr(a, b - a);
}

// Formato do arquivo (minipar.hosts):
//   # comentário
//   computador_1 = 127.0.0.1
//   computador_2 = 192.168.0.20
//   port.calculadora = 7000        (porta do canal "calculadora", opcional)
inline void load_hosts_file(const std::string& path, bool required) {
    std::ifstream f(path);
    if (!f) {
        if (required) fail("Não foi possível abrir o arquivo de computadores: " + path);
        return;
    }
    std::string line;
    int n = 0;
    while (std::getline(f, line)) {
        ++n;
        size_t hash = line.find('#');
        if (hash != std::string::npos) line.erase(hash);
        line = trim_str(line);
        if (line.empty()) continue;
        size_t eq = line.find('=');
        if (eq == std::string::npos)
            fail(path + ":" + std::to_string(n) + ": esperava 'nome = valor'");
        std::string key = trim_str(line.substr(0, eq));
        std::string val = trim_str(line.substr(eq + 1));
        if (key.rfind("port.", 0) == 0) {
            char* end = nullptr;
            long port = std::strtol(val.c_str(), &end, 10);
            if (val.empty() || *end != '\0' || port < 1 || port > 65535)
                fail(path + ":" + std::to_string(n) + ": porta inválida '" + val + "'");
            config().ports[key.substr(5)] = static_cast<int>(port);
        } else {
            config().hosts[key] = val;
        }
    }
}

inline int default_port(const std::string& channel) {
    uint32_t h = 2166136261u;                         // FNV-1a: o mesmo valor em todos os computadores
    for (unsigned char c : channel) { h ^= c; h *= 16777619u; }
    return 20000 + static_cast<int>(h % 20000u);
}

inline int port_of(const std::string& channel) {
    auto it = config().ports.find(channel);
    return it != config().ports.end() ? it->second : default_port(channel);
}

inline std::string host_of(const std::string& endpoint) {
    auto it = config().hosts.find(endpoint);
    return it != config().hosts.end() ? it->second : "127.0.0.1";
}

// ----------------------------------------------------------------------------
// Sockets TCP (POSIX e Winsock)
// ----------------------------------------------------------------------------
#ifdef _WIN32
using sock_t = SOCKET;
inline const sock_t BAD_SOCK = INVALID_SOCKET;
inline void close_socket(sock_t s) { closesocket(s); }
#else
using sock_t = int;
constexpr sock_t BAD_SOCK = -1;
inline void close_socket(sock_t s) { ::close(s); }
#endif
#ifndef MSG_NOSIGNAL
#  define MSG_NOSIGNAL 0
#endif

inline void net_init() {
#ifdef _WIN32
    static bool done = []() { WSADATA d; WSAStartup(MAKEWORD(2, 2), &d); return true; }();
#else
    static bool done = []() { signal(SIGPIPE, SIG_IGN); return true; }();
#endif
    (void)done;
}

inline void net_log(const std::string& msg) {
    std::lock_guard<std::mutex> lock(io_mutex());
    std::fprintf(stderr, "[rede] %s\n", msg.c_str());
}

inline void set_nodelay(sock_t s) {
    int yes = 1;
    setsockopt(s, IPPROTO_TCP, TCP_NODELAY, reinterpret_cast<const char*>(&yes), sizeof yes);
}

// Conecta com novas tentativas (a ordem de início dos programas não importa).
inline sock_t tcp_connect(const std::string& host, int port, double timeout) {
    net_init();
    auto start = std::chrono::steady_clock::now();
    bool warned = false;
    while (true) {
        addrinfo hints;
        std::memset(&hints, 0, sizeof hints);
        hints.ai_family = AF_UNSPEC;
        hints.ai_socktype = SOCK_STREAM;
        addrinfo* res = nullptr;
        std::string service = std::to_string(port);
        if (getaddrinfo(host.c_str(), service.c_str(), &hints, &res) == 0) {
            for (addrinfo* p = res; p != nullptr; p = p->ai_next) {
                sock_t s = ::socket(p->ai_family, p->ai_socktype, p->ai_protocol);
                if (s == BAD_SOCK) continue;
                if (::connect(s, p->ai_addr, static_cast<int>(p->ai_addrlen)) == 0) {
                    freeaddrinfo(res);
                    set_nodelay(s);
                    return s;
                }
                close_socket(s);
            }
            freeaddrinfo(res);
        }
        double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
        if (elapsed >= timeout)
            fail("Não foi possível conectar a " + host + ":" + std::to_string(port) + " depois de " +
                 num_to_str(timeout) + " s. O outro programa está em execução?");
        if (!warned) {
            net_log("aguardando o outro programa em " + host + ":" + std::to_string(port) + " ...");
            warned = true;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
}

// Abre a porta para receber conexões.
inline sock_t open_listener(int port) {
    net_init();
    sock_t ls = ::socket(AF_INET, SOCK_STREAM, 0);
    if (ls == BAD_SOCK) fail("Não foi possível criar o socket");
    int yes = 1;
    setsockopt(ls, SOL_SOCKET, SO_REUSEADDR, reinterpret_cast<const char*>(&yes), sizeof yes);
    sockaddr_in addr;
    std::memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(static_cast<unsigned short>(port));
    if (::bind(ls, reinterpret_cast<sockaddr*>(&addr), sizeof addr) != 0 || ::listen(ls, 16) != 0) {
        close_socket(ls);
        fail("Não foi possível abrir a porta " + std::to_string(port) + " (já está em uso?)");
    }
    return ls;
}

// Abre a porta e espera uma conexão.
inline sock_t tcp_accept(int port, double timeout) {
    sock_t ls = open_listener(port);
    net_log("aguardando conexão na porta " + std::to_string(port) + " ...");
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(ls, &fds);
    timeval tv;
    tv.tv_sec = static_cast<long>(timeout);
    tv.tv_usec = static_cast<long>((timeout - static_cast<long>(timeout)) * 1e6);
    int r = ::select(static_cast<int>(ls) + 1, &fds, nullptr, nullptr, &tv);
    if (r <= 0) {
        close_socket(ls);
        fail("Tempo esgotado (" + num_to_str(timeout) + " s) aguardando conexão na porta " +
             std::to_string(port));
    }
    sock_t c = ::accept(ls, nullptr, nullptr);
    close_socket(ls);
    if (c == BAD_SOCK) fail("Falha ao aceitar a conexão");
    set_nodelay(c);
    return c;
}

inline void send_all(sock_t s, const char* d, size_t n) {
    while (n > 0) {
#ifdef _WIN32
        int k = ::send(s, d, static_cast<int>(n), 0);
#else
        ssize_t k = ::send(s, d, n, MSG_NOSIGNAL);
#endif
        if (k <= 0) fail("Falha ao enviar pela conexão (o outro programa encerrou?)");
        d += k;
        n -= static_cast<size_t>(k);
    }
}

inline void recv_all(sock_t s, char* d, size_t n) {
    while (n > 0) {
#ifdef _WIN32
        int k = ::recv(s, d, static_cast<int>(n), 0);
#else
        ssize_t k = ::recv(s, d, n, 0);
#endif
        if (k == 0) fail("Conexão encerrada pelo outro programa");
        if (k < 0) fail("Falha ao receber pela conexão");
        d += k;
        n -= static_cast<size_t>(k);
    }
}

// ----------------------------------------------------------------------------
// Mensagens: serialização de valores (número, string, bool, null e listas)
// ----------------------------------------------------------------------------
inline void put_u32(std::string& out, uint32_t v) {
    for (int i = 3; i >= 0; --i) out.push_back(static_cast<char>((v >> (8 * i)) & 0xFF));
}

inline void encode(const Value& v, std::string& out) {
    switch (v.tag) {
        case Value::NIL: out.push_back(0); break;
        case Value::BOOL: out.push_back(1); out.push_back(v.b ? 1 : 0); break;
        case Value::NUM: {
            uint64_t bits;
            std::memcpy(&bits, &v.n, 8);
            out.push_back(2);
            for (int i = 7; i >= 0; --i) out.push_back(static_cast<char>((bits >> (8 * i)) & 0xFF));
            break;
        }
        case Value::STR:
            out.push_back(3);
            put_u32(out, static_cast<uint32_t>(v.str().size()));
            out += v.str();
            break;
        case Value::LIST:
            out.push_back(4);
            put_u32(out, static_cast<uint32_t>(v.list().v.size()));
            for (const auto& item : v.list().v) encode(item, out);
            break;
        default:
            fail(std::string("Um valor do tipo ") + type_name(v) +
                 " não pode ser enviado por um canal (use números, strings, bool, null e listas)");
    }
}

inline Value decode(const std::string& buf, size_t& pos, int depth = 0) {
    auto need = [&](size_t n) {
        if (pos + n > buf.size()) fail("Mensagem recebida está corrompida");
    };
    if (depth > 64) fail("Mensagem recebida tem listas aninhadas demais");
    need(1);
    unsigned char tag = static_cast<unsigned char>(buf[pos++]);
    switch (tag) {
        case 0: return Value();
        case 1: need(1); return Value(buf[pos++] != 0);
        case 2: {
            need(8);
            uint64_t bits = 0;
            for (int i = 0; i < 8; ++i) bits = (bits << 8) | static_cast<unsigned char>(buf[pos++]);
            double d;
            std::memcpy(&d, &bits, 8);
            return Value(d);
        }
        case 3: {
            need(4);
            uint32_t n = 0;
            for (int i = 0; i < 4; ++i) n = (n << 8) | static_cast<unsigned char>(buf[pos++]);
            need(n);
            Value r{std::string(buf, pos, n)};
            pos += n;
            return r;
        }
        case 4: {
            need(4);
            uint32_t n = 0;
            for (int i = 0; i < 4; ++i) n = (n << 8) | static_cast<unsigned char>(buf[pos++]);
            Value r = Value::make_list();
            for (uint32_t i = 0; i < n; ++i) r.list().v.push_back(decode(buf, pos, depth + 1));
            return r;
        }
        default: fail("Mensagem recebida tem um tipo desconhecido");
    }
}

// Quadro = 4 bytes com o tamanho + conteúdo.
inline void send_frame(sock_t s, const std::string& payload) {
    if (payload.size() > 0x7FFFFFFFu) fail("Mensagem grande demais");
    std::string frame;
    put_u32(frame, static_cast<uint32_t>(payload.size()));
    frame += payload;
    send_all(s, frame.data(), frame.size());
}

inline std::string recv_frame(sock_t s) {
    char head[4];
    recv_all(s, head, 4);
    uint32_t n = 0;
    for (int i = 0; i < 4; ++i) n = (n << 8) | static_cast<unsigned char>(head[i]);
    if (n > 0x40000000u) fail("Mensagem recebida é grande demais");
    std::string payload(n, '\0');
    if (n > 0) recv_all(s, &payload[0], n);
    return payload;
}

// ----------------------------------------------------------------------------
// Canais de comunicação
//   * declarado:   c_channel canal computador_1 computador_2;
//       o computador_1 conecta e o computador_2 escuta (o endereço de cada um vem
//       de minipar.hosts; quem é este programa vem de --node)
//   * expressão:   c_channel("ip", porta)
//       conecta ao endereço; com "" ou "0.0.0.0" como endereço, escuta na porta
// ----------------------------------------------------------------------------
struct Channel {
    enum Kind { DECLARED, CLIENT, SERVER };
    Kind kind = DECLARED;
    std::string name, a, b, host;
    int port = 0;
    sock_t fd = BAD_SOCK;
    std::mutex conn_m, send_m, recv_m;
    bool closed = false;
    ~Channel() {
        if (fd != BAD_SOCK) close_socket(fd);
    }
};

inline Value make_channel(const char* name, const char* a, const char* b) {
    auto c = std::make_shared<Channel>();
    c->kind = Channel::DECLARED;
    c->name = name; c->a = a; c->b = b;
    return Value::make_channel(c);
}

inline Value new_channel(const Value& host, const Value& port) {
    if (host.tag != Value::STR || port.tag != Value::NUM)
        fail("c_channel(endereço, porta) exige uma string e um número");
    auto c = std::make_shared<Channel>();
    c->host = host.str();
    c->port = static_cast<int>(port.n);
    c->kind = (c->host.empty() || c->host == "0.0.0.0" || c->host == "*") ? Channel::SERVER
                                                                          : Channel::CLIENT;
    return Value::make_channel(c);
}

inline Channel& need_channel(const Value& v, const char* what) {
    if (v.tag != Value::CHAN)
        fail(std::string(what) + " exige um canal (c_channel), mas recebeu " + type_name(v));
    return v.chan();
}

// Estabelece a conexão na primeira vez que o canal é usado.
inline void ensure_connected(Channel& c) {
    std::lock_guard<std::mutex> lock(c.conn_m);
    if (c.closed) fail("O canal já foi fechado");
    if (c.fd != BAD_SOCK) return;
    double timeout = config().timeout;
    if (c.kind == Channel::DECLARED) {
        const std::string& me = config().node;
        if (me != c.a && me != c.b) {
            fail("O canal '" + c.name + "' liga '" + c.a + "' e '" + c.b + "'. Informe qual deles este "
                 "programa é, por exemplo: --node " + c.a +
                 (me.empty() ? "" : "  (valor atual: '" + me + "')"));
        }
        int port = port_of(c.name);
        if (me == c.a) c.fd = tcp_connect(host_of(c.b), port, timeout);
        else c.fd = tcp_accept(port, timeout);
    } else if (c.kind == Channel::CLIENT) {
        c.fd = tcp_connect(c.host, c.port, timeout);
    } else {
        c.fd = tcp_accept(c.port, timeout);
    }
}

inline void chan_send(const Value& ch, const Args& args) {
    Channel& c = need_channel(ch, "send");
    std::string payload;
    payload.push_back(4);
    put_u32(payload, static_cast<uint32_t>(args.size()));
    for (const auto& a : args) encode(a, payload);
    if (payload.size() > 0x7FFFFFFFu) fail("Mensagem grande demais");
    std::string frame;
    put_u32(frame, static_cast<uint32_t>(payload.size()));
    frame += payload;
    ensure_connected(c);
    std::lock_guard<std::mutex> lock(c.send_m);
    send_all(c.fd, frame.data(), frame.size());
}

inline Value chan_receive(const Value& ch) {
    Channel& c = need_channel(ch, "receive");
    ensure_connected(c);
    std::lock_guard<std::mutex> lock(c.recv_m);
    char head[4];
    recv_all(c.fd, head, 4);
    uint32_t n = 0;
    for (int i = 0; i < 4; ++i) n = (n << 8) | static_cast<unsigned char>(head[i]);
    if (n > 0x40000000u) fail("Mensagem recebida é grande demais");
    std::string payload(n, '\0');
    if (n > 0) recv_all(c.fd, &payload[0], n);
    size_t pos = 0;
    return decode(payload, pos);
}

inline void chan_close(const Value& ch) {
    Channel& c = need_channel(ch, "close");
    std::lock_guard<std::mutex> lock(c.conn_m);
    if (c.fd != BAD_SOCK) {
        close_socket(c.fd);
        c.fd = BAD_SOCK;
    }
    c.closed = true;
}

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

inline std::mt19937_64& rng() {
    static std::mt19937_64 gen{std::random_device{}()};
    return gen;
}
inline std::mutex& rng_mutex() {
    static std::mutex m;
    return m;
}

inline Value bi_random() {
    std::lock_guard<std::mutex> lock(rng_mutex());
    return Value(std::uniform_real_distribution<double>(0.0, 1.0)(rng()));
}

// Fixa a semente do gerador aleatório (execuções reproduzíveis).
inline Value bi_seed(const Value& s) {
    std::lock_guard<std::mutex> lock(rng_mutex());
    rng().seed(static_cast<uint64_t>(need_num(s, "seed")));
    return Value();
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

inline Value bi_trim(const Value& v) {
    const std::string& s = need_str(v, "trim");
    size_t a = 0, b = s.size();
    while (a < b && std::isspace(static_cast<unsigned char>(s[a]))) ++a;
    while (b > a && std::isspace(static_cast<unsigned char>(s[b - 1]))) --b;
    return Value(s.substr(a, b - a));
}

inline Value bi_write_file(const Value& path, const Value& text) {
    const std::string& p = need_str(path, "write_file");
    const std::string& t = need_str(text, "write_file");
    FILE* f = std::fopen(p.c_str(), "wb");
    if (f == nullptr) fail("Não foi possível abrir '" + p + "' para escrita");
    std::fwrite(t.data(), 1, t.size(), f);
    std::fclose(f);
    return Value();
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
// Subtarefas: par (grupo de threads) e fork (threads nomeadas, com núcleo e resultado)
//
// Cada subtarefa é uma função registrada pelo programa (register_task) e recebe
// CÓPIAS dos valores que usa, como um processo independente: a comunicação com
// o programa principal é só pelo valor devolvido (join) ou por canais.
// ----------------------------------------------------------------------------
using TaskFn = std::function<Value(Args&)>;

inline std::map<std::string, TaskFn>& task_registry() {
    static std::map<std::string, TaskFn> r;
    return r;
}

inline void register_task(const std::string& id, TaskFn fn) { task_registry()[id] = std::move(fn); }

inline Value run_registered(const std::string& id, Args& args) {
    auto it = task_registry().find(id);
    if (it == task_registry().end())
        fail("Tarefa desconhecida: '" + id + "' (o programa deste computador é o mesmo código compilado?)");
    return it->second(args);
}

// Cópia profunda de listas e objetos (canais são compartilhados, para poder comunicar).
inline Value copy_for_task(const Value& v, std::unordered_map<const void*, Value>& seen) {
    if (v.tag == Value::LIST) {
        auto it = seen.find(v.p.get());
        if (it != seen.end()) return it->second;
        Value r = Value::make_list();
        seen[v.p.get()] = r;
        r.list().v.reserve(v.list().v.size());
        for (const auto& item : v.list().v) r.list().v.push_back(copy_for_task(item, seen));
        return r;
    }
    if (v.tag == Value::OBJ) {
        auto it = seen.find(v.p.get());
        if (it != seen.end()) return it->second;
        Value r = Value::make_obj(v.obj().cls);
        seen[v.p.get()] = r;
        for (const auto& kv : v.obj().fields) r.obj().fields[kv.first] = copy_for_task(kv.second, seen);
        return r;
    }
    return v;
}

inline Value copy_for_task(const Value& v) {
    std::unordered_map<const void*, Value> seen;
    return copy_for_task(v, seen);
}

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

inline Value run_task(const std::string& name, int core, const std::function<Value()>& fn) {
    try {
        pin_to_core(core, name);
        return fn();
    } catch (const std::exception& e) {
        report_task_error(name, e);
        return Value();
    }
}

// par { ... }: uma thread por comando; o join é feito ao final do bloco.
class TaskGroup {
    std::vector<std::thread> threads_;
public:
    void spawn(const std::string& name, int core, const std::string& id, Args args) {
        threads_.emplace_back([name, core, id, args]() mutable {
            run_task(name, core, [&]() { return run_registered(id, args); });
        });
    }
    void join() {
        for (auto& t : threads_)
            if (t.joinable()) t.join();
        threads_.clear();
    }
    ~TaskGroup() { join(); }
};

// ----------------------------------------------------------------------------
// Execução remota: o mesmo programa executado com --worker PORTA no outro computador
// recebe o nome da tarefa e as cópias das variáveis, executa e devolve o resultado.
// ----------------------------------------------------------------------------
inline std::string resolve_host(const std::string& h) {
    auto it = config().hosts.find(h);
    return it != config().hosts.end() ? it->second : h;
}

inline Value remote_call(const std::string& name, const Value& host, const Value& port,
                         const std::string& id, const Args& args) {
    if (host.tag != Value::STR) fail("fork ... on host exige o endereço do computador como string");
    int p = port.tag == Value::NUM ? static_cast<int>(port.n) : 9000;
    std::string h = resolve_host(host.str());
    std::string payload;
    Value arglist = Value::make_list();
    arglist.list().v = args;
    payload.push_back(4);
    put_u32(payload, 3);
    encode(Value("run"), payload);
    encode(Value(id), payload);
    encode(arglist, payload);                      // falha aqui se algum valor não for serializável

    sock_t s = tcp_connect(h, p, config().timeout);
    struct Closer { sock_t s; ~Closer() { close_socket(s); } } closer{s};
    send_frame(s, payload);
    std::string resp = recv_frame(s);
    size_t pos = 0;
    Value r = decode(resp, pos);
    if (r.tag != Value::LIST || r.list().v.size() != 2 || r.list().v[0].tag != Value::STR)
        fail("Resposta inválida do trabalhador em " + h + ":" + std::to_string(p));
    if (r.list().v[0].str() != "ok")
        fail("A tarefa remota '" + name + "' falhou em " + h + ":" + std::to_string(p) + ": " +
             to_str(r.list().v[1]));
    return r.list().v[1];
}

inline void handle_worker_connection(sock_t s) {
    auto reply = [&](const char* status, const Value& v) {
        Value msg = Value::make_list();
        msg.list().v.push_back(Value(status));
        msg.list().v.push_back(v);
        std::string payload;
        encode(msg, payload);
        send_frame(s, payload);
    };
    try {
        std::string payload = recv_frame(s);
        size_t pos = 0;
        Value req = decode(payload, pos);
        if (req.tag != Value::LIST || req.list().v.size() != 3 || !req.list().v[0].is_str() ||
            req.list().v[0].str() != "run" || !req.list().v[1].is_str() || !req.list().v[2].is_list())
            fail("Pedido inválido");
        std::string id = req.list().v[1].str();
        Args args = req.list().v[2].list().v;
        Value result = run_registered(id, args);
        reply("ok", result);
    } catch (const std::exception& e) {
        try { reply("erro", Value(std::string(e.what()))); } catch (...) {}
    }
    close_socket(s);
}

// Modo trabalhador: atende pedidos de execução de tarefas.
inline void serve_worker(int port, int max_tasks) {
    sock_t ls = open_listener(port);
    net_log("trabalhador aguardando tarefas na porta " + std::to_string(port) + " ...");
    std::vector<std::thread> handlers;
    int served = 0;
    while (max_tasks <= 0 || served < max_tasks) {
        sock_t c = ::accept(ls, nullptr, nullptr);
        if (c == BAD_SOCK) continue;
        set_nodelay(c);
        ++served;
        handlers.emplace_back(handle_worker_connection, c);
    }
    for (auto& t : handlers) t.join();
    close_socket(ls);
}

// fork nome [on core N | on host H, P] { ... }: threads nomeadas, com resultado (join).
class ForkTable {
    struct Entry {
        std::thread th;
        Value result;
    };
    std::map<std::string, std::unique_ptr<Entry>> tasks_;

    void reap(const std::string& name) {
        auto it = tasks_.find(name);
        if (it == tasks_.end()) return;
        if (it->second->th.joinable()) it->second->th.join();
        tasks_.erase(it);
    }
public:
    void spawn(const std::string& name, const Value& core, const std::string& id, Args args) {
        int c = core.tag == Value::NUM ? static_cast<int>(core.n) : -1;
        reap(name);
        auto e = std::make_unique<Entry>();
        Entry* raw = e.get();
        raw->th = std::thread([raw, name, c, id, args]() mutable {
            raw->result = run_task(name, c, [&]() { return run_registered(id, args); });
        });
        tasks_[name] = std::move(e);
    }
    void spawn_host(const std::string& name, const Value& host, const Value& port,
                    const std::string& id, Args args) {
        reap(name);
        auto e = std::make_unique<Entry>();
        Entry* raw = e.get();
        raw->th = std::thread([raw, name, host, port, id, args]() {
            raw->result = run_task(name, -1, [&]() { return remote_call(name, host, port, id, args); });
        });
        tasks_[name] = std::move(e);
    }
    void join(std::initializer_list<const char*> names) {
        for (const char* n : names) {
            auto it = tasks_.find(n);
            if (it == tasks_.end()) fail(std::string("join de subtarefa desconhecida: ") + n);
            if (it->second->th.joinable()) it->second->th.join();
        }
    }
    Value join_value(const char* name) {
        auto it = tasks_.find(name);
        if (it == tasks_.end()) fail(std::string("join de subtarefa desconhecida: ") + name);
        if (it->second->th.joinable()) it->second->th.join();
        return it->second->result;
    }
    void join_all() {
        for (auto& kv : tasks_)
            if (kv.second->th.joinable()) kv.second->th.join();
    }
    ~ForkTable() { join_all(); }
};

// ----------------------------------------------------------------------------
// Execução do programa
//   opções:  --node NOME   quem este programa é (ex.: computador_1)
//            --hosts ARQ   arquivo de endereços (padrão: minipar.hosts, se existir)
//   variáveis de ambiente: MINIPAR_NODE, MINIPAR_HOSTS, MINIPAR_TIMEOUT (segundos)
// ----------------------------------------------------------------------------
inline bool parse_args(int argc, char** argv, std::string& hosts_file) {
    if (const char* e = std::getenv("MINIPAR_NODE")) config().node = e;
    if (const char* e = std::getenv("MINIPAR_HOSTS")) hosts_file = e;
    if (const char* e = std::getenv("MINIPAR_TIMEOUT")) config().timeout = std::atof(e);
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        auto value_of = [&](const char* flag, std::string& out) {
            std::string f = flag;
            if (a == f) {
                if (i + 1 >= argc) fail("A opção " + f + " precisa de um valor");
                out = argv[++i];
                return true;
            }
            if (a.rfind(f + "=", 0) == 0) {
                out = a.substr(f.size() + 1);
                return true;
            }
            return false;
        };
        if (a == "--help" || a == "-h") {
            std::printf("Uso: %s [--node NOME] [--hosts ARQUIVO] [--worker PORTA [--worker-tasks N]]\n"
                        "  --node NOME        quem este programa é (ex.: computador_1)\n"
                        "  --hosts ARQUIVO    endereços dos computadores (padrão: minipar.hosts)\n"
                        "  --worker PORTA     modo trabalhador: executa tarefas enviadas por\n"
                        "                     'fork ... on host' de outro computador\n"
                        "  --worker-tasks N   o trabalhador encerra depois de N tarefas (padrão: sempre)\n",
                        argv[0]);
            return false;
        }
        std::string tmp;
        if (value_of("--node", config().node)) continue;
        if (value_of("--hosts", hosts_file)) continue;
        if (value_of("--worker", tmp)) { config().worker_port = std::atoi(tmp.c_str()); continue; }
        if (value_of("--worker-tasks", tmp)) { config().worker_tasks = std::atoi(tmp.c_str()); continue; }
    }
    return true;
}

inline int run_program(int argc, char** argv, const std::function<void()>& init,
                       const std::function<void()>& entry) {
    start_time();
    std::ios::sync_with_stdio(true);
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
#endif
    int code = 0;
    try {
        std::string hosts_file;
        if (!parse_args(argc, argv, hosts_file)) return 0;
        if (!hosts_file.empty()) load_hosts_file(hosts_file, true);
        else load_hosts_file("minipar.hosts", false);
        init();
        if (config().worker_port > 0) serve_worker(config().worker_port, config().worker_tasks);
        else entry();
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
