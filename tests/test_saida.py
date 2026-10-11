import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

import saida

CARTAS = [
    ("Passado", "O Louco", ""),
    ("Presente", "A Lua", " (invertida)"),
    ("Futuro", "Ás de Copas", ""),
]


class TestSaida(unittest.TestCase):
    def test_resultado_imprime_cartas_antes_da_interpretacao(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            saida.apresentar_resultado(CARTAS, "Texto do oráculo")
        texto = out.getvalue()

        self.assertIn("  Presente: A Lua (invertida)", texto)
        self.assertLess(texto.index("Futuro"), texto.index("Texto do oráculo"))
        self.assertEqual(err.getvalue(), "")

    def test_erro_vai_para_stderr(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            saida.apresentar_erro("algo deu errado")

        self.assertEqual(err.getvalue(), "Erro: algo deu errado\n")
        self.assertEqual(out.getvalue(), "")

    def test_aviso_vai_para_stderr(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            saida.apresentar_aviso("Interrompido")

        self.assertIn("Interrompido", err.getvalue())
        self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
