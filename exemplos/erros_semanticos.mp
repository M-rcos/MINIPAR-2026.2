# Erros semânticos propositais (cada um em uma linha) para testar o analisador.
class Animal {
    var nome = "animal";
    func falar() { print("..."); }
}

class Cachorro extends Animal {
    func latir(vezes) { print("Au!", vezes); }
}

class Fantasma extends Inexistente { }

func soma(a, b) { return a + b; }

func sem_retorno() { print("oi"); }

var x = 10;
var x = 20;
y = 5;
var texto = "a" + 1;
number n = "texto";
if (x) { print("x"); }
print(soma(1));
print(naoexiste(3));
var v = sem_retorno();
var c = new Cachorro();
c.miar();
c.latir();
print(c.idade);
var w = new Inexistente();
break;
return 3;
print(this);
var lista = [1, 2];
lista.voar();
var s = "abc";
s[0] = "z";
fork t1 { x = 99; }
join t2;
c_channel canal a a;
send(x, 1);
print(len(5));
print(1 && true);
