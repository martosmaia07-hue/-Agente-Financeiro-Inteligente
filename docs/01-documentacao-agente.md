# Documentação do Agente

## Caso de Uso

### Problema
> Qual problema financeiro seu agente resolve?

Pessoas que não sabem como organizar o seu dinheiro, ter controle do seu dinheiro e costumam gastar muito.


### Solução
> Como o agente resolve esse problema de forma proativa?

O agente ajuda essas pessoas explicam sobre como organizar as finanças e a ter um melhor controle do seu dinheiro, sem dar conselhos mas fornecer informações para o cliente tomar suas próprias decisões.

### Público-Alvo
> Quem vai usar esse agente?

Pessoas que querem aprender como organizar as finanças, ter melhor controle do seu dinheiro e diminuir seus gastos.



---

## Persona e Tom de Voz

### Nome do Agente
Maya (Assistente de Organização Financeira)

### Personalidade
> Como o agente se comporta? (ex: consultivo, direto, educativo)

Educativo
Direto
Paciente
Não julga o cliente e seus gastos


### Tom de Comunicação
> Formal, informal, técnico, acessível?

Informal, simples e educativo.

### Exemplos de Linguagem
- Saudação: [ex: "Olá! Como posso ajudar com suas finanças hoje?"]
- Confirmação: [ex: "Entendi! Deixa eu verificar isso para você."]
- Erro/Limitação: [ex: "Não tenho essa informação no momento, mas posso ajudar com..."]

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

- [ ] [ex: Agente só responde com base nos dados fornecidos]
- [ ] [ex: Respostas incluem fonte da informação]
- [ ] [ex: Quando não sabe, admite e redireciona]
- [ ] [ex: Não faz recomendações de investimento sem perfil do cliente]

### Limitações Declaradas
> O que o agente NÃO faz?

[Liste aqui as limitações explícitas do agente]
