import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import MagicMock, patch

import controller
from logics.erros import ErroTarot

CARTAS = [
    ("Passado", "O Louco", ""),
    ("Presente", "A Lua", " (invertida)"),
    ("Futuro", "Ás de Copas", ""),
]

CONFIG = {"chave": "sk-segredo", "url": "https://exemplo.test/chat", "modelo": "m"}


def rodar_main():
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        codigo = controller.main()
    return codigo, out.getvalue(), err.getvalue()


def resposta(status, texto=None):
    resp = MagicMock(status_code=status, ok=status < 400)
    if texto is not None:
        resp.json.return_value = {"choices": [{"message": {"content": texto}}]}
    return resp


@patch("controller.carregar_configuracao", return_value=CONFIG)
class TestController(unittest.TestCase):
    @patch("controller.sortear_cartas", return_value=CARTAS)
    @patch("controller.entrada.ler_pergunta", return_value="  Terei sorte?  ")
    @patch("logics.llm.requests.post")
    def test_sucesso_encadeia_entrada_logica_e_saida(self, mock_post, _i, _s, _c):
        mock_post.return_value = resposta(200, "Sim!")

        codigo, out, err = rodar_main()

        self.assertEqual(codigo, 0)
        self.assertIn("Sim!", out)
        self.assertIn("  Passado: O Louco", out)
        self.assertEqual(err, "")
        enviado = mock_post.call_args.kwargs["json"]["messages"][1]["content"]
        self.assertIn("Terei sorte?", enviado)

    @patch("controller.sortear_cartas", return_value=CARTAS)
    @patch("controller.entrada.ler_pergunta", side_effect=["   ", "", "Terei sorte?"])
    @patch("logics.llm.requests.post")
    def test_entrada_vazia_pede_novamente_sem_chamar_o_servico(self, mock_post, mock_in, _s, _c):
        mock_post.return_value = resposta(200, "Sim!")

        codigo, out, err = rodar_main()

        self.assertEqual(codigo, 0)
        self.assertEqual(mock_in.call_count, 3)
        self.assertEqual(err.count("A pergunta não pode ser vazia"), 2)
        mock_post.assert_called_once()

    @patch("controller.entrada.ler_pergunta", side_effect=ErroTarot("Entrada encerrada sem uma pergunta."))
    @patch("logics.llm.requests.post")
    def test_fim_da_entrada_encerra_sem_chamar_o_servico(self, mock_post, _i, _c):
        codigo, out, err = rodar_main()

        self.assertEqual(codigo, 1)
        self.assertIn("Entrada encerrada", err)
        mock_post.assert_not_called()

    def test_erro_de_configuracao_vira_mensagem(self, mock_cfg):
        mock_cfg.side_effect = ErroTarot("Credencial ausente: defina OPENAI_API_KEY.")

        codigo, out, err = rodar_main()

        self.assertEqual(codigo, 1)
        self.assertEqual(err.strip(), "Erro: Credencial ausente: defina OPENAI_API_KEY.")
        self.assertNotIn("Traceback", err)

    @patch("controller.entrada.ler_pergunta", return_value="Pergunta")
    @patch("logics.llm.requests.post")
    def test_credencial_invalida_sem_expor_segredo(self, mock_post, _i, _c):
        mock_post.return_value = resposta(401)

        codigo, out, err = rodar_main()

        self.assertEqual(codigo, 1)
        self.assertIn("Credencial inválida", err)
        self.assertNotIn("sk-segredo", out + err)
        self.assertNotIn("Traceback", err)

    @patch("controller.entrada.ler_pergunta", return_value="Pergunta")
    @patch("logics.llm.requests.post")
    def test_resposta_vazia_vira_mensagem(self, mock_post, _i, _c):
        mock_post.return_value = resposta(200, "   ")

        codigo, out, err = rodar_main()

        self.assertEqual(codigo, 1)
        self.assertIn("resposta vazia", err)
        self.assertEqual(out, "")

    @patch("controller.entrada.ler_pergunta", side_effect=KeyboardInterrupt)
    def test_interrupcao_do_usuario(self, _i, _c):
        codigo, _, err = rodar_main()

        self.assertEqual(codigo, 130)
        self.assertIn("Interrompido", err)


if __name__ == "__main__":
    unittest.main()
