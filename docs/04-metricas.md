# Avaliação e Métricas

## Como Avaliar seu Agente

A avaliação pode ser feita de duas formas complementares:

1. **Testes estruturados:** Você define perguntas e respostas esperadas;
2. **Feedback real:** Pessoas testam o agente e dão notas.

---

## Métricas de Qualidade

| Métrica | O que avalia | Exemplo de teste |
|---------|--------------|------------------|
| **Assertividade** | O agente respondeu o que foi perguntado? | Perguntar um conceito em Python e responder correto|
| **Segurança** | O agente evitou inventar informações? | Perguntar algo fora do contexto e ele admitir que não sabe |
| **Coerência** | A resposta faz sentido para o perfil do cliente? | Sugerir uma maneira para abordar certo problema no Python |

---

## Exemplos de Cenários de Teste

Crie testes simples para validar seu agente:

### Teste 1: Pergunta sobre assuntos fora do escopo
- **Pergunta:** "Qual o placar do jogo da copa entre Portugal e Uzbequistão?"
- **Resposta esperada:** Agente informa que não pode tratar de assuntos que não sejam programação em Python.
- **Resultado:** [X] Correto  [ ] Incorreto

### Teste 2: Pergunta sobre outra linguagem de programação
- **Pergunta:** "Como funciona a herança e polimorfismo em Java?"
- **Resposta esperada:** Agente informa que não pode responder a partir de outras linguagens de programação e caso o usuário queira ele pode explicar baseado em Python.
- **Resultado:** [X] Correto  [ ] Incorreto

### Teste 3: Pergunta genérica sobre um assunto de Python
- **Pergunta:** "Me ajude a entender dicionários em Python"
- **Resposta esperada:** Realiza a explicação de dicionários em Python utilizando o método de Scaffolding.
- **Resultado:** [X] Correto  [ ] Incorreto

### Teste 4: Pergunta direta sobre um assunto de Python
- **Pergunta:** "De forma direta, me ajude a entender dicionários em Python"
- **Resposta esperada:** Realiza a explicação de dicionários em Python sem utilizar o método de Scaffolding, de forma direta.
- **Resultado:** [X] Correto  [ ] Incorreto

---

## Resultados

Após os testes, registre suas conclusões:

**O que funcionou bem:**
- O agente entendeu bem o seu papel como mentor de Python, ajudando o usuário a entender mais sobre a linguagem de programação e podendo aprender de forma personalizada.

**O que pode melhorar:**
- O agente embora explique corretamente os conceitos, acaba não se aprofundando no assunto, deixando assim um modelo menos completo em sua explicação.

---
