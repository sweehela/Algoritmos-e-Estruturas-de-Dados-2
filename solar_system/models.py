"""Modelos de dados internos da aplicação.

Representam os corpos celestes, as posições visíveis e as contagens de
objetos conhecidos que vêm da API.
"""

from dataclasses import dataclass, field

from solar_system.config import AU_KM


def to_float(value, default=None):
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_str(value, default=""):
    if value is None:
        return default
    return str(value)


@dataclass
class Body:
    """Um corpo celeste do catálogo (planeta, lua, asteroide, cometa...)."""

    id: str
    name: str
    english_name: str
    is_planet: bool
    body_type: str
    moons: list = field(default_factory=list)
    semimajor_axis_km: float = 0.0
    perihelion_km: float = 0.0
    aphelion_km: float = 0.0
    eccentricity: float = 0.0
    inclination_deg: float = 0.0
    mass_kg: float = 0.0
    density: float = 0.0
    gravity: float = 0.0
    escape_velocity: float = 0.0
    mean_radius_km: float = 0.0
    equa_radius_km: float = 0.0
    polar_radius_km: float = 0.0
    flattening: float = 0.0
    sideral_orbit_days: float = 0.0
    sideral_rotation_hours: float = 0.0
    around_planet_id: str = ""
    discovered_by: str = ""
    discovery_date: str = ""
    alternative_name: str = ""
    axial_tilt_deg: float = 0.0
    avg_temp_k: float = None
    rel_url: str = ""

    @property
    def distance_au(self):
        """Distância média do Sol (ou do planeta anfitrião) em UA."""
        return self.semimajor_axis_km / AU_KM if self.semimajor_axis_km else 0.0

    def has_temperature(self):
        return self.avg_temp_k is not None and self.avg_temp_k != 0.0

    def has_radius(self):
        return bool(self.mean_radius_km and self.mean_radius_km > 0.0)

    def full_name(self):
        if self.english_name and self.english_name.lower() != self.name.lower():
            return "{0} ({1})".format(self.name, self.english_name)
        return self.name


def _parse_degrees(text):
    """Converte algo como '-27°00\'41"' em -27.0 (pega o primeiro número)."""
    text = str(text).strip()
    if not text:
        return None
    end = text.find("\u00b0")
    if end < 0:
        end = 0
        while end < len(text) and (text[end].isdigit() or text[end] in "+-."):
            end += 1
    number = text[:end]
    try:
        return float(number)
    except ValueError:
        return None


@dataclass
class Position:
    """Posição de um corpo no céu vista por um observador na Terra."""

    name: str
    right_ascension: str
    declination: str
    azimuth: str
    altitude: str

    @property
    def altitude_deg(self):
        return _parse_degrees(self.altitude)

    @property
    def visible(self):
        alt = self.altitude_deg
        return alt is not None and alt > 0.0


@dataclass
class KnownCount:
    """Quantos objetos conhecidos existem de uma categoria."""

    category: str
    count: int
    update_date: str
