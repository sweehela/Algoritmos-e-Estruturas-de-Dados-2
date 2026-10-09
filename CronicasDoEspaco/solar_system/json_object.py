"""Representa objetos JSON sem usar o tipo dict do Python.

O trabalho proíbe usar dict, então os documentos JSON são lidos como 
uma lista de pares (chave, valor). Esta classe guarda esses pares
e permite buscar valores por chave.
"""


class JsonObject:
    """Objeto JSON guardado como lista de pares (chave, valor)."""

    __slots__ = ("_pairs",)

    def __init__(self, pairs):
        self._pairs = list(pairs)

    def get(self, key, default=None):
        for k, v in self._pairs:
            if k == key:
                return v
        return default

    def has(self, key):
        for k, _ in self._pairs:
            if k == key:
                return True
        return False

    def keys(self):
        return [k for k, _ in self._pairs]

    def items(self):
        return iter(self._pairs)

    def __contains__(self, key):
        return self.has(key)

    def __len__(self):
        return len(self._pairs)

    def __repr__(self):
        inner = ", ".join("{0!r}: {1!r}".format(k, v) for k, v in self._pairs)
        return "JsonObject({0})".format(inner)
