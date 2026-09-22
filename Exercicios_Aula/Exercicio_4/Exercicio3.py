N = 7

VAZIO = None
LAPIDE = "LAPIDE"

class Linear:
    def __init__(self):
        self.tabela = [VAZIO] * N

    def inserir(self, id_ameaca):
        indice = id_ameaca % N

        for i in range(N):
            posicao = (indice + i) % N

            if self.tabela[posicao] is VAZIO or self.tabela[posicao] == LAPIDE:
                self.tabela[posicao] = id_ameaca
                return

        print("Tabela cheia.")

    def buscar(self, id_ameaca):
        indice = id_ameaca % N

        for i in range(N):
            posicao = (indice + i) % N

            if self.tabela[posicao] == id_ameaca:
                return posicao

            if self.tabela[posicao] is VAZIO:
                return -1

        return -1

    def remover(self, id_ameaca):
        posicao = self.buscar(id_ameaca)

        if posicao != -1:
            self.tabela[posicao] = LAPIDE
            return True

        return False

    def imprimir(self):
        print("\nTabela:")

        for i in range(N):
            print(f"[{i}] -> {self.tabela[i]}")

tabela = Linear()

valores = [10, 17, 24, 31, 5, 12]

for valor in valores:
    tabela.inserir(valor)

print("Tabela antes da remoção:")
tabela.imprimir()

tabela.remover(24)

print("\nTabela depois da remoção do ID 24:")
tabela.imprimir()

posicao = tabela.buscar(31)

print("\nBusca pelo ID 31:")

if posicao != -1:
    print(f"ID 31 encontrado na posição {posicao}.")
else:
    print("ID 31 não encontrado.")

# 3C: Sim, o ID 31 foi encontrado. A busca passou pela posição "lápide" e continuou procurando nas posições seguintes até encontrar o ID 31.