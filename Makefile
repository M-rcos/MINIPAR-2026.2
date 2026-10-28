# Atalhos de desenvolvimento (Arch Linux: sudo pacman -S make python)
PY ?= python3
export PYTHONPATH := src

.PHONY: test tokens clean

test:
	$(PY) -m unittest discover -s tests -v

# uso: make tokens F=exemplos/teste02_par_fatorial_fibonacci.mp
tokens:
	$(PY) -m minipar tokens $(F)

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
