# 🤖 Agente Financeiro Inteligente com IA Generativa — **San (Multiagente)**

## Contexto

Os assistentes virtuais no setor financeiro estão evoluindo de simples chatbots reativos para **agentes inteligentes e proativos**. Este projeto implementa o **San**, um agente financeiro multi-modo que usa IA Generativa para:

* **Antecipar necessidades** (roteamento automático por intenção)
* **Personalizar** orientações com base no contexto do cliente (perfil + transações + histórico)
* **Cocriar soluções** com linguagem simples (educação + plano prático)
* **Garantir segurança** (anti-golpe + anti-alucinação + regras e validação final)

O San opera em **3 personas**:

* 🛡️ **Guardião:** anti-golpe / anti-fraude (prioridade máxima)
* 📚 **Finanças:** educação financeira didática, sem recomendar investimentos específicos
* 🧭 **Autopiloto:** planejamento e organização de orçamento com base em transações

---

## Visão Geral do Projeto

### O problema que resolve

Clientes frequentemente:

* caem em golpes (WhatsApp/SMS/ligação falsa, taxa de liberação, pedido de código);
* não entendem conceitos básicos de finanças e tomam decisões impulsivas;
* não conseguem controlar gastos e manter reserva.

### A solução

O San combina:

* **LangGraph** (fluxo consistente): `router → build_prompt → LLM → checker`
* **Ollama** (LLM local): roda modelos leves com baixo custo e bom desempenho
* **Streamlit**: interface de chat rápida e simples
* **Base mock (CSV/JSON)**: dados sintéticos do cliente para personalizar as respostas

---

## Como Rodar

### Requisitos

* Python 3.10+
* Ollama instalado e rodando
* Dependências Python (Streamlit, requests, pandas, langgraph)

### 1) Preparar ambiente

```bash
pip install -r requirements.txt
```

### 2) Baixar um modelo leve no Ollama (recomendado)

Modelo recomendado (baixo custo SSD e bom desempenho):

```bash
ollama pull llama3.2
```

> Alternativa ainda mais leve: `gemma2:2b` (se SSD estiver muito apertado).

### 3) Configurar caminho do dataset (opcional)

O projeto pode ler os datasets a partir de um caminho fixo no Windows. Exemplo:

```python
BASE_DATA = Path(r"D:\Pessoal\Secular\Machine Learning\protótipo_bia\dio-lab-bia-do-futuro\data")
```

Ou via variável de ambiente (recomendado):

**PowerShell**

```powershell
setx BIA_DATA_DIR "D:\Pessoal\Secular\Machine Learning\protótipo_bia\dio-lab-bia-do-futuro\data"
```

### 4) Rodar o app

```bash
streamlit run src/app.py
```

---

## Troca de Modelo e Economia de SSD

### Remover modelo antigo do Ollama (ex.: `gpt-oss`)

```bash
ollama list
ollama rm gpt-oss
```

### Baixar modelo novo

```bash
ollama pull llama3.2
```

### Trocar o modelo no código

No `src/app.py`, altere:

```python
MODELO = "llama3.2"
```

---

## O Que Você Deve Entregar (como este repo resolve)

### 1. Documentação do Agente ✅

* Caso de uso, persona/tom de voz, arquitetura e segurança.
  📄 `docs/01-documentacao-agente.md`

### 2. Base de Conhecimento ✅

* Uso de dataset mock (CSV/JSON), redução de contexto e filtros por agente.
  📄 `docs/02-base-conhecimento.md`

### 3. Prompts do Agente ✅

* 3 System Prompts (Guardião, Finanças, Autopiloto), exemplos e edge cases.
  📄 `docs/03-prompts.md`

### 4. Aplicação Funcional ✅

* Chat em Streamlit + Ollama + LangGraph.
  📁 `src/`

### 5. Avaliação e Métricas ✅

* Métricas de roteamento, segurança, consistência, uso do contexto e latência.
  📄 `docs/04-metricas.md`

### 6. Pitch ✅

* Roteiro do pitch de 3 minutos + checklist e link.
  📄 `docs/05-pitch.md`

---

## Arquitetura (resumo)

O fluxo é controlado pelo **LangGraph** para manter consistência de comportamento:

1. `router`: escolhe o agente com base na mensagem (Guardião tem prioridade)
2. `build_prompt`: monta o prompt com system prompt + contexto (CSV/JSON), aplicando filtros por agente
3. `llm`: chama Ollama (`/api/generate`)
4. `checker`: reforça regras finais (máx. 3 parágrafos, reforço anti-sensível)

---

## Ferramentas Usadas

| Categoria    | Ferramentas       |
| ------------ | ----------------- |
| Interface    | Streamlit         |
| LLM local    | Ollama            |
| Orquestração | LangGraph         |
| Dados        | CSV/JSON + pandas |
| HTTP         | requests          |

---

## Estrutura do Repositório

> Observação: no projeto final, os datasets podem estar em `data/` ou em uma pasta externa configurada por caminho (ex.: `BIA_DATA_DIR`).

```
📁 lab-agente-financeiro/
│
├── 📄 README.md
│
├── 📁 data/                          # Dados mockados (opcional/local)
│   ├── historico_atendimento.csv
│   ├── perfil_investidor.json
│   ├── produtos_financeiros.json
│   └── transacoes.csv
│
├── 📁 docs/
│   ├── 01-documentacao-agente.md
│   ├── 02-base-conhecimento.md
│   ├── 03-prompts.md
│   ├── 04-metricas.md
│   └── 05-pitch.md
│
├── 📁 src/
│   └── app.py
│
└── 📁 examples/
    └── README.md
```

---

## Dicas Finais

1. **Segurança primeiro:** qualquer sinal de golpe deve ser tratado pelo Guardião.
2. **Contexto enxuto:** reduzir CSV/JSON melhora qualidade e latência.
3. **Consistência com LangGraph:** o fluxo reduz “mudança de personalidade” e aumenta previsibilidade.
4. **Teste cenários reais:** use prompts de golpe, educação e orçamento para validar roteamento e regras.
5. **Cuide do SSD:** remova modelos antigos com `ollama rm` e prefira modelos menores.


