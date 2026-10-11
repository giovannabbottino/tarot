# RELATORIO_EXECUCAO

## Evolução por nível

**Básico:** aplicação em Python que lê uma pergunta no terminal, sorteia 3 cartas do tarot (Passado, Presente, Futuro) de um baralho de 78 cartas, envia pergunta e cartas ao ChatGPT via REST e exibe a interpretação. A chave e a URL da API ficam em `.env` (há um `.env.example`). O fluxo é dividido em etapas (entrada, credencial, solicitação, chamada, resposta, saída), cada uma testada separadamente.

## Decisões principais

| Decisão | Alternativa considerada | Justificativa |
|---|---|---|
| Separar o sorteio (`tarot.py`) da chamada ao LLM (`app.py`) | Tudo em um único arquivo | Permite testar o sorteio isoladamente e usá-lo sem LLM. |
| Dividir `app.py` em uma função por etapa (entrada, credencial, solicitação, chamada, resposta, saída) | Uma única função `main` com tudo | Cada etapa pode ser testada isoladamente, e uma falha aponta para a etapa responsável. |
| Credenciais em `.env` carregado por `python-dotenv` (`.env` no `.gitignore`) | Chave no código ou pedida no terminal | Evita vazar segredos no repositório. |

## Testes e resultados

| Teste | Entrada ou situação | Resultado esperado | Resultado obtido |
|---|---|---|---|
| Pergunta vazia | Enter sem texto em `app.py` | Encerrar com mensagem de erro | Passou ("A pergunta não pode ser vazia.") |
| Captura da entrada | Pergunta com espaços nas pontas | Espaços removidos | Passou (automatizado) |
| Credencial | Variáveis presentes; modelo ausente | Lê as três; modelo padrão `gpt-4o-mini` | Passou (automatizado) |
| Credencial (falha) | Sem `OPENAI_API_KEY` ou sem `OPENAI_API_URL` | Encerra com mensagem citando a variável | Passou (automatizado) |
| Preparação da solicitação | Pergunta e cartas | Prompt com pergunta e cartas; cabeçalho `Bearer`, modelo, mensagens e `timeout` | Passou (automatizado) |
| Chamada ao modelo (falha) | HTTP 401 e falha de rede simulados | Exceção propagada | Passou (automatizado) |
| Chave inválida (falha) | `OPENAI_API_KEY=chave-invalida` | Erro de autenticação | Passou: HTTP 401, mas exibido como traceback (teste manual) |
| Chave ausente | Sem `OPENAI_API_KEY` | Mensagem pedindo para configurar o `.env` | Passou apenas no teste automatizado; o manual não foi feito, pois o `.env` local já continha uma chave |


## Falhas e limitações


## Uso de IA no desenvolvimento

## Reflexão final

- **Principal aprendizado:** separar a lógica determinística (sorteio) e cada etapa do fluxo com a chamada externa (LLM) facilita testar, localizar falhas e trocar o provedor.
- **Competência mais desenvolvida:** integração com API REST mantendo segredos fora do código e testes por etapa com mocks.
- **A aprimorar:** tratamento amigável de erros de rede e API, e validação da integração real com a API.
