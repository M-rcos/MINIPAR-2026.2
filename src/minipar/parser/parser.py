"""Analisador Sintático (Parser) da linguagem MiniPar 2026.2.

Técnica: descida recursiva (um método por produção da gramática BNF, ver
docs/GRAMATICA_BNF_2026_2.md). A precedência dos operadores é obtida pela
hierarquia de métodos expressao_ou > expressao_e > ... > primaria.

Tratamento de erros:
  * Erros de pontuação (faltou ';', ')' ou ']') são registrados e o parser
    continua como se o símbolo existisse (recuperação local).
  * Demais erros interrompem apenas o comando atual: o parser descarta
    tokens até um ponto seguro (após ';' ou antes de uma palavra que inicia
    comando) e segue adiante (modo pânico). Assim vários erros aparecem de
    uma só vez.
"""

from __future__ import annotations

from typing import Callable, List, Optional

from ..common import MiniParError, ParseError
from ..lexer.tokens import T_EOF, T_IDENT, T_NUMBER, T_STRING, TYPE_KEYWORDS, Token
from .ast_nodes import (
    Allocation, Assign, Binary, Block, Break, Call, ChannelDecl, ChannelExpr,
    ClassDecl, Continue, DoWhile, Expr, ExprStmt, For, ForIn, Fork, FuncDecl,
    Identifier, If, Index, Input, Join, ListLiteral, Literal, MatrixExpr,
    Member, MethodCall, New, Node, Param, ParBlock, Print, Program, Receive,
    Return, Send, This, Unary, VarDecl, While,
)
from .interface import IParser

ASSIGN_OPS = {"=", "+=", "-=", "*=", "/="}

# Tokens que iniciam um comando/declaração: pontos seguros de ressincronização.
SYNC_START = {
    "class", "func", "var", "if", "while", "for", "do", "return", "print",
    "send", "fork", "join", "par", "seq", "break", "continue", "c_channel",
} | TYPE_KEYWORDS


def describe(tok: Token) -> str:
    """Nome amigável do token para mensagens de erro."""
    if tok.type == T_EOF:
        return "o fim do arquivo"
    if tok.type == T_IDENT:
        return f"o identificador '{tok.lexeme}'"
    if tok.type == T_NUMBER:
        return f"o número {tok.lexeme}"
    if tok.type == T_STRING:
        return f"o texto {tok.lexeme}"
    return f"'{tok.lexeme}'"


class Parser(IParser):
    def __init__(self, tokens: List[Token]):
        # Garante o EOF final para o parser nunca ler além do fim.
        if not tokens or tokens[-1].type != T_EOF:
            last = tokens[-1] if tokens else None
            tokens = list(tokens) + [
                Token(T_EOF, "", last.line if last else 1, last.col if last else 1)
            ]
        self._toks = tokens
        self._i = 0
        self._errors: List[MiniParError] = []

    # ==================================================================
    # Interface IParser
    # ==================================================================
    @property
    def errors(self) -> List[MiniParError]:
        return self._errors

    def parse(self) -> Program:
        first = self._peek()
        program = Program(line=first.line, col=first.col)
        while not self._at_eof():
            if self._check("}"):
                tok = self._advance()
                if not self._errors:  # evita erro em cascata
                    self._report(ParseError("'}' inesperado: não há bloco aberto para fechar",
                                            tok.line, tok.col))
                continue
            node = self._guarded(self._parse_global)
            if node is not None:
                program.body.append(node)
        return program

    # ==================================================================
    # Utilitários de leitura de tokens
    # ==================================================================
    def _peek(self, k: int = 0) -> Token:
        i = min(self._i + k, len(self._toks) - 1)
        return self._toks[i]

    def _prev(self) -> Optional[Token]:
        return self._toks[self._i - 1] if self._i > 0 else None

    def _at_eof(self) -> bool:
        return self._peek().type == T_EOF

    def _check(self, ttype: str) -> bool:
        return self._peek().type == ttype

    def _advance(self) -> Token:
        tok = self._peek()
        if tok.type != T_EOF:
            self._i += 1
        return tok

    def _match(self, *types: str) -> Optional[Token]:
        if self._peek().type in types:
            return self._advance()
        return None

    def _is_word(self, word: str) -> bool:
        """Palavra contextual (IDENTIFIER com texto específico, ex.: 'on')."""
        tok = self._peek()
        return tok.type == T_IDENT and tok.lexeme == word

    # ==================================================================
    # Erros e recuperação
    # ==================================================================
    def _report(self, err: MiniParError) -> None:
        last = self._errors[-1] if self._errors else None
        if last and (last.line, last.col) == (err.line, err.col):
            return
        self._errors.append(err)

    def _fail(self, message: str, tok: Optional[Token] = None) -> ParseError:
        tok = tok or self._peek()
        return ParseError(message, tok.line, tok.col)

    def _expect(self, ttype: str, what: Optional[str] = None, recover: bool = False) -> Token:
        tok = self._peek()
        if tok.type == ttype:
            return self._advance()
        what = what or f"'{ttype}'"
        message = f"Esperava {what}, mas encontrou {describe(tok)}"
        line, col = tok.line, tok.col
        if ttype == ";" and self._prev() is not None:
            # Aponta para o fim do comando anterior, onde o ';' deveria estar.
            prev = self._prev()
            line, col = prev.line, prev.col + len(prev.lexeme)
        err = ParseError(message, line, col)
        if recover:
            self._report(err)
            return Token(ttype, ttype, line, col)
        raise err

    def _guarded(self, fn: Callable[[], Optional[Node]]) -> Optional[Node]:
        """Executa uma regra; em caso de erro registra e ressincroniza."""
        start = self._i
        try:
            return fn()
        except ParseError as err:
            self._report(err)
            if self._i == start:
                self._advance()
            self._synchronize()
            return None

    def _synchronize(self) -> None:
        while not self._at_eof():
            prev = self._prev()
            if prev is not None and prev.type == ";":
                return
            if self._peek().type in SYNC_START or self._check("}"):
                return
            self._advance()

    # ==================================================================
    # Nível global
    # ==================================================================
    def _parse_global(self) -> Optional[Node]:
        tok = self._peek()
        if tok.type == "class":
            return self._parse_class()
        if tok.type == "func":
            return self._parse_func()
        if tok.type == "c_channel" and self._peek(1).type == T_IDENT:
            return self._parse_channel_decl()
        return self._parse_statement()

    def _parse_class(self) -> ClassDecl:
        kw = self._advance()
        name = self._expect(T_IDENT, "o nome da classe").lexeme
        superclass = None
        if self._match("extends"):
            superclass = self._expect(T_IDENT, "o nome da superclasse").lexeme
        open_tok = self._expect("{", "'{' para abrir o corpo da classe")
        node = ClassDecl(name, superclass, [], line=kw.line, col=kw.col)
        while not self._check("}") and not self._at_eof():
            member = self._guarded(self._parse_member)
            if member is not None:
                node.members.append(member)
        if self._at_eof():
            self._report(ParseError(f"A classe '{name}' aberta aqui não foi fechada com '}}'",
                                    open_tok.line, open_tok.col))
        else:
            self._advance()
        return node

    def _parse_member(self) -> Node:
        tok = self._peek()
        if tok.type == "func":
            return self._parse_func()
        if tok.type == "var" or tok.type in TYPE_KEYWORDS:
            return self._parse_var_decl()
        raise self._fail(f"Dentro de uma classe esperava um atributo ('var') ou um método "
                         f"('func'), mas encontrou {describe(tok)}")

    def _parse_func(self) -> FuncDecl:
        kw = self._advance()
        name = self._expect(T_IDENT, "o nome da função").lexeme
        self._expect("(", "'(' após o nome da função")
        params: List[Param] = []
        if not self._check(")"):
            params.append(self._parse_param())
            while self._match(","):
                params.append(self._parse_param())
        self._expect(")", "')' para fechar os parâmetros", recover=True)
        body = self._parse_block(required=True)
        return FuncDecl(name, params, body, line=kw.line, col=kw.col)

    def _parse_param(self) -> Param:
        type_name = None
        if self._peek().type in TYPE_KEYWORDS:
            type_name = self._advance().type
        name = self._expect(T_IDENT, "o nome do parâmetro")
        return Param(name.lexeme, type_name, line=name.line, col=name.col)

    def _parse_channel_decl(self) -> ChannelDecl:
        kw = self._advance()
        name = self._expect(T_IDENT, "o nome do canal").lexeme
        a = self._expect(T_IDENT, "o nome do primeiro computador").lexeme
        b = self._expect(T_IDENT, "o nome do segundo computador").lexeme
        self._expect(";", "';' ao final da declaração do canal", recover=True)
        return ChannelDecl(name, a, b, line=kw.line, col=kw.col)

    # ==================================================================
    # Declaração de variável
    # ==================================================================
    def _parse_var_decl(self, terminated: bool = True) -> VarDecl:
        kw = self._advance()                       # 'var' ou nome do tipo
        type_name = None if kw.type == "var" else kw.type
        name = self._expect(T_IDENT, "o nome da variável").lexeme
        init = None
        if self._match("="):
            init = self._parse_expression()
        if terminated:
            self._expect(";", "';' ao final da declaração", recover=True)
        return VarDecl(name, type_name, init, line=kw.line, col=kw.col)

    # ==================================================================
    # Comandos
    # ==================================================================
    def _parse_statement(self) -> Node:
        tok = self._peek()
        t = tok.type

        if t == "var" or t in TYPE_KEYWORDS:
            return self._parse_var_decl()
        if t == "{":
            return self._parse_block()
        if t == "seq":
            return self._parse_block()
        if t == "par":
            return self._parse_par()
        if t == "fork":
            return self._parse_fork()
        if t == "join":
            return self._parse_join()
        if t == "if":
            return self._parse_if()
        if t == "while":
            return self._parse_while()
        if t == "do":
            return self._parse_do_while()
        if t == "for":
            return self._parse_for()
        if t == "print":
            return self._parse_print()
        if t == "send":
            return self._parse_send_command()
        if t == "return":
            return self._parse_return()
        if t == "break":
            self._advance()
            self._expect(";", "';' após 'break'", recover=True)
            return Break(line=tok.line, col=tok.col)
        if t == "continue":
            self._advance()
            self._expect(";", "';' após 'continue'", recover=True)
            return Continue(line=tok.line, col=tok.col)
        if t in ("class", "func"):
            raise self._fail(f"Declarações de {'classe' if t == 'class' else 'função'} "
                             f"só são permitidas no nível global (fora de blocos)")
        if t == "c_channel" and self._peek(1).type == T_IDENT:
            raise self._fail("A declaração 'c_channel' só é permitida no nível global")
        return self._parse_simple(terminated=True)

    def _parse_simple(self, terminated: bool) -> Node:
        """Atribuição ou chamada usada como comando."""
        start = self._peek()
        expr = self._parse_expression()
        if self._peek().type in ASSIGN_OPS:
            op = self._advance()
            if not isinstance(expr, (Identifier, Member, Index)):
                self._report(ParseError(
                    "O lado esquerdo da atribuição deve ser uma variável, um atributo "
                    "(obj.campo) ou um elemento de lista (lista[i])", start.line, start.col))
            value = self._parse_expression()
            node: Node = Assign(expr, op.type, value, line=op.line, col=op.col)
        else:
            if terminated and not isinstance(expr, (Call, MethodCall)):
                self._report(ParseError(
                    "Esta expressão não pode ser usada como comando: esperava uma atribuição "
                    "ou uma chamada de função/método", start.line, start.col))
            node = ExprStmt(expr, line=start.line, col=start.col)
        if terminated:
            self._expect(";", "';' ao final do comando", recover=True)
        return node

    def _parse_block(self, required: bool = False) -> Block:
        explicit = False
        tok = self._peek()
        if tok.type == "seq":
            explicit = True
            self._advance()
        open_tok = self._expect("{", "'{' para abrir o bloco")
        node = Block([], explicit, line=tok.line, col=tok.col)
        node.statements = self._parse_block_body(open_tok)
        return node

    def _parse_block_body(self, open_tok: Token) -> List[Node]:
        stmts: List[Node] = []
        while not self._check("}") and not self._at_eof():
            stmt = self._guarded(self._parse_statement)
            if stmt is not None:
                stmts.append(stmt)
        if self._at_eof():
            self._report(ParseError(
                f"O bloco aberto com '{{' na linha {open_tok.line} não foi fechado com '}}'",
                open_tok.line, open_tok.col))
        else:
            self._advance()
        return stmts

    def _parse_par(self) -> ParBlock:
        kw = self._advance()
        open_tok = self._expect("{", "'{' após 'par'")
        return ParBlock(self._parse_block_body(open_tok), line=kw.line, col=kw.col)

    def _parse_fork(self) -> Fork:
        kw = self._advance()
        name = self._expect(T_IDENT, "o nome da subtarefa após 'fork'").lexeme
        allocation = None
        if self._is_word("on"):
            on = self._advance()
            if self._is_word("core"):
                self._advance()
                allocation = Allocation("core", self._parse_expression(),
                                        line=on.line, col=on.col)
            elif self._is_word("host"):
                self._advance()
                target = self._parse_expression()
                port = self._parse_expression() if self._match(",") else None
                allocation = Allocation("host", target, port, line=on.line, col=on.col)
            else:
                raise self._fail(f"Após 'on' esperava 'core' ou 'host', mas encontrou "
                                 f"{describe(self._peek())}")
        body = self._parse_block(required=True)
        return Fork(name, allocation, body, line=kw.line, col=kw.col)

    def _parse_join(self) -> Join:
        kw = self._advance()
        names: List[str] = []
        if self._check(T_IDENT):
            names.append(self._advance().lexeme)
            while self._match(","):
                names.append(self._expect(T_IDENT, "o nome de uma subtarefa").lexeme)
        self._expect(";", "';' após 'join'", recover=True)
        return Join(names, line=kw.line, col=kw.col)

    def _parse_if(self) -> If:
        kw = self._advance()
        self._expect("(", "'(' após 'if'")
        cond = self._parse_expression()
        self._expect(")", "')' para fechar a condição do 'if'", recover=True)
        then_branch = self._parse_statement()
        else_branch = None
        if self._match("else"):
            else_branch = self._parse_statement()
        return If(cond, then_branch, else_branch, line=kw.line, col=kw.col)

    def _parse_while(self) -> While:
        kw = self._advance()
        self._expect("(", "'(' após 'while'")
        cond = self._parse_expression()
        self._expect(")", "')' para fechar a condição do 'while'", recover=True)
        return While(cond, self._parse_statement(), line=kw.line, col=kw.col)

    def _parse_do_while(self) -> DoWhile:
        kw = self._advance()
        body = self._parse_statement()
        self._expect("while", "'while' após o corpo do 'do'")
        self._expect("(", "'(' após 'while'")
        cond = self._parse_expression()
        self._expect(")", "')' para fechar a condição do 'do-while'", recover=True)
        self._match(";")
        return DoWhile(body, cond, line=kw.line, col=kw.col)

    def _parse_for(self) -> Node:
        kw = self._advance()
        self._expect("(", "'(' após 'for'")
        # for (var x in colecao)
        if (self._check("var") and self._peek(1).type == T_IDENT
                and self._peek(2).type == "in"):
            self._advance()
            var = self._advance().lexeme
            self._advance()
            iterable = self._parse_expression()
            self._expect(")", "')' para fechar o 'for'", recover=True)
            return ForIn(var, iterable, self._parse_statement(), line=kw.line, col=kw.col)
        # for (init; cond; update)
        init: Optional[Node] = None
        if not self._check(";"):
            if self._check("var") or self._peek().type in TYPE_KEYWORDS:
                init = self._parse_var_decl(terminated=False)
            else:
                init = self._parse_simple(terminated=False)
        self._expect(";", "';' após o inicializador do 'for'", recover=True)
        cond = None
        if not self._check(";"):
            cond = self._parse_expression()
        self._expect(";", "';' após a condição do 'for'", recover=True)
        update = None
        if not self._check(")"):
            update = self._parse_simple(terminated=False)
        self._expect(")", "')' para fechar o 'for'", recover=True)
        return For(init, cond, update, self._parse_statement(), line=kw.line, col=kw.col)

    def _parse_print(self) -> Print:
        kw = self._advance()
        self._expect("(", "'(' após 'print'")
        args = self._parse_args_rest()
        self._expect(";", "';' ao final do 'print'", recover=True)
        return Print(args, line=kw.line, col=kw.col)

    def _parse_send_command(self) -> Send:
        kw = self._advance()
        self._expect("(", "'(' após 'send'")
        args = self._parse_args_rest()
        if len(args) < 2:
            self._report(ParseError("'send' exige o canal e ao menos um valor: send(canal, valor)",
                                    kw.line, kw.col))
        self._expect(";", "';' ao final do 'send'", recover=True)
        return Send(args, line=kw.line, col=kw.col)

    def _parse_return(self) -> Return:
        kw = self._advance()
        value = None
        if not self._check(";"):
            value = self._parse_expression()
        self._expect(";", "';' após o 'return'", recover=True)
        return Return(value, line=kw.line, col=kw.col)

    # ==================================================================
    # Expressões (precedência: ou < e < comparação < soma < produto < unário)
    # ==================================================================
    def _parse_expression(self) -> Expr:
        return self._binary(self._parse_and, ("||",))

    def _parse_and(self) -> Expr:
        return self._binary(self._parse_comparison, ("&&",))

    def _parse_comparison(self) -> Expr:
        return self._binary(self._parse_term, ("==", "!=", "<", ">", "<=", ">="))

    def _parse_term(self) -> Expr:
        return self._binary(self._parse_factor, ("+", "-"))

    def _parse_factor(self) -> Expr:
        return self._binary(self._parse_unary, ("*", "/", "%"))

    def _binary(self, sub: Callable[[], Expr], ops) -> Expr:
        left = sub()
        while self._peek().type in ops:
            op = self._advance()
            right = sub()
            left = Binary(op.type, left, right, line=op.line, col=op.col)
        return left

    def _parse_unary(self) -> Expr:
        tok = self._peek()
        if tok.type in ("-", "+", "!"):
            self._advance()
            return Unary(tok.type, self._parse_unary(), line=tok.line, col=tok.col)
        return self._parse_postfix()

    def _parse_postfix(self) -> Expr:
        node = self._parse_primary()
        while True:
            if self._match("."):
                name_tok = self._peek()
                if name_tok.type in (T_IDENT, "send", "receive"):
                    self._advance()
                else:
                    raise self._fail(f"Esperava o nome de um atributo ou método após '.', "
                                     f"mas encontrou {describe(name_tok)}")
                if self._match("("):
                    args = self._parse_args_rest()
                    node = MethodCall(node, name_tok.lexeme, args,
                                      line=name_tok.line, col=name_tok.col)
                else:
                    node = Member(node, name_tok.lexeme, line=name_tok.line, col=name_tok.col)
            elif self._check("["):
                br = self._advance()
                idx = self._parse_expression()
                self._expect("]", "']' para fechar o índice", recover=True)
                node = Index(node, idx, line=br.line, col=br.col)
            else:
                return node

    def _parse_args_rest(self) -> List[Expr]:
        """Lê argumentos depois do '(' já consumido, até o ')'."""
        args: List[Expr] = []
        if not self._check(")"):
            args.append(self._parse_expression())
            while self._match(","):
                args.append(self._parse_expression())
        self._expect(")", "')' para fechar a lista de argumentos", recover=True)
        return args

    def _parse_primary(self) -> Expr:
        tok = self._peek()
        t = tok.type
        pos = {"line": tok.line, "col": tok.col}

        if t == T_NUMBER:
            self._advance()
            return Literal("number", tok.value, **pos)
        if t == T_STRING:
            self._advance()
            return Literal("string", tok.value, **pos)
        if t in ("true", "false"):
            self._advance()
            return Literal("bool", tok.value, **pos)
        if t == "null":
            self._advance()
            return Literal("null", None, **pos)
        if t == T_IDENT:
            self._advance()
            if self._match("("):
                return Call(tok.lexeme, self._parse_args_rest(), **pos)
            return Identifier(tok.lexeme, **pos)
        if t == "this":
            self._advance()
            return This(**pos)
        if t == "new":
            self._advance()
            cls = self._expect(T_IDENT, "o nome da classe após 'new'").lexeme
            self._expect("(", "'(' após o nome da classe")
            return New(cls, self._parse_args_rest(), **pos)
        if t == "c_channel":
            self._advance()
            self._expect("(", "'(' após 'c_channel'")
            args = self._parse_args_rest()
            if len(args) != 2:
                raise ParseError("c_channel(endereço, porta) exige exatamente 2 argumentos",
                                 tok.line, tok.col)
            return ChannelExpr(args[0], args[1], **pos)
        if t == "receive":
            self._advance()
            self._expect("(", "'(' após 'receive'")
            args = self._parse_args_rest()
            if len(args) != 1:
                raise ParseError("receive(canal) exige exatamente 1 argumento",
                                 tok.line, tok.col)
            return Receive(args[0], **pos)
        if t == "input":
            self._advance()
            self._expect("(", "'(' após 'input'")
            args = self._parse_args_rest()
            if len(args) > 1:
                raise ParseError("input aceita no máximo 1 argumento (a mensagem)",
                                 tok.line, tok.col)
            return Input(args[0] if args else None, **pos)
        if t == "matrix":
            self._advance()
            self._expect("(", "'(' após 'matrix'")
            args = self._parse_args_rest()
            if len(args) != 3:
                raise ParseError("matrix(linhas, colunas, valor) exige exatamente 3 argumentos",
                                 tok.line, tok.col)
            return MatrixExpr(args[0], args[1], args[2], **pos)
        if t == "[":
            self._advance()
            elements: List[Expr] = []
            if not self._check("]"):
                elements.append(self._parse_expression())
                while self._match(","):
                    elements.append(self._parse_expression())
            self._expect("]", "']' para fechar a lista", recover=True)
            return ListLiteral(elements, **pos)
        if t == "(":
            self._advance()
            expr = self._parse_expression()
            self._expect(")", "')' para fechar a expressão", recover=True)
            return expr

        raise self._fail(f"Esperava uma expressão, mas encontrou {describe(tok)}")
