"""Analisador Léxico (Lexer) da linguagem MiniPar 2026.2.

Varre o código-fonte caractere a caractere (autômato manual) e produz uma
lista de tokens. Comentários iniciados por '#' são descartados.

Tratamento de erros: ao encontrar um problema (caractere inválido, string
não terminada, número malformado...) o lexer registra um LexicalError e
continua a análise (recuperação em modo pânico), para reportar vários erros
de uma só vez.
"""

from __future__ import annotations

from typing import List

from ..common import LexicalError, MiniParError
from .interface import ILexer
from .tokens import (
    DELIMITERS,
    KEYWORDS,
    OPERATORS_1,
    OPERATORS_2,
    T_EOF,
    T_IDENT,
    T_NUMBER,
    T_STRING,
    TYPE_KEYWORDS,
    Token,
)

_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "0": "\0"}


class Lexer(ILexer):
    def __init__(self, source: str):
        self._src = source
        self._pos = 0
        self._line = 1
        self._col = 1
        self._errors: List[MiniParError] = []

    # ------------------------------------------------------------------
    # Interface ILexer
    # ------------------------------------------------------------------
    @property
    def errors(self) -> List[MiniParError]:
        return self._errors

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            self._skip_blank_and_comments()
            if self._eof():
                break
            tok = self._next_token()
            if tok is not None:
                tokens.append(tok)
        tokens.append(Token(T_EOF, "", self._line, self._col))
        return tokens

    # ------------------------------------------------------------------
    # Utilitários de leitura
    # ------------------------------------------------------------------
    def _eof(self) -> bool:
        return self._pos >= len(self._src)

    def _peek(self, k: int = 0) -> str:
        i = self._pos + k
        return self._src[i] if i < len(self._src) else "\0"

    def _advance(self) -> str:
        ch = self._src[self._pos]
        self._pos += 1
        if ch == "\n":
            self._line += 1
            self._col = 1
        else:
            self._col += 1
        return ch

    def _error(self, msg: str, line: int, col: int) -> None:
        self._errors.append(LexicalError(msg, line, col))

    def _skip_blank_and_comments(self) -> None:
        while not self._eof():
            ch = self._peek()
            if ch in " \t\r\n":
                self._advance()
            elif ch == "#":
                while not self._eof() and self._peek() != "\n":
                    self._advance()
            else:
                break

    # ------------------------------------------------------------------
    # Reconhecimento dos tokens
    # ------------------------------------------------------------------
    def _next_token(self):
        ch = self._peek()
        line, col = self._line, self._col

        if ch.isalpha() or ch == "_":
            return self._read_word(line, col)
        if ch.isdigit():
            return self._read_number(line, col)
        if ch == '"':
            return self._read_string(line, col)

        two = ch + self._peek(1)
        if two in OPERATORS_2:
            self._advance()
            self._advance()
            return Token(two, two, line, col)

        if ch in OPERATORS_1 or ch in DELIMITERS:
            self._advance()
            return Token(ch, ch, line, col)

        if ch in "&|":
            self._advance()
            self._error(f"Operador incompleto '{ch}'. Você quis dizer '{ch}{ch}'?", line, col)
            return None

        self._advance()
        self._error(f"Caractere inválido {ch!r}", line, col)
        return None

    def _read_word(self, line: int, col: int) -> Token:
        start = self._pos
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        word = self._src[start:self._pos]
        if word in KEYWORDS or word in TYPE_KEYWORDS:
            value = None
            if word == "true":
                value = True
            elif word == "false":
                value = False
            return Token(word, word, line, col, value)
        return Token(T_IDENT, word, line, col, word)

    def _read_number(self, line: int, col: int):
        start = self._pos
        while self._peek().isdigit():
            self._advance()
        is_float = False
        # Parte fracionária: só se houver dígito depois do ponto.
        if self._peek() == "." and self._peek(1).isdigit():
            is_float = True
            self._advance()
            while self._peek().isdigit():
                self._advance()
        text = self._src[start:self._pos]
        # Número colado em letras (ex.: 12abc) é malformado.
        if self._peek().isalpha() or self._peek() == "_":
            while self._peek().isalnum() or self._peek() == "_":
                self._advance()
            bad = self._src[start:self._pos]
            self._error(f"Número malformado {bad!r}", line, col)
            return None
        value = float(text) if is_float else int(text)
        return Token(T_NUMBER, text, line, col, value)

    def _read_string(self, line: int, col: int):
        start = self._pos
        self._advance()  # abre aspas
        chars: List[str] = []
        ok = True
        while True:
            if self._eof() or self._peek() == "\n":
                self._error("String não terminada (faltou fechar as aspas)", line, col)
                return None
            ch = self._advance()
            if ch == '"':
                break
            if ch == "\\":
                if self._eof():
                    continue
                esc_line, esc_col = self._line, self._col - 1
                nxt = self._advance()
                if nxt in _ESCAPES:
                    chars.append(_ESCAPES[nxt])
                else:
                    self._error(f"Sequência de escape inválida '\\{nxt}'", esc_line, esc_col)
                    ok = False
            else:
                chars.append(ch)
        if not ok:
            return None
        return Token(T_STRING, self._src[start:self._pos], line, col, "".join(chars))
