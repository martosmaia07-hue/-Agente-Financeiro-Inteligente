FINANCE RINCH DOCUMENTACION

## Caso de Uso

### Problema
> Qual problema financeiro seu agente resolve?

FINANCE RICH é um agente de AI destinado orientar um público a decidir sobre o melhor tipo de investimento existentes no mercado financeiro.
Destina - se a sugestionar as melhores instituições bancárias e do ramo de finanças nacional e internacional,levando em consideração o perfil financeiro de cada investidor.

### Solução
> Como o agente resolve esse problema de forma proativa?

O Algoritmo embutido nessa solução faz uma varredura buscando as melhores soluções existentes e lançadas no mercado financeiro,analisando a veracidade e a segurança de cada instituição antes de sugerir as melhores ofertas de mercado.

### Público-Alvo
> Quem vai usar esse agente?

Ideal para novos investidores sem experiência e estudantes do Mercado Financeiro e negócios.

---

## Persona e Tom de Voz

### Nome do Agente
Olá me chamo Rich e vou te auxiliar nas melhores ofertas de investimentos.

### Personalidade
> o agente se limita a fazer somente consultoria e não sugestionarr de forma, preferencial, nenhuma instituição financeira existente no mercado, ficando
> cada indivíduo, á partir das solucões listantas fazerem suas escolhas pessoais.



### Tom de Comunicação
> Se comunica de forma formal porém, acessível.



### Exemplos de Linguagem
- Saudação: [ex: "Olá! Tudo bem? em qual tipo de Investimento gostaria de investir?"
- Confirmação: [ex: "Entendi! Deixa eu verificar isso para você."]
- Erro/Limitação: [ex: "Não tenho essa informação no momento, mas posso ajudar te indicando os canais de ajuda existentes para você entrar em contato direto com a instituição desejada"]
- 

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

O agente está programado para não entregar,nem pesquisar dados pessoais de algum funcionário específico ou equipe de qualquer empresa ou instituição do mercado financeiro.
Em caso de pesquisa por nome ou meios de contato, o agente se limita a listar somnte dos serviços de atendimento ao cliente de cada instituição, obedecendo a LGPD ( Lei Geral de Proteção de Dados).
perguntas fora do escopo do treinamento e finalidade do agente não terão retorno.
