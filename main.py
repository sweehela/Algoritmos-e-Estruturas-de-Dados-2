"""
Comandos:
    info           Resumo do catálogo e métricas da Tabela Hash
    localizar      Achar um corpo por id ou nome
    buscar         Buscar por texto nos nomes
    listar         Listar corpos por filtros (tipo, gravidade, raio, ...)
    plan           Planejar missões (estratégia gulosa)
    comparar       Guloso vs. melhor possível (testa todas as combinações)
    observatorio   Posições dos corpos no céu a partir de um lugar
"""

import argparse
import sys

from solar_system.catalog import Catalog, Criteria
from solar_system.data_acquisition import SolarSystemData
from solar_system.mission_planner import MissionPlanner
from solar_system.observatory import Observatory


def _configure_console():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ------------------------------------------------- funções de ajuda

def print_table(headers, rows):
    widths = [len(str(header)) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    separator = "  ".join("-" * width for width in widths)
    format_str = "  ".join("{{:<{0}}}".format(width) for width in widths)
    print(format_str.format(*[str(h) for h in headers]))
    print(separator)
    for row in rows:
        print(format_str.format(*[str(cell) for cell in row]))


def _banner(title):
    print("")
    print("=" * 72)
    print("  " + title)
    print("=" * 72)


def _load_catalog(offline=False):
    """Carrega os dados (da internet ou do snapshot local) e o catálogo.

    No fim, mostra as métricas da Tabela Hash (exigido pela instrumentação).
    """
    source = "snapshot local (Nivel 2/offline)" if offline else \
        "API Solar System openData (Nivel 1/dinámico)"
    print("[aquisição] Carregando dados a partir de {0}...".format(source))
    data = SolarSystemData()
    bodies = data.fetch_bodies(offline=offline)
    catalog = Catalog()
    catalog.load(bodies)
    print("[aquisição] {0} corpos celestes mapeados a modelos internos."
          .format(len(bodies)))
    print("[Tabela Hash] {0}".format(catalog.index_metrics()))
    return data, catalog


def _display_name(body):
    """Nome para mostrar: português se tiver, senão inglês, senão o original."""
    from solar_system.catalog import _pt_names_for
    pt = _pt_names_for(body.id)
    if pt:
        return pt[0]
    return body.english_name or body.name


def _body_table_row(body, catalog):
    host = catalog.host_of(body)
    return [
        body.id,
        _display_name(body),
        body.body_type,
        "sim" if body.is_planet else "não",
        host.id if host else "-",
        "{0:.3f}".format(body.distance_au),
        body.gravity if body.gravity else "-",
        body.avg_temp_k if body.has_temperature() else "-",
    ]


def _list_bodies(catalog, bodies, title):
    _banner(title)
    if not bodies:
        print("Sem resultados.")
        return
    headers = ["id", "nome", "tipo", "planeta", "anfitrião", "dist(UA)",
               "gravidade", "temp(K)"]
    rows = [_body_table_row(body, catalog) for body in bodies]
    print_table(headers, rows)
    print("Total: {0} corpos.".format(len(bodies)))


# ------------------------------------------------- comandos do programa

def cmd_info(args, data, catalog):
    _banner("Resumo do universo: Solar System openData")
    print("Corpos no catálogo: {0}".format(len(catalog)))
    counts = catalog.count_by_type()
    for body_type, count in sorted(counts.items(),
                                   key=lambda pair: pair[1], reverse=True):
        print("  - {0}: {1}".format(body_type, count))
    print("")
    print("Contagens oficiais de objetos conhecidos (GET /knowncount):")
    try:
        known = data.fetch_known_counts()
    except Exception as exc:
        print("Não disponíveis sem conexão ({0}).".format(exc))
        return
    rows = [[entry.category, entry.count, entry.update_date]
            for entry in known]
    print_table(["categoria", "quantidade conhecida", "atualização"], rows)


def cmd_locate(args, data, catalog):
    body = catalog.locate(args.id)
    if body is None:
        print("Não foi encontrado nenhum corpo com id/nome '{0}'.".format(args.id))
        return 1
    if not args.offline:
        try:
            fresh = data.fetch_body(body.id)
            if fresh is not None and fresh.id:
                body = fresh
        except Exception:
            pass
    _banner("Ficha do corpo celeste")
    host = catalog.host_of(body)
    from solar_system.catalog import _pt_names_for
    pt_name = _pt_names_for(body.id)
    rows = [
        ["id", body.id],
        ["nome (português)", pt_name[0] if pt_name else "-"],
        ["nome (original)", body.name],
        ["nome inglês", body.english_name],
        ["tipo", body.body_type],
        ["é planeta", "sim" if body.is_planet else "não"],
        ["anfitrião", _display_name(host) if host else "-"],
        ["luas", ", ".join(body.moons[:8]) + ("..." if len(body.moons) > 8 else "")],
        ["semieixo maior (km)", "{0:,.0f}".format(body.semimajor_axis_km) if body.semimajor_axis_km else "-"],
        ["distância média (UA)", "{0:.3f}".format(body.distance_au) if body.distance_au else "-"],
        ["excentricidade", body.eccentricity],
        ["inclinação (°)", body.inclination_deg],
        ["massa (kg)", "{0:.3e}".format(body.mass_kg) if body.mass_kg else "-"],
        ["densidade (g/cm3)", body.density if body.density else "-"],
        ["gravidade (m/s2)", body.gravity if body.gravity else "-"],
        ["vel. escape (m/s)", body.escape_velocity if body.escape_velocity else "-"],
        ["raio médio (km)", "{0:,.1f}".format(body.mean_radius_km) if body.mean_radius_km else "-"],
        ["período orbital (dias)", body.sideral_orbit_days if body.sideral_orbit_days else "-"],
        ["temperatura média (K)", body.avg_temp_k if body.has_temperature() else "-"],
        ["descoberto por", body.discovered_by or "-"],
        ["data de descobrimento", body.discovery_date or "-"],
    ]
    print_table(["atributo", "valor"], rows)


def cmd_search(args, data, catalog):
    results = catalog.search_name(args.texto)
    _list_bodies(catalog, results,
                 "Busca por nome que contém: '{0}'".format(args.texto))


def cmd_list(args, data, catalog):
    criteria = Criteria(
        body_type=args.tipo,
        host_id=args.anfitriao,
        min_gravity=args.gravidade_min,
        max_gravity=args.gravidade_max,
        min_radius=args.raio_min,
        max_radius=args.raio_max,
        min_temp_k=args.temp_k_min,
        max_temp_k=args.temp_k_max,
        min_mass=args.massa_min,
        max_mass=args.massa_max,
        discovered_by=args.descobridor,
        has_discovery=args.descoberto,
    )
    results = catalog.list_bodies(criteria)
    _list_bodies(catalog, results, "Listado por critérios")


def _print_plan(plan, title, budget, max_missions=None):
    _banner(title)
    if not plan.selected:
        print("Nenhum destino selecionado (recursos insuficientes).")
        return
    headers = ["id", "nome", "tipo", "dist(UA)", "custo", "benefício", "ratio"]
    rows = [[
        c.body.id,
        _display_name(c.body),
        c.body.body_type,
        "{0:.3f}".format(c.body.distance_au),
        "{0:.2f}".format(c.cost),
        c.benefit,
        "{0:.3f}".format(c.ratio),
    ] for c in plan.selected]
    print_table(headers, rows)
    print("")
    if max_missions is not None:
        print("Missões selecionadas: {0} (limite {1})"
              .format(plan.missions_used(), max_missions))
    print("Combustível utilizado: {0:.2f} / {1} | restante: {2:.2f}"
          .format(plan.used_cost, budget, plan.remaining_cost))
    print("Benefício científico total: {0}".format(plan.total_benefit))


def cmd_plan(args, data, catalog):
    planner = MissionPlanner(catalog)
    plan = planner.plan_greedy(args.orcamento, args.max,
                               exclude_star=not args.incluir_estrela)
    _print_plan(plan,
                "Plano de missões (estratégia gulosa: ratio benefício/custo)",
                args.orcamento, args.max)
    print("")
    print("Critério: pega primeiro os destinos com maior ratio benefício/custo,")
    print("aceitando cada um se ainda cabe no combustível restante e no")
    print("limite de missões. Detalhes e limitações: ver README.")
    if args.top:
        _banner("Ranking de candidatos por ratio (top {0})".format(args.top))
        headers = ["#", "id", "nome", "tipo", "dist(UA)", "custo",
                   "benefício", "ratio"]
        rows = [[i + 1, c.body.id, _display_name(c.body), c.body.body_type,
                 "{0:.3f}".format(c.body.distance_au), "{0:.2f}".format(c.cost),
                 c.benefit, "{0:.3f}".format(c.ratio)]
                for i, c in enumerate(plan.candidates[:args.top])]
        print_table(headers, rows)


def cmd_compare(args, data, catalog):
    planner = MissionPlanner(catalog)
    candidates = planner.candidates(exclude_star=not args.incluir_estrela)
    if args.tipo:
        candidates = [c for c in candidates if c.body.body_type == args.tipo]
    if len(candidates) > 20:
        print("O conjunto tem {0} candidatos; a força bruta exige <= 20."
              .format(len(candidates)))
        print("Sugestão: restrinja com --tipo (p. ex. Planet, Comet, Moon).")
        return 1
    greedy = planner.plan_greedy(args.orcamento, args.max,
                                 exclude_star=not args.incluir_estrela,
                                 candidates=candidates)
    optimal = planner.plan_optimal(args.orcamento, args.max,
                                   exclude_star=not args.incluir_estrela,
                                   candidates=candidates)
    print("")
    print("Candidatos considerados: {0} | orçamento: {1} | missões máx: {2}"
          .format(len(candidates), args.orcamento, args.max))
    _print_plan(greedy, "Solução GULOSA", args.orcamento, args.max)
    _print_plan(optimal, "Solução ÓPTIMA (força bruta)", args.orcamento,
                args.max)
    gap = optimal.total_benefit - greedy.total_benefit
    print("")
    if gap > 0:
        print("A solução gulosa perde {0} pontos de benefício frente ao "
              "óptimo global (limitação da estratégia).".format(gap))
    else:
        print("Neste cenário a solução gulosa coincide com o óptimo.")


def cmd_observatory(args, data, catalog):
    _banner("Observatório virtual: posições aparentes")
    observatory = Observatory(data)
    positions = observatory.observe(args.lat, args.lon, args.elev,
                                    args.fecha, args.zona)
    headers = ["corpo", "asc. reta", "declinação", "azimut", "altura",
               "estado"]
    rows = [[position.name, position.right_ascension, position.declination,
             position.azimuth, position.altitude,
             "visível" if position.visible else "abaixo do horizonte"]
            for position in positions]
    print_table(headers, rows)
    visible = observatory.visible_positions(positions)
    print("")
    print("Corpos visíveis a partir de ({0}, {1}): {2} de {3}"
          .format(args.lat, args.lon, len(visible), len(positions)))
    highest = observatory.highest_position(positions)
    if highest:
        print("Corpo mais alto sobre o horizonte: {0} (altura {1})"
              .format(highest.name, highest.altitude))


# ----------------------------------------------------------- menu interativo

MENU_OPTIONS = [
    ("info", "Resumo do universo e métricas da Tabela Hash"),
    ("localizar <id>", "Localizar um corpo por id ou nome"),
    ("buscar <texto>", "Buscar corpos cujo nome contém o texto"),
    ("listar [critérios]", "Listar corpos por critérios (tipo, gravidade...)"),
    ("plan", "Plano de missões com estratégia gulosa"),
    ("comparar", "Comparar solução gulosa vs. óptima"),
    ("observatorio", "Posições visíveis a partir de uma localização"),
    ("sair", "Encerrar o programa"),
]


def _run_menu(data, catalog):
    print("")
    print("Bem-vindo a Crónicas do Espaço. Catálogo: {0} corpos."
          .format(len(catalog)))
    while True:
        print("")
        for i, (option, description) in enumerate(MENU_OPTIONS, start=1):
            print("  {0}. {1} - {2}".format(i, option, description))
        try:
            choice = input("Opção > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("")
            return
        args = argparse.Namespace(offline=False, id=choice, texto=choice,
                                  orcamento=100, max=4,
                                  incluir_estrela=False, top=10,
                                  tipo=None, anfitriao=None,
                                  gravidade_min=None, gravidade_max=None,
                                  raio_min=None, raio_max=None,
                                  temp_k_min=None, temp_k_max=None,
                                  massa_min=None, massa_max=None,
                                  descobridor=None, descoberto=False,
                                   lat=-31.7719, lon=-52.3426, elev=7,
                                   fecha=None, zona=-3)
        if choice == "1":
            cmd_info(args, data, catalog)
        elif choice == "2":
            target = input("Id ou nome do corpo > ").strip()
            args.id = target
            cmd_locate(args, data, catalog)
        elif choice == "3":
            text = input("Texto a buscar > ").strip()
            args.texto = text
            cmd_search(args, data, catalog)
        elif choice == "4":
            tipo = input("Tipo de corpo (vazio = todos) > ").strip()
            args.tipo = tipo or None
            cmd_list(args, data, catalog)
        elif choice == "5":
            cmd_plan(args, data, catalog)
        elif choice == "6":
            cmd_compare(args, data, catalog)
        elif choice == "7":
            cmd_observatory(args, data, catalog)
        elif choice in ("8", "sair", "q"):
            print("Até a próxima missão.")
            return
        else:
            print("Opção não reconhecida.")


# ---------------------------------------------------- configuração da linha de comandos

def build_parser():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Crónicas do Espaço: universo temático com a API "
                    "Solar System openData.",
    )
    parser.add_argument("--offline", action="store_true",
                        help="usar o snapshot local (data/snapshot.json) em "
                             "vez de consultar a API")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("info", help="resumo do universo e métricas")

    p_locate = subparsers.add_parser("localizar",
                                     help="localizar um corpo por id ou nome")
    p_locate.add_argument("id")

    p_search = subparsers.add_parser("buscar",
                                     help="buscar por texto nos nomes")
    p_search.add_argument("texto")

    p_list = subparsers.add_parser("listar", help="listados por critérios")
    p_list.add_argument("--tipo", help="tipo de corpo (Planet, Moon, ...)")
    p_list.add_argument("--anfitriao", help="id do planeta anfitrião")
    p_list.add_argument("--gravidade-min", type=float)
    p_list.add_argument("--gravidade-max", type=float)
    p_list.add_argument("--raio-min", type=float, help="raio médio mínimo (km)")
    p_list.add_argument("--raio-max", type=float)
    p_list.add_argument("--temp-k-min", type=float, dest="temp_k_min",
                        help="temperatura mínima (kelvin)")
    p_list.add_argument("--temp-k-max", type=float, dest="temp_k_max")
    p_list.add_argument("--massa-min", type=float, dest="massa_min")
    p_list.add_argument("--massa-max", type=float, dest="massa_max")
    p_list.add_argument("--descobridor", help="texto do descobridor")
    p_list.add_argument("--descoberto", action="store_true",
                        help="só corpos com descobridor e data")

    p_plan = subparsers.add_parser("plan", help="plano de missões (guloso)")
    p_plan.add_argument("--orcamento", type=float, default=100.0,
                        help="combustível disponível (por padrão 100)")
    p_plan.add_argument("--max", type=int, default=4,
                        help="número máximo de missões (por padrão 4)")
    p_plan.add_argument("--incluir-estrela", action="store_true",
                        help="incluir o Sol como candidato")
    p_plan.add_argument("--top", type=int, default=15,
                        help="quantos candidatos mostrar no ranking")

    p_compare = subparsers.add_parser(
        "comparar", help="guloso vs. óptimo (força bruta, <= 20 candidatos)")
    p_compare.add_argument("--orcamento", type=float, default=100.0)
    p_compare.add_argument("--max", type=int, default=4)
    p_compare.add_argument("--tipo", help="restringir candidatos por tipo")
    p_compare.add_argument("--incluir-estrela", action="store_true")

    p_obs = subparsers.add_parser("observatorio",
                                   help="posições dos corpos no céu")
    p_obs.add_argument("--lat", type=float, default=-31.7719)
    p_obs.add_argument("--lon", type=float, default=-52.3426)
    p_obs.add_argument("--elev", type=int, default=7)
    p_obs.add_argument("--fecha", default=None,
                       help="instante UTC ISO 8601 (yyyy-MM-ddThh:mm:ss)")
    p_obs.add_argument("--zona", type=int, default=-3, help="zona horária")

    return parser


def main(argv=None):
    _configure_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    data, catalog = _load_catalog(offline=args.offline)

    if args.command == "info":
        cmd_info(args, data, catalog)
    elif args.command == "localizar":
        cmd_locate(args, data, catalog)
    elif args.command == "buscar":
        cmd_search(args, data, catalog)
    elif args.command == "listar":
        cmd_list(args, data, catalog)
    elif args.command == "plan":
        cmd_plan(args, data, catalog)
    elif args.command == "comparar":
        cmd_compare(args, data, catalog)
    elif args.command == "observatorio":
        cmd_observatory(args, data, catalog)
    else:
        _run_menu(data, catalog)
    return 0


if __name__ == "__main__":
    sys.exit(main())