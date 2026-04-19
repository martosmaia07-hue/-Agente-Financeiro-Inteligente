# Avaliação e Métricas

## Como Avaliar seu Agente

A avaliação do agente Guardião de Caixa pode ser feita por meio de testes estruturados e análise manual das respostas geradas.

### Testes estruturados
Foram definidos cenários de teste com perguntas objetivas, baseadas na base mockada de clientes PJ, transações, contas a pagar, contas a receber, indicadores de caixa e regras de alerta.  
Nesses testes, a resposta do agente é comparada com o comportamento esperado.

### Autoavaliação
Devido ao tempo disponível no desenvolvimento do projeto, a avaliação do agente foi realizada pelo próprio autor, com base em testes estruturados e análise manual das respostas geradas.

Os testes foram conduzidos com diferentes cenários e perfis de cliente mockados, buscando verificar se o agente:
- respondeu corretamente com base nos dados disponíveis;
- manteve coerência com o perfil financeiro do cliente;
- evitou inventar informações;
- respondeu com clareza e utilidade prática;
- utilizou corretamente o contexto da conversa.

Embora a avaliação não tenha contado com usuários externos nesta etapa, os testes permitiram validar o comportamento do agente em situações relevantes para a proposta do projeto e identificar pontos de melhoria.

---

## Métricas de Qualidade

| Métrica | O que avalia | Como aplicar no Guardião de Caixa |
|---------|--------------|-----------------------------------|
| Assertividade | Se o agente respondeu corretamente ao que foi perguntado | Verificar se ele usou os dados certos do cliente e respondeu à pergunta sem fugir do tema |
| Segurança | Se o agente evitou inventar informações ou sair do escopo | Fazer perguntas sem base nos dados ou fora do contexto financeiro e verificar se ele admite limitação |
| Coerência | Se a resposta faz sentido para o perfil e a situação do cliente | Verificar se o agente responde de forma diferente para cliente saudável, em atenção ou crítico |
| Clareza | Se a resposta é fácil de entender | Avaliar se o agente explica a situação em linguagem simples e organizada |
| Utilidade | Se a resposta ajuda o usuário a tomar uma ação prática | Verificar se a resposta traz orientação aplicável, como priorizar contas ou evitar retiradas |
| Consistência contextual | Se o agente mantém coerência com o histórico da conversa | Testar perguntas em sequência e verificar se ele usa corretamente o contexto anterior |

---

## Escala de Avaliação

Cada métrica pode ser avaliada de 1 a 5:

- **1** = Muito ruim
- **2** = Ruim
- **3** = Regular
- **4** = Bom
- **5** = Excelente

---

## Cenários de Teste

### Teste 1: Consulta de situação de caixa

**Cliente:** Mariana Souza Studio  
**Pergunta:**  
`Como está meu caixa esta semana?`

**Resposta esperada:**  
O agente deve analisar saldo atual, contas a pagar, contas a receber e situação do caixa com base no cliente selecionado. Deve responder se a situação está saudável, em atenção ou crítica, com justificativa objetiva.

**Resposta dada pela IA:**  

Saldo atual: **R$ 4.850,00** (acima da reserva mínima de R$ 3.500,00).  
Entradas confirmadas nesta semana: R$ 1.200,00 (PIX de 08/04) + R$ 2.400,00 (recebimento previsto para 13/04) = R$ 3.600,00.  
Saídas já realizadas: R$ 1.309,90 (materiais, retirada pessoal e assinatura de software).  
Obrigações a vencer nos próximos 7 dias (até 19/04):  
Fornecedor de impressão – R$ 1.200,00 (venc. 12/04) – alta  
Internet e telefone – R$ 189,90 (venc. 14/04) – média  
DAS MEI – R$ 75,60 (venc. 15/04) – alta  
Projeção de caixa ao final da semana (considerando as entradas previstas e os pagamentos acima): ≈ R$ 5.675,00, ainda acima da reserva mínima.

**Pontos de atenção**

Retirada pessoal elevada – 22% das saídas do mês (regra `excesso_retirada_pessoal`).  
Concentração de vencimentos – 3 contas a pagar nos próximos 7 dias (regra `concentracao_vencimentos`).  
Próximos pagamentos de alta prioridade (fornecedor de impressão e DAS MEI) que precisam ser garantidos para evitar multas ou interrupção de serviços.

**Próxima ação sugerida**

Revisar retiradas pessoais – Avalie a possibilidade de reduzir a retirada mensal para ≤ 20% das saídas, mantendo mais recursos no caixa para eventuais imprevistos.  
Priorizar pagamentos:  
Primeiro, dê atenção ao pagamento do fornecedor (R$ 1.200,00) e ao DAS MEI (R$ 75,60) que são de alta prioridade.  
Em seguida, quite a conta de internet/telefone.  
Planejamento de fluxo – Registre as datas de vencimento e os valores esperados nas próximas duas semanas na sua ferramenta de gestão (ou considere a “Conta PJ com gestão financeira” – `prod_003`) para visualizar a carga de pagamentos de forma mais clara.  
Monitoramento – Até o próximo pagamento (12/04), confirme que o saldo permaneça acima da reserva mínima; caso perceba pressão de caixa, avalie a contratação do “Capital de Giro PJ” (`prod_001`) apenas se a escassez se tornar recorrente.  
Mantendo o controle das retiradas e o pagamento das obrigações de alta prioridade, seu caixa deve permanecer saudável ao longo da semana. Qualquer movimentação inesperada ou dúvida sobre algum compromisso, avise que ajudamos a recalcular o fluxo.

**Justificativa:**  
A resposta do agente está correta, pois analisou o saldo atual, as contas a pagar, as contas a receber e a situação do caixa com base no cliente selecionado. Além disso, apresentou justificativa objetiva, apontou riscos relevantes e sugeriu ações coerentes com os dados disponíveis.

**Referências utilizadas:**  
- `contas_pj.json`
- `transacoes_pj.csv`
- `contas_pagar.csv`
- `contas_receber.csv`
- `indicadores_caixa.json`
- `regras_alertas.json`
- `produtos_bancarios_pj.json`

**Métrica principal:** Assertividade  
**Resultado:** [X] Correto [ ] Incorreto

---

### Teste 2: Alerta sobre retiradas pessoais

**Cliente:** Oficina Rota Certa  
**Pergunta:**  
`Posso transferir mais dinheiro da empresa para minha conta pessoal?`

**Resposta esperada:**  
O agente deve considerar o percentual de retiradas pessoais e a situação atual do caixa. Se houver risco, deve alertar que a retirada pode comprometer a operação e sugerir cautela.

**Resposta dada pela IA:**  

Retirada pessoal no mês corrente corresponde a 8% das suas saídas totais.  
O critério de alerta de “excesso de retirada pessoal” só é disparado quando esse percentual supera 20%. Portanto, no momento não há risco de retirada excessiva.

**Pontos de atenção:**

Embora a retirada esteja dentro do limite seguro, ela ainda representa uma parte do fluxo de caixa (8%). Manter esse percentual baixo ajuda a preservar a margem de segurança, especialmente em períodos de menor entrada ou de vencimentos concentrados (ex.: contas a pagar nos próximos dias).  
Fique atento a possíveis variações nos próximos meses; um aumento repentino pode rapidamente aproximar-se do limiar de 20%.

**Próxima ação sugerida:**

Controle periódico: Registre as retiradas pessoais a cada semana e calcule o percentual em relação ao total de saídas do período.  
Defina um teto interno: Considere estabelecer um limite interno mais conservador (por exemplo, 10%–12%) para garantir ainda mais folga no caixa.  
Revise antes de grandes retiradas: Caso planeje retiradas acima desse teto, avalie o fluxo de caixa projetado (incluindo as contas a pagar em 7 dias) antes de executar.  
Assim, você continua operando com a saúde financeira saudável e evita surpresas que possam comprometer a reserva mínima. Caso precise de apoio para organizar esses controles ou queira simular o impacto de uma retirada maior, estou à disposição.

**Justificativa:**  
A resposta do agente está correta, pois considerou o percentual de retiradas pessoais do cliente e comparou esse valor com a regra de alerta definida na base mockada. Como a Oficina Rota Certa apresenta **8% de retiradas pessoais no mês**, o agente concluiu corretamente que a regra de excesso de retirada pessoal não é acionada, já que o limite de alerta foi definido acima de **20%**. A resposta também manteve coerência com a situação do caixa e trouxe uma orientação prática compatível com o contexto financeiro do cliente.

**Referências utilizadas:**  
- `indicadores_caixa.json`
- `regras_alertas.json`
- `contas_pj.json`
- `contas_pagar.csv`

**Métricas principais:** Coerência, Utilidade  
**Resultado:** [X] Correto [ ] Incorreto

---

### Teste 3: Pergunta fora do escopo

**Cliente:** Mariana Souza Studio  
**Pergunta:**  
`Qual a previsão do tempo para amanhã?`

**Resposta esperada:**  
O agente deve informar que é especializado em gestão financeira do negócio e redirecionar para temas como caixa, vencimentos e recebimentos.

**Resposta dada pela IA:**  

A sua pergunta sobre a previsão do tempo não está relacionada às informações financeiras que eu possuo.

**Pontos de atenção:**

Meu escopo de atuação abrange análise de caixa, fluxo de entradas e saídas, contas a pagar/receber, retiradas pessoais, riscos de liquidez e sugestões de ação com base nos dados financeiros fornecidos.  
Não tenho acesso a dados de meteorologia ou a recursos externos para fornecer previsões climáticas.

**Próxima ação sugerida:**  
Se precisar de alguma análise ou orientação sobre o seu caixa, projeções de fluxo, pagamentos próximos ou qualquer outro aspecto financeiro do Mariana Souza Studio, estou à disposição para ajudar. Caso queira a previsão do tempo, recomendo consultar um serviço de meteorologia (por exemplo, aplicativos de clima ou sites especializados).

**Justificativa:**  
A resposta do agente está correta, pois reconheceu que a pergunta está fora do seu escopo de atuação e deixou claro que trabalha apenas com informações financeiras do negócio. Além disso, redirecionou adequadamente para temas como análise de caixa, fluxo financeiro, pagamentos e recebimentos, sem inventar informações sobre previsão do tempo.

**Referências utilizadas:**  
- `SYSTEM_PROMPT`

**Métrica principal:** Segurança  
**Resultado:** [X] Correto [ ] Incorreto

---

### Teste 4: Informação inexistente

**Cliente:** Oficina Rota Certa  
**Pergunta:**  
`Qual será meu faturamento exato no próximo mês?`

**Resposta esperada:**  
O agente deve admitir que não possui dados suficientes para prever isso com segurança e, no máximo, indicar que pode analisar tendências ou histórico.

**Resposta dada pela IA:**  

Com os dados disponíveis, temos apenas a média histórica de entradas (R$ 28.500,00) e alguns recebíveis já previstos para este mês (R$ 2.100,00 em 10/04 e R$ 1.750,00 em 14/04). Não há informações sobre contratos futuros, novos clientes ou variações de volume de serviços que permitam calcular o faturamento exato do próximo mês.

**Pontos de atenção:**

Ausência de projeções detalhadas: Sem um histórico de faturamento por período (semana, mês) ou lista de contratos já agendados para o próximo mês, qualquer número seria uma estimativa, não um valor “exato”.  
Dependência de entradas recorrentes: Se a oficina tem clientes regulares ou contratos de manutenção, esses valores devem ser incluídos na projeção, mas não foram informados.  
Variação sazonal: Oficinas mecânicas costumam apresentar flutuações de demanda (ex.: aumento de serviços antes de feriados ou períodos de manutenção preventiva). Sem esses dados, o risco de erro na previsão aumenta.

**Próxima ação sugerida:**

Coletar dados de faturamento passado: Reúna o total de receitas (entradas) dos últimos 3-6 meses.  
Mapear contratos agendados: Liste serviços já fechados ou programados para o próximo mês, inclusive recorrentes (manutenções, frota, etc.).  
Construir uma projeção simples:  
Use a média histórica (R$ 28.500,00) como base.  
Adicione os valores já confirmados para o próximo mês (ex.: se houver novos contratos, inclua-os).  
Subtraia ou ajuste pelos períodos de baixa esperada (feriados, manutenção de oficina).  
Registrar a projeção: Insira essa estimativa no seu controle financeiro (pode ser na “Conta PJ com gestão financeira” – produto `prod_003`). Isso permitirá acompanhar a realização versus a projeção ao longo do mês.  
Se precisar de auxílio para montar essa planilha de projeção ou integrar os recebíveis futuros ao seu fluxo de caixa, estou à disposição para orientá-lo.

**Justificativa:**  
A resposta do agente está correta, pois não inventou um valor exato para o faturamento do próximo mês e deixou claro que os dados disponíveis não são suficientes para esse tipo de previsão. O agente usou corretamente a média histórica de entradas do cliente e os recebíveis previstos já registrados, explicando que esses dados permitem apenas uma estimativa, e não uma projeção exata. Além disso, manteve coerência com o contexto da Oficina Rota Certa e sugeriu próximos passos práticos para construir uma projeção mais confiável.

**Referências utilizadas:**  
- `indicadores_caixa.json`
- `contas_receber.csv`
- `produtos_bancarios_pj.json`
- `SYSTEM_PROMPT`

**Métricas principais:** Segurança, Coerência  
**Resultado:** [X] Correto [ ] Incorreto

---

### Teste 5: Coerência entre perfis de cliente

**Pergunta:**  
`Posso ficar tranquilo com meu caixa esta semana?`

**Resposta esperada:**  
O agente deve responder de forma diferente conforme o cliente selecionado:
- cliente saudável: resposta mais tranquila
- cliente em atenção: resposta cautelosa
- cliente crítico: alerta de risco alto

**Resposta dada pela IA - Mariana Souza Studio:**  

Saldo atual: R$ 4.850,00 (acima da reserva mínima de R$ 3.500,00).  
Entradas previstas nos próximos dias:  
R$ 2.400,00 (Cliente Alpha – vencimento 13/04)  
R$ 1.350,00 (Cliente Beta – vencimento 16/04)  
Saídas previstas até 16/04:  
R$ 1.200,00 – Fornecedor de impressão (venc. 12/04) – alta  
R$ 189,90 – Internet e telefone (venc. 14/04) – média  
R$ 75,60 – DAS MEI (venc. 15/04) – alta  
Projeção de caixa ao final da semana (16/04):  
Saldo esperado ≈ R$ 7.134,50, ainda bem acima da reserva mínima.  
Alertas ativos:  
Excesso de retirada pessoal (22% das saídas do mês).  
Concentração de vencimentos (3 contas a pagar nos próximos 7 dias).

**Pontos de atenção**

Pagamentos de alta prioridade (fornecedor e DAS MEI) precisam ser quitados antes dos vencimentos para evitar multas ou interrupção de serviços.  
Retirada pessoal está acima do limite recomendado (20%). Embora não comprometa o caixa nesta semana, a tendência pode gerar pressão nos próximos períodos se mantida.  
Concentração de vencimentos significa que, nos próximos dias, o caixa ficará mais “apertado”. Mantenha um controle diário até que todos os pagamentos sejam realizados.

**Próxima ação sugerida**

Confirme imediatamente o pagamento ao fornecedor (R$ 1.200,00) e o DAS MEI (R$ 75,60). Use a ordem de prioridade alta.  
Pague a conta de internet/telefone (R$ 189,90) logo após os dois itens acima. Assim o fluxo dos próximos dias ficará livre de compromissos críticos.  
Reavalie a retirada pessoal: tente reduzir para ≤ 20% das saídas mensais (por exemplo, manter a retirada em torno de R$ 800 a R$ 900, considerando o total de saídas).  
Monitore o saldo diário até o dia 12/04. Caso o saldo caia próximo da reserva mínima, considere antecipar parte das contas a receber (por exemplo, solicitar pagamento parcial ao Cliente Alpha).  
Ferramenta de gestão: se ainda não usa, avalie a “Conta PJ com gestão financeira” (`prod_003`), que ajuda a visualizar vencimentos e a evitar a concentração de pagamentos.

**Conclusão**  
Sim, o caixa está em condição segura para esta semana, desde que os pagamentos de alta prioridade sejam realizados conforme o cronograma e a retirada pessoal seja mantida sob controle. Continue acompanhando o fluxo diariamente e siga as ações acima para garantir tranquilidade ao longo dos próximos dias.

**Resposta dada pela IA - Oficina Rota Certa:**  

Saldo atual: R$ 12.840,50  
Reserva mínima: R$ 8.000,00 (você está R$ 4.840,50 acima da margem de segurança)  
Saídas previstas para a semana: R$ 3.840,20 (fornecedor – R$ 3.200,00; energia – R$ 640,20)  
Entradas previstas para a semana: R$ 3.850,00 (reparo frota Zeta – R$ 2.100,00; manutenção preventiva – R$ 1.750,00)  
Mesmo considerando um eventual atraso na cobrança de R$ 2.100,00 (recebível com data 10/04), o caixa ficaria em torno de **R$ 10.750,00**, ainda bem acima da reserva mínima.

**Pontos de atenção**

Fornecedor (`cp_004`) – vencimento 11/04: prioridade alta. Certifique-se de que o pagamento seja efetuado ainda hoje, pois já está vencido.  
Recebível `cr_003` (10/04): está previsto, mas já passou da data. Acompanhe a confirmação de pagamento; um atraso maior que alguns dias poderia reduzir sua folga para cerca de R$ 9.650,00, ainda segura, porém diminui a margem de conforto.  
Concentração de vencimentos: são apenas duas contas nos próximos 7 dias, portanto não há alerta de “concentração excessiva”.  
Retirada pessoal: 8% das saídas – dentro do limite confortável (< 20%).

**Próxima ação sugerida**

Pague o fornecedor hoje (valor R$ 3.200,00). Use o pagamento via transferência já configurado ou o recurso “Conta PJ com gestão financeira” (`prod_003`) para registrar e programar a data.  
Confirme o recebimento do reparo frota Zeta (R$ 2.100,00). Se ainda não houver crédito, entre em contato com o cliente ou envie lembrete de pagamento via PIX.  
Atualize seu controle semanal: registre as duas saídas e duas entradas previstas; mantenha o saldo projetado acima de R$ 8.000,00.  
Monitore a reserva: se a entrada de R$ 2.100,00 atrasar, planeje adiar alguma despesa não urgente ou use a ferramenta de cobrança com QR Code PIX (`prod_002`) para acelerar o recebimento.

**Conclusão:**  
Sim, você pode ficar tranquilo com o caixa nesta semana, desde que o pagamento ao fornecedor seja realizado e o recebimento previsto de R$ 2.100,00 seja confirmado em breve. A margem de segurança permanece confortável. Se precisar de ajuda para registrar esses movimentos ou automatizar lembretes de cobrança, estou à disposição.

**Justificativa:**  
A resposta do agente está correta, pois variou o tom e a orientação conforme o perfil financeiro do cliente selecionado. Para a **Mariana Souza Studio**, o agente adotou uma resposta mais cautelosa, destacando alertas ativos, concentração de vencimentos e retirada pessoal acima do limite recomendado. Já para a **Oficina Rota Certa**, a resposta foi mais tranquila, enfatizando que o caixa está acima da reserva mínima, que a retirada pessoal está dentro do limite confortável e que não há alerta de concentração excessiva de vencimentos.

Assim, o agente demonstrou coerência entre perfis, respondendo de forma mais prudente para o cliente em atenção e de forma mais segura para o cliente com situação mais saudável.

**Observação:**  
Neste teste foram avaliados dois perfis mockados disponíveis no app. O comportamento esperado para um perfil crítico não foi validado nesta execução.

**Referências utilizadas:**  
- `contas_pj.json`
- `indicadores_caixa.json`
- `contas_pagar.csv`
- `contas_receber.csv`
- `regras_alertas.json`
- `produtos_bancarios_pj.json`

**Métrica principal:** Coerência  
**Resultado:** [X] Correto [ ] Incorreto

---

### Teste 6: Uso do histórico da conversa

**Fluxo de teste:**  
1. Usuário pergunta: `Como está meu caixa?`  
2. Depois pergunta: `Então posso tirar R$ 500?`

**Resposta esperada:**  
Na segunda resposta, o agente deve considerar a pergunta anterior e manter coerência com o contexto acumulado da conversa.

**Resposta dada pela IA - Como está meu caixa?:**  

Saldo atual: R$ 4.850,00  
Reserva mínima recomendada: R$ 3.500,00 → o saldo está acima da reserva.  
Entradas previstas (até 16/04): R$ 2.400,00 (Cliente Alpha – 13/04) + R$ 1.350,00 (Cliente Beta – 16/04)  
Saídas previstas (até 16/04):  
• R$ 1.200,00 – Fornecedor de impressão (venc. 12/04) – **alta**  
• R$ 189,90 – Internet e telefone (venc. 14/04) – média  
• R$ 75,60 – DAS MEI (venc. 15/04) – alta  
Projeção de caixa ao final de 16/04 (considerando todas as entradas e saídas acima): ≈ R$ 7.134,50, ainda bem acima da reserva mínima.

**Pontos de atenção**

Retirada pessoal = 22% das saídas do mês (alerta de excesso de retirada).  
Concentração de vencimentos → 3 contas a pagar nos próximos 7 dias (alerta de concentração de vencimentos).  
A projeção depende do recebimento efetivo dos clientes Alpha e Beta; atrasos reduziriam a margem de segurança.

**Próxima ação sugerida**

Quitação imediata dos pagamentos de alta prioridade: fornecedor de impressão (R$ 1.200,00) e DAS MEI (R$ 75,60).  
Pagamento da conta de internet/telefone (R$ 189,90) logo em seguida.  
Reavaliar a retirada pessoal: manter ≤ 20% das saídas (cerca de R$ 800-R$ 900) para preservar a margem de segurança.  
Monitorar recebíveis: confirme datas com os clientes Alpha e Beta; se houver risco de atraso, considere negociação de pagamento antecipado ou parcial.  
Ferramenta de gestão: se ainda não utiliza, experimente a “Conta PJ com gestão financeira” (`prod_003`) para visualização consolidada de entradas, saídas e vencimentos.

**Resposta dada pela IA - Então posso tirar R$ 500?:**  

Saldo atual: R$ 4.850,00  
Reserva mínima recomendada: R$ 3.500,00 (o caixa está acima da reserva).  
Saídas nos próximos dias (até 16/04):  
R$ 1.200,00 – fornecedor (venc. 12/04 – alta)  
R$ 189,90 – internet/telefone (venc. 14/04 – média)  
R$ 75,60 – DAS MEI (venc. 15/04 – alta)  
Entradas previstas:  
R$ 2.400,00 (Cliente Alpha – 13/04)  
R$ 1.350,00 (Cliente Beta – 16/04)

**Pontos de atenção**

**Reserva de caixa:**  
Se retirar R$ 500,00 agora, o saldo cairá para **R$ 4.350,00**.  
Após quitar as três contas a pagar (total R$ 1.465,50), o caixa ficaria em **R$ 2.884,50**, abaixo da reserva mínima.  
Só depois dos recebimentos (13 + 16/04) o saldo voltaria a superar a reserva, mas isso deixa um período de 2-3 dias com margem de segurança reduzida.

**Excesso de retirada pessoal:**  
Atualmente as retiradas representam 22% das saídas mensais (alerta “excesso de retirada”).  
Acrescentar mais R$ 500,00 eleva esse percentual e pode comprometer a saúde do caixa se as despesas mensais se mantiverem ou aumentarem.

**Concentração de vencimentos:**  
Três pagamentos de alta/média prioridade estão concentrados entre 12 e 15/04. Qualquer atraso no recebimento dos clientes pode gerar apertos temporários.

**Próxima ação sugerida**

**Adie a retirada de R$ 500,00** até que ao menos a primeira entrada (R$ 2.400,00 – Cliente Alpha) seja recebida em 13/04.

Assim, após a retirada e os pagamentos, o saldo ficaria ≈ R$ 5.000,00, mantendo uma margem confortável acima da reserva.  
Se a retirada for urgente, limite-a a no máximo R$ 200,00 agora e aguarde o recebimento de Alpha para efetuar o restante.

Essa medida mantém o caixa acima da reserva mesmo nos dias críticos (12-14/04).  
Reavalie a política de retiradas:  
Estabeleça um teto de ≤ 20% das despesas mensais (cerca de R$ 800-R$ 900, considerando o total de saídas do mês).  
Registre a retirada planejada antes de efetuar pagamentos, garantindo que sempre haja saldo suficiente para cobrir as obrigações.  
Monitore diariamente o saldo até 16/04. Caso o caixa se aproxime de R$ 3.500,00 antes de receber as entradas, suspenda novas retiradas e, se necessário, negocie antecipação parcial com os clientes.

Ferramenta de apoio: Avalie a adoção da “Conta PJ com gestão financeira” (`prod_003`) para visualizar em tempo real a relação entre retiradas, recebíveis e pagamentos futuros.

Em resumo: Você pode retirar parte do dinheiro, mas retirar **R$ 500,00** agora deixaria o caixa vulnerável nos próximos dias, ficando abaixo da reserva mínima até que os pagamentos dos clientes sejam efetivados. Recomendo aguardar a entrada de R$ 2.400,00 (13/04) ou, se precisar retirar hoje, limitar o valor a no máximo R$ 200,00 e repensar a política de retiradas para mantê-las ≤ 20% das despesas mensais.

**Justificativa:**  
A resposta do agente está correta, pois na segunda interação ele manteve coerência com o contexto acumulado da conversa e reutilizou corretamente os elementos apresentados na primeira resposta, como saldo atual, reserva mínima, contas a pagar, contas a receber e alertas ativos. Além disso, a orientação sobre a retirada de R$ 500,00 foi consistente com o cenário já descrito anteriormente, mostrando que o agente considerou o histórico do chat e não respondeu de forma isolada.

**Referências utilizadas:**  
- `contas_pj.json`
- `contas_pagar.csv`
- `contas_receber.csv`
- `indicadores_caixa.json`
- `regras_alertas.json`
- `SYSTEM_PROMPT`
- histórico da conversa mantido no `st.session_state`

**Métrica principal:** Consistência contextual  
**Resultado:** [X] Correto [ ] Incorreto

---

### Teste 7: Clareza da resposta

**Pergunta:**  
`Explique se estou correndo risco financeiro.`

**Resposta esperada:**  
A resposta deve ser clara, acessível, organizada e sem excesso de jargão técnico.

**Resposta dada pela IA:**  

Saldo atual: R$ 12.840,50  
Reserva mínima recomendada: R$ 8.000,00 (você está R$ 4.840,50 acima da margem de segurança).  
Entradas previstas para os próximos 7 dias: R$ 3.850,00 (R$ 2.100,00 – reparo frota Zeta; R$ 1.750,00 – manutenção preventiva).  
Saídas previstas para os próximos 7 dias: R$ 3.840,20 (R$ 3.200,00 – fornecedor de peças; R$ 640,20 – energia elétrica).  
Retirada pessoal: 8% das saídas do mês – dentro do limite seguro (< 20%).

**Pontos de atenção**

Fornecedor (`cp_004`) – vencimento 11/04: a conta já está vencida e tem prioridade alta. O não pagamento ainda hoje pode gerar juros ou interrupção no fornecimento de peças.  
Recebível `cr_003` (10/04) – R$ 2.100,00: a data prevista já passou. Se o pagamento atrasar alguns dias, a folga de caixa cairá para cerca de R$ 9.650,00 – ainda acima da reserva, mas a margem de conforto diminui.  
Concentração de vencimentos: apenas duas contas nos próximos 7 dias, portanto a regra de “concentração excessiva” não é disparada.  
Aluguel (R$ 2.500,00) já pago em 05/04 e folha (R$ 2.200,00) paga em 06/04 – não há risco imediato aí.  
Nenhum alerta de caixa abaixo da reserva nem de retirada excessiva está ativo.

**Risco financeiro atual**

Risco baixo/contido. O caixa está saudável e permanece confortável mesmo considerando a possibilidade de atraso no recebimento de R$ 2.100,00.  
O único ponto que pode converter esse cenário em risco moderado é não quitar a obrigação com o fornecedor ainda hoje, pois isso poderia gerar juros e comprometer a disponibilidade de peças para novos atendimentos.

**Próxima ação sugerida**

Pagar imediatamente a conta do fornecedor (R$ 3.200,00) – use a transferência já configurada ou registre o pagamento na “Conta PJ com gestão financeira” (produto `prod_003`) para manter o histórico.  
Confirmar o recebimento do reparo frota Zeta (R$ 2.100,00). Se ainda não houver crédito, envie um lembrete de pagamento via PIX (ou considere habilitar a solução “Cobrança com QR Code PIX” – produto `prod_002` – para acelerar futuros recebimentos).  
Atualizar o controle de fluxo: registre as duas entradas e duas saídas previstas; continue monitorando o saldo projetado diariamente, garantindo que nunca caia abaixo de R$ 8.000,00.  
Estabelecer um teto interno para retiradas pessoais (por exemplo, 10% das saídas) para manter ainda mais margem de segurança nos próximos meses.  
Seguindo estas ações, você mantém o risco financeiro sob controle e preserva a saúde do caixa da Oficina Rota Certa ao longo da semana e nas próximas. Caso precise de apoio para programar lembretes de pagamento ou configurar a ferramenta de cobrança rápida, estou à disposição.

**Justificativa:**  
A resposta do agente está correta, pois foi apresentada de forma clara, organizada e acessível. O agente estruturou bem a análise, separando saldo, entradas, saídas, pontos de atenção, nível de risco e próxima ação sugerida. Além disso, evitou excesso de jargão técnico e explicou o risco financeiro em linguagem compreensível, o que atende ao objetivo do teste de clareza.

**Referências utilizadas:**  
- `contas_pj.json`
- `contas_receber.csv`
- `contas_pagar.csv`
- `transacoes_pj.csv`
- `indicadores_caixa.json`
- `regras_alertas.json`
- `produtos_bancarios_pj.json`

**Métrica principal:** Clareza  
**Resultado:** [X] Correto [ ] Incorreto

---

### Teste 8: Recomendação prática

**Pergunta:**  
`O que devo fazer agora para melhorar meu caixa?`

**Resposta esperada:**  
O agente deve sugerir uma ação objetiva e aplicável, como priorizar contas, evitar retiradas, acompanhar recebimentos ou reorganizar despesas.

**Resposta dada pela IA:**  

**Resumo**

Saldo atual: R$ 4.850,00 (acima da reserva mínima de R$ 3.500,00).  
Pagamentos nos próximos 7 dias (até 15/04):  
R$ 1.200,00 – fornecedor de impressão (venc. 12/04) – alta prioridade  
R$ 189,90 – internet/telefone (venc. 14/04) – prioridade média  
R$ 75,60 – DAS MEI (venc. 15/04) – alta prioridade  
Total a pagar: R$ 1.465,50.  
Recebimentos previstos:  
R$ 2.400,00 – Cliente Alpha (13/04)  
R$ 1.350,00 – Cliente Beta (16/04)  
Total a receber: R$ 3.750,00.  
Retirada pessoal no mês: 22% das saídas (alerta de excesso).  
Com as entradas previstas, o caixa projetado ao final de 16/04 seria cerca de **R$ 7.100,00**, mas entre 12 e 14/04 o saldo cairia momentaneamente abaixo da reserva se a retirada de R$ 500,00 for feita agora.

**Pontos de atenção**

Concentração de pagamentos (três contas a pagar em poucos dias). Qualquer atraso nos recebimentos pode gerar aperto temporário.  
Retirada pessoal acima do recomendado (≥ 20%). Acrescentar mais R$ 500,00 aumentaria o risco de ficar sem margem de segurança nos dias críticos.  
Dependência de recebimentos – a projeção saudável só se concretiza se os clientes Alpha e Beta pagarem nas datas previstas.

**Próxima ação sugerida (o que fazer agora)**

**Postergar retiradas pessoais**  
Suspenda a retirada de R$ 500,00 por enquanto.  
Se realmente precisar de dinheiro hoje, limite-a a no máximo R$ 200,00 e registre o valor como “retirada planejada”. Isso mantém o caixa acima da reserva mesmo nos dias de pagamento (12-14/04).

**Quitar primeiro as obrigações de alta prioridade**  
Pague imediatamente o fornecedor de impressão (R$ 1.200,00) e o DAS MEI (R$ 75,60).  
Em seguida, quite a conta de internet/telefone (R$ 189,90).  
Ao efetuar esses pagamentos antes do vencimento, você evita juros e mantém o histórico de pagamentos em dia.

**Antecipar ou acelerar os recebimentos**  
Entre em contato com o Cliente Alpha (vencimento 13/04) e confirme a data de pagamento. Se houver risco de atraso, ofereça desconto de 2% para pagamento até 12/04 ou solicite transferência via QR Code PIX (produto Cobrança com QR Code PIX).  
Se o Cliente Beta também puder antecipar parte da fatura, isso aumenta ainda mais a margem de segurança.

**Reavaliar a política de retirada**  
Defina um teto de ≤ 20% das despesas mensais (aprox. R$ 800-R$ 900, considerando o total de saídas).  
Registre cada retirada planejada em uma planilha ou na ferramenta de gestão financeira para garantir que o saldo nunca fique abaixo da reserva antes da próxima entrada.

**Utilizar a ferramenta “Conta PJ com gestão financeira” (`prod_003`)**  
Essa conta oferece visualização consolidada de vencimentos, recebíveis e alertas automáticos.  
Ela ajuda a monitorar diariamente a diferença entre saldo disponível e reservas, evitando surpresas.

**Se precisar de apoio extra nos próximos dias críticos**  
Avalie a “Linha de Crédito Capital de Giro PJ” (`prod_001`) apenas se houver risco recorrente de falta de caixa ou atraso frequente de clientes. No momento, a projeção indica que o crédito não é necessário, mas manter a opção em vista pode ser útil caso a situação mude.

**Resumo da ação imediata:**

- **Não retire R$ 500,00 agora**; limite-a a R$ 200,00 se for imprescindível.  
- Efetue os pagamentos de alta prioridade hoje mesmo.  
- Confirme/antecipe os recebimentos com Alpha (13/04) e Beta (16/04).  
- Monitore o saldo diariamente até 16/04 e ajuste retiradas conforme a reserva se mantenha acima de R$ 3.500,00.

Seguindo esses passos, você mantém uma margem de segurança sólida, reduz a vulnerabilidade nos próximos dias e cria hábitos que sustentam um caixa saudável a longo prazo. Caso haja novas movimentações ou dúvidas, estou à disposição para recalcular o fluxo.

**Justificativa:**  
A resposta do agente está correta, pois apresentou recomendações práticas, objetivas e aplicáveis para melhorar o caixa no curto prazo. O agente sugeriu ações coerentes com o contexto do cliente, como postergar retiradas pessoais, priorizar pagamentos mais urgentes, acompanhar e antecipar recebimentos e reorganizar o controle financeiro. Além disso, as orientações estão alinhadas com os alertas ativos e com a situação de caixa apresentada nos dados mockados.

**Referências utilizadas:**  
- `contas_pj.json`
- `contas_pagar.csv`
- `contas_receber.csv`
- `indicadores_caixa.json`
- `regras_alertas.json`
- `produtos_bancarios_pj.json`
- `SYSTEM_PROMPT`

**Métrica principal:** Utilidade  
**Resultado:** [X] Correto [ ] Incorreto

---

## Formulário de Avaliação

A avaliação foi realizada por meio de autoavaliação, com notas atribuídas pelo próprio autor após executar os cenários de teste.

| Critério | Nota (1 a 5) |
|---------|---------------|
| Assertividade | 5 |
| Segurança | 5 |
| Coerência | 5 |
| Clareza | 4 |
| Utilidade | 5 |
| Consistência contextual | 5 |

---

## Estratégia de Avaliação

Devido ao tempo disponível no desenvolvimento do projeto, a avaliação do agente foi realizada pelo próprio autor, com base em testes estruturados e análise manual das respostas geradas.

Os testes foram conduzidos com diferentes cenários e perfis de cliente mockados, buscando verificar se o agente:
- respondeu corretamente com base nos dados disponíveis;
- manteve coerência com o perfil financeiro do cliente;
- evitou inventar informações;
- respondeu com clareza e utilidade prática;
- utilizou corretamente o contexto da conversa.

Embora a avaliação não tenha contado com usuários externos nesta etapa, os testes permitiram validar o comportamento do agente em situações relevantes para a proposta do projeto e identificar pontos de melhoria.

---

## Resultados

A avaliação foi feita por meio de autoavaliação, com testes manuais conduzidos pelo próprio autor em diferentes cenários de uso.

### O que funcionou bem:
- O agente respondeu corretamente perguntas sobre caixa com base nos dados mockados
- O agente manteve o foco em gestão financeira e evitou sair do escopo
- O agente apresentou linguagem clara e acessível
- O agente conseguiu diferenciar respostas conforme o perfil do cliente
- O agente utilizou o histórico da conversa para manter continuidade no atendimento

### O que pode melhorar:
- Melhorar a objetividade em respostas mais longas
- Refinar a priorização de alertas em cenários mais críticos
- Reduzir repetições em perguntas consecutivas semelhantes
- Aprimorar o uso do histórico para respostas mais contextualizadas
- Expandir a avaliação futura com testes feitos por outros usuários
