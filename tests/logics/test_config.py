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
        cfg = carregar(VALIDO)
        self.assertEqual(cfg["chave"], "sk-teste123")
        self.assertEqual(cfg["url"], VALIDO["OPENAI_API_URL"])
        self.assertEqual(cfg["modelo"], "modelo-teste")
        self.assertEqual(cfg["parametros"], {})
        self.assertEqual(cfg["timeout"], config.TIMEOUT_PADRAO)
        self.assertIsNone(cfg["sistema"])

    def test_parametros_opcionais_do_env(self):
        cfg = carregar({
            **VALIDO,
            "OPENAI_MAX_TOKENS": "300",
            "OPENAI_TEMPERATURE": "0.5",
            "OPENAI_TOP_P": "0.9",
            "OPENAI_TIMEOUT": "10",
            "OPENAI_SYSTEM_PROMPT": "  Seja breve.  ",
        })
        self.assertEqual(cfg["parametros"], {"max_tokens": 300, "temperature": 0.5, "top_p": 0.9})
        self.assertEqual(cfg["timeout"], 10)
        self.assertEqual(cfg["sistema"], "Seja breve.")

    def test_parametros_invalidos(self):
        casos = {
            "OPENAI_MAX_TOKENS": ["abc", "0", "1.5"],
            "OPENAI_TEMPERATURE": ["quente", "3", "-1"],
            "OPENAI_TOP_P": ["2"],
            "OPENAI_TIMEOUT": ["0", "x"],
        }
        for nome, valores in casos.items():
            for valor in valores:
                with self.subTest(nome=nome, valor=valor):
                    with self.assertRaisesRegex(ErroTarot, nome):
                        carregar({**VALIDO, nome: valor})

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
