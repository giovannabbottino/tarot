# tarot

Programa de terminal que sorteia 3 cartas de tarot e pede ao ChatGPT uma interpretação para a sua pergunta.

## 1. Problema escolhido

Uma pessoa que busca reflexão pessoal por meio do tarot precisa transformar **uma pergunta e 3 cartas sorteadas** em **uma interpretação clara**, porque atualmente tem dificuldade de entender o significado combinado das cartas sem consultar um tarólogo ou vários materiais.

## 2. Público

Pessoas curiosas sobre tarot que querem uma leitura rápida pelo terminal.

## 3. Por que usar um LLM

Sortear as cartas é simples e feito em código. Interpretá-las exige linguagem natural: relacionar cada carta, sua posição (Passado, Presente, Futuro) e a inversão com a pergunta. Respostas pré-escritas não dariam conta, e o LLM sim.

## 4. Como funciona

1. Você digita uma pergunta (se vier vazia, o programa avisa e pede de novo).
2. O programa sorteia 3 cartas de um baralho de 78, podendo sair invertidas.
3. Envia a pergunta e as cartas ao ChatGPT por requisição REST.
4. Mostra as cartas e a interpretação.

Estrutura do código:

```
src/
  app.py          ponto de entrada
  controller.py   orquestra o fluxo e trata os erros
  entrada.py      lê do terminal
  saida.py        imprime no terminal
  logics/         regras: config, pergunta, tarot, llm, erros
tests/            testes automatizados
```

## 5. Limites

- Só terminal, uma consulta por execução.
- Sempre 3 cartas, com posições fixas.
- Serve para entretenimento e reflexão, não é aconselhamento profissional.
- Precisa de internet e de chave de API válida.

## 6. Instalação

Python 3.8 ou superior.

```
pip install -r requirements.txt
```

## 7. Configuração do LLM e testes

Copie o exemplo e preencha o `.env` (ele não é versionado):

```
copy .env.example .env
```

| Variável | Descrição |
|---|---|
| `OPENAI_API_KEY` | Chave da API da OpenAI (obrigatória) |
| `OPENAI_API_URL` | Endereço da API, ex.: `https://api.openai.com/v1/chat/completions` (obrigatória) |
| `OPENAI_MODEL` | Modelo (opcional, padrão `gpt-4o-mini`) |

**Testes simulados** (automatizados): usam mocks, sem acessar a API nem precisar de chave.

**Testes reais** (rodando `python src/app.py` com o serviço de verdade):

**Testes manuais obrigatórios** (rode todos; o P0 exige os dois primeiros após o sucesso). Com o `.env` configurado, use `python src/app.py`:

| # | Cenário | Como executar | Resultado esperado |
|---|---|---|---|
| 1 | Chamada com sucesso | `.env` correto; digite uma pergunta | Cartas e interpretação exibidas |
| 2 | Credencial ausente (P0) | Remova a linha `OPENAI_API_KEY` do `.env` (ou use uma cópia do projeto sem `.env`) | "Credencial ausente", sem traceback |
| 3 | Credencial inválida (P0) | `OPENAI_API_KEY=sk-chave-falsa` no `.env` | API responde 401; "Credencial inválida", sem expor a chave |
| 4 | URL inválida | `OPENAI_API_URL=abc` no `.env` | "Configuração inválida", sem traceback |
| 5 | Sem rede | `OPENAI_API_URL=https://host-inexistente.invalid/v1` | "Falha de comunicação", sem traceback |
| 6 | Pergunta vazia | Aperte Enter sem digitar | Aviso "A pergunta não pode ser vazia" e o programa pergunta de novo |

Restaure o `.env` correto depois de cada teste. Registre os resultados obtidos no `RELATORIO_EXECUCAO.md`.

Timeout, erro 5xx, limite de uso (429) e resposta vazia ou em formato inesperado **só foram testados de forma simulada**.

## 8. Execução

A partir da raiz do projeto:

```
python src/app.py
```

Só o sorteio, sem LLM:

```
python src/logics/tarot.py
```

## 9. Exemplos

Sucesso (as cartas mudam a cada execução; interpretação abreviada):

```
Qual a sua pergunta para o tarot? Terei sorte?

Cartas sorteadas:
  Passado: Rei de Paus
  Presente: 5 de Paus
  Futuro: 6 de Copas

Interpretação:

Passado - Rei de Paus: ...
Presente - 5 de Paus: ...
Futuro - 6 de Copas: ...
Síntese: ...
```

Erros (sem traceback, e a chave nunca aparece):

```
Erro: Credencial ausente: defina OPENAI_API_KEY no arquivo .env (veja .env.example).
Erro: Credencial inválida: o serviço recusou a OPENAI_API_KEY. Verifique a chave no .env.
Aviso (o programa pede a pergunta de novo): A pergunta não pode ser vazia. Digite o que deseja saber.
```

## 10. Testes

```
python -m unittest discover -s tests -t . -v
```

Cobrem o sorteio, a validação da pergunta, a configuração, a chamada ao LLM (status HTTP, timeout, falha de rede, resposta vazia ou inesperada), a entrada, a saída e o fluxo completo.

## 11. Limitações conhecidas

- A chave só é validada no formato; quem confirma é o serviço.
- Não há nova tentativa automática (retry) em caso de falha.
- Os testes automatizados não acessam o serviço real.
- A resposta do LLM varia entre execuções.

## 12. Vídeo

Link: _a ser adicionado_
