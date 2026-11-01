# Atalhos de desenvolvimento (Arch Linux: sudo pacman -S make python)
PY ?= python3
export PYTHONPATH := src

.PHONY: teste8 teste9 teste10 test test-rapido tokens ast check tac cpp build run teste1-servidor teste1-cliente teste1-demo clean

test:
	$(PY) -m unittest discover -s tests -v

# testes sem compilar com o g++ (rápido); "make test" roda tudo
test-rapido:
	$(PY) -m unittest tests.test_lexer tests.test_parser tests.test_semantic tests.test_tac

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

# Testes 8, 9 e 10 (fork/join em 4, 5 e 6 núcleos)
teste8:
	$(PY) -m minipar run exemplos/teste08_avaliacao_4nucleos.mp -O2
teste9:
	$(PY) -m minipar run exemplos/teste09_5nucleos_fractal.mp -O2
teste10:
	$(PY) -m minipar run exemplos/teste10_6nucleos_2fractais.mp -O2

# Teste 1 (calculadora cliente/servidor): em dois terminais, ou tudo de uma vez com teste1-demo
teste1-servidor:
	$(PY) -m minipar build exemplos/teste01_servidor.mp > /dev/null
	./build/teste01_servidor --node computador_2

teste1-cliente:
	$(PY) -m minipar build exemplos/teste01_cliente.mp > /dev/null
	./build/teste01_cliente --node computador_1

teste1-demo:
	$(PY) -m minipar build exemplos/teste01_servidor.mp > /dev/null
	$(PY) -m minipar build exemplos/teste01_cliente.mp > /dev/null
	./build/teste01_servidor --node computador_2 & \
	sleep 1; printf '+\n3\n4\n*\n6\n7\n/\n1\n0\nsair\n' | ./build/teste01_cliente --node computador_1; wait

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
