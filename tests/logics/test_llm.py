import unittest
from unittest.mock import MagicMock, patch

import requests

from logics import llm
from logics.erros import ErroTarot

CARTAS = [
    ("Passado", "O Louco", ""),
    ("Presente", "A Lua", " (invertida)"),
    ("Futuro", "Ás de Copas", ""),
]

CONFIG = {"chave": "sk-segredo", "url": "https://exemplo.test/chat", "modelo": "modelo-teste"}


def resposta_fake(status=200, json_data=None, json_erro=None):
    resp = MagicMock()
    resp.status_code = status
    resp.ok = status < 400
    if json_erro:
        resp.json.side_effect = json_erro
    else:
        resp.json.return_value = json_data
    return resp


def chamar():
    return llm.chamar_modelo(llm.montar_requisicao("p", CONFIG))


class TestPreparacaoSolicitacao(unittest.TestCase):
    def test_prompt_inclui_pergunta_e_cartas(self):
        prompt = llm.montar_prompt("Devo viajar?", CARTAS)

        self.assertIn("Devo viajar?", prompt)
        self.assertIn("- Passado: O Louco", prompt)
        self.assertIn("- Presente: A Lua (invertida)", prompt)
        self.assertIn("- Futuro: Ás de Copas", prompt)

    def test_requisicao(self):
        req = llm.montar_requisicao("meu prompt", CONFIG)

        self.assertEqual(req["url"], CONFIG["url"])
        self.assertEqual(req["headers"]["Authorization"], "Bearer sk-segredo")
        self.assertEqual(req["json"]["model"], "modelo-teste")
        self.assertEqual(req["json"]["messages"][0]["role"], "system")
        self.assertEqual(req["json"]["messages"][1], {"role": "user", "content": "meu prompt"})
        self.assertEqual(req["timeout"], llm.TIMEOUT_SEGUNDOS)
        for campo in ("max_tokens", "temperature", "top_p"):
            self.assertNotIn(campo, req["json"])

    def test_requisicao_com_configuracoes_do_env(self):
        cfg = {
            **CONFIG,
            "parametros": {"max_tokens": 100, "temperature": 0.2},
            "timeout": 5,
            "sistema": "Seja breve.",
        }
        req = llm.montar_requisicao("p", cfg)

        self.assertEqual(req["json"]["max_tokens"], 100)
        self.assertEqual(req["json"]["temperature"], 0.2)
        self.assertEqual(req["json"]["messages"][0]["content"], "Seja breve.")
        self.assertEqual(req["timeout"], 5)

class TestChamadaModelo(unittest.TestCase):
    @patch("logics.llm.requests.post")
    def test_sucesso_retorna_json(self, mock_post):
        mock_post.return_value = resposta_fake(json_data={"ok": 1})
        req = llm.montar_requisicao("p", CONFIG)

        self.assertEqual(llm.chamar_modelo(req), {"ok": 1})
        mock_post.assert_called_once_with(**req)

    def test_erros_por_status(self):
        casos = {
            401: "Credencial inválida",
            403: "Credencial inválida",
            404: "Serviço não encontrado",
            429: "Limite de uso",
            500: "indisponível",
            503: "indisponível",
            400: "recusou a solicitação",
        }
        for status, trecho in casos.items():
            with self.subTest(status=status):
                with patch("logics.llm.requests.post", return_value=resposta_fake(status)):
                    with self.assertRaisesRegex(ErroTarot, trecho):
                        chamar()

    def test_timeout(self):
        with patch("logics.llm.requests.post", side_effect=requests.Timeout("lento")):
            with self.assertRaisesRegex(ErroTarot, "não respondeu"):
                chamar()

    def test_timeout_de_conexao_e_tratado_como_timeout(self):
        with patch("logics.llm.requests.post", side_effect=requests.ConnectTimeout("lento")):
            with self.assertRaisesRegex(ErroTarot, "não respondeu"):
                chamar()

    def test_falha_de_comunicacao(self):
        with patch("logics.llm.requests.post", side_effect=requests.ConnectionError("sem rede")):
            with self.assertRaisesRegex(ErroTarot, "Falha de comunicação"):
                chamar()

    def test_falha_generica_de_requests(self):
        with patch("logics.llm.requests.post", side_effect=requests.RequestException("x")):
            with self.assertRaisesRegex(ErroTarot, "Falha inesperada"):
                chamar()

    def test_corpo_que_nao_e_json(self):
        resp = resposta_fake(json_erro=ValueError("nao json"))
        with patch("logics.llm.requests.post", return_value=resp):
            with self.assertRaisesRegex(ErroTarot, "JSON válido"):
                chamar()

    def test_mensagens_nao_expoem_a_chave(self):
        for status in (401, 500):
            with patch("logics.llm.requests.post", return_value=resposta_fake(status)):
                with self.assertRaises(ErroTarot) as ctx:
                    chamar()
            self.assertNotIn("sk-segredo", str(ctx.exception))
        with patch("logics.llm.requests.post", side_effect=requests.ConnectionError("sk-segredo")):
            with self.assertRaises(ErroTarot) as ctx:
                chamar()
        self.assertNotIn("sk-segredo", str(ctx.exception))


class TestTratamentoResposta(unittest.TestCase):
    def test_extrai_texto(self):
        dados = {"choices": [{"message": {"content": "  Boa sorte!  "}}]}
        self.assertEqual(llm.extrair_resposta(dados), "Boa sorte!")

    def test_formato_inesperado(self):
        for dados in ({}, {"choices": []}, {"choices": [{}]}, None, [], "texto"):
            with self.subTest(dados=dados):
                with self.assertRaisesRegex(ErroTarot, "formato inesperado"):
                    llm.extrair_resposta(dados)

    def test_resposta_vazia(self):
        for conteudo in ("", "   \n", None, 123):
            with self.subTest(conteudo=conteudo):
                dados = {"choices": [{"message": {"content": conteudo}}]}
                with self.assertRaisesRegex(ErroTarot, "vazia"):
                    llm.extrair_resposta(dados)


if __name__ == "__main__":
    unittest.main()
