"""Testes da Tabela Hash e das métricas que ela mede."""

import unittest

from solar_system.structures.hash_table import HashTable, fnv1a_32


class TestHashTable(unittest.TestCase):

    def setUp(self):
        self.table = HashTable()

    def test_insert_and_get(self):
        self.table.insert("mercure", 1)
        self.table.insert("venus", 2)
        self.assertEqual(self.table.get("mercure"), 1)
        self.assertEqual(self.table.get("venus"), 2)
        self.assertEqual(len(self.table), 2)

    def test_update_existing_key(self):
        self.table.insert("tierra", 1)
        self.table.insert("tierra", 2)
        self.assertEqual(self.table.get("tierra"), 2)
        self.assertEqual(len(self.table), 1)

    def test_missing_key_raises(self):
        with self.assertRaises(KeyError):
            self.table.get("no-existe")

    def test_contains_and_delete(self):
        self.table.insert("marte", 10)
        self.assertTrue(self.table.contains("marte"))
        self.assertTrue(self.table.delete("marte"))
        self.assertFalse(self.table.contains("marte"))
        self.assertFalse(self.table.delete("marte"))
        self.assertEqual(len(self.table), 0)

    def test_load_factor(self):
        for i in range(100):
            self.table.insert("clave-{0}".format(i), i)
        expected = 100 / self.table.capacity
        self.assertAlmostEqual(self.table.load_factor, expected, places=6)
        self.assertLessEqual(self.table.load_factor, 0.75)

    def test_collisions_instrumentation(self):
        self.assertEqual(self.table.collisions, 0)
        for i in range(300):
            self.table.insert("clave-{0}".format(i), i)
        metrics = self.table.metrics()
        self.assertEqual(metrics.get("colisões"), self.table.collisions)
        self.assertEqual(metrics.get("entradas"), len(self.table))
        self.assertIsNotNone(metrics.get("cadeia máxima"))
        self.assertIsNotNone(metrics.get("redimensionamentos"))

    def test_iteration_covers_all_keys(self):
        keys = ["a", "b", "c", "d", "e"]
        for key in keys:
            self.table.insert(key, key.upper())
        found = sorted(key for key, _ in self.table.items())
        self.assertEqual(found, sorted(keys))

    def test_large_scale_integrity(self):
        for i in range(2000):
            self.table.insert("cuerpo-{0}".format(i), i)
        self.assertEqual(len(self.table), 2000)
        for i in range(0, 2000, 37):
            self.assertEqual(self.table.get("cuerpo-{0}".format(i)), i)

    def test_fnv_is_deterministic(self):
        self.assertEqual(fnv1a_32("jupiter"), fnv1a_32("jupiter"))
        self.assertNotEqual(fnv1a_32("jupiter"), fnv1a_32("saturno"))


if __name__ == "__main__":
    unittest.main()
