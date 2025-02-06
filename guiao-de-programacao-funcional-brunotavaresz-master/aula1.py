#Exercicio 1.1
def comprimento(lista):
		if lista == []:
			return 0
		else:
			return 1 + comprimento(lista[1:])

#Exercicio 1.2
def soma(lista):
		if lista == []:
			return 0
		else:
			return lista[0] + soma(lista[1:])

#Exercicio 1.3
def existe(lista, elem):
		if lista == []:
			return False
		elif lista[0] == elem:
			return True
		else:
			return existe(lista[1:], elem)

#Exercicio 1.4
def concat(l1, l2):
		if l1 == []:
			return l2
		else:
			return [l1[0]] + concat(l1[1:], l2)

#Exercicio 1.5
def inverte(lista):
		if lista == []:
			return []
		else:
			return inverte(lista[1:]) + [lista[0]]

#Exercicio 1.6
def capicua(lista):
		if len(lista) <= 1:
			return True
		elif lista[0] != lista[-1]:
			return False
		else:
			return capicua(lista[1:-1])

#Exercicio 1.7
def concat_listas(lista):
		if lista == []:
			return []
		else:
			return lista[0] + concat_listas(lista[1:])

#Exercicio 1.8
def substitui(lista, original, novo):
		if lista == []:
			return []
		elif lista[0] == original:
			return [novo] + substitui(lista[1:], original, novo)
		else:
			return [lista[0]] + substitui(lista[1:], original, novo)

#Exercicio 1.9
def fusao_ordenada(lista1, lista2):
		if lista1 == []:
			return lista2
		elif lista2 == []:
			return lista1
		elif lista1[0] < lista2[0]:
			return [lista1[0]] + fusao_ordenada(lista1[1:], lista2)
		else:
			return [lista2[0]] + fusao_ordenada(lista1, lista2[1:])

#Exercicio 1.10
def lista_subconjuntos(lista):
		if lista == []:
			return [[]]
		else:
			semp = lista_subconjuntos(lista[1:])
			comp = [[lista[0]] + sub for sub in semp]
			return semp + comp


#Exercicio 2.1
def separar(lista):
		if lista == []:
			return ([], [])
		else:
			(primeiros, segundos) = separar(lista[1:])
			return ([lista[0][0]] + primeiros, [lista[0][1]] + segundos)

#Exercicio 2.2
def remove_e_conta(lista, elem):
		if lista == []:
			return ([], 0)
		else:
			nova_lista, contagem = remove_e_conta(lista[1:], elem)
			if lista[0] == elem:
				return (nova_lista, contagem + 1)
			else:
				return ([lista[0]] + nova_lista, contagem)
			
#Exercicio 2.3
def contar_ocorrencias(lista):
		if lista == []:
			return []
		else:
			primeiro = lista[0]
			nova_lista, contagem = remove_e_conta(lista, primeiro)
			return [(primeiro, contagem)] + contar_ocorrencias(nova_lista)

# Exercicio 3.1
def cabeca(lista):
    if lista == []:
        return None
    else:
        return lista[0]


# Exercicio 3.2
def cauda(lista):
    if lista == []:
        return None
    else:
        return lista[1:]

# Exercicio 3.3
def juntar(l1, l2):
    if len(l1) != len(l2):
        return None
    else:
        if l1 == []:
            return []
        else:
            return [(l1[0], l2[0])] + juntar(l1[1:], l2[1:])

#Exercicio 3.4
def menor(lista):
    if len(lista) == 0:
        return None
    else:
        menor_valor = menor(lista[1:])
        if menor_valor == None or lista[0] < menor_valor:
            return lista[0]
        else:
            return menor_valor


#Exercicio 3.6
def max_min(lista):
    if lista == []:
        return None
    if len(lista) == 1:
        return lista[0], lista[0]
    else:
        maior_valor, menor_valor = max_min(lista[1:])
        if menor_valor == None or lista[0] < menor_valor:
            menor_valor = lista[0]
        if maior_valor == None or lista[0] > maior_valor:
            maior_valor = lista[0]
        return maior_valor, menor_valor

