"""Definição dos tokens da linguagem MiniPar 2026.2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Palavras reservadas (herdadas da 2026.1 + fork/join da 2026.2 + null).
# Obs.: "on", "core" e "host" NÃO são reservadas: o parser as reconhece
# como palavras contextuais logo após "fork <nome>".
KEYWORDS = {
    "class", "extends", "new", "func", "var",
    "if", "else", "while", "do", "for", "in",
    "break", "continue", "return",
    "seq", "par", "fork", "join", "this",
    "c_channel", "send", "receive", "input", "print", "matrix",
    "true", "false", "null",
}

# Tipos declaráveis ("float" é novo na 2026.2).
TYPE_KEYWORDS = {"number", "int", "float", "string", "bool", "void", "list", "dict"}

# Operadores de dois caracteres (testados antes dos de um caractere).
OPERATORS_2 = {"==", "!=", "<=", ">=", "&&", "||", "+=", "-=", "*=", "/="}

OPERATORS_1 = {"+", "-", "*", "/", "%", "<", ">", "=", "!"}

DELIMITERS = {"(", ")", "{", "}", "[", "]", ".", ";", ",", ":"}

# Categorias usadas na exibição (CLI e interface web).
CAT_KEYWORD = "PALAVRA_RESERVADA"
CAT_TYPE = "TIPO"
CAT_IDENT = "IDENTIFICADOR"
CAT_NUMBER = "NUMERO"
CAT_STRING = "STRING"
CAT_OPERATOR = "OPERADOR"
CAT_DELIMITER = "DELIMITADOR"
CAT_EOF = "EOF"

# Nomes de tipo especiais (não-literais) de token.
T_IDENT = "IDENTIFIER"
T_NUMBER = "NUMBER"
T_STRING = "STRING"
T_EOF = "EOF"


@dataclass(frozen=True)
class Token:
    """Um token.

    type   : para palavras reservadas, tipos, operadores e delimitadores é o
             próprio texto (ex.: "while", "==", "{"). Para os demais é
             IDENTIFIER, NUMBER, STRING ou EOF.
    lexeme : texto exato lido do código-fonte.
    value  : valor já convertido (int/float para NUMBER, str decodificada
             para STRING, bool para true/false, None para null).
    """

    type: str
    lexeme: str
    line: int
    col: int
    value: Any = None

    @property
    def category(self) -> str:
        if self.type == T_IDENT:
            return CAT_IDENT
        if self.type == T_NUMBER:
            return CAT_NUMBER
        if self.type == T_STRING:
            return CAT_STRING
        if self.type == T_EOF:
            return CAT_EOF
        if self.type in TYPE_KEYWORDS:
            return CAT_TYPE
        if self.type in KEYWORDS:
            return CAT_KEYWORD
        if self.type in DELIMITERS:
            return CAT_DELIMITER
        return CAT_OPERATOR

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "lexeme": self.lexeme,
            "category": self.category,
            "value": self.value,
            "line": self.line,
            "col": self.col,
        }

    def __str__(self) -> str:
        return f"<{self.type} {self.lexeme!r} @{self.line}:{self.col}>"
