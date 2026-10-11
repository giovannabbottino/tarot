import unittest
from unittest.mock import patch

from tarot import sortear_cartas


class TestSortearCartas(unittest.TestCase):
    @patch("tarot.random.choice", return_value="")
    @patch("tarot.random.sample", return_value=["O Louco", "A Lua", "Ás de Copas"])
    def test_retorna_cartas_com_posicoes(self, mock_sample, mock_choice):
        resultado = sortear_cartas()

        self.assertEqual(
            resultado,
            [
                ("Passado", "O Louco", ""),
                ("Presente", "A Lua", ""),
                ("Futuro", "Ás de Copas", ""),
            ],
        )
        mock_sample.assert_called_once()
        self.assertEqual(mock_sample.call_args.args[1], 3)

    @patch("tarot.random.choice", return_value=" (invertida)")
    @patch("tarot.random.sample", return_value=["O Sol", "A Torre", "O Mundo"])
    def test_cartas_invertidas(self, mock_sample, mock_choice):
        resultado = sortear_cartas()

        self.assertTrue(all(o == " (invertida)" for _, _, o in resultado))
        self.assertEqual(mock_choice.call_count, 3)


if __name__ == "__main__":
    unittest.main()
