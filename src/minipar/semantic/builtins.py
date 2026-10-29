"""Biblioteca nativa da linguagem MiniPar 2026.2 (assinaturas para o semântico).

Cada função é descrita por: (mínimo de argumentos, máximo de argumentos,
tipo de retorno, tipos aceitos por posição). Um conjunto vazio em uma posição
significa "qualquer tipo". UNKNOWN sempre é aceito pelo verificador.
"""

from ..symtable.types import BOOL, LIST, MATRIX, NUMBER, STRING, UNKNOWN, VOID

ANY = frozenset()
_ITER = frozenset({LIST, STRING, MATRIX})

# nome: (min, max, retorno, [tipos aceitos por argumento])
FUNCTIONS = {
    "len":        (1, 1, NUMBER, [_ITER]),
    "range":      (1, 2, LIST,   [frozenset({NUMBER}), frozenset({NUMBER})]),
    "to_number":  (1, 1, NUMBER, [frozenset({STRING, NUMBER, BOOL})]),
    "to_int":     (1, 1, NUMBER, [frozenset({STRING, NUMBER, BOOL})]),
    "to_string":  (1, 1, STRING, [ANY]),
    "parse_ints": (1, 1, LIST,   [frozenset({STRING})]),
    "exp":        (1, 1, NUMBER, [frozenset({NUMBER})]),
    "sqrt":       (1, 1, NUMBER, [frozenset({NUMBER})]),
    "abs":        (1, 1, NUMBER, [frozenset({NUMBER})]),
    "floor":      (1, 1, NUMBER, [frozenset({NUMBER})]),
    "pow":        (2, 2, NUMBER, [frozenset({NUMBER}), frozenset({NUMBER})]),
    "max":        (2, 2, NUMBER, [frozenset({NUMBER}), frozenset({NUMBER})]),
    "min":        (2, 2, NUMBER, [frozenset({NUMBER}), frozenset({NUMBER})]),
    "random":     (0, 0, NUMBER, []),
    "fmt":        (2, 2, STRING, [frozenset({NUMBER}), frozenset({NUMBER})]),
    "is_digit":   (1, 1, BOOL,   [frozenset({STRING})]),
    "is_alpha":   (1, 1, BOOL,   [frozenset({STRING})]),
    "substr":     (3, 3, STRING, [frozenset({STRING}), frozenset({NUMBER}), frozenset({NUMBER})]),
    "split":      (2, 2, LIST,   [frozenset({STRING}), frozenset({STRING})]),
    "clock":      (0, 0, NUMBER, []),
    "sleep":      (1, 1, VOID,   [frozenset({NUMBER})]),
}

# Métodos nativos por tipo: nome: (min, max, retorno)
LIST_METHODS = {
    "append":    (1, 1, VOID),
    "push_back": (1, 1, VOID),
    "pop":       (0, 0, UNKNOWN),
    "size":      (0, 0, NUMBER),
}
STRING_METHODS = {
    "size": (0, 0, NUMBER),
}
CHANNEL_METHODS = {
    "send":    (1, None, VOID),   # None = sem limite superior
    "receive": (0, 0, LIST),
    "close":   (0, 0, VOID),
}
