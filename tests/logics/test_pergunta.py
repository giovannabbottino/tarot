import unittest

from logics.erros import ErroTarot
from logics.pergunta import validar_pergunta


class TestValidarPergunta(unittest.TestCase):
    def test_remove_espacos(self):
        self.assertEqual(validar_pergunta("  Devo viajar?  "), "Devo viajar?")

    def test_entradas_vazias_sao_rejeitadas(self):
        for texto in ("", "   ", "\t\n", None):
            with self.subTest(texto=texto):
                with self.assertRaisesRegex(ErroTarot, "não pode ser vazia"):
                    validar_pergunta(texto)


if __name__ == "__main__":
    unittest.main()
