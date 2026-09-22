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

        print("Tabela cheia!")

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
        print("\n=== SONDAGEM LINEAR ===")

        for i in range(N):
            print(f"[{i}] -> {self.tabela[i]}")

tabela = Linear()

valores = [10, 17, 24, 31, 5, 12]

for valor in valores:
    tabela.inserir(valor)

tabela.imprimir()

# PARTE C:

# Se a tabela fosse armazenada diretamente em um disco rígido, o encadeamento externo causaria mais lentidão nas buscas. Isso acontece porque os nós das listas encadeadas são alocados dinamicamente e podem ficar espalhados em diferentes regiões do disco. Já na sondagem linear, os elementos ficam dentro do próprio array, reduzindo a quantidade de acessos ao disco.