import os
from urllib.parse import urlparse

from dotenv import load_dotenv

from logics.erros import ErroTarot

MODELO_PADRAO = "gpt-4o-mini"
CHAVE_EXEMPLO = "sua-chave-aqui"
TIMEOUT_PADRAO = 60

# variável do .env -> (campo da API, conversor, mínimo, máximo)
PARAMETROS_GERACAO = {
    "OPENAI_MAX_TOKENS": ("max_tokens", int, 1, None),
    "OPENAI_TEMPERATURE": ("temperature", float, 0, 2),
    "OPENAI_TOP_P": ("top_p", float, 0, 1),
}


def _ler_numero(nome, conversor, minimo, maximo):
    texto = (os.getenv(nome) or "").strip()
    if not texto:
        return None
    try:
        valor = conversor(texto)
    except ValueError:
        valor = None
    if valor is None or valor < minimo or (maximo is not None and valor > maximo):
        faixa = f"entre {minimo} e {maximo}" if maximo is not None else f"maior ou igual a {minimo}"
        tipo = "inteiro" if conversor is int else "número"
        raise ErroTarot(f"Configuração inválida: {nome} deve ser um {tipo} {faixa}.")
    return valor


def _carregar_parametros():
    parametros = {}
    for nome, (campo, conversor, minimo, maximo) in PARAMETROS_GERACAO.items():
        valor = _ler_numero(nome, conversor, minimo, maximo)
        if valor is not None:
            parametros[campo] = valor
    return parametros


def carregar_configuracao():
    load_dotenv()
    chave = (os.getenv("OPENAI_API_KEY") or "").strip()
    url = (os.getenv("OPENAI_API_URL") or "").strip()
    modelo = (os.getenv("OPENAI_MODEL") or "").strip() or MODELO_PADRAO

    if not chave:
        raise ErroTarot(
            "Credencial ausente: defina OPENAI_API_KEY no arquivo .env (veja .env.example)."
        )
    if chave == CHAVE_EXEMPLO or not chave.isascii() or any(c.isspace() for c in chave):
        raise ErroTarot(
            "Credencial inválida: OPENAI_API_KEY está com o valor de exemplo ou em formato "
            "incorreto. Informe a chave real, sem espaços."
        )

    if not url:
        raise ErroTarot(
            "Configuração ausente: defina OPENAI_API_URL no arquivo .env (veja .env.example)."
        )
    partes = urlparse(url)
    if partes.scheme not in ("http", "https") or not partes.netloc:
        raise ErroTarot(
            "Configuração inválida: OPENAI_API_URL deve ser uma URL completa, "
            "como https://api.openai.com/v1/chat/completions."
        )

    return {
        "chave": chave,
        "url": url,
        "modelo": modelo,
        "parametros": _carregar_parametros(),
        "timeout": _ler_numero("OPENAI_TIMEOUT", int, 1, None) or TIMEOUT_PADRAO,
        "sistema": (os.getenv("OPENAI_SYSTEM_PROMPT") or "").strip() or None,
    }
