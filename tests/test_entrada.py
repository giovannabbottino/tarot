import unittest
from unittest.mock import patch

import entrada
from logics.erros import ErroTarot


class TestLerPergunta(unittest.TestCase):
    @patch("builtins.input", return_value="  texto cru  ")
    def test_retorna_o_texto_sem_validar(self, mock_input):
        self.assertEqual(entrada.ler_pergunta(), "  texto cru  ")
        self.assertIn("pergunta", mock_input.call_args.args[0])

    @patch("builtins.input", side_effect=EOFError)
    def test_fim_da_entrada_gera_erro_claro(self, _):
        with self.assertRaises(ErroTarot):
            entrada.ler_pergunta()


if __name__ == "__main__":
    unittest.main()
