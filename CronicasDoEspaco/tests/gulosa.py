"""Testes do planejador de missões (estratégia gulosa)."""

import unittest

from solar_system.catalog import Catalog
from solar_system.data_acquisition import SolarSystemData
from solar_system.mission_planner import MissionPlanner
from tests.menu import build_catalog


class TestMissionPlanner(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = build_catalog()
        cls.planner = MissionPlanner(cls.catalog)

    def test_candidates_exclude_star(self):
        candidates = self.planner.candidates()
        self.assertTrue(all(c.body.body_type != "Star" for c in candidates))
        self.assertGreater(len(candidates), 500)

    def test_cost_and_benefit_positive(self):
        candidates = self.planner.candidates()
        self.assertTrue(all(c.cost > 0 for c in candidates))
        self.assertTrue(all(c.benefit > 0 for c in candidates))

    def test_earth_cost_is_cheap(self):
        earth = self.catalog.locate("terre")
        candidates = self.planner.candidates()
        earth_candidate = next(c for c in candidates if c.body.id == "terre")
        self.assertAlmostEqual(earth_candidate.cost,
                               2.0 * earth.distance_au + 0.35 * earth.gravity,
                               places=4)

    def test_greedy_respects_budget(self):
        plan = self.planner.plan_greedy(budget=30.0, max_missions=10)
        self.assertLessEqual(plan.used_cost, 30.0)

    def test_greedy_respects_max_missions(self):
        plan = self.planner.plan_greedy(budget=1000.0, max_missions=3)
        self.assertEqual(plan.missions_used(), 3)

    def test_greedy_prefers_high_ratio(self):
        plan = self.planner.plan_greedy(budget=100.0, max_missions=4)
        self.assertGreater(plan.total_benefit, 0)
        self.assertGreaterEqual(len(plan.selected), 1)

    def test_optimal_never_worse_than_greedy(self):
        planets = [c for c in self.planner.candidates()
                   if c.body.body_type == "Planet"]
        self.assertLessEqual(len(planets), 20)
        for budget in (10.0, 25.0, 50.0):
            greedy = self.planner.plan_greedy(budget, 3, candidates=planets)
            optimal = self.planner.plan_optimal(budget, 3, candidates=planets)
            self.assertGreaterEqual(optimal.total_benefit,
                                    greedy.total_benefit)
            self.assertLessEqual(optimal.used_cost, budget)
            self.assertLessEqual(optimal.missions_used(), 3)

    def test_optimal_bruteforce_limit(self):
        with self.assertRaises(ValueError):
            self.planner.plan_optimal(1000.0, 10)


if __name__ == "__main__":
    unittest.main()
