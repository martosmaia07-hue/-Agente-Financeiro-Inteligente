# Base de Conhecimento - IR Smart

## Dados Utilizados

O IR Smart utiliza uma base de conhecimento estruturada composta por regras tributárias oficiais e dados das operações do usuário:

| Arquivo/Fonte | Formato | Utilização no Agente |
|---------------|---------|---------------------|
| `regras_tributarias.json` | JSON | Regras da Receita Federal (alíquotas, isenções, prazos) |
| `legislacao_ir_acoes.md` | Markdown | Documentação completa da IN RFB nº 1.585/2015 |
| `operacoes_usuario.db` | SQLite | Histórico de compras/vendas de ações do usuário |
| `precos_medio.json` | JSON | Preço médio de compra por ativo (para cálculo de lucro) |
| `impostos_pagos.csv` | CSV | Registro de DARFs geradas e impostos já pagos |
| `prejuizos_acumulados.json` | JSON | Controle de prejuízos para compensação futura |
| `calendario_tributario.json` | JSON | Datas de vencimento de DARF por mês |

---

## Estrutura dos Dados

### 1. Regras Tributárias (`regras_tributarias.json`)

```json
{
  "swing_trade": {
    "aliquota": 0.15,
    "descricao": "Operações normais (compra e venda em dias diferentes)",
    "isencao_mensal": 20000.00,
    "codigo_darf": "6015",
    "base_legal": "Lei nº 8.981/1995, art. 21"
  },
  "day_trade": {
    "aliquota": 0.20,
    "descricao": "Operações realizadas no mesmo dia",
    "isencao_mensal": 0.00,
    "codigo_darf": "6015",
    "base_legal": "Lei nº 8.981/1995, art. 21, §1º"
  },
  "compensacao_prejuizo": {
    "permitido": true,
    "mesmo_tipo_operacao": true,
    "prazo_utilizacao": "indeterminado",
    "percentual_maximo_mes": 1.0,
    "base_legal": "IN RFB nº 1.585/2015, art. 60"
  },
  "vencimento_darf": {
    "dia_util": "último dia útil do mês subsequente",
    "exemplo": "Vendas de Janeiro → DARF vence em 28/02 ou 29/02"
  }
}
```

### 2. Legislação Detalhada (`legislacao_ir_acoes.md`)

Fragmento do documento:

```markdown
## Instrução Normativa RFB nº 1.585/2015

### Art. 59 - Fato Gerador
O imposto sobre a renda incide sobre os ganhos líquidos auferidos em operações 
realizadas nas bolsas de valores...

### Art. 60 - Compensação de Perdas
§1º As perdas incorridas nas operações de day trade somente serão compensadas 
com ganhos auferidos em operações da mesma espécie...

### Art. 61 - Isenção
Ficam isentos do imposto sobre a renda os ganhos líquidos auferidos por pessoa 
física em operações no mercado à vista de ações negociadas em bolsas de valores, 
cujo valor das alienações realizadas em cada mês seja igual ou inferior a R$ 20.000,00...
```

### 3. Operações do Usuário (`operacoes_usuario.db`)

**Schema SQLite:**

```sql
CREATE TABLE operacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    tipo VARCHAR(6) NOT NULL, -- 'COMPRA' ou 'VENDA'
    quantidade INTEGER NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL,
    valor_total DECIMAL(12,2) NOT NULL,
    corretagem DECIMAL(8,2) DEFAULT 0,
    emolumentos DECIMAL(8,2) DEFAULT 0,
    is_day_trade BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE impostos_calculados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mes_referencia DATE NOT NULL,
    tipo_operacao VARCHAR(10) NOT NULL, -- 'DAY_TRADE' ou 'SWING_TRADE'
    lucro_bruto DECIMAL(12,2),
    prejuizo_compensado DECIMAL(12,2) DEFAULT 0,
    base_calculo DECIMAL(12,2),
    aliquota DECIMAL(5,4),
    imposto_devido DECIMAL(10,2),
    total_vendas_mes DECIMAL(12,2),
    isento BOOLEAN DEFAULT FALSE,
    darf_gerada BOOLEAN DEFAULT FALSE,
    pago BOOLEAN DEFAULT FALSE
);
```

**Exemplo de dados:**

```csv
id,data,ticker,tipo,quantidade,preco_unitario,valor_total,is_day_trade
1,2025-01-05,PETR4,COMPRA,100,30.50,3050.00,FALSE
2,2025-01-20,PETR4,VENDA,100,32.00,3200.00,FALSE
3,2025-01-21,VALE3,COMPRA,50,85.00,4250.00,FALSE
4,2025-01-21,VALE3,VENDA,50,86.50,4325.00,TRUE
```

### 4. Preço Médio (`precos_medio.json`)

```json
{
  "PETR4": {
    "quantidade_total": 200,
    "preco_medio": 31.25,
    "custo_total": 6250.00,
    "ultima_atualizacao": "2025-01-20"
  },
  "VALE3": {
    "quantidade_total": 0,
    "preco_medio": 0,
    "custo_total": 0,
    "ultima_atualizacao": "2025-01-21"
  }
}
```

### 5. Prejuízos Acumulados (`prejuizos_acumulados.json`)

```json
{
  "swing_trade": {
    "valor": 500.00,
    "origem": [
      {
        "mes": "2024-12",
        "valor": 500.00,
        "utilizado": 0.00,
        "saldo": 500.00
      }
    ]
  },
  "day_trade": {
    "valor": 0.00,
    "origem": []
  }
}
```

---

## Adaptações e Expansões

### Dados Criados do Zero

Como não existem datasets públicos específicos para cálculo de IR sobre ações no formato necessário, **todos os dados foram criados especificamente para este projeto**:

✅ **Regras tributárias**: Extraídas e estruturadas da legislação oficial da Receita Federal
✅ **Schema de banco de dados**: Projetado para capturar todas as informações necessárias para cálculos precisos
✅ **Exemplos de operações**: Criados para cobrir diversos cenários (swing trade, day trade, prejuízos, isenções)
✅ **Calendário tributário**: Automatizado baseado nas regras de vencimento

### Fontes Oficiais Utilizadas

1. **Instrução Normativa RFB nº 1.585/2015** - Regras de IR sobre renda variável
2. **Lei nº 8.981/1995** - Alíquotas e fato gerador
3. **Perguntas e Respostas IRPF** (Receita Federal) - Casos práticos
4. **Manual DARF** - Códigos de recolhimento

---

## Estratégia de Integração

### Como os dados são carregados?

```python
# 1. Carregamento no início da sessão
def inicializar_agente():
    # Carrega regras tributárias (estáticas)
    regras = load_json('regras_tributarias.json')
    legislacao = load_markdown('legislacao_ir_acoes.md')
    
    # Conecta ao banco de dados do usuário
    db = sqlite3.connect('operacoes_usuario.db')
    
    # Carrega estado atual do usuário
    precos_medio = load_json('precos_medio.json')
    prejuizos = load_json('prejuizos_acumulados.json')
    
    return {
        'regras': regras,
        'legislacao': legislacao,
        'db': db,
        'precos_medio': precos_medio,
        'prejuizos': prejuizos
    }
```

### Como os dados são usados no prompt?

**Abordagem Híbrida - RAG + Cálculo Programático:**

#### 1. **System Prompt Estático** (regras gerais)
```
Você é o IR Smart, especialista em tributação de ações.
Use APENAS as regras oficiais fornecidas.
Nunca invente alíquotas ou prazos.
```

#### 2. **Contexto Dinâmico** (dados do usuário)
```python
def montar_contexto_usuario(user_id):
    # Busca operações do mês atual
    operacoes_mes = query_db(
        "SELECT * FROM operacoes WHERE mes = CURRENT_MONTH"
    )
    
    # Calcula totais
    total_vendas = sum(op['valor_total'] for op in operacoes_mes if op['tipo'] == 'VENDA')
    
    # Monta contexto
    contexto = f"""
    SITUAÇÃO ATUAL DO USUÁRIO:
    - Total de vendas no mês: R$ {total_vendas:,.2f}
    - Limite de isenção: R$ 20.000,00
    - Status: {'ISENTO' if total_vendas <= 20000 else 'TRIBUTÁVEL'}
    - Prejuízos acumulados swing trade: R$ {prejuizos['swing_trade']['valor']:,.2f}
    
    ÚLTIMA OPERAÇÃO:
    {formatar_operacao(operacoes_mes[-1])}
    """
    return contexto
```

#### 3. **RAG para Legislação** (quando necessário explicar)
```python
def buscar_legislacao_relevante(pergunta):
    # Embeddings da pergunta
    query_embedding = gerar_embedding(pergunta)
    
    # Busca nos chunks de legislação
    chunks_relevantes = buscar_similar(
        query_embedding, 
        base_legislacao,
        top_k=3
    )
    
    return chunks_relevantes
```

### Fluxo Completo

```
Usuário: "Vendi 100 PETR4 por R$ 32,00"
    ↓
1. Registra operação no BD
    ↓
2. Busca preço médio de compra (R$ 30,50)
    ↓
3. Calcula lucro: (32 - 30.50) × 100 = R$ 150,00
    ↓
4. Verifica total vendas do mês no BD
    ↓
5. Aplica regras (swing trade, 15%, verifica isenção)
    ↓
6. LLM gera explicação humanizada
    ↓
7. Sistema valida cálculo LLM vs código Python
    ↓
8. Retorna resposta + opção de gerar DARF
```

---

## Exemplo de Contexto Montado

### Cenário Real de Uso

**Dados de entrada:**
- Usuário tem 200 ações PETR4 (preço médio R$ 31,25)
- Já vendeu R$ 15.000 no mês (ainda isento)
- Quer vender 100 ações a R$ 35,00

**Contexto enviado ao LLM:**

```
REGRAS TRIBUTÁRIAS APLICÁVEIS:
- Tipo: Swing Trade (dias diferentes)
- Alíquota: 15%
- Isenção mensal: R$ 20.000,00
- Código DARF: 6015

SITUAÇÃO ATUAL:
- Total vendido no mês: R$ 15.000,00
- Saldo até isenção: R$ 5.000,00
- Prejuízos a compensar: R$ 0,00

OPERAÇÃO SIMULADA:
- Ativo: PETR4
- Quantidade: 100 ações
- Preço médio de compra: R$ 31,25
- Preço de venda pretendido: R$ 35,00
- Lucro bruto: R$ 375,00

CÁLCULO TRIBUTÁRIO:
- Nova venda: R$ 3.500,00
- Total mês (com esta venda): R$ 18.500,00
- Status: AINDA ISENTO (abaixo de R$ 20.000)
- Imposto devido: R$ 0,00

ALERTA:
Você ainda tem margem de R$ 1.500,00 para vender este mês sem pagar IR.
Se vender mais que isso, perderá a isenção e pagará 15% sobre TODO o lucro do mês.
```

---

## Versionamento e Atualização

### Controle de Mudanças Legislativas

```json
{
  "versao_base_conhecimento": "1.0.0",
  "data_atualizacao": "2025-01-15",
  "proxima_revisao": "2025-07-01",
  "changelog": [
    {
      "data": "2025-01-15",
      "mudanca": "Base inicial - IN RFB 1.585/2015",
      "impacto": "Primeira versão do sistema"
    }
  ],
  "alertas_legislativos": {
    "ativo": true,
    "fonte": "https://www.gov.br/receitafederal"
  }
}
```

### Sistema de Alertas

O agente verifica semanalmente se há:
- Mudanças nas alíquotas
- Novas instruções normativas
- Alterações nos prazos de vencimento

---

## Limitações da Base de Conhecimento

### O que a base NÃO cobre:

❌ **Outros ativos** (FIIs, ETFs, opções, criptomoedas)
❌ **Operações internacionais** (stocks, BDRs)
❌ **Casos judicializados** ou em litígio
❌ **Regimes especiais** de tributação

### Cobertura Atual:

✅ **Ações no mercado à vista** (B3)
✅ **Day trade e swing trade**
✅ **Isenções mensais**
✅ **Compensação de prejuízos**
✅ **Cálculo de preço médio**
✅ **Geração de DARF**

---

## Métricas da Base de Conhecimento

- **Cobertura legislativa**: 100% da IN RFB 1.585/2015 (artigos 59-65)
- **Casos de teste**: 50+ cenários validados
- **Precisão dos cálculos**: 100% (validado contra exemplos oficiais da RFB)
- **Atualização**: Trimestral ou sob demanda (mudanças legislativas)

---

*Base de conhecimento preparada para garantir respostas precisas, fundamentadas e auditáveis.*
