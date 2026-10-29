"""Símbolos armazenados na Tabela de Símbolos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .types import UNKNOWN

# Categorias de símbolo
VARIABLE = "VARIAVEL"
PARAMETER = "PARAMETRO"
FUNCTION = "FUNCAO"
METHOD = "METODO"
CLASS = "CLASSE"
ATTRIBUTE = "ATRIBUTO"
CHANNEL_SYM = "CANAL"
TASK = "SUBTAREFA"


@dataclass
class ParamInfo:
    name: str
    type: str = UNKNOWN


@dataclass(eq=False)
class ClassInfo:
    name: str
    superclass: Optional[str] = None
    attributes: Dict[str, "Symbol"] = field(default_factory=dict)
    methods: Dict[str, "Symbol"] = field(default_factory=dict)


@dataclass(eq=False)
class Symbol:
    name: str
    kind: str
    type: str = UNKNOWN
    line: int = 0
    col: int = 0
    declared_type: Optional[str] = None            # tipo escrito no código (int, float...)
    params: Optional[List[ParamInfo]] = None       # funções e métodos
    return_type: str = UNKNOWN                     # funções e métodos
    class_info: Optional[ClassInfo] = None         # símbolos de classe
    owner: Optional[str] = None                    # classe dona (atributo/método)
    endpoints: Optional[tuple] = None              # canais: (computador_1, computador_2)

    def signature(self) -> str:
        if self.params is None:
            return self.type
        args = ", ".join(
            p.name if p.type == UNKNOWN else f"{p.name}: {p.type}" for p in self.params
        )
        return f"({args}) -> {self.return_type}"

    def to_dict(self) -> dict:
        data = {
            "name": self.name,
            "kind": self.kind,
            "type": self.type,
            "line": self.line,
            "col": self.col,
        }
        if self.params is not None:
            data["params"] = [{"name": p.name, "type": p.type} for p in self.params]
            data["return_type"] = self.return_type
        if self.owner:
            data["owner"] = self.owner
        if self.class_info is not None:
            data["superclass"] = self.class_info.superclass
        if self.endpoints:
            data["endpoints"] = list(self.endpoints)
        return data
