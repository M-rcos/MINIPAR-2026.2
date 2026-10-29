"""Nomes de tipos usados pela Tabela de Símbolos e pelo Analisador Semântico.

Os tipos numéricos declaráveis (int, float, number) pertencem à mesma família
e são tratados como NUMBER. Classes definidas pelo usuário usam o próprio nome
da classe como tipo. UNKNOWN é compatível com qualquer tipo (tipo ainda não
inferido, como parâmetros sem tipo); isso evita erros em cascata.
"""

NUMBER = "number"
STRING = "string"
BOOL = "bool"
LIST = "list"
DICT = "dict"
MATRIX = "matrix"
CHANNEL = "c_channel"
VOID = "void"
NULL = "null"
UNKNOWN = "unknown"

_NUMERIC_NAMES = {"int", "float", "number"}


def normalize_declared(type_name):
    """Converte o tipo escrito no código para o tipo canônico."""
    if type_name is None:
        return UNKNOWN
    if type_name in _NUMERIC_NAMES:
        return NUMBER
    return type_name
