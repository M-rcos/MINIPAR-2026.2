# fork, join e execução em outros computadores

As subtarefas da MiniPar se comportam como **processos independentes**: cada uma recebe uma CÓPIA das variáveis que usa e só se comunica por mensagem (canais) ou pelo valor que devolve. Há dois blocos:

```
par { comando1; comando2; ... }                  # cada comando vira uma thread; o bloco só termina quando todas acabam
fork nome [on core N | on host "ip", porta] { ...; return valor; }    # subtarefa nomeada
join a, b;                                       # espera as subtarefas indicadas (sem nomes: todas)
var r = join nome;                               # espera e RECEBE o valor do return da subtarefa
```

## Onde a subtarefa executa

| Forma | Execução |
|---|---|
| `fork t { ... }` | thread local, o sistema escolhe o núcleo |
| `fork t on core 2 { ... }` | thread fixada no núcleo 2 (`pthread_setaffinity_np` no Linux, `SetThreadAffinityMask` no Windows). Se a máquina não tiver esse núcleo, a execução continua sem fixação e um aviso aparece na tela |
| `fork t on host "192.168.0.20", 9000 { ... }` | outro computador: o corpo é executado por um **trabalhador** (o mesmo programa em modo `--worker`) |

## Execução em outro computador (trabalhador)

O corpo do `fork` vira uma função do programa compilado. Para executá-lo em outra máquina:

1. Copie o **mesmo executável** (ou compile o mesmo `.mp` lá).
2. No computador remoto: `./programa --worker 9000` (opcional: `--worker-tasks N` encerra depois de N tarefas).
3. No computador principal: `./programa` (o endereço e a porta vêm do `fork ... on host`).

O programa principal envia o nome da tarefa e as cópias das variáveis locais que ela usa; o trabalhador executa e devolve o resultado, que chega no `join`. Os `print` da tarefa saem na tela do computador remoto. O nome do computador pode vir do `minipar.hosts` (`servidor = 192.168.0.20` e depois `on host "servidor", 9000`); sem porta, vale 9000. Para testar em um só computador use `127.0.0.1` (exemplo: `exemplos/fork_remoto.mp`).

Regras para tarefas remotas:

* o corpo não pode ler **variáveis globais** (o outro computador não as tem); o compilador avisa e pede para copiar o valor para uma variável local (dentro de uma função ou de um bloco `seq { }`);
* só números, strings, booleanos, `null` e listas viajam pela rede; objetos e canais não (erro claro);
* um erro dentro da tarefa remota chega ao programa principal com a mensagem original e o programa termina com código 1;
* o trabalhador só executa tarefas que existem no programa compilado, mas não tem autenticação: use apenas em rede confiável.

## Isolamento (regra do enunciado)

* o compilador impede atribuir, dentro de `par`/`fork`, a variáveis declaradas fora;
* listas e objetos são copiados em profundidade na criação da subtarefa (canais são compartilhados, para poderem comunicar);
* variáveis **globais** continuam compartilhadas entre as threads de um mesmo programa (leitura é permitida; cuidado ao alterá-las dentro de funções chamadas pelas subtarefas, pois não há exclusão mútua).

## Como o compilador trata as subtarefas

No código de três endereços cada subtarefa vira uma função separada (`main$professor`), que recebe como parâmetros as variáveis locais que usa:

```
fork professor on core 0 -> executar$professor(nome0, lote0)
r0 = join professor
```

O C++ gerado registra essas funções (`mp::register_task`) e cria as threads (ou a chamada remota) com cópias dos argumentos.

## Testes 8, 9 e 10 (4, 5 e 6 núcleos)

```
python3 mp.py run exemplos/teste08_avaliacao_4nucleos.mp -O2
python3 mp.py run exemplos/teste09_5nucleos_fractal.mp -O2
python3 mp.py run exemplos/teste10_6nucleos_2fractais.mp -O2     # grava sierpinski.svg na pasta atual
```

* O **gerador aleatório** do Python (congruencial linear com `& 0x7FFFFFFF`) foi reproduzido sem operadores bit a bit; os testes conferem que a sequência é idêntica à do Python. Cada avaliador tem o seu gerador, como cada processo tinha o seu estado no programa original.
* O **Mandelbrot** gerado é idêntico, caractere por caractere, ao do código Python do enunciado (verificado nos testes automáticos).
* O **Tapete de Sierpinski** do Teste 10 usava a biblioteca `turtle` (janela gráfica), que não existe em C++. Aqui ele é gerado como o arquivo `sierpinski.svg` (586 quadrados, aberto no navegador). Há uma imagem de conferência em `exemplos/saidas/sierpinski.png`.
* O programa imprime "Atividades corrigidas: 160 (sequencial) e 160 (paralelo)" para provar que as quatro subtarefas devolveram todo o trabalho.

### Por que o speedup do enunciado no Teste 10 foi 0,52x

No programa Python o tempo paralelo incluía abrir a janela do `turtle` e desenhar, e o modo sequencial não fazia o desenho. A comparação não era justa. Nesta versão os dois modos fazem **o mesmo trabalho** (160 atividades, Mandelbrot e Sierpinski) e só a geração do desenho (milissegundos) entra na medição; gravar e abrir o arquivo fica de fora. O tempo para gerar o desenho também é impresso à parte.

### Como interpretar o speedup

Cada correção simula trabalho com um laço de CPU, então o ganho depende do número de núcleos livres da máquina: com 4 núcleos o Teste 8 tende a 3x ou mais; em uma máquina de 1 núcleo o speedup fica perto de 1x (como em ambientes de teste simples). Com C++ compilado com `-O2` o trabalho todo leva cerca de 0,1 s (contra 3 s do Python), então os tempos são pequenos e variam entre execuções: repita algumas vezes.
