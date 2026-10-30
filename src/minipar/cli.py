"""Interface de linha de comando (Terminal) do compilador MiniPar 2026.2.

Comandos disponíveis nesta etapa:
    tokens  <arquivo.mp> [--json]   mostra a tokenização
    ast     <arquivo.mp> [--json]   mostra a árvore sintática (AST)
    check   <arquivo.mp> [--symbols] [--json]
                                    análise semântica (e tabela de símbolos)
    tac     <arquivo.mp> [-o saida.tac] [--json]
                                    código intermediário de três endereços
    cpp     <arquivo.mp> [-o saida.cpp]     gera o código C++
    build   <arquivo.mp> [-o exe] [-O2]     compila até o executável (GCC)
    run     <arquivo.mp> [-O2]              compila e executa

Os demais comandos (ast, check, tac, cpp, build, run) serão adicionados
conforme os componentes forem implementados.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .lexer import Lexer
from .parser import Parser, format_tree, to_dict
from .semantic import SemanticAnalyzer
from .pipeline import CompileErrors, front_end
from .tac import TACGenerator


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


def cmd_ast(args: argparse.Namespace) -> int:
    source = _read(args.arquivo)
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    tree = parser.parse()
    errors = list(lexer.errors) + list(parser.errors)
    errors.sort(key=lambda e: (e.line, e.col))

    if args.json:
        print(json.dumps(
            {"ast": to_dict(tree), "errors": [e.to_dict() for e in errors]},
            ensure_ascii=False,
            indent=2,
        ))
    else:
        print(format_tree(tree))
        for e in errors:
            print(e.format(source), file=sys.stderr)
        if errors:
            print(f"\n{len(errors)} erro(s) encontrado(s).", file=sys.stderr)

    return 1 if errors else 0


def cmd_check(args: argparse.Namespace) -> int:
    source = _read(args.arquivo)
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    tree = parser.parse()
    front_errors = sorted(list(lexer.errors) + list(parser.errors),
                          key=lambda e: (e.line, e.col))

    analyzer = None
    errors = front_errors
    if not front_errors:
        analyzer = SemanticAnalyzer()
        analyzer.analyze(tree)
        errors = sorted(analyzer.errors, key=lambda e: (e.line, e.col))

    if args.json:
        data = {"errors": [e.to_dict() for e in errors]}
        if analyzer is not None:
            data["symbols"] = analyzer.symbol_table.to_dict()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 1 if errors else 0

    for e in errors:
        print(e.format(source), file=sys.stderr)
    if front_errors:
        print(f"\n{len(errors)} erro(s) léxico(s)/sintático(s). A análise semântica só roda "
              f"depois que eles forem corrigidos.", file=sys.stderr)
    elif errors:
        print(f"\n{len(errors)} erro(s) semântico(s) encontrado(s).", file=sys.stderr)
    else:
        print("Análise semântica concluída sem erros.")
    if args.symbols and analyzer is not None:
        print("\n=== Tabela de Símbolos ===")
        print(analyzer.symbol_table.format())
    return 1 if errors else 0


def cmd_tac(args: argparse.Namespace) -> int:
    source = _read(args.arquivo)
    tree, analyzer, errors = front_end(source)
    if errors:
        for e in errors:
            print(e.format(source), file=sys.stderr)
        print(f"\n{len(errors)} erro(s): corrija-os antes de gerar o código intermediário.",
              file=sys.stderr)
        return 1
    program = TACGenerator(analyzer).generate(tree)
    if args.json:
        text = json.dumps(program.to_dict(), ensure_ascii=False, indent=2)
    else:
        text = program.format()
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Código intermediário gravado em {args.saida}")
    else:
        print(text, end="" if text.endswith("\n") else "\n")
    return 0


def _build(args: argparse.Namespace):
    from .codegen import BuildError, build_executable
    try:
        return build_executable(args.arquivo, out_dir=args.dir, opt=args.opt,
                                exe_name=getattr(args, "saida", None))
    except CompileErrors as err:
        print(err.format(), file=sys.stderr)
        print(f"\n{len(err.errors)} erro(s): corrija-os antes de compilar.", file=sys.stderr)
    except BuildError as err:
        print(err, file=sys.stderr)
    return None


def cmd_cpp(args: argparse.Namespace) -> int:
    from .pipeline import to_cpp
    source = _read(args.arquivo)
    try:
        code = to_cpp(source)
    except CompileErrors as err:
        print(err.format(), file=sys.stderr)
        print(f"\n{len(err.errors)} erro(s): corrija-os antes de gerar o C++.", file=sys.stderr)
        return 1
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Código C++ gravado em {args.saida}")
    else:
        print(code, end="")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    result = _build(args)
    if result is None:
        return 1
    print(f"C++ gerado:  {result.cpp_path}")
    print(f"Executável:  {result.exe_path}")
    if result.compiler_output.strip():
        print(result.compiler_output, file=sys.stderr)
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    import subprocess
    result = _build(args)
    if result is None:
        return 1
    return subprocess.call([str(result.exe_path.resolve())])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="minipar", description=f"Compilador MiniPar {__version__}"
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_tok = sub.add_parser("tokens", help="mostra os tokens do programa")
    p_tok.add_argument("arquivo")
    p_tok.add_argument("--json", action="store_true", help="saída em JSON")
    p_tok.set_defaults(func=cmd_tokens)

    p_ast = sub.add_parser("ast", help="mostra a árvore sintática do programa")
    p_ast.add_argument("arquivo")
    p_ast.add_argument("--json", action="store_true", help="saída em JSON")
    p_ast.set_defaults(func=cmd_ast)

    p_chk = sub.add_parser("check", help="análise semântica do programa")
    p_chk.add_argument("arquivo")
    p_chk.add_argument("--symbols", action="store_true", help="mostra a tabela de símbolos")
    p_chk.add_argument("--json", action="store_true", help="saída em JSON")
    p_chk.set_defaults(func=cmd_check)

    p_tac = sub.add_parser("tac", help="gera o código de três endereços")
    p_tac.add_argument("arquivo")
    p_tac.add_argument("-o", "--saida", help="grava o resultado neste arquivo")
    p_tac.add_argument("--json", action="store_true", help="saída em JSON")
    p_tac.set_defaults(func=cmd_tac)

    p_cpp = sub.add_parser("cpp", help="gera o código C++")
    p_cpp.add_argument("arquivo")
    p_cpp.add_argument("-o", "--saida", help="grava o C++ neste arquivo")
    p_cpp.set_defaults(func=cmd_cpp)

    for name, func, helptext in (("build", cmd_build, "compila até o executável"),
                                 ("run", cmd_run, "compila e executa")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("arquivo")
        if name == "build":
            p.add_argument("-o", "--saida", help="caminho do executável")
        p.add_argument("-O", dest="opt", default="2", choices=["0", "1", "2", "3", "s"],
                       help="nível de otimização do GCC (padrão: 2)")
        p.add_argument("--dir", default="build", help="pasta de saída (padrão: build)")
        p.set_defaults(func=func)

    args = parser.parse_args(argv)
    return args.func(args)
