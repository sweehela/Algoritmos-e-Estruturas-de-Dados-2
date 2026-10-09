"""Testes do catálogo: localização, buscas, listas e contagens.

Todos os testes são offline: leem os dados do snapshot local
(data/snapshot.json) sem fazer nenhuma requisição de rede.
"""

import os
import unittest

from solar_system.catalog import Catalog, Criteria
from solar_system.data_acquisition import SolarSystemData
from solar_system.json_object import JsonObject


def build_catalog():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "snapshot.json")
    with open(path, "r", encoding="utf-8") as handle:
        raw = handle.read()
    bodies = SolarSystemData.build_from_raw(raw)
    catalog = Catalog()
    catalog.load(bodies)
    return catalog


class TestCatalog(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = build_catalog()

    def test_load_size(self):
        self.assertGreater(len(self.catalog), 500)

    def test_locate_by_id(self):
        earth = self.catalog.locate("terre")
        self.assertIsNotNone(earth)
        self.assertEqual(earth.english_name, "Earth")
        self.assertTrue(earth.is_planet)

    def test_locate_by_name_insensitive(self):
        mars = self.catalog.locate("Mars")
        self.assertIsNotNone(mars)
        self.assertEqual(mars.id, "mars")
        moon = self.catalog.locate("la lune")
        self.assertIsNotNone(moon)

    def test_locate_unknown(self):
        self.assertIsNone(self.catalog.locate("narnia"))

    def test_search_name_contains(self):
        results = self.catalog.search_name("Titan")
        self.assertTrue(any(b.id == "titan" for b in results))
        self.assertTrue(all("titan" in (b.name + " " + b.english_name).lower()
                            for b in results))

    def test_list_planets(self):
        planets = self.catalog.list_planets()
        self.assertEqual(len(planets), 8)
        self.assertTrue(all(b.is_planet for b in planets))

    def test_list_moons_of_earth(self):
        moons = self.catalog.list_moons("terre")
        self.assertEqual(len(moons), 1)
        self.assertEqual(moons[0].id, "lune")

    def test_criteria_filters(self):
        criteria = Criteria(body_type="Moon", min_radius=1000.0,
                            max_radius=5000.0)
        results = self.catalog.list_bodies(criteria)
        self.assertTrue(all(b.body_type == "Moon" for b in results))
        self.assertTrue(all(1000.0 <= b.mean_radius_km <= 5000.0
                            for b in results))

    def test_count_by_type(self):
        counts = self.catalog.count_by_type()
        self.assertEqual(counts.get("Planet"), 8)
        self.assertGreater(counts.get("Moon"), 400)

    def test_index_metrics_available(self):
        report = self.catalog.index_metrics()
        self.assertIn("colisões", report)
        self.assertIn("fator de carga", report)

    def test_host_of(self):
        moon = self.catalog.locate("lune")
        host = self.catalog.host_of(moon)
        self.assertEqual(host.id, "terre")

    def test_locate_portuguese_names(self):
        # nomes em português sem acento e em minúsculas
        self.assertEqual(self.catalog.locate("plutao").id, "pluton")
        self.assertEqual(self.catalog.locate("terra").id, "terre")
        self.assertEqual(self.catalog.locate("marte").id, "mars")
        self.assertEqual(self.catalog.locate("saturno").id, "saturne")
        self.assertEqual(self.catalog.locate("urano").id, "uranus")
        self.assertEqual(self.catalog.locate("neptuno").id, "neptune")
        self.assertEqual(self.catalog.locate("mercurio").id, "mercure")
        self.assertEqual(self.catalog.locate("sol").id, "soleil")
        self.assertEqual(self.catalog.locate("lua").id, "lune")

    def test_locate_portuguese_with_accent(self):
        # com acento e maiúsculas também funciona (normaliza)
        self.assertEqual(self.catalog.locate("Plutão").id, "pluton")
        self.assertEqual(self.catalog.locate("MERCÚRIO").id, "mercure")
        self.assertEqual(self.catalog.locate("Saturno").id, "saturne")

    def test_locate_english_names(self):
        self.assertEqual(self.catalog.locate("pluto").id, "pluton")
        self.assertEqual(self.catalog.locate("earth").id, "terre")
        self.assertEqual(self.catalog.locate("mars").id, "mars")

    def test_locate_rejects_other_languages(self):
        # entradas que não são português nem inglês não encontram nada
        self.assertIsNone(self.catalog.locate("narnia"))
        self.assertIsNone(self.catalog.locate("xyzabc"))

    def test_search_name_portuguese(self):
        results = self.catalog.search_name("plutao")
        self.assertTrue(any(b.id == "pluton" for b in results))


class TestJsonObject(unittest.TestCase):

    def test_parse_without_dict(self):
        from solar_system import api_client
        document = api_client.parse_json(
            '{"bodies": [{"id": "x", "mass": {"massValue": 1, "massExponent": 2}}]}')
        self.assertIsInstance(document, JsonObject)
        bodies = document.get("bodies")
        self.assertEqual(bodies[0].get("id"), "x")
        self.assertEqual(bodies[0].get("mass").get("massValue"), 1)

    def test_nested_values_are_json_objects(self):
        from solar_system import api_client
        document = api_client.parse_json('{"a": {"b": {"c": 1}}, "d": [1, 2]}')
        self.assertIsInstance(document.get("a"), JsonObject)
        self.assertIsInstance(document.get("a").get("b"), JsonObject)
        self.assertEqual(document.get("d"), [1, 2])


if __name__ == "__main__":
    unittest.main()
