"""Cliente HTTP simples para a API Solar System openData.

Só usa bibliotecas que já vêm com o Python (urllib). Todas as respostas
são entregues como JsonObject/listas — nunca como dict, porque o
trabalho proíbe usar dict. :D
"""

import json
import urllib.error
import urllib.parse
import urllib.request

from solar_system import config
from solar_system.json_object import JsonObject


class ApiError(Exception):
    """Erro ao tentar falar com a API."""


def _object_pairs_hook(pairs):
    return JsonObject(pairs)


def parse_json(text):
    """Converte texto JSON em JsonObject/listas, sem usar dict."""
    return json.loads(text, object_pairs_hook=_object_pairs_hook)


def _headers():
    return {
        "Authorization": "Bearer {0}".format(config.API_KEY),
        "Accept": "application/json",
        "User-Agent": "cronicas-do-espaco/1.0",
    }


def get_json(path, query=None):
    """Faz uma requisição GET e devolve o JSON já convertido.

    Se a rede falhar, tenta de novo algumas vezes antes de desistir.
    """
    url = config.API_BASE_URL + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    request = urllib.request.Request(url, headers=_headers())
    last_error = None
    for attempt in range(config.DEFAULT_RETRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=config.DEFAULT_TIMEOUT_SECONDS) as response:
                raw = response.read().decode("utf-8")
                return parse_json(raw), raw
        except urllib.error.HTTPError as exc:
            message = "HTTP {0} ao consultar {1}".format(exc.code, path)
            raise ApiError(message) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
    raise ApiError("Não foi possível contactar a API após {0} tentativas: {1}".format(
        config.DEFAULT_RETRIES + 1, last_error))
