# Base de Conhecimento

## Dados Utilizados

Foram utilizados os ficheiros na pasta `data`, que representam o ecossistema financeiro e comportamental do cliente:

| Ficheiro | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores e dar "memória" ao agente. |
| `perfil_investidor.json` | JSON | Definir o alvo: contém a renda, património atual e as metas com prazos rígidos. |
| `produtos_financeiros.json` | JSON | Base de mercado usada para comparar rentabilidades, riscos e sugerir produtos adequados ao perfil. |
| `transacoes.csv` | CSV | Analisar o padrão de gastos do cliente e monitorizar oportunidades de aporte de forma proativa. |

---

## Adaptações nos Dados

Os dados originais foram mantidos, mas a lógica de processamento do Atlas cria **variáveis derivadas** em tempo de execução:
- **Taxa de Poupança Real:** Calculada dinamicamente subtraindo as saídas das entradas do `transacoes.csv`.
- **Status de Viabilidade:** O agente calcula a diferença entre a "Reserva Atual" e o "Valor Necessário" no `perfil_investidor.json` e cruza com a taxa de poupança para determinar se a meta está "Em dia" ou "Em risco".

---

## Estratégia de Integração

### Como os dados são carregados?
Os ficheiros CSV e JSON são lidos no *backend* no momento em que a sessão do utilizador é iniciada. Para evitar exceder o limite de *tokens* do LLM e otimizar o tempo de resposta, os dados tabulares (`transacoes.csv` e `historico_atendimento.csv`) são processados e sumarizados via código antes de serem enviados para o modelo. A base de produtos financeiros é carregada e indexada para permitir pesquisas rápidas.

### Como os dados são usados no prompt?
Os dados do `perfil_investidor` e o resumo das `transacoes` são injetados diretamente no **System Prompt** do Atlas no início da conversa, fornecendo a base de cálculo e o contexto primário. 
Já os `produtos_financeiros` e o `historico_atendimento` funcionam via **RAG**: quando o utilizador pergunta sobre onde investir, o sistema faz uma pesquisa rápida, seleciona apenas os produtos adequados ao perfil (e ao prazo da meta) e insere-os dinamicamente no prompt antes de gerar a resposta final.

---

## Exemplo de Contexto Montado

Quando o agente inicia a conversa, recebe da aplicação um bloco de contexto estruturado semelhante a este:

```text
[CONTEXTO DO SISTEMA]
Você é o Atlas. Analise os dados abaixo antes de responder:

DADOS DO CLIENTE:
- Nome: João Silva (32 anos)
- Renda Mensal: R$ 5.000,00
- Perfil: Moderado
- Património Total: R$ 15.000,00

METAS ATIVAS:
1. Reserva de Emergência: Faltam R$ 5.000,00 (Prazo: Jun/2026)
2. Entrada Apartamento: Faltam R$ 35.000,00 (Prazo: Dez/2027)

ÚLTIMAS TRANSAÇÕES (Resumo):
- Total Entradas: R$ 5.000,00
- Total Saídas: R$ 2.188,90
- Saldo Livre Estimado: R$ 2.811,10 (Alerta de Oportunidade de Aporte)

PRODUTOS PERMITIDOS PARA SUGESTÃO ATUAL:
- Tesouro Selic (Risco: Baixo)
- Fundo Multimercado (Risco: Médio, CDI + 2%)
[/CONTEXTO DO SISTEMA]