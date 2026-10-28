"""Interface de linha de comando (Terminal) do compilador MiniPar 2026.2.

Comandos disponíveis nesta etapa:
    tokens  <arquivo.mp> [--json]   mostra a tokenização

Os demais comandos (ast, check, tac, cpp, build, run) serão adicionados
conforme os componentes forem implementados.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .lexer import Lexer


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def cmd_tokens(args: argparse.Namespace) -> int:
    source = _read(args.arquivo)
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    if args.json:
        print(json.dumps(
            {
                "tokens": [t.to_dict() for t in tokens],
                "errors": [e.to_dict() for e in lexer.errors],
            },
            ensure_ascii=False,
            indent=2,
        ))
    else:
        print(f"{'LINHA':>5} {'COL':>4}  {'CATEGORIA':<18} LEXEMA")
        print("-" * 52)
        for t in tokens:
            print(f"{t.line:>5} {t.col:>4}  {t.category:<18} {t.lexeme!r}")
        for e in lexer.errors:
            print(e.format(source), file=sys.stderr)

    return 1 if lexer.errors else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="minipar", description=f"Compilador MiniPar {__version__}"
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_tok = sub.add_parser("tokens", help="mostra os tokens do programa")
    p_tok.add_argument("arquivo")
    p_tok.add_argument("--json", action="store_true", help="saída em JSON")
    p_tok.set_defaults(func=cmd_tokens)

    args = parser.parse_args(argv)
    return args.func(args)
