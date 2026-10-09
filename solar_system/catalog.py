"""Catálogo do universo: índices e operações de busca.

A Tabela Hash implementada é usada aqui como índice de acesso:
  - índice por id (cada corpo tem um id único);
  - índice por nome em português e inglês (sem acentos e sem maiúsculas).

As buscas aceitam português e inglês, normalizados sem acentos e em
minúsculas (ex: "plutao" -> pluton). Com esses índices o sistema localiza 
corpos, busca por texto e lista por critérios.
"""

import unicodedata

from solar_system.structures.hash_table import HashTable


# Nomes em português dos corpos principais (id da API -> nome em PT).
# É uma lista de pares.
_PORTUGUESE_NAMES = [
    ("mercure", "Mercúrio"),
    ("venus", "Vénus"),
    ("terre", "Terra"),
    ("mars", "Marte"),
    ("jupiter", "Júpiter"),
    ("saturne", "Saturno"),
    ("uranus", "Úrano"),
    ("neptune", "Neptuno"),
    ("pluton", "Plutão"),
    ("ceres", "Ceres"),
    ("eris", "Éris"),
    ("makemake", "Makemaké"),
    ("haumea", "Haumea"),
    ("soleil", "Sol"),
    ("lune", "Lua"),
    ("ganymede", "Ganimedes"),
    ("callisto", "Calisto"),
    ("europa", "Europa"),
    ("io", "Io"),
    ("titan", "Titã"),
    ("rhea", "Reia"),
    ("iapetus", "Jápeto"),
    ("dione", "Dione"),
    ("enceladus", "Encélado"),
    ("mimas", "Mimas"),
    ("triton", "Tritão"),
    ("titania", "Titânia"),
    ("oberon", "Oberon"),
    ("umbriel", "Umbriel"),
    ("ariel", "Ariel"),
    ("miranda", "Miranda"),
    ("phobos", "Fobos"),
    ("deimos", "Deimos"),
]


def _fold_accents(text):
    """Tira acentos do texto."""
    nfkd = unicodedata.normalize("NFKD", str(text))
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def _normalize(text):
    """Padroniza para comparar: sem acentos, minúsculas, sem espaços nas pontas."""
    return _fold_accents(text).strip().lower()


def _pt_names_for(body_id):
    """Devolve os nomes em português de um corpo (lista, pode ser vazia)."""
    return [pt_name for api_id, pt_name in _PORTUGUESE_NAMES
            if api_id == body_id]


class Criteria:
    """As temperaturas são em kelvin (a unidade usada pela API)."""

    def __init__(self, body_type=None, host_id=None, min_gravity=None,
                 max_gravity=None, min_radius=None, max_radius=None,
                 min_temp_k=None, max_temp_k=None,
                 min_mass=None, max_mass=None,
                 discovered_by=None, has_discovery=False):
        self.body_type = body_type
        self.host_id = host_id
        self.min_gravity = min_gravity
        self.max_gravity = max_gravity
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.min_temp_k = min_temp_k
        self.max_temp_k = max_temp_k
        self.min_mass = min_mass
        self.max_mass = max_mass
        self.discovered_by = discovered_by
        self.has_discovery = has_discovery

    def matches(self, body):
        if self.body_type and body.body_type != self.body_type:
            return False
        if self.host_id and body.around_planet_id != self.host_id:
            return False
        if self.min_gravity is not None and body.gravity < self.min_gravity:
            return False
        if self.max_gravity is not None and body.gravity > self.max_gravity:
            return False
        if self.min_radius is not None and body.mean_radius_km < self.min_radius:
            return False
        if self.max_radius is not None and body.mean_radius_km > self.max_radius:
            return False
        if self.min_temp_k is not None and (
                not body.has_temperature() or body.avg_temp_k < self.min_temp_k):
            return False
        if self.max_temp_k is not None and (
                not body.has_temperature() or body.avg_temp_k > self.max_temp_k):
            return False
        if self.min_mass is not None and body.mass_kg < self.min_mass:
            return False
        if self.max_mass is not None and body.mass_kg > self.max_mass:
            return False
        if self.discovered_by and self.discovered_by.lower() not in (
                body.discovered_by or "").lower():
            return False
        if self.has_discovery and not (body.discovered_by and body.discovery_date):
            return False
        return True


class Catalog:
    """Catálogo de corpos celestes guardado em Tabelas Hash."""

    def __init__(self):
        self._by_id = HashTable()
        self._by_name = HashTable()
        self._bodies = []

    # ------------------------------------------------------------------ carga

    def load(self, bodies):
        """Carrega os corpos nos índices."""
        for body in bodies:
            self._by_id.insert(body.id, body)
            names = [body.english_name, body.name]
            names.extend(_pt_names_for(body.id))
            for raw_name in names:
                normalized = _normalize(raw_name)
                if normalized and not self._by_name.contains(normalized):
                    self._by_name.insert(normalized, body)
            self._bodies.append(body)

    # -------------------------------------------------- localização por id

    def locate(self, identifier):
        """Acha um corpo por id ou por nome (português ou inglês).

        Não diferencia maiúsculas de minúsculas nem acentos. Só aceita
        português e inglês.
        """
        if not identifier:
            return None
        key = _normalize(identifier)
        found = self._by_id.get_or_default(key)
        if found is not None:
            return found
        return self._by_name.get_or_default(key)

    # ------------------------------------------------------- buscas por texto

    def search_name(self, query):
        """Corpos cujo nome (português ou inglês) contém o texto."""
        needle = _normalize(query)
        if not needle:
            return []
        results = []
        for body in self._bodies:
            haystack = _normalize(body.name + " " + body.english_name)
            pt_haystack = " ".join(_normalize(n) for n in _pt_names_for(body.id))
            if needle in haystack or needle in pt_haystack:
                results.append(body)
        return results

    # -------------------------------------------------------------- listados

    def list_bodies(self, criteria=None):
        """Corpos que passam em todos os filtros indicados."""
        if criteria is None:
            criteria = Criteria()
        return [body for body in self._bodies if criteria.matches(body)]

    def list_by_type(self, body_type):
        return [body for body in self._bodies if body.body_type == body_type]

    def list_planets(self):
        return self.list_by_type("Planet")

    def list_dwarf_planets(self):
        return self.list_by_type("Dwarf Planet")

    def list_moons(self, host_id=None):
        if host_id:
            return [body for body in self._bodies
                    if body.body_type == "Moon" and body.around_planet_id == host_id]
        return self.list_by_type("Moon")

    def list_asteroids(self):
        return self.list_by_type("Asteroid")

    def list_comets(self):
        return self.list_by_type("Comet")

    # ------------------------------------------------------------ agregações

    def count_by_type(self):
        """Conta corpos por tipo, usando uma Tabela Hash."""
        counts = HashTable()
        for body in self._bodies:
            current = counts.get_or_default(body.body_type, 0)
            counts.insert(body.body_type, current + 1)
        return counts

    def host_of(self, body):
        """Devolve o planeta anfitrião de uma lua (None se não tem)."""
        if not body.around_planet_id:
            return None
        return self.locate(body.around_planet_id)

    def all(self):
        return list(self._bodies)

    def __len__(self):
        return len(self._bodies)

    # --------------------------------------------------------- instrumentação

    def index_metrics(self):
        return self._by_id.metrics_report()
