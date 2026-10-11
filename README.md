# tarot

Script simples em Python que sorteia 3 cartas do tarot (Passado, Presente e Futuro) a partir de um baralho completo de 78 cartas. Cada carta pode sair invertida.

## Uso

```
python tarot.py
```

Exemplo de saída:

```
Passado: A Lua
Presente: 7 de Espadas (invertida)
Futuro: O Sol
```

## Testes

```
python -m unittest test_tarot -v
```

Os testes mockam `random.sample` e `random.choice` para tornar o sorteio determinístico.
