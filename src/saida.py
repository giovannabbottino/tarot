import sys


def apresentar_resultado(cartas, interpretacao):
    print("\nCartas sorteadas:")
    for posicao, carta, orientacao in cartas:
        print(f"  {posicao}: {carta}{orientacao}")
    print("\nInterpretação:\n")
    print(interpretacao)


def apresentar_erro(mensagem):
    print(f"Erro: {mensagem}", file=sys.stderr)


def apresentar_aviso(mensagem):
    print(f"\n{mensagem}", file=sys.stderr)
