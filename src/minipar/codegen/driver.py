"""Integração com o GCC: gera o .cpp, compila e produz o executável."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

from ..pipeline import to_cpp


class BuildError(Exception):
    """Falha ao compilar o C++ gerado (ou compilador não encontrado)."""


@dataclass
class BuildResult:
    cpp_path: Path
    exe_path: Path
    command: List[str]
    compiler_output: str


def runtime_dir() -> Path:
    """Pasta com o cabeçalho minipar_runtime.hpp."""
    return Path(__file__).resolve().parent / "runtime"


def find_compiler() -> str:
    cxx = os.environ.get("CXX") or shutil.which("g++") or shutil.which("c++")
    if not cxx:
        raise BuildError(
            "Compilador C++ não encontrado. Instale o GCC:\n"
            "  Arch Linux:  sudo pacman -S --needed gcc\n"
            "  Ubuntu:      sudo apt install g++\n"
            "  Windows:     MSYS2 (pacman -S mingw-w64-ucrt-x86_64-gcc) e adicione ao PATH")
    return cxx


def build_executable(source_path: str, out_dir: str = "build", opt: str = "2",
                     exe_name: Optional[str] = None,
                     extra_flags: Sequence[str] = ()) -> BuildResult:
    """Compila um programa MiniPar até o executável.

    Levanta ``CompileErrors`` (erros do programa) ou ``BuildError`` (erro do GCC).
    """
    path = Path(source_path)
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    cpp_code = to_cpp(source)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = path.stem
    cpp_path = out / f"{stem}.cpp"
    cpp_path.write_text(cpp_code, encoding="utf-8")
    shutil.copyfile(runtime_dir() / "minipar_runtime.hpp", out / "minipar_runtime.hpp")

    is_windows = sys.platform.startswith("win")
    exe_path = Path(exe_name) if exe_name else out / (stem + (".exe" if is_windows else ""))

    cmd = [find_compiler(), "-std=c++17", f"-O{opt}", "-pthread", "-I", str(out),
           "-o", str(exe_path), str(cpp_path)]
    if is_windows:
        cmd += ["-static", "-lws2_32"]
    cmd += list(extra_flags)

    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        raise BuildError("Falha ao compilar o C++ gerado:\n" + output)
    return BuildResult(cpp_path, exe_path, cmd, output)
