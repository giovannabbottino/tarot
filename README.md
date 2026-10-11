# tarot

## 1. Problema escolhido

Uma pessoa que busca orientação ou reflexão sobre uma questão pessoal por meio do tarot precisa transformar **uma pergunta em texto e 3 cartas sorteadas** em **uma interpretação clara e contextualizada**, porque atualmente enfrenta **a dificuldade de entender o significado combinado das cartas (posição, inversão e relação com a pergunta) sem consultar um tarólogo ou vários materiais de referência**.

## 2. Usuário ou público

Pessoas curiosas sobre tarot, ou que buscam uma reflexão rápida sobre uma questão pessoal, usando o terminal.

## 3. Justificativa para utilizar um LLM

O sorteio das cartas é simples e feito em código. Já a interpretação exige linguagem natural contextualizada: relacionar o significado de cada carta, sua posição (Passado, Presente, Futuro) e se está invertida com a pergunta do usuário. Isso seria inviável com respostas pré-escritas e é o que o LLM (ChatGPT) faz bem.

## 4. Funcionamento da solução

1. O usuário digita uma pergunta no terminal.
2. `tarot.py` sorteia 3 cartas distintas de um baralho de 78 cartas (22 arcanos maiores e 56 menores). Cada carta pode sair invertida.
3. `app.py` monta um prompt com a pergunta e as cartas e o envia por requisição REST (`requests`) à API de chat completions. O código é dividido em uma função por etapa (captura da pergunta, carregamento da credencial, preparação da solicitação, chamada ao modelo, interpretação da resposta e apresentação da saída), cada uma testada separadamente.
4. A interpretação retornada é exibida no terminal.

## 5. Limites do projeto

- Interface apenas por terminal, uma consulta por execução.
- Sempre sorteia 3 cartas com posições fixas (Passado, Presente, Futuro).
- Entretenimento e reflexão: a interpretação não é aconselhamento profissional.
- Depende de acesso à internet e de uma chave de API válida.

## 6. Instalação

Requer Python 3.8 ou superior.

```
pip install -r requirements.txt
```

## 7. Configuração do acesso ao LLM

Copie o arquivo de exemplo e preencha os valores:

```
copy .env.example .env
```

| Variável | Descrição |
|---|---|
| `OPENAI_API_KEY` | Chave da API da OpenAI |
| `OPENAI_API_URL` | Endpoint (ex.: `https://api.openai.com/v1/chat/completions`) |
| `OPENAI_MODEL` | Modelo usado (opcional; padrão `gpt-4o-mini`) |


## 8. Execução

```
python app.py
```

Para apenas sortear as cartas, sem LLM:

```
python tarot.py
```

## 9. Exemplos de entrada e saída

Entrada:

```
Qual a sua pergunta para o tarot? Devo mudar de emprego?
```

Saída (as cartas variam a cada execução; a interpretação abaixo é ilustrativa e não foi obtida de uma chamada real):

```
Cartas sorteadas:
  Passado: O Carro
  Presente: 7 de Espadas (invertida)
  Futuro: A Estrela

Interpretação:

Passado: O Carro indica ...
Presente: ...
Futuro: ...
Síntese: ...
```

Saída de `python tarot.py`:

```
Passado: A Lua
Presente: 7 de Espadas (invertida)
Futuro: O Sol
```

## 10. Execução dos testes

```
python -m unittest -v
```

Cobre `tarot.py` (`test_tarot.py`) e cada etapa de `app.py` (`test_app.py`): captura da entrada, credencial, preparação da solicitação, chamada ao modelo, interpretação da resposta e apresentação da saída, além do fluxo integrado. Todos usam mocks: nenhum teste acessa a API.

## 11. Limitações conhecidas

- Erros de API (ex.: chave inválida, HTTP 401) aparecem como traceback, sem mensagem amigável.
- Os testes de `app.py` mockam `requests.post`, então não validam a integração real com a API.
- A resposta do LLM pode variar entre execuções e não é validada.

## 12. Vídeo

