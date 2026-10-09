"""Opção A: Planejamento e Triagem de Missões (otimização logística).

A agência de exploração tem recursos limitados (combustível) e um número
máximo de missões. Cada destino possível tem um custo (viagem de ida e
volta + pouso) e um benefício científico. O sistema atua como um filtro
inteligente de prioridades usando uma estratégia gulosa.

Critério de seleção (explicado no README):
  ratio = benefício / custo; os candidatos são processados em ordem
  decrescente de ratio e cada um é aceito se ainda cabe nos recursos.

Custo (unidades de combustível):
  custo = 2 * distância_efetiva_UA + 0,35 * gravidade
  - ida e volta: 2 x distância até o Sol (para luas, soma a distância
    do planeta anfitrião);
  - pouso/decolagem: proporcional à gravidade do destino.

Benefício (pontos científicos):
  - base por tipo: Planeta 50, Planeta Anão 40, Lua 30, Cometa 20,
    Asteroide 15, Estrela 10;
  - +15 se a temperatura está na zona habitável (223 a 323 K);
  - +10 se o raio médio é maior ou igual a 1.000 km;
  - +10 se a densidade é maior ou igual a 5,0 g/cm³.
"""

from dataclasses import dataclass

from solar_system.catalog import Catalog

TYPE_BASE_BENEFIT = {
    "Planet": 50,
    "Dwarf Planet": 40,
    "Moon": 30,
    "Comet": 20,
    "Asteroid": 15,
    "Star": 10,
}

HABITABLE_MIN_K = 223.0
HABITABLE_MAX_K = 323.0
LANDING_FUEL_FACTOR = 0.35
LARGE_RADIUS_KM = 1000.0
METALLIC_DENSITY = 5.0


@dataclass
class Candidate:
    """Um destino possível com seu custo, benefício e ratio."""

    body: object
    cost: float
    benefit: float

    @property
    def ratio(self):
        return self.benefit / self.cost if self.cost > 0 else 0.0


@dataclass
class MissionPlan:
    """Resultado do planejamento: destinos escolhidos e recursos gastos."""

    candidates: list
    selected: list
    used_cost: float
    total_benefit: float
    remaining_cost: float

    def missions_used(self):
        return len(self.selected)


class MissionPlanner:
    """Planeja missões usando a estratégia gulosa."""

    def __init__(self, catalog):
        self._catalog = catalog

    # ------------------------------------------------------------------ custos

    def effective_distance_au(self, body):
        """Distância até o Sol (luas somam a distância do anfitrião)."""
        if body.around_planet_id:
            host = self._catalog.host_of(body)
            if host is not None:
                return host.distance_au + body.distance_au
        return body.distance_au

    @staticmethod
    def compute_cost(body, distance_au):
        return 2.0 * distance_au + LANDING_FUEL_FACTOR * (body.gravity or 0.0)

    @staticmethod
    def compute_benefit(body):
        score = TYPE_BASE_BENEFIT.get(body.body_type, 0)
        if (body.has_temperature()
                and HABITABLE_MIN_K <= body.avg_temp_k <= HABITABLE_MAX_K):
            score += 15
        if body.mean_radius_km and body.mean_radius_km >= LARGE_RADIUS_KM:
            score += 10
        if body.density and body.density >= METALLIC_DENSITY:
            score += 10
        return score

    def candidates(self, exclude_star=True):
        """Monta a lista de destinos possíveis com custo e benefício."""
        result = []
        for body in self._catalog.all():
            if exclude_star and body.body_type == "Star":
                continue
            distance = self.effective_distance_au(body)
            if distance <= 0.0:
                continue
            result.append(Candidate(
                body=body,
                cost=self.compute_cost(body, distance),
                benefit=self.compute_benefit(body),
            ))
        return result

    # ------------------------------------------------------------------ guloso

    def plan_greedy(self, budget, max_missions, exclude_star=True,
                    candidates=None):
        """Seleção gulosa: pega primeiro os de maior ratio benefício/custo.

        Regra: o candidato entra se o combustível restante permite e se
        ainda não bateu o limite de missões.
        """
        if candidates is None:
            candidates = self.candidates(exclude_star)
        ordered = sorted(
            candidates,
            key=lambda c: (-c.ratio, c.cost),
        )
        selected = []
        used = 0.0
        for candidate in ordered:
            if len(selected) >= max_missions:
                break
            if used + candidate.cost <= budget:
                selected.append(candidate)
                used += candidate.cost
        total_benefit = sum(c.benefit for c in selected)
        return MissionPlan(ordered, selected, used, total_benefit,
                           budget - used)

    # ------------------------------------------------------- comparação ótima

    def plan_optimal(self, budget, max_missions, exclude_star=True,
                     candidates=None):
        """A melhor solução possível, testando todas as combinações.

        Só funciona com até 20 candidatos (testar todas as combinações
        fica inviável com mais que isso). Serve para comparar com o
        guloso e mostrar onde ele erra.
        """
        if candidates is None:
            candidates = self.candidates(exclude_star)
        if len(candidates) > 20:
            raise ValueError(
                "Muitos candidatos para testar todas as combinações "
                "(máx. 20): {0}".format(len(candidates)))
        best = MissionPlan(candidates, [], 0.0, 0.0, budget)
        limit = 1 << len(candidates)
        for mask in range(limit):
            if bin(mask).count("1") > max_missions:
                continue
            used = 0.0
            benefit = 0.0
            for i, candidate in enumerate(candidates):
                if mask & (1 << i):
                    used += candidate.cost
                    benefit += candidate.benefit
            if used <= budget and benefit > best.total_benefit:
                chosen = [candidates[i] for i in range(len(candidates))
                          if mask & (1 << i)]
                best = MissionPlan(candidates, chosen, used, benefit,
                                   budget - used)
        return best
