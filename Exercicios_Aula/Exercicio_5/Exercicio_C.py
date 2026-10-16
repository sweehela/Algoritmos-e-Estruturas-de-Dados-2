def tempo_minimo(e, x, a, t, n):
    memo = {}

    def calcular(linha, estacao):
        # primeira estação
        if estacao == 0:
            return e[linha] + a[linha][0]

        # retorna o resultado se já foi calculado
        if (linha, estacao) in memo:
            return memo[(linha, estacao)]

        continuar = calcular(linha, estacao - 1) + a[linha][estacao]

        # troca de linha
        outra_linha = 1 - linha
        trocar = (
            calcular(outra_linha, estacao - 1)
            + t[outra_linha][estacao - 1]
            + a[linha][estacao]
        )

        # armazena o menor tempo
        memo[(linha, estacao)] = min(continuar, trocar)

        return memo[(linha, estacao)]

    # tempos de saída
    linha1 = calcular(0, n - 1) + x[0]
    linha2 = calcular(1, n - 1) + x[1]

    return min(linha1, linha2)


# ex:
e = [2, 4]  # entrada
x = [3, 2]  # saída

a = [
    [7, 9, 3, 4, 8, 4],
    [8, 5, 6, 4, 5, 7]
]

t = [
    [2, 3, 1, 3, 4],  # 1 -> 2
    [2, 1, 2, 2, 1]   # 2 -> 1
]

n = 6

resultado = tempo_minimo(e, x, a, t, n)

print("Tempo mínimo total:", resultado)