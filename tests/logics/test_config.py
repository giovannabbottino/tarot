import unittest
from unittest.mock import patch

from logics import config
from logics.erros import ErroTarot

VALIDO = {
    "OPENAI_API_KEY": "sk-teste123",
    "OPENAI_API_URL": "https://exemplo.test/v1/chat/completions",
    "OPENAI_MODEL": "modelo-teste",
}


def carregar(env):
    with patch("logics.config.load_dotenv"), patch.dict("os.environ", env, clear=True):
        return config.carregar_configuracao()


def sem(chave):
    return {k: v for k, v in VALIDO.items() if k != chave}


class TestConfiguracao(unittest.TestCase):
    def test_configuracao_valida(self):
        self.assertEqual(
            carregar(VALIDO),
            {"chave": "sk-teste123", "url": VALIDO["OPENAI_API_URL"], "modelo": "modelo-teste"},
        )

    def test_modelo_padrao_quando_ausente_ou_vazio(self):
        self.assertEqual(carregar(sem("OPENAI_MODEL"))["modelo"], config.MODELO_PADRAO)
        self.assertEqual(
            carregar({**VALIDO, "OPENAI_MODEL": "  "})["modelo"], config.MODELO_PADRAO
        )

    def test_credencial_ausente(self):
        for env in (sem("OPENAI_API_KEY"), {**VALIDO, "OPENAI_API_KEY": "   "}):
            with self.subTest(env=env):
                with self.assertRaisesRegex(ErroTarot, "Credencial ausente"):
                    carregar(env)

    def test_credencial_com_formato_invalido(self):
        for chave in (config.CHAVE_EXEMPLO, "sk com espaço", "sk-çhave"):
            with self.subTest(chave=chave):
                with self.assertRaisesRegex(ErroTarot, "Credencial inválida"):
                    carregar({**VALIDO, "OPENAI_API_KEY": chave})

    def test_url_ausente(self):
        with self.assertRaisesRegex(ErroTarot, "OPENAI_API_URL"):
            carregar(sem("OPENAI_API_URL"))

    def test_url_invalida(self):
        for url in ("api.openai.com", "ftp://x.test/a", "https://"):
            with self.subTest(url=url):
                with self.assertRaisesRegex(ErroTarot, "Configuração inválida"):
                    carregar({**VALIDO, "OPENAI_API_URL": url})

    def test_mensagem_de_erro_nao_expoe_a_chave(self):
        chave = "sk-segredo with espaco"
        with self.assertRaises(ErroTarot) as ctx:
            carregar({**VALIDO, "OPENAI_API_KEY": chave})
        self.assertNotIn("segredo", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
