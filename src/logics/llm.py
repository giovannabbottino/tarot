import requests

from logics.erros import ErroTarot

SISTEMA = "Você é um tarólogo experiente. Responda em português, de forma clara e acolhedora."
TIMEOUT_SEGUNDOS = 60


def montar_prompt(pergunta, cartas):
    linhas = [f"- {posicao}: {carta}{orientacao}" for posicao, carta, orientacao in cartas]
    return (
        f"Pergunta do consulente: {pergunta}\n\n"
        "Cartas sorteadas:\n" + "\n".join(linhas) + "\n\n"
        "Interprete cada carta em sua posição e finalize com uma síntese "
        "que responda à pergunta."
    )


def montar_requisicao(prompt, configuracao):
    return {
        "url": configuracao["url"],
        "headers": {"Authorization": f"Bearer {configuracao['chave']}"},
        "json": {
            "model": configuracao["modelo"],
            "messages": [
                {"role": "system", "content": configuracao.get("sistema") or SISTEMA},
                {"role": "user", "content": prompt},
            ],
            **configuracao.get("parametros", {}),
        },
        "timeout": configuracao.get("timeout", TIMEOUT_SEGUNDOS),
    }


def _erro_por_status(status):
    if status in (401, 403):
        return "Credencial inválida: o serviço recusou a OPENAI_API_KEY. Verifique a chave no .env."
    if status == 404:
        return "Serviço não encontrado: confira OPENAI_API_URL e OPENAI_MODEL no .env."
    if status == 429:
        return "Limite de uso excedido ou sem créditos no serviço. Tente novamente mais tarde."
    if status >= 500:
        return f"O serviço do LLM está indisponível no momento (HTTP {status}). Tente novamente mais tarde."
    return f"O serviço recusou a solicitação (HTTP {status}). Confira OPENAI_MODEL e a configuração."


def chamar_modelo(requisicao):
    try:
        resposta = requests.post(**requisicao)
    except requests.Timeout:
        raise ErroTarot(
            f"O serviço não respondeu em {requisicao['timeout']} segundos. Tente novamente."
        ) from None
    except requests.ConnectionError:
        raise ErroTarot(
            "Falha de comunicação: não foi possível conectar ao serviço. "
            "Verifique sua internet e OPENAI_API_URL."
        ) from None
    except requests.RequestException:
        raise ErroTarot("Falha inesperada ao se comunicar com o serviço.") from None

    if not resposta.ok:
        raise ErroTarot(_erro_por_status(resposta.status_code))

    try:
        return resposta.json()
    except ValueError:
        raise ErroTarot("O serviço retornou uma resposta que não é um JSON válido.") from None


def extrair_resposta(dados):
    try:
        conteudo = dados["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise ErroTarot("A resposta do serviço veio em formato inesperado.") from None
    if not isinstance(conteudo, str) or not conteudo.strip():
        raise ErroTarot("O serviço retornou uma resposta vazia. Tente novamente.")
    return conteudo.strip()
