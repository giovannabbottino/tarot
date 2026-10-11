import random

ARCANOS_MAIORES = [
    "O Louco", "O Mago", "A Sacerdotisa", "A Imperatriz", "O Imperador",
    "O Hierofante", "Os Enamorados", "O Carro", "A Força", "O Eremita",
    "A Roda da Fortuna", "A Justiça", "O Enforcado", "A Morte",
    "A Temperança", "O Diabo", "A Torre", "A Estrela", "A Lua", "O Sol",
    "O Julgamento", "O Mundo",
]

NAIPES = ["Paus", "Copas", "Espadas", "Ouros"]
VALORES = [
    "Ás", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "Valete", "Cavaleiro", "Rainha", "Rei",
]

BARALHO = ARCANOS_MAIORES + [f"{v} de {n}" for n in NAIPES for v in VALORES]


def sortear_cartas(quantidade=3):
    posicoes = ["Passado", "Presente", "Futuro"]
    cartas = random.sample(BARALHO, quantidade)
    return [
        (posicao, carta, random.choice(["", " (invertida)"]))
        for posicao, carta in zip(posicoes, cartas)
    ]


if __name__ == "__main__":
    for posicao, carta, orientacao in sortear_cartas():
        print(f"{posicao}: {carta}{orientacao}")
