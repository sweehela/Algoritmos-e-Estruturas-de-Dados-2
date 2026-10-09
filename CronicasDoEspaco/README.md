# Crônicas do Espaço

Sistema em **Python** que usa a API *Solar System openData* para montar um
catálogo do Sistema Solar com os 554 corpos celestes (planetas, luas,
asteroides, cometas, planetas anões e o Sol). Dá para localizar corpos por
nome, buscar por atributos, listar por filtros, ver onde eles estão no céu
e planejar missões espaciais com uma estratégia gulosa.

Trabalho prático de Estruturas de Dados Avançadas — Parte 1.

---

## 1. Fonte de dados

| Dado | Valor |
| --- | --- |
| **API** | Solar System openData (v3.0.1) |
| **Endereço** | `https://api.le-systeme-solaire.net/rest` |
| **Documentação** | `https://api.le-systeme-solaire.net/rest/` (OpenAPI 3.1) |
| **Autenticação** | Cabeçalho `Authorization: Bearer <chave>` |
| **Chave pessoal** | guardada em `secrets.py` (não vai para o git; ver sessão 8) |
| **Data da consulta** | 23/09/2026 |

Escolhi essa API porque ela tem dados reais dos 554 corpos do
Sistema Solar, com atributos físicos e orbitais que permitem localizar corpos
por nome, buscar por características, listar por critérios e montar um
problema de seleção de missões com custo e benefício.

### 1.1 Endpoints usados

| Endpoint | O que faz | Onde é usado |
| --- | --- | --- |
| `GET /bodies` | Lista todos os corpos celestes | Carrega o catálogo no início |
| `GET /bodies/{id}` | Mostra um corpo específico | Comando `localizar` (online) |
| `GET /knowncount` | Contagens oficiais de objetos conhecidos | Comando `info` |
| `GET /positions` | Posição dos corpos no céu a partir de um lugar | Comando `observatorio` |

### 1.2 Exemplos de requisição

Nos exemplos, `$API_KEY` é a chave pessoal (que fica em `secrets.py`).

```bash
# Lista todos os corpos
curl -H "Authorization: Bearer $API_KEY" \
     "https://api.le-systeme-solaire.net/rest/bodies/"

# Só asteroides, com alguns campos e ordenados
curl -H "Authorization: Bearer $API_KEY" \
  "https://api.le-systeme-solaire.net/rest/bodies?filter[]=bodyType,eq,Asteroid&data=id,name,semimajorAxis,gravity&order=id,asc&page=1,5"

# Um corpo específico
curl -H "Authorization: Bearer $API_KEY" \
     "https://api.le-systeme-solaire.net/rest/bodies/terre"

# Posições visíveis a partir de Pelotas/RS
curl -H "Authorization: Bearer $API_KEY" \
  "https://api.le-systeme-solaire.net/rest/positions?lat=-31.7719&lon=-52.3426&elev=7&datetime=2026-09-23T00:00:00&zone=-3"
```

Exemplo de resposta (fragmento):

```json
{"bodies":[{"id":"2006sq372","name":"(308933) 2006 SQ372","semimajorAxis":151692240180,"gravity":0.0},
            {"id":"9-metis","name":"(9) M\u01d0tis","semimajorAxis":357052000,"gravity":0.0}]}
```

### 1.3 Estrutura dos dados

`GET /bodies` devolve um objeto com uma lista `bodies`. Cada corpo tem essa
forma:

```json
{
  "id": "uranus",
  "name": "Uranus",
  "englishName": "Uranus",
  "isPlanet": true,
  "moons": [{"moon": "Ariel", "rel": "https://.../bodies/ariel"}, ...],
  "semimajorAxis": 2870658186,
  "density": 1.27,
  "gravity": 8.87,
  "escape": 21380.0,
  "meanRadius": 25362.0,
  "sideralOrbit": 30685.4,
  "aroundPlanet": null,
  "discoveredBy": "William Herschel",
  "discoveryDate": "13/03/1781",
  "avgTemp": 76,
  "bodyType": "Planet",
  "rel": "https://api.le-systeme-solaire.net/rest/bodies/uranus"
}
```

Observações:
- `avgTemp` está em **kelvin** (0 = desconhecido). Ex: Vénus 737 K, Terra 288 K.
- `aroundPlanet` mostra o planeta anfitrião das luas (`{"planet": "terra", ...}`).
- A consulta de 23/09/2026 trouxe **554 corpos**: 8 Planet, 479 Moon,
  55 Asteroid, 7 Comet, 4 Dwarf Planet e 1 Star.

---

## 2. Arquitetura do sistema

```
cronicasDoEspaco/
├── main.py                     # Programa principal: menu e comandos
├── requirements.txt            # Sem dependências externas (só stdlib)
├── data/snapshot.json          # Resposta da API guardada (para usar offline)
├── solar_system/
│   ├── config.py               # Configurações: URL, chave, caminhos
│   ├── api_client.py           # Cliente HTTP e leitura de JSON (sem dict)
│   ├── json_object.py          # Objeto JSON guardado como lista de pares
│   ├── models.py               # Modelos: Body, Position, KnownCount
│   ├── data_acquisition.py     # ★ Pega os dados da API e organiza
│   ├── catalog.py              # Catálogo: índices Tabela Hash + buscas
│   ├── observatory.py          # Observatório virtual (funcionalidade extra)
│   ├── mission_planner.py      # ★ Opção A: planejamento guloso de missões
│   └── structures/
│       ├── instrumented.py     # Base para as estruturas medirem métricas
│       ├── hash_table.py       # ★ Tabela Hash implementada (Parte 1)
│       ├── trie_interface.py   # Interface da Trie (Parte 2)
│       └── btree_interface.py  # Interface da Árvore B (Parte 2)
└── tests/                      # Testes (35 casos, sem internet)
```

**Restrição cumprida:** em todo o código é proibido usar o tipo `dict` do
Python. Os documentos JSON são lidos com `json.loads(text, object_pairs_hook=...)`,
que entrega cada objeto como uma lista de pares (chave, valor) guardada na
classe `JsonObject` (`solar_system/json_object.py`). As agregações internas
usam a Tabela Hash que implementei.

---

## 3. Módulo de aquisição de dados

`solar_system/data_acquisition.py` — classe `SolarSystemData`. O que ele faz:

1. **Faz as requisições HTTP**: `api_client.get_json()` faz `GET` com o
   cabeçalho `Authorization: Bearer <chave>`, timeout de 30 s e 2 tentativas
   se a rede falhar.
2. **Lê e interpreta as respostas**: converte o JSON sem usar `dict`
   (JsonObject + listas).
3. **Filtra os campos importantes**: `_map_body()` pega os ~30 campos
   relevantes de cada corpo e descarta o resto.
4. **Transforma nos modelos internos**: cada corpo vira um objeto `Body`
   que depois carrega o catálogo.

**Modalidade principal: Nível 1 — Consumo Dinâmico (100%).** O programa
consulta a API em tempo real, lê a resposta e carrega as estruturas locais:

```
[aquisição] Carregando dados a partir de API Solar System openData (Nivel 1/dinâmico)...
[aquisição] 554 corpos celestes mapeados a modelos internos.
[Tabela Hash] entradas: 554 | capacidade: 1024 | fator de carga: 0.541 | colisões: 145 | cadeia máxima: 4 | redimensionamentos: 4
```

**Backup Nível 2 (Consumo Estático).** Cada resposta com sucesso é guardada
crua em `data/snapshot.json`. A flag `--offline` lê esse arquivo sem internet
(útil para demonstrações e testes). O módulo mantém as duas modalidades, com
o Nível 1 como padrão.

---

## 4. Estrutura implementada: Tabela Hash

### 4.1 Por que escolhi a Tabela Hash

Das três estruturas previstas, implementei a Tabela Hash por completo na
Parte 1. Justificativa:

| O que o sistema mais precisa fazer | Qual estrutura resolve melhor |
| --- | --- |
| Achar um corpo por **id** | Tabela Hash: **O(1)** em média |
| Buscar por nome exato | Tabela Hash: **O(1)** em média |
| Buscar por prefixo do nome ("mar", "titan"...) | Trie → **Parte 2** |
| Listar por intervalos numéricos (raio, gravidade) | Árvore B → **Parte 2** |

O que o sistema mais faz é *localizar corpos a partir de uma identificação*.
Essa operação, repetida milhares de vezes sobre 554 chaves, é justamente o
que a Tabela Hash resolve rápido (tempo constante médio). A Trie é melhor
para prefixos e a Árvore B para intervalos ordenados, mas ambas fariam a
busca exata por id de forma mais lenta. Por isso, essas duas ficam só como
interfaces (sessão 5) para implementar na Parte 2.

### 4.2 Como a Tabela Hash funciona

Arquivo: `solar_system/structures/hash_table.py`

- **Encadeamento separado**: quando duas chaves caem na mesma posição
  (colisão), elas ficam numa lista ligada dentro daquele espaço.
- **Função hash**: FNV-1a de 32 bits — espalha as chaves de forma uniforme.
- **Cresce sozinha**: quando fica mais de 75% cheia, dobra o tamanho e
  reorganiza tudo automaticamente.
- **Métricas medidas por dentro** (não calculadas depois):

| Métrica | Valor após carregar os 554 corpos |
| --- | --- |
| Entradas | 554 |
| Capacidade | 1024 |
| **Fator de carga** | **0,541** |
| **Colisões** | **145** (vezes que uma chave encontrou a posição ocupada) |
| Cadeia mais longa | 4 |
| Redimensionamentos | 4 |

As métricas aparecem no fim do carregamento (ver saída da sessão 3) e podem
ser consultadas a qualquer momento com `info`.

### 4.3 Como ela está integrada no sistema

`catalog.py` usa duas Tabelas Hash como índices:
- `_by_id`: índice principal, pela chave `id` de cada corpo;
- `_by_name`: índice secundário, pelos nomes em **português e inglês**
  (sem acentos e em minúsculas).

Com esses índices o sistema faz `locate()`, `search_name()` e as listagens
por critérios. A contagem por tipo (`count_by_type()`) também usa uma
Tabela Hash, evitando `dict`.

**Buscas em português e inglês.** As buscas aceitam português e inglês,
normalizados sem acentos e sem maiúsculas. Os nomes em português dos corpos
principais (Plutão→pluton, Saturno→saturne, Úrano→uranus, Lua→lune,
Sol→soleil...) estão numa lista `_PORTUGUESE_NAMES` em `catalog.py`. Assim,
`localizar plutao`, `Plutão` e `pluto` acham todos o corpo de id `pluton`.
Entradas em outros idiomas ou inexistentes devolvem `None`.

### 4.4 Análise de complexidade

Seja *n* o número de entradas, *m* a capacidade e α = n/m o fator de carga.
Com encadeamento separado e uma boa função hash (FNV-1a), as listas têm
tamanho médio α, então:

| Operação | Pior caso | Caso médio |
| --- | --- | --- |
| `insert` (sem redimensionar) | O(α) | O(1) quando α ≤ 0,75 |
| `insert` (com redimensionar) | O(n) | **O(1) amortizado** (ver 4.5) |
| `get` / `contains` | O(α) | O(1) |
| `delete` | O(α) | O(1) |
| `keys` / `values` / `items` | O(n + m) | O(n + m) |

Como a tabela mantém α ≤ 0,75 crescendo antes de passar desse limite, na
prática α ≈ 0,5 e cada lista tem tamanho médio ≈ 0,5. A instrumentação
registrou **cadeia máxima = 4** e **145 colisões** em 554 inserções,
confirmando o caso médio O(1).

### 4.5 Análise amortizada do redimensionamento

O redimensionamento é a operação mais cara da Tabela Hash: quando ela fica
muito cheia, é preciso criar um vetor maior e realocar todas as *n* entradas.
Uma inserção que dispara um redimensionamento custa O(n); as outras custam
O(1). A análise de pior caso (O(n)) é **estrita demais** para descrever
o custo de várias inserções seguidas, porque só uma a cada Θ(n) inserções
paga o redimensionamento. A análise amortizada mostra que o custo *por
operação* se mantém O(1).

**Traço real do carregamento de 554 corpos** (duas tabelas, 4
redimensionamentos cada, capacidade inicial 64):

| Redim. | Capacidade | Entradas realocadas |
| --- | --- | --- |
| 1.º | 64 → 128 | 48 |
| 2.º | 128 → 256 | 96 |
| 3.º | 256 → 512 | 192 |
| 4.º | 512 → 1024 | 384 |

Custo total = 554 inserções + 1440 realocações (4 redim. × 2 tabelas) =
**1994** operações. Custo amortizado por inserção = 1994 / 554 ≈ **3,60**
— claramente constante, o que contradiz a leitura pessimista O(n).

**Justificação pelo método contábil.** A cada inserção damos um crédito de
3 unidades: 1 paga a inserção e 2 ficam guardadas. Um redimensionamento que
realoca *k* entradas custa *k* unidades. Após redimensionar para capacidade
*m*, a tabela tem *k* ≤ m/2 entradas (porque dobrou). Ao chegar a *m*
entradas, o crédito acumulado é 2·(m − k) ≥ m, o que cobre o próximo
redimensionamento. Assim, cada inserção custa no máximo 3 unidades pagas
com seus próprios créditos → **O(1) amortizado**. No traço real: 3 × 554 =
1662 ≥ 1440 — sobra poupança, confirmando.

**Justificação pelo método do potencial.** Definimos Φ(T) = 2·n − m
(≥ 0 logo após um redimensionamento, quando n ≤ m/2). O custo amortizado de
uma inserção sem redimensionar é 1 + ΔΦ = 1 + 2 = **3** = O(1). Quando a
inserção faz n = m e dispara um redimensionamento (m dobra, n mantém),
ΔΦ = (2n − 2m) − (2n − m) = −m, então o custo amortizado é (n+1) − m ≤
**1** = O(1). Como Φ é sempre ≥ 0, a soma dos custos amortizados limita o
custo real: para *N* inserções o custo total é O(N), ou seja, **O(1)
amortizado por operação**. Para N = 554, isso dá ≈ 3,6 por inserção —
exatamente o 3,60 medido.

---

## 5. Interfaces projetadas: Trie e Árvore B (Parte 2)

As duas são classes abstratas (`abc.ABC`) que separam o *uso* da
*implementação*: o resto do sistema vai usar a estrutura sem precisar saber
como ela funciona por dentro.

- **Trie** (`trie_interface.py`): `insert`, `get`, `search`,
  `starts_with(prefix)`, `delete`, `__len__` e a métrica `nodes_visited()`
  (quantos nós foram percorridos nas buscas). Uso previsto: buscar corpos
  pelo prefixo do nome.
- **Árvore B** (`btree_interface.py`): `insert`, `search`,
  `range_query(lo, hi)`, `minimum`, `maximum`, `delete`, `__len__` e as
  métricas `height()` (altura) e `splits()` (divisões de nós). Uso previsto:
  listas ordenadas por números e buscas por faixa (ex: "corpos com raio entre
  1.000 e 3.000 km") sem precisar olhar item por item.

---

## 6. Operações do sistema

### 6.1 Localizar por identificação

```bash
python main.py localizar plutao        # por id ou nome em português
python main.py localizar "lua"         # por nome (português ou inglês)
python main.py localizar Pluto         # inglês também funciona
```

Mostra a ficha completa do corpo (órbita, massa, gravidade, temperatura,
descobrimento...). Em modo online também consulta `GET /bodies/{id}` para
mostrar o dado mais recente da API.

### 6.2 Buscar por atributos

```bash
python main.py buscar titan            # nome que contém o texto
python main.py listar --tipo Moon --anfitriao terra
python main.py listar --tipo "Dwarf Planet" --raio-min 500
python main.py listar --gravidade-min 20 --gravidade-max 30
python main.py listar --temp-k-min 200 --temp-k-max 330 --massa-min 1e23
python main.py listar --descobridor Herschel --descoberto
```

Filtros disponíveis: `--tipo`, `--anfitriao`, `--gravidade-min/max`,
`--raio-min/max`, `--temp-k-min/max`, `--massa-min/max`, `--descobridor`,
`--descoberto`.

### 6.3 Listar por critérios

São os mesmos filtros de 6.2: tipos do universo (Planet, Moon, Asteroid,
Comet, Dwarf Planet), luas de um planeta, corpos por intervalos de
gravidade, raio, temperatura ou massa, e corpos com descobrimento
documentado.

### 6.4 Funcionalidade extra: Observatório virtual

`observatory.py` + `GET /positions`: a partir de um lugar e horário, mostra
onde os corpos estão no céu (ascensão reta, declinação, azimut e altura) e
quais estão acima do horizonte (visíveis).

*Por que essa funcionalidade:* aproveita o endpoint mais diferente da API,
dá ao sistema uma dimensão de tempo e lugar (o céu muda com a hora e o
local) e ajuda a planejar quando observar um destino de missão. O padrão é
Pelotas/RS.

```bash
python main.py observatorio
python main.py observatorio --lat -31.7719 --lon -52.3426 --elev 7
python main.py observatorio --fecha 2026-09-29T20:00:00 --zona -3
```

---

## 7. Opção A: Planejamento e Triagem de Missões (estratégia gulosa)

### 7.1 O problema

A agência tem **combustível limitado** (orçamento `B`) e um **número máximo
de missões** (`M`). Cada destino tem um **custo** e um **benefício**
científico. O objetivo é escolher um conjunto de destinos que *maximize o
benefício total* respeitando as duas restrições (problema tipo *knapsack 0/1*
com limite de quantidade).

**Custo** (unidades de combustível):

```
custo = 2 × distância_efetiva_UA + 0,35 × gravidade
```

- **Ida e volta**: 2 × distância até o Sol (luas somam a distância do
  planeta anfitrião).
- **Pouso e decolagem**: proporcional à gravidade (pousar em gigantes
  gasosos ou na Terra é caro; em asteroides, quase grátis).

**Benefício** (pontos científicos):

| Condição | Pontos |
| --- | --- |
| Base por tipo: Planeta 50, Planeta Anão 40, Lua 30, Cometa 20, Asteroide 15, Estrela 10 | base |
| Temperatura na zona habitável (223–323 K) | +15 |
| Raio médio ≥ 1.000 km | +10 |
| Densidade ≥ 5,0 g/cm³ (rico em metais) | +10 |

O Sol (tipo Star) é excluído por padrão (não dá para pousar); pode ser
incluído com `--incluir-estrela`.

### 7.2 Critério e algoritmo guloso

**Critério: ratio benefício/custo, do maior para o menor** — ou seja, quais
destinos entregam mais ciência por unidade de combustível. É o critério
clássico do knapsack: prioriza os destinos mais eficientes, é rápido (uma
ordenação, O(n log n)) e dá decisões justificáveis numa só passagem.

```
1. Calcular o custo e o benefício de cada candidato.
2. Ordenar pelo ratio (maior primeiro; empate → menor custo).
3. Percorrer a lista aceitando cada um se:
     - ainda cabe no orçamento B, e
     - ainda não bateu o limite M de missões.
```

```bash
python main.py plan --orcamento 100 --max 4
```

### 7.3 Solução encontrada (dados de 23/09/2026)

```
Missões selecionadas: 4 (limite 4)
id      nome        tipo    dist(UA)  custo  benefício  ratio
mercure Mercúrio    Planet  0.387     2.07   70         33.830
terre   Terra       Planet  1.000     5.43   85         15.647
lune    Lua         Moon    0.003     2.57   40         15.551
venus   Vénus       Planet  0.723     4.55   70         15.381

Combustível utilizado: 14.62 / 100 | restante: 85.38
Benefício científico total: 265
```

### 7.4 Por que esse critério funciona

O ratio benefício/custo premia os destinos próximos e de alto valor
científico (Mercúrio, Terra, a Lua) e deixa de fora os gigantes longe
(Úrano: ~41,5 de custo; Neptuno: ~64), cujo transporte não compensa. Com as
duas restrições ativas, o método é determinista, rápido e fácil de auditar.

### 7.5 Onde a estratégia gulosa falha

A escolha puramente gulosa **não garante a melhor solução possível** no
knapsack 0/1: ao decidir pelo ratio, pode gastar combustível num item
"barato e eficiente" que impede pegar depois um item um pouco mais caro mas
com benefício maior. O sistema tem um comparador com a **melhor solução
possível** (força bruta, até 20 candidatos) para mostrar isso.

**Contra-exemplo real** (só os 8 planetas, orçamento 5,5, máximo 3 missões):

```
Solução GULOSA:  {Mercúrio}     benefício 70
Solução ÓTIMA:   {Terra}       benefício 85
A solução gulosa perde 15.0 pontos de benefício.
```

Mercúrio tem o melhor ratio (33,83) e entra primeiro, mas gasta 2,07 dos 5,5
disponíveis e nenhuma outra combinação cabe no restante (Vénus custa 4,55).
A Terra, um pouco mais cara (5,43) mas com mais benefício (85), é a escolha
ótima que o guloso descarta por não ser a primeira da fila.

```bash
python main.py comparar --tipo Planet --orcamento 5.5 --max 3
```

Outras limitações: (a) com orçamento frouxo e poucas missões, o ratio pode
pegar muitos destinos pequenos em vez de poucos grandes; (b) o resultado
depende de como se define custo e benefício; (c) por ser de uma só
passagem, não explora trocas (trocar dois destinos por um melhor). No caso
com orçamento 100 e máximo 4, o guloso coincide com o ótimo.

### 7.6 Análise da solução

**Complexidade.** Três fases: (1) calcular custo/benefício — O(n);
(2) ordenar pelo ratio — O(n log n); (3) percorrer aceitando — O(n). A
ordenação domina, então o total é **O(n log n)** em tempo e O(n) em espaço.
Para o catálogo completo (n ≈ 553) é instantâneo. A força bruta seria
**O(2ⁿ)** (só viável até n ≤ 20, por isso o limite no `comparar`).

**Qualidade.** O guloso por ratio é a heurística clássica do knapsack
fracionário (onde é ótimo). No knapsack 0/1 (nosso caso, missões não são
divisíveis) não garante o ótimo, mas tem garantias:

- *Nunca é pior que o melhor item único*: o guloso sempre pega o de maior
  ratio. No contra-exemplo (orçamento 5,5): 70/85 ≈ **0,82**, ou seja,
  atingiu **82%** do ótimo.
- *No cenário principal* (orçamento 100, máximo 4): benefício **265** e
  **coincidiu com o ótimo** (razão 1,00). Quando os custos são pequenos
  frente ao orçamento, o ratio se aproxima ou iguala o ótimo.
- *Gap médio*: sobre os 8 planetas, testando 91 orçamentos de 5 a 50, o
  guloso **coincidiu com o ótimo em 87 casos (96%)**; nos 4 restantes o gap
  foi no máximo **20%**.

Em resumo: a estratégia gulosa dá um **bom equilíbrio entre qualidade e
velocidade** — produz soluções próximas do ótimo em tempo quase-linear, e é
adequada para selecionar destinos num catálogo grande, onde a força bruta
seria inviável.

---

## 8. Como executar

Requisitos: **Python 3.8+** (sem dependências externas).

**Configurar a chave (uma vez).** A chave da API fica em `secrets.py`, na
raiz do projeto. Esse arquivo está no `.gitignore` (não vai para o
repositório). Crie assim:

```python
# secrets.py  (NÃO fazer commit — já no .gitignore)
API_KEY = "a-sua-chave-pessoal-uuid"
```

Sem `secrets.py`, o modo online falha sem erro e o sistema usa o snapshot
local (`data/snapshot.json`, também fora do git).

```bash
# Modo online (Nível 1): consulta a API em tempo real
python main.py info
python main.py localizar plutao
python main.py plan --orcamento 100 --max 4

# Modo offline (Nível 2): usa data/snapshot.json
python main.py --offline observatorio --lat -31.7719 --lon -52.3426

# Menu interativo
python main.py
```

Todos os comandos aceitam `--offline`. Ajuda: `python main.py -h`.

**Arquivos ignorados pelo git** (`.gitignore`): `secrets.py` (chave),
`data/snapshot.json` (snapshot da API), `__pycache__/`, ambiente virtual.

Testes (35 casos, sem internet):

```bash
python -m unittest discover -s tests -p "*.py"
```

---

## 9. Módulos e responsabilidades

| Módulo | O que faz |
| --- | --- |
| `data_acquisition.py` | Pega os dados da API, lê, filtra e transforma nos modelos (Nível 1 online, backup Nível 2 offline) |
| `catalog.py` | Índices Tabela Hash, localização por id/nome, busca por texto, listas por filtros, contagem por tipo |
| `hash_table.py` | Tabela Hash implementada (encadeamento, FNV-1a, redimensionamento) com métricas de colisões e fator de carga |
| `trie_interface.py` / `btree_interface.py` | Interfaces abstratas para a Parte 2 |
| `mission_planner.py` | Custo/benefício, seleção gulosa e comparação com o ótimo (força bruta) |
| `observatory.py` | Funcionalidade extra: observatório virtual (posições dos corpos no céu) |
| `main.py` | Linha de comandos e menu interativo |
