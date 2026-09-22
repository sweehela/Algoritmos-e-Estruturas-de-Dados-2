N = 7

class No:
    def __init__(self, id_ameaca):
        self.id = id_ameaca
        self.proximo = None

class EncExt:
    def __init__(self):
        self.tabela = [None] * N

    def inserir(self, id_ameaca):
        indice = id_ameaca % N

        novo = No(id_ameaca)

        if self.tabela[indice] is None:
            self.tabela[indice] = novo
        else:
            atual = self.tabela[indice]

            while atual.proximo is not None:
                atual = atual.proximo

            atual.proximo = novo

    def imprimir(self):
        print("\n=== ENCADEAMENTO EXTERNO ===")

        for i in range(N):
            print(f"[{i}] -> ", end="")

            atual = self.tabela[i]

            if atual is None:
                print("vazio")
                continue

            while atual is not None:
                print(atual.id, end="")

                if atual.proximo is not None:
                    print(" -> ", end="")

                atual = atual.proximo

            print()

tabela_externa = EncExt()

valores = [10, 17, 24, 31, 5, 12]

for valor in valores:
    tabela_externa.inserir(valor)

tabela_externa.imprimir()