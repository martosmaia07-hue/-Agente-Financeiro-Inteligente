# Base de Conhecimento

## Dados Utilizados

A base de conhecimento do agente foi construída com dados mockados, simulando o contexto financeiro de pequenos empreendedores, autônomos, MEIs e microempresas. O objetivo foi permitir testes realistas do agente em cenários de gestão de caixa, vencimentos, risco financeiro e apoio à tomada de decisão.

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `clientes_pj.json` | JSON | Armazena dados cadastrais e perfil financeiro dos clientes PJ |
| `contas_pj.json` | JSON | Representa informações das contas bancárias PJ, saldos e limites |
| `transacoes_pj.csv` | CSV | Registra entradas, saídas, transferências, tarifas e movimentações financeiras |
| `contas_pagar.csv` | CSV | Lista despesas e compromissos futuros do negócio |
| `contas_receber.csv` | CSV | Lista receitas previstas e valores a receber |
| `produtos_bancarios_pj.json` | JSON | Contém produtos financeiros disponíveis para sugestão contextual |
| `regras_alertas.json` | JSON | Define regras de negócio para geração de alertas e recomendações |
| `historico_interacoes.csv` | CSV | Guarda interações anteriores do cliente com o agente |
| `indicadores_caixa.json` | JSON | Armazena parâmetros e métricas de referência para saúde financeira |
| `metas_financeiras.json` | JSON | Permite simular metas de reserva, crescimento e organização do caixa |

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

Sim. Os dados mockados foram estruturados especificamente para refletir o contexto de pequenos negócios e contas PJ, com foco em fluxo de caixa, previsibilidade financeira e apoio à decisão. Diferente de bases mais genéricas de clientes bancários, os dados foram adaptados para incluir movimentações típicas de microempresas, como pagamento de fornecedores, recebimento por vendas, transferências entre contas, retiradas dos sócios, despesas operacionais, impostos e obrigações futuras.

Também foram incluídos arquivos auxiliares com regras de alerta e produtos bancários PJ para permitir que o agente não apenas interprete o histórico financeiro, mas também gere mensagens proativas e contextualizadas, como alertas de risco de caixa, excesso de retiradas pessoais, concentração de despesas ou necessidade de capital de giro.

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

Os arquivos JSON e CSV são carregados no início da execução da aplicação por meio de funções auxiliares de leitura. Os arquivos CSV são utilizados para análise tabular das movimentações e compromissos financeiros, enquanto os JSON armazenam estruturas mais estáticas, como perfil do cliente, produtos disponíveis, regras de alerta e parâmetros de saúde financeira.

Durante a execução, o agente consulta essas bases para montar o contexto do cliente e responder com base em dados concretos do cenário simulado.

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

Os dados não são inseridos integralmente no prompt principal. Em vez disso, são consultados dinamicamente conforme a necessidade da interação. O sistema recupera apenas as informações relevantes para cada pergunta ou alerta, como saldo atual, transações recentes, contas a vencer, valores a receber e regras aplicáveis ao caso.

Depois disso, um resumo estruturado é montado e enviado ao modelo de linguagem como contexto da resposta. Essa abordagem reduz ruído, melhora a precisão e ajuda a limitar respostas ao escopo dos dados disponíveis.

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

```text
Dados do Cliente:
- Nome: Mariana Souza Studio
- Tipo: MEI
- Segmento: Design Gráfico
- Banco: Bradesco PJ
- Saldo atual: R$ 4.850,00
- Limite disponível: R$ 2.000,00
- Reserva mínima recomendada: R$ 3.500,00

Indicadores Financeiros:
- Média de entradas mensais: R$ 12.400,00
- Média de saídas mensais: R$ 10.950,00
- Percentual de retiradas pessoais no mês: 22%
- Situação atual do caixa: Atenção

Contas a pagar (próximos 7 dias):
- 12/04: Fornecedor de impressão - R$ 1.200,00
- 14/04: Internet e telefone - R$ 189,90
- 15/04: DAS MEI - R$ 75,60

Contas a receber (próximos 7 dias):
- 13/04: Cliente Alpha - R$ 2.400,00
- 16/04: Cliente Beta - R$ 1.350,00

Últimas transações:
- 08/04: Recebimento PIX Cliente Alpha - R$ 1.200,00
- 08/04: Compra de insumos - R$ 320,00
- 07/04: Transferência para conta pessoal - R$ 900,00
- 06/04: Assinatura de ferramenta de design - R$ 89,90

Regras de Negócio Ativadas:
- Alerta de risco de caixa abaixo da reserva mínima
- Alerta de excesso de retiradas pessoais
- Sugestão de organização de contas por prioridade
