"""Tabela Hash com encadeamento separado (listas ligadas).

Estrutura implementada por completo na Parte 1 do trabalho.

Como funciona:
  - a tabela cresce sozinha: quando fica mais de 75% cheia, dobra o
    tamanho e reorganiza tudo;
  - quando duas chaves caem na mesma posição (colisão), elas ficam
    numa lista ligada dentro daquele espaço;
  - a função hash usada é a FNV-1a, que espalha as chaves de forma
    uniforme;
  - a estrutura mede e conta coisas por dentro: quantas colisões
    aconteceram, quão cheia está, qual a maior lista e quantas vezes
    cresceu.

Restrição do trabalho: não usa o tipo dict do Python.
"""

from solar_system.structures.instrumented import Instrumented, Metrics

INITIAL_CAPACITY = 64
MAX_LOAD_FACTOR = 0.75
GROWTH_FACTOR = 2

FNV_PRIME = 16777619
FNV_OFFSET = 2166136261


def fnv1a_32(text):
    """Função hash FNV-1a: transforma um texto num número de 32 bits."""
    hash_value = FNV_OFFSET
    for char in str(text):
        hash_value ^= ord(char)
        hash_value = (hash_value * FNV_PRIME) & 0xFFFFFFFF
    return hash_value


class Node:
    """Um item de uma lista ligada dentro da tabela."""

    __slots__ = ("key", "value", "next")

    def __init__(self, key, value, next_node=None):
        self.key = key
        self.value = value
        self.next = next_node


class Chain:
    """Lista ligada simples: guarda os itens que caíram na mesma posição."""

    __slots__ = ("head", "length")

    def __init__(self):
        self.head = None
        self.length = 0

    def find(self, key):
        current = self.head
        while current is not None:
            if current.key == key:
                return current
            current = current.next
        return None

    def prepend(self, key, value):
        self.head = Node(key, value, self.head)
        self.length += 1

    def remove(self, key):
        current = self.head
        previous = None
        while current is not None:
            if current.key == key:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                self.length -= 1
                return True
            previous = current
            current = current.next
        return False

    def __iter__(self):
        current = self.head
        while current is not None:
            yield current
            current = current.next


class HashTable(Instrumented):
    """Tabela hash que mede as próprias métricas por dentro."""

    def __init__(self, capacity=INITIAL_CAPACITY):
        self._buckets = [None] * capacity
        self._capacity = capacity
        self._size = 0
        self._collisions = 0
        self._resizes = 0
        self._max_chain = 0

    # ----------------------------------------------------------- internals

    def _index_of(self, key):
        return fnv1a_32(key) % self._capacity

    def _grow_if_needed(self):
        if self._size + 1 > self._capacity * MAX_LOAD_FACTOR:
            self._resize(self._capacity * GROWTH_FACTOR)

    def _resize(self, new_capacity):
        old_buckets = self._buckets
        self._buckets = [None] * new_capacity
        self._capacity = new_capacity
        self._size = 0
        self._collisions = 0
        self._max_chain = 0
        for chain in old_buckets:
            if chain is None:
                continue
            for node in chain:
                self._insert_node(node.key, node.value)
        self._resizes += 1

    def _insert_node(self, key, value):
        index = self._index_of(key)
        chain = self._buckets[index]
        if chain is None:
            chain = Chain()
            self._buckets[index] = chain
        else:
            existing = chain.find(key)
            if existing is not None:
                existing.value = value
                return
            self._collisions += 1
        chain.prepend(key, value)
        self._size += 1
        if chain.length > self._max_chain:
            self._max_chain = chain.length

    # -------------------------------------------------------------- public

    def insert(self, key, value):
        """Guarda ou atualiza um valor. Conta as colisões reais."""
        self._grow_if_needed()
        self._insert_node(key, value)

    def get(self, key):
        """Devolve o valor da chave; dá KeyError se não existir."""
        chain = self._buckets[self._index_of(key)]
        if chain is None:
            raise KeyError(key)
        node = chain.find(key)
        if node is None:
            raise KeyError(key)
        return node.value

    def get_or_default(self, key, default=None):
        try:
            return self.get(key)
        except KeyError:
            return default

    def contains(self, key):
        chain = self._buckets[self._index_of(key)]
        if chain is None:
            return False
        return chain.find(key) is not None

    def delete(self, key):
        """Remove a chave; devolve True se ela existia."""
        index = self._index_of(key)
        chain = self._buckets[index]
        if chain is None:
            return False
        if chain.remove(key):
            self._size -= 1
            if chain.length == 0:
                self._buckets[index] = None
            return True
        return False

    def keys(self):
        for key, _ in self.items():
            yield key

    def values(self):
        for _, value in self.items():
            yield value

    def items(self):
        for chain in self._buckets:
            if chain is None:
                continue
            for node in chain:
                yield (node.key, node.value)

    def __iter__(self):
        return self.items()

    def __len__(self):
        return self._size

    def __contains__(self, key):
        return self.contains(key)

    @property
    def size(self):
        return self._size

    @property
    def capacity(self):
        return self._capacity

    @property
    def load_factor(self):
        return self._size / self._capacity if self._capacity else 0.0

    @property
    def collisions(self):
        return self._collisions

    # ----------------------------------------------------- instrumentação

    def metrics(self):
        m = Metrics()
        m.add("entradas", self._size)
        m.add("capacidade", self._capacity)
        m.add("fator de carga", round(self.load_factor, 4))
        m.add("colisões", self._collisions)
        m.add("cadeia máxima", self._max_chain)
        m.add("redimensionamentos", self._resizes)
        return m
