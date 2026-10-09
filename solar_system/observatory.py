"""Observatório virtual (funcionalidade extra do projeto).

Consulta o endpoint /positions da API: dado um lugar (latitude, longitude,
altitude) e um horário, devolve onde cada corpo está no céu (ascensão
reta, declinação, azimut e altura) e diz quais estão acima do horizonte,
ou seja, visíveis daquele ponto.
"""

from solar_system.data_acquisition import SolarSystemData


class Observatory:
    """Observa as posições dos corpos no céu a partir de um lugar."""

    def __init__(self, data_source=None):
        self._data = data_source or SolarSystemData()

    def observe(self, lat, lon, elev=0, datetime_iso=None, zone=0):
        """Devolve a lista de posições dos corpos no céu."""
        if datetime_iso is None:
            import datetime
            datetime_iso = datetime.datetime.utcnow().strftime(
                "%Y-%m-%dT%H:%M:%S")
        return self._data.fetch_positions(lat, lon, elev, datetime_iso, zone)

    @staticmethod
    def visible_positions(positions):
        return [position for position in positions if position.visible]

    @staticmethod
    def highest_position(positions):
        """Corpo mais alto no céu (None se não houver nenhum visível)."""
        visible = [p for p in positions if p.altitude_deg is not None]
        if not visible:
            return None
        visible.sort(key=lambda p: p.altitude_deg, reverse=True)
        return visible[0]
