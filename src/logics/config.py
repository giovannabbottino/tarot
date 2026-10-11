import os
from urllib.parse import urlparse

from dotenv import load_dotenv

from logics.erros import ErroTarot

MODELO_PADRAO = "gpt-4o-mini"
CHAVE_EXEMPLO = "sua-chave-aqui"


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

    return {"chave": chave, "url": url, "modelo": modelo}
