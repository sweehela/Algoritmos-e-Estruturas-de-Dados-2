"""Interface da estrutura Árvore B (para implementar na Parte 2).

A interface separa o uso da implementação: o resto do sistema vai usar
esta estrutura sem precisar saber como ela funciona por dentro.

Uso previsto (Parte 2):
  O catálogo vai gerar listas ordenadas por números (gravidade, raio,
  temperatura) e consultas por faixa, ex: "corpos com raio entre 1.000
  e 3.000 km". Como a Árvore B mantém tudo ordenado, ela responde rápido,
  sem precisar olhar item por item como faz hoje.

Métricas exigidas:
  - splits: quantas vezes um nó foi dividido ao inserir (especialmente
    durante o carregamento inicial dos dados);
  - altura: altura final da árvore depois de carregar tudo.
"""

from abc import ABC, abstractmethod


class BTree(ABC):
    """Árvore B ordenada por número, ligando cada chave a um valor."""

    @abstractmethod
    def insert(self, key, value):
        """Insere (número, valor) mantendo a ordem."""

    @abstractmethod
    def search(self, key):
        """Devolve o valor da chave; KeyError se não existir."""

    @abstractmethod
    def range_query(self, low, high):
        """Devolve os pares (chave, valor) entre low e high (inclusive)."""

    @abstractmethod
    def minimum(self):
        """Par (chave, valor) com a menor chave."""

    @abstractmethod
    def maximum(self):
        """Par (chave, valor) com a maior chave."""

    @abstractmethod
    def delete(self, key):
        """Remove a chave; devolve True se ela existia."""

    @abstractmethod
    def __len__(self):
        """Quantas chaves estão guardadas."""

    @abstractmethod
    def height(self):
        """Métrica: altura atual da árvore."""

    @abstractmethod
    def splits(self):
        """Métrica: total de divisões de nós que aconteceram."""
