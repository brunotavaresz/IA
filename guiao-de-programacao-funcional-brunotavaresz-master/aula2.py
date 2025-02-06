import math;

#Exercicio 4.1
impar = lambda n: n % 2 != 0

#Exercicio 4.2
positivo = lambda n: n > 0

#Exercicio 4.3
comparar_modulo = lambda x, y: abs(x) < abs(y)

#Exercicio 4.4
cart2pol = lambda x, y: (math.sqrt(x**2 + y**2), math.atan2(y, x))

#Exercicio 4.5
ex5 = lambda f, g, h: lambda x, y, z: h(f(x, y), g(y, z))

#Exercicio 4.6
def quantificador_universal(lista, f):
    return [n for n in lista if not f(n)] == []

#Exercicio 4.8
def subconjunto(lista1, lista2):
    return quantificador_universal(lista1, lambda x: x in lista2)

#Exercicio 4.9
def menor_ordem(lista, f):
    if len(lista) == 1:
        return lista[0]
    else:
        n = menor_ordem(lista[1:], f)
        return lista[0] if f(lista[0], n) else n

#Exercicio 4.10
def menor_e_resto_ordem(lista, f):
    if len(lista) == 1:
        return lista[0], []
    else:
        n, p = menor_e_resto_ordem(lista[1:], f)
        return ((lista[0], lista[1:]) if f(lista[0], n) else (n, [lista[0]] + p))

#Exercicio 5.2
def ordenar_seleccao(lista, ordem):
    if lista == []:
        return []
    else:
        n, resto = menor_e_resto_ordem(lista, ordem)
        return [n] + ordenar_seleccao(resto, ordem)
