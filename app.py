import os

import requests
from dotenv import load_dotenv

from tarot import sortear_cartas

SISTEMA = "Você é um tarólogo experiente. Responda em português, de forma clara e acolhedora."


def capturar_pergunta():
    pergunta = input("Qual a sua pergunta para o tarot? ").strip()
    if not pergunta:
        raise SystemExit("A pergunta não pode ser vazia.")
    return pergunta


def carregar_credenciais():
    load_dotenv()
    chave = os.getenv("OPENAI_API_KEY")
    url = os.getenv("OPENAI_API_URL")
    if not chave or not url:
        raise SystemExit(
            "Defina OPENAI_API_KEY e OPENAI_API_URL no arquivo .env (veja .env.example)."
        )
    return {"chave": chave, "url": url, "modelo": os.getenv("OPENAI_MODEL", "gpt-4o-mini")}


def montar_prompt(pergunta, cartas):
    linhas = [f"- {posicao}: {carta}{orientacao}" for posicao, carta, orientacao in cartas]
    return (
        f"Pergunta do consulente: {pergunta}\n\n"
        "Cartas sorteadas:\n" + "\n".join(linhas) + "\n\n"
        "Interprete cada carta em sua posição e finalize com uma síntese "
        "que responda à pergunta."
    )


def montar_requisicao(prompt, credenciais):
    return {
        "url": credenciais["url"],
        "headers": {"Authorization": f"Bearer {credenciais['chave']}"},
        "json": {
            "model": credenciais["modelo"],
            "messages": [
                {"role": "system", "content": SISTEMA},
                {"role": "user", "content": prompt},
            ],
        },
        "timeout": 60,
    }


def chamar_modelo(requisicao):
    resposta = requests.post(**requisicao)
    resposta.raise_for_status()
    return resposta.json()


def extrair_resposta(dados):
    try:
        return dados["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as erro:
        raise ValueError("Resposta do modelo em formato inesperado.") from erro


def apresentar_saida(cartas, interpretacao):
    print("\nCartas sorteadas:")
    for posicao, carta, orientacao in cartas:
        print(f"  {posicao}: {carta}{orientacao}")
    print("\nInterpretação:\n")
    print(interpretacao)


def main():
    credenciais = carregar_credenciais()
    pergunta = capturar_pergunta()
    cartas = sortear_cartas()
    prompt = montar_prompt(pergunta, cartas)
    dados = chamar_modelo(montar_requisicao(prompt, credenciais))
    apresentar_saida(cartas, extrair_resposta(dados))


if __name__ == "__main__":
    main()
