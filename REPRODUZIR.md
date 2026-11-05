# Guia de Configuração do Ambiente e Reprodução de Testes

### 1. Pré-requisitos de Ambiente

* **Sistema Operacional:** Windows 10/11 ou Linux (Ubuntu/Debian)
* **Compilador C++:** GCC 13+ com suporte a C++17 e POSIX threads.
  * **No Windows:** Utilizar o ambiente **MSYS2 (UCRT64)** com pacote `mingw-w64-ucrt-x86_64-gcc`. *(Importante: MinGW antigo com thread modelo win32 causa erros de compilação no runtime concorrente)*.
  * **No Linux:** `build-essential` (`g++` / `gcc`).
* **Python:** Python 3.10 ou superior adicionado ao PATH.

---

### 2. Instruções de Compilação
No terminal (CMD ou PowerShell no Windows, Bash no Linux):

1. Limpar compilações anteriores:
   make clean

2. Compilar o compilador MiniPar e o runtime C++:
   make

### 3. Execução da Suíte de Testes Automatizados
Para executar a bateria completa de 262 testes automatizados:

py run_tests.py
