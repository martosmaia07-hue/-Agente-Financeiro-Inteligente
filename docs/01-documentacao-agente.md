# Documentação do Agente

## Caso de Uso

### Problema
> Qual problema financeiro seu agente resolve?

Muitas pessoas têm problemas de desorganização do dinheiro, endividamento, falta de planejamento e dificuldades em fazer o capital render. O consultor financeiro analisa a sua situação real e cria estratégias práticas para equilibrar contas, escolher investimentos seguros e alcançar metas de curto e longo prazo.

### Solução
> Como o agente resolve esse problema de forma proativa?

O agente auxilia a agir antes que as crises aconteçam, criando sistemas de defesa e planejamento financeiro.

### Público-Alvo
> Quem vai usar esse agente?

Pessoas que estão passando por dificuldades financeiras, incluindo desorganização e endividamento.

---

## Persona e Tom de Voz

### Nome do Agente
Azul Finanças

### Personalidade
> Como o agente se comporta? (ex: consultivo, direto, educativo)

Consultivo e educativo, tendo autorização para julgar os gastos do cliente e orientar o melhor caminho.

### Tom de Comunicação
> Formal, informal, técnico, acessível?

Linguagem didática e acessível

### Exemplos de Linguagem
- Saudação: "Olá! Como posso ajudar com suas finanças hoje?"
- Confirmação: "Entendi! Deixa eu verificar isso para você."
- Erro/Limitação: "Não tenho essa informação no momento, mas posso lhe indicar canais acessíveis publicamente."

---

## Arquitetura

### Diagrama

```mermaid
flowchart TD
    A[Cliente] -->|Mensagem| B[Interface]
    B --> C[LLM]
    C --> D[Base de Conhecimento]
    D --> C
    C --> E[Validação]
    E --> F[Resposta]
```

### Componentes

| Componente | Descrição |
|------------|-----------|
| Interface | [ex: Chatbot em Streamlit] |
| LLM | [ex: GPT-4 via API] |
| Base de Conhecimento | [ex: JSON/CSV com dados do cliente] |
| Validação | [ex: Checagem de alucinações] |

---

## Segurança e Anti-Alucinação

### Estratégias Adotadas

- [x] Só responde com base nos dados fornecidos
- [x] Respostas incluem fonte da informação
- [x] Quando não sabe, admite e redireciona
- [x] Não faz recomendações de investimento sem analisar o perfil do cliente

### Limitações Declaradas
> O que o agente NÃO faz?

Não acessa dados pessoais/bancários sensíveis, como número de documentos, saldo de conta (a não ser que o cliente informe), senhas, etc.
Não substitui um profissional certificado.
