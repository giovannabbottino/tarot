from logics.erros import ErroTarot


def ler_pergunta():
    try:
        return input("Qual a sua pergunta para o tarot? ")
    except EOFError:
        raise ErroTarot("Entrada encerrada sem uma pergunta.") from None
