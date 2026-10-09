"""Módulo de aquisição e organização de dados.

O que este módulo faz:
  - faz as requisições HTTP (GET) à API Solar System openData;
  - lê e interpreta as respostas em JSON (sem usar dict);
  - separa os campos importantes de cada corpo celeste;
  - transforma tudo nos modelos internos da aplicação (Body).

Modalidade principal: Nível 1 (Consumo Dinâmico) — as requisições são
feitas enquanto o programa roda. Como backup, a resposta bruta é salva
em data/snapshot.json e pode ser reaproveitada sem internet (Nível 2,
Consumo Estático), útil para demonstrações e testes.
"""

import os

from solar_system import api_client, config
from solar_system.json_object import JsonObject
from solar_system.models import Body, KnownCount, Position, to_float


class SolarSystemData:
    """Pega os dados da API e transforma nos modelos do sistema."""

    # ---------------------------------------------------------------- bodies

    def fetch_bodies(self, offline=False):
        """Devolve a lista de todos os corpos celestes.

        offline=True  -> lê o snapshot local (data/snapshot.json).
        offline=False -> consulta a API em tempo real.
        """
        if offline:
            raw = self.load_snapshot()
            return self.build_from_raw(raw)
        document, raw = api_client.get_json(config.ENDPOINT_BODIES)
        self.save_snapshot(raw)
        return self._extract_bodies(document)

    def fetch_body(self, body_id):
        """Devolve um corpo específico via GET /bodies/{id}."""
        document, _ = api_client.get_json(
            config.ENDPOINT_BODY.format(id=body_id))
        if not isinstance(document, JsonObject):
            return None
        return self._map_body(document)

    @staticmethod
    def _extract_bodies(document):
        bodies = document.get("bodies")
        if bodies is None:
            return []
        return [SolarSystemData._map_body(item) for item in bodies]

    @staticmethod
    def _map_body(item):
        """Pega os campos importantes do JSON e transforma num Body."""
        mass = item.get("mass")
        mass_kg = 0.0
        if isinstance(mass, JsonObject):
            value = mass.get("massValue")
            exponent = mass.get("massExponent")
            if value is not None and exponent is not None:
                mass_kg = float(value) * (10.0 ** int(exponent))

        moons = item.get("moons")
        moon_names = []
        if moons:
            for moon in moons:
                if isinstance(moon, JsonObject):
                    name = moon.get("moon")
                    if name:
                        moon_names.append(str(name))
                else:
                    moon_names.append(str(moon))

        around = item.get("aroundPlanet")
        around_id = ""
        if isinstance(around, JsonObject):
            around_id = str(around.get("planet") or "")

        return Body(
            id=str(item.get("id") or ""),
            name=str(item.get("name") or ""),
            english_name=str(item.get("englishName") or ""),
            is_planet=bool(item.get("isPlanet")),
            body_type=str(item.get("bodyType") or ""),
            moons=moon_names,
            semimajor_axis_km=to_float(item.get("semimajorAxis"), 0.0),
            perihelion_km=to_float(item.get("perihelion"), 0.0),
            aphelion_km=to_float(item.get("aphelion"), 0.0),
            eccentricity=to_float(item.get("eccentricity"), 0.0),
            inclination_deg=to_float(item.get("inclination"), 0.0),
            mass_kg=mass_kg,
            density=to_float(item.get("density"), 0.0),
            gravity=to_float(item.get("gravity"), 0.0),
            escape_velocity=to_float(item.get("escape"), 0.0),
            mean_radius_km=to_float(item.get("meanRadius"), 0.0),
            equa_radius_km=to_float(item.get("equaRadius"), 0.0),
            polar_radius_km=to_float(item.get("polarRadius"), 0.0),
            flattening=to_float(item.get("flattening"), 0.0),
            sideral_orbit_days=to_float(item.get("sideralOrbit"), 0.0),
            sideral_rotation_hours=to_float(item.get("sideralRotation"), 0.0),
            around_planet_id=around_id,
            discovered_by=str(item.get("discoveredBy") or ""),
            discovery_date=str(item.get("discoveryDate") or ""),
            alternative_name=str(item.get("alternativeName") or ""),
            axial_tilt_deg=to_float(item.get("axialTilt"), 0.0),
            avg_temp_k=to_float(item.get("avgTemp"), None),
            rel_url=str(item.get("rel") or ""),
        )

    # --------------------------------------------------------------- snapshot

    @staticmethod
    def build_from_raw(raw_text):
        """Recupera a lista de corpos a partir do texto JSON salvo."""
        document = api_client.parse_json(raw_text)
        return SolarSystemData._extract_bodies(document)

    @staticmethod
    def save_snapshot(raw_text):
        os.makedirs(os.path.dirname(config.SNAPSHOT_PATH), exist_ok=True)
        with open(config.SNAPSHOT_PATH, "w", encoding="utf-8") as handle:
            handle.write(raw_text)

    @staticmethod
    def load_snapshot():
        with open(config.SNAPSHOT_PATH, "r", encoding="utf-8") as handle:
            return handle.read()

    # ------------------------------------------------------------- knowncount

    def fetch_known_counts(self):
        """Devolve as contagens de objetos conhecidos (GET /knowncount)."""
        document, _ = api_client.get_json(config.ENDPOINT_KNOWNCOUNT)
        entries = document.get("knowncount") or []
        result = []
        for entry in entries:
            result.append(KnownCount(
                category=str(entry.get("id") or ""),
                count=int(entry.get("knownCount") or 0),
                update_date=str(entry.get("updateDate") or ""),
            ))
        return result

    # ------------------------------------------------------------- positions

    def fetch_positions(self, lat, lon, elev, datetime_iso, zone):
        """Posições dos corpos no céu (GET /positions)."""
        query = {
            "lat": lat,
            "lon": lon,
            "elev": elev,
            "datetime": datetime_iso,
            "zone": zone,
        }
        document, _ = api_client.get_json(config.ENDPOINT_POSITIONS, query=query)
        entries = document.get("positions") or []
        result = []
        for entry in entries:
            result.append(Position(
                name=str(entry.get("name") or ""),
                right_ascension=str(entry.get("ra") or ""),
                declination=str(entry.get("dec") or ""),
                azimuth=str(entry.get("az") or ""),
                altitude=str(entry.get("alt") or ""),
            ))
        return result
