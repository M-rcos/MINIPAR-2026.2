#!/usr/bin/env python3
"""Atalho para o compilador: python3 mp.py <comando> ...

Equivale a "PYTHONPATH=src python3 -m minipar <comando> ..." e funciona em qualquer
sistema (Linux, macOS e Windows), sem configurar variáveis de ambiente.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from minipar.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
