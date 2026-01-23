# Base de Conhecimento

## Dados Utilizados

O agente utiliza um conjunto de dados **mock/sintético** localizado na pasta `data` (ou dentro do pacote `dados_sinteticos_pack` / `dados_sinteticos`), organizado por cenários (`guardiao`, `autopiloto`, `misto`). Cada cenário contém os mesmos arquivos-base, usados para personalizar e contextualizar as respostas.

| Arquivo                     | Formato | Utilização no Agente                                                                                                                                                                               |
| --------------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `perfil_investidor.json`    | JSON    | Identificar o cliente (nome/idade), perfil (conservador/moderado/agressivo), objetivo principal, patrimônio e reserva atual. Usado em todos os modos para personalização.                          |
| `transacoes.csv`            | CSV     | Base para detectar padrões e riscos: transações recentes (últimas ~40/60 linhas) ajudam o Guardião a identificar comportamento suspeito e o Autopiloto a propor ajustes de orçamento.              |
| `historico_atendimento.csv` | CSV     | Contextualiza atendimentos anteriores (últimos ~15) para manter coerência e entender histórico de problemas/dúvidas do cliente. Mais relevante para o Guardião.                                    |
| `produtos_financeiros.json` | JSON    | Lista de produtos financeiros disponíveis. No projeto é enviado como **resumo** (nome/categoria/risco) para evitar prompt gigante. Usado principalmente para contexto geral e exemplos educativos. |

---

## Adaptações nos Dados

* **Redução de contexto** para performance e consistência:

  * `transacoes.csv`: usado somente o recorte mais recente (ex.: `tail(40)` ou `tail(60)`), evitando enviar o histórico inteiro.
  * `historico_atendimento.csv`: usado somente o recorte recente (ex.: `tail(15)`).
  * `produtos_financeiros.json`: convertido em um **resumo** (ex.: até 30 itens com `nome`, `categoria`, `risco`) em vez do JSON completo.
* **Filtro por agente** (na montagem do prompt):

  * **Finanças** recebe um contexto mais leve (prioriza perfil/objetivo e evita tabelas longas).
  * **Guardião** recebe mais sinal de risco (transações + atendimentos; produtos podem ser removidos).
  * **Autopiloto** recebe foco em transações (padrões de gasto) e menos histórico de atendimento.

Essas adaptações diminuem tokens enviados ao modelo, melhorando latência e reduzindo custo computacional.

---

## Estratégia de Integração

### Como os dados são carregados?

Os dados são carregados localmente a partir do diretório do cenário selecionado (ex.: `cenario_guardiao/data`). O carregamento é feito via:

* `json.load()` para arquivos `.json`
* `pandas.read_csv()` para arquivos `.csv`

Para performance, o contexto é gerado por uma função cacheada (ex.: `@st.cache_data`), evitando reprocessar os mesmos arquivos a cada rerun do Streamlit.

### Como os dados são usados no prompt?

Os dados **não entram no system prompt**. O system prompt define apenas a persona e as regras (Guardião / Finanças / Autopiloto).
Os dados entram no **bloco de contexto** (`CONTEXTO DO CLIENTE`) montado dinamicamente:

* O LangGraph decide qual agente será acionado (`router`).
* O `build_prompt` monta o contexto a partir dos arquivos e aplica:

  * recorte (tail) de transações/atendimentos
  * resumo de produtos
  * filtro por agente (o que entra e o que é removido)

Isso mantém o comportamento consistente e evita respostas “soltas” sem ligação com os dados.

---

## Exemplo de Contexto Montado

Exemplo (formato aproximado) do bloco enviado ao modelo:

```
CONTEXTO DO CLIENTE:
CLIENTE: João Silva, 32 anos, perfil Moderado
OBJETIVO: Montar reserva e organizar gastos
PATRIMÔNIO: R$25000 | RESERVA: R$1500

TRANSAÇÕES (últimas 40):
data        descricao              valor   tipo
2025-12-28  Supermercado           450.00  debito
2025-12-29  Streaming               55.00  debito
2025-12-30  Pix para favorecido X  900.00  pix
...

ATENDIMENTOS (últimos 15):
data        assunto                resultado
2025-12-20  Dúvida sobre Pix       orientado
2025-12-22  Suspeita de golpe      bloqueio_sugerido
...

PRODUTOS (resumo):
[
  {"nome":"CDB Liquidez Diária","categoria":"Renda Fixa","risco":"Baixo"},
  {"nome":"Tesouro Selic","categoria":"Renda Fixa","risco":"Baixo"}
]
```
