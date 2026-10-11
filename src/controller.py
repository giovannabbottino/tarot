import entrada
import saida
from logics.config import carregar_configuracao
from logics.erros import ErroTarot
from logics.llm import chamar_modelo, extrair_resposta, montar_prompt, montar_requisicao
from logics.pergunta import validar_pergunta
from logics.tarot import sortear_cartas


def obter_pergunta():
    while True:
        texto = entrada.ler_pergunta()
        try:
            return validar_pergunta(texto)
        except ErroTarot as erro:
            saida.apresentar_aviso(str(erro))


def executar():
    configuracao = carregar_configuracao()
    pergunta = obter_pergunta()
    cartas = sortear_cartas()
    requisicao = montar_requisicao(montar_prompt(pergunta, cartas), configuracao)
    interpretacao = extrair_resposta(chamar_modelo(requisicao))
    saida.apresentar_resultado(cartas, interpretacao)


def main():
    try:
        executar()
    except ErroTarot as erro:
        saida.apresentar_erro(str(erro))
        return 1
    except KeyboardInterrupt:
        saida.apresentar_aviso("Interrompido pelo usuário.")
        return 130
    return 0
