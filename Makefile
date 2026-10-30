# Atalhos de desenvolvimento (Arch Linux: sudo pacman -S make python)
PY ?= python3
export PYTHONPATH := src

.PHONY: test test-rapido tokens ast check tac cpp build run clean

test:
	$(PY) -m unittest discover -s tests -v

# testes sem compilar com o g++ (rápido); "make test" roda tudo
test-rapido:
	$(PY) -m unittest discover -s tests -p "test_[lpst]*.py"

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

# uso: make cpp F=exemplos/teste03_neuronio.mp
cpp:
	$(PY) -m minipar cpp $(F)

# uso: make build F=exemplos/teste03_neuronio.mp   (gera build/<nome>)
build:
	$(PY) -m minipar build $(F)

# uso: make run F=exemplos/teste03_neuronio.mp
run:
	$(PY) -m minipar run $(F)

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
