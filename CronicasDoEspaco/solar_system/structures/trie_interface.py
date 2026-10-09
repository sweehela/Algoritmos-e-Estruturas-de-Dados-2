"""Interface da estrutura Trie (para implementar na Parte 2).

A interface separa o uso da implementação: o resto do sistema vai usar
esta estrutura sem precisar saber como ela funciona por dentro.

Uso previsto (Parte 2):
  O catálogo vai buscar corpos pelo prefixo do nome (ex: "mar" encontra
  Marte, Marte I...). Hoje essa busca olha todos os nomes; com o Trie
  vai olhar só o pedaço que começa com o prefixo, bem mais rápido.

Métrica exigida:
  - nodos_visitados: quantos nós da árvore foram percorridos nas buscas,
    contados pela própria estrutura.
"""

from abc import ABC, abstractmethod


class Trie(ABC):
    """Árvore de prefixos: liga cada texto (chave) a um valor."""

    @abstractmethod
    def insert(self, key, value):
        """Guarda um valor associado a um texto."""

    @abstractmethod
    def get(self, key):
        """Devolve o valor da chave; KeyError se não existir."""

    @abstractmethod
    def search(self, key):
        """Devolve True se a chave completa existe no Trie."""

    @abstractmethod
    def starts_with(self, prefix):
        """Devolve os pares (chave, valor) que começam com o prefixo."""

    @abstractmethod
    def delete(self, key):
        """Remove a chave; devolve True se ela existia."""

    @abstractmethod
    def __len__(self):
        """Quantas chaves estão guardadas."""

    @abstractmethod
    def nodes_visited(self):
        """Métrica: quantos nós foram percorridos nas buscas."""
