# Pitch (3 minutos)

## Roteiro Sugerido

### 1. O Problema (30 seg)

Hoje o cliente de banco enfrenta duas dores ao mesmo tempo:
**(1)** golpes digitais cada vez mais convincentes (WhatsApp, SMS, ligações falsas, “taxa de liberação”, pedido de código), e **(2)** dificuldade de organizar a vida financeira com base no que realmente acontece nas transações — o dinheiro “some” e ele não sabe por quê.
O resultado é perda financeira, ansiedade e atendimento humano sobrecarregado com dúvidas repetidas.

### 2. A Solução (1 min)

Eu criei o **San**, um agente financeiro multi-modo com três especialidades:

* **Guardião:** detecta sinais de golpe/fraude e orienta ações imediatas e seguras (sem pedir dados sensíveis).
* **Finanças:** explica conceitos financeiros de forma didática, usando o perfil do cliente como exemplo.
* **Autopiloto:** organiza orçamento e propõe um plano simples baseado nos padrões de transações.

O diferencial é que o San não responde “no improviso”: ele usa um fluxo com **LangGraph** (roteamento → prompt builder → LLM → checker). Isso deixa o comportamento **consistente**, com regras reforçadas no final: resposta curta (até 3 parágrafos) e segurança (nunca pedir senha/token/código).

Tudo roda localmente com **Ollama** e uma interface em **Streamlit**, usando uma base de conhecimento mock (CSV/JSON) com perfil, transações, histórico de atendimento e produtos.

### 3. Demonstração (1 min)

Na demo eu vou mostrar 3 testes rápidos:

1. **Golpe (Guardião):** “Recebi WhatsApp pedindo taxa pra liberar Pix” → o San identifica alto risco e dá o passo a passo seguro.
2. **Educação (Finanças):** “O que é CDI?” → o San explica simples, sem recomendar investimento específico.
3. **Planejamento (Autopiloto):** “Como faço pra sobrar dinheiro no fim do mês?” → o San sugere regras práticas com base em transações recentes.

Enquanto isso, eu mostro na tela:

* qual agente foi escolhido (caption no chat),
* e que a resposta sempre respeita as regras (curta e segura).

### 4. Diferencial e Impacto (30 seg)

O diferencial é unir **segurança + educação + planejamento** num único chatbot, com consistência garantida por uma arquitetura de fluxo (LangGraph) e validação final.
O impacto é direto: ajuda a **reduzir prejuízos por golpes**, melhora a **alfabetização financeira**, e ainda pode reduzir carga do atendimento com respostas padronizadas e seguras — principalmente para públicos que mais sofrem com fraude digital.

---

## Checklist do Pitch

* [ ] Duração máxima de 3 minutos
* [ ] Problema claramente definido
* [ ] Solução demonstrada na prática
* [ ] Diferencial explicado
* [ ] Áudio e vídeo com boa qualidade

---

## Link do Vídeo

[Link do vídeo]


