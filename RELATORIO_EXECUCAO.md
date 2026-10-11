# RELATORIO_EXECUCAO

## Evolução por nível

**Básico:** o programa lê uma pergunta no terminal, sorteia 3 cartas de tarot, envia tudo ao ChatGPT por REST e mostra a interpretação. Chave e URL ficam no `.env`.

**Intermediário:** o código foi separado em entrada, saída, lógica e controller. Entrada vazia gera um aviso e o programa pergunta de novo, e as falhas previstas (credencial ou configuração ausente ou inválida, indisponibilidade, falha de rede, timeout, resposta vazia ou inesperada) viram mensagens claras, sem traceback e sem expor a chave.

## Decisões principais

| Decisão | Alternativa | Justificativa |
|---|---|---|
| Separar entrada, saída, lógica e controller | Tudo misturado em um arquivo | Cada parte pode ser testada sozinha. |
| Erro próprio (`ErroTarot`) tratado só no controller | Deixar as exceções do `requests` subirem | Um único ponto transforma erro em mensagem clara. |
| Mensagens sem repassar o texto da exceção | Mostrar o erro original | Evita vazar URL, detalhes técnicos ou a chave. |

## Testes e resultados

Automatizados: 35 testes simulados, todos passaram.

| Teste | Situação | Esperado | Obtido |
|---|---|---|---|
| Sorteio | Cartas e inversão mockadas | Posições corretas | Passou |
| Pergunta vazia | `""`, espaços, `None` | Rejeitar sem chamar o serviço | Passou |
| Credencial ausente ou inválida | Sem chave, chave de exemplo, com espaços | Mensagem clara | Passou |
| URL ausente ou inválida | Sem URL, `api.openai.com` | Mensagem clara | Passou |
| Status HTTP | 401, 403, 404, 429, 5xx, 400 | Mensagem de cada caso | Passou |
| Timeout e rede | Timeout, falha de conexão | Mensagem clara | Passou |
| Resposta ruim | Não JSON, vazia, formato inesperado | Mensagem clara | Passou |
| Fluxo completo | Serviço simulado | Cartas e texto impressos | Passou |

Manuais, com o serviço real:

| Teste | Situação | Esperado | Obtido |
|---|---|---|---|
| Sucesso | Chave do `.env` | Interpretação exibida | Passou |
| Credencial ausente | Sem chave e sem `.env` (cópia temporária) | Mensagem clara | Passou |
| Credencial inválida | Chave falsa, URL real | HTTP 401 vira mensagem clara | Passou |
| URL inválida e sem rede | `api.openai.com`; host inexistente | Mensagem clara | Passou |


## Falhas e limitações

## Uso de IA no desenvolvimento

## Reflexão final

- **Principal aprendizado:** tratar falhas previstas em um só ponto, com mensagens que dizem o que fazer, deixa o programa mais útil e mais fácil de testar. Uma demonstração também precisa isolar o ambiente.
- **Competência mais desenvolvida:** tratamento de erros e testes com mocks, sem vazar segredos.
- **A aprimorar:** testar com o serviço real os casos de timeout e indisponibilidade e avaliar retry.
