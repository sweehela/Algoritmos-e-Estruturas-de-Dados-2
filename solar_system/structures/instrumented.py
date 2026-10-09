"""Infraestrutura para que as estruturas de dados reportem métricas.

Toda estrutura avançada do sistema herda de Instrumented e deve informar
as métricas internas que ela mesma mede (não vale calcular depois).
"""


class Metrics:
    """Guarda métricas por nome e valor (sem usar dict)."""

    __slots__ = ("_entries",)

    def __init__(self):
        self._entries = []

    def add(self, name, value):
        self._entries.append((name, value))

    def entries(self):
        return iter(self._entries)

    def get(self, name):
        for key, value in self._entries:
            if key == name:
                return value
        return None

    def __str__(self):
        return " | ".join("{0}: {1}".format(name, value)
                          for name, value in self._entries)

    def __repr__(self):
        return "Metrics({0})".format(str(self))


class Instrumented:
    """Classe base que garante que toda estrutura saiba mostrar métricas."""

    def metrics(self):
        """Devolve as métricas internas atuais."""
        raise NotImplementedError

    def metrics_report(self):
        return str(self.metrics())
