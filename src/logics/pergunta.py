from logics.erros import ErroTarot


def validar_pergunta(texto):
    pergunta = (texto or "").strip()
    if not pergunta:
        raise ErroTarot("A pergunta não pode ser vazia. Digite o que deseja saber.")
    return pergunta
