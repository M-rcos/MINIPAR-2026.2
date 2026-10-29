# Atalhos de desenvolvimento (Arch Linux: sudo pacman -S make python)
PY ?= python3
export PYTHONPATH := src

.PHONY: test tokens ast check tac clean

test:
	$(PY) -m unittest discover -s tests -v

# uso: make tokens F=exemplos/teste02_par_fatorial_fibonacci.mp
tokens:
	$(PY) -m minipar tokens $(F)

# uso: make ast F=exemplos/teste03_neuronio.mp
ast:
	$(PY) -m minipar ast $(F)

# uso: make check F=exemplos/teste03_neuronio.mp   (mostra também a tabela de símbolos)
check:
	$(PY) -m minipar check $(F) --symbols

# uso: make tac F=exemplos/teste07_quicksort_iterativo.mp
tac:
	$(PY) -m minipar tac $(F)

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
