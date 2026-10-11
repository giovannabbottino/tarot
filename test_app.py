import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

import requests

import app

CARTAS = [
    ("Passado", "O Louco", ""),
    ("Presente", "A Lua", " (invertida)"),
    ("Futuro", "Ás de Copas", ""),
]

CRED = {"chave": "chave-teste", "url": "https://exemplo.test/chat", "modelo": "modelo-teste"}


class TestCapturaEntrada(unittest.TestCase):
    @patch("builtins.input", return_value="  Devo viajar?  ")
    def test_remove_espacos(self, _):
        self.assertEqual(app.capturar_pergunta(), "Devo viajar?")

    @patch("builtins.input", return_value="   ")
    def test_vazia_encerra(self, _):
        with self.assertRaises(SystemExit) as ctx:
            app.capturar_pergunta()
        self.assertIn("vazia", str(ctx.exception))


@patch("app.load_dotenv")
class TestCarregamentoCredencial(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {"OPENAI_API_KEY": "k", "OPENAI_API_URL": "u", "OPENAI_MODEL": "m"},
        clear=True,
    )
    def test_le_variaveis(self, mock_dotenv):
        self.assertEqual(app.carregar_credenciais(), {"chave": "k", "url": "u", "modelo": "m"})
        mock_dotenv.assert_called_once()

    @patch.dict("os.environ", {"OPENAI_API_KEY": "k", "OPENAI_API_URL": "u"}, clear=True)
    def test_modelo_padrao(self, _):
        self.assertEqual(app.carregar_credenciais()["modelo"], "gpt-4o-mini")

    @patch.dict("os.environ", {"OPENAI_API_URL": "u"}, clear=True)
    def test_sem_chave_encerra(self, _):
        with self.assertRaises(SystemExit) as ctx:
            app.carregar_credenciais()
        self.assertIn("OPENAI_API_KEY", str(ctx.exception))

    @patch.dict("os.environ", {"OPENAI_API_KEY": "k"}, clear=True)
    def test_sem_url_encerra(self, _):
        with self.assertRaises(SystemExit) as ctx:
            app.carregar_credenciais()
        self.assertIn("OPENAI_API_URL", str(ctx.exception))


class TestPreparacaoSolicitacao(unittest.TestCase):
    def test_prompt_inclui_pergunta_e_cartas(self):
        prompt = app.montar_prompt("Devo viajar?", CARTAS)

        self.assertIn("Devo viajar?", prompt)
        self.assertIn("- Passado: O Louco", prompt)
        self.assertIn("- Presente: A Lua (invertida)", prompt)
        self.assertIn("- Futuro: Ás de Copas", prompt)

    def test_requisicao(self):
        req = app.montar_requisicao("meu prompt", CRED)

        self.assertEqual(req["url"], CRED["url"])
        self.assertEqual(req["headers"]["Authorization"], "Bearer chave-teste")
        self.assertEqual(req["json"]["model"], "modelo-teste")
        self.assertEqual(req["json"]["messages"][0]["role"], "system")
        self.assertEqual(
            req["json"]["messages"][1], {"role": "user", "content": "meu prompt"}
        )
        self.assertEqual(req["timeout"], 60)


class TestChamadaModelo(unittest.TestCase):
    @patch("app.requests.post")
    def test_sucesso_retorna_json(self, mock_post):
        mock_post.return_value.json.return_value = {"ok": 1}
        req = app.montar_requisicao("p", CRED)

        self.assertEqual(app.chamar_modelo(req), {"ok": 1})
        mock_post.assert_called_once_with(**req)

    @patch("app.requests.post")
    def test_erro_http_propaga(self, mock_post):
        mock_post.return_value.raise_for_status.side_effect = requests.HTTPError("401")

        with self.assertRaises(requests.HTTPError):
            app.chamar_modelo(app.montar_requisicao("p", CRED))

    @patch("app.requests.post", side_effect=requests.ConnectionError("sem rede"))
    def test_falha_de_rede_propaga(self, _):
        with self.assertRaises(requests.ConnectionError):
            app.chamar_modelo(app.montar_requisicao("p", CRED))


class TestInterpretacaoResposta(unittest.TestCase):
    def test_extrai_texto(self):
        dados = {"choices": [{"message": {"content": "Boa sorte!"}}]}
        self.assertEqual(app.extrair_resposta(dados), "Boa sorte!")

    def test_formatos_invalidos(self):
        for dados in ({}, {"choices": []}, {"choices": [{}]}, None):
            with self.subTest(dados=dados):
                with self.assertRaises(ValueError):
                    app.extrair_resposta(dados)


class TestApresentacaoSaida(unittest.TestCase):
    def test_imprime_cartas_e_interpretacao(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            app.apresentar_saida(CARTAS, "Texto do oráculo")
        saida = buffer.getvalue()

        self.assertIn("  Passado: O Louco", saida)
        self.assertIn("  Presente: A Lua (invertida)", saida)
        self.assertIn("Texto do oráculo", saida)
        self.assertLess(saida.index("Futuro"), saida.index("Texto do oráculo"))


class TestFluxoIntegrado(unittest.TestCase):
    @patch("app.apresentar_saida")
    @patch("app.requests.post")
    @patch("app.sortear_cartas", return_value=CARTAS)
    @patch("app.capturar_pergunta", return_value="Terei sorte?")
    @patch("app.carregar_credenciais", return_value=CRED)
    def test_main_encadeia_etapas(self, _c, _p, _s, mock_post, mock_saida):
        resp = MagicMock()
        resp.json.return_value = {"choices": [{"message": {"content": "Sim!"}}]}
        mock_post.return_value = resp

        app.main()

        enviado = mock_post.call_args.kwargs["json"]["messages"][1]["content"]
        self.assertIn("Terei sorte?", enviado)
        mock_saida.assert_called_once_with(CARTAS, "Sim!")


if __name__ == "__main__":
    unittest.main()
