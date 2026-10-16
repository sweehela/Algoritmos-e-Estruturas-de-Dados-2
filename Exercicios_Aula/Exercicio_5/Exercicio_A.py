def troco_dinamico(V, moedas):
    dp = [float('inf')] * (V + 1)

    # não precisamos de moedas para o troco 0
    dp[0] = 0

    # calcula quantidade mínima para cada valor
    for valor in range(1, V + 1):
        for moeda in moedas:
            if moeda <= valor:
                dp[valor] = min(dp[valor], dp[valor - moeda] + 1)

    # tabela resultante
    print("Tabela:")
    print(dp)

    # retorna a quantidade mínima de moedas
    if dp[V] == float('inf'):
        return -1

    return dp[V]


# ex:
moedas = [1, 3, 4]
V = 6

resultado = troco_dinamico(V, moedas)
print("Quantidade mínima de moedas:", resultado)