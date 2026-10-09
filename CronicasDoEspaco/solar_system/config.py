"""Configurações gerais do projeto: endereço da API, chave e caminhos.

A chave pessoal da API fica em ``secrets.py`` (não vai para o git). Se
esse arquivo não existir, a chave fica vazia e o sistema usa o snapshot
local em vez de consultar a internet.
"""

API_BASE_URL = "https://api.le-systeme-solaire.net/rest"

try:
    from secrets import API_KEY
except ImportError:
    API_KEY = ""

ENDPOINT_BODIES = "/bodies"
ENDPOINT_BODY = "/bodies/{id}"
ENDPOINT_POSITIONS = "/positions"
ENDPOINT_KNOWNCOUNT = "/knowncount"

SNAPSHOT_PATH = "data/snapshot.json"

AU_KM = 149597870.7

DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_RETRIES = 2
