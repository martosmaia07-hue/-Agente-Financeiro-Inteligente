import json
import pandas as pd
import requests
import streamlit as st

# ================  CONFIGURAÇÃO =================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO ="gpt-oss"

# =============== Carregar Dados ================ 
perfil = json.load(open('./data/perfil_investidor.json'))
transacoes = pd.read_csv('./data/transacoes.csv')
historico = pd.read_csv('./data/historico_atendimento.csv')
produtos = json.load(open('./data/produtos_financeiros.json'))

# ===============Montar Contexto ================= 
contexto = f"""
CLIENTE: {perfil['nome']}, {perfil['idade']} anos, {perfil['perfil_investidor']}
OBJETIVO: {perfil['objetivo_principal']}
PATRIMÔNIO: R$ {perfil['patrimonio_total']} | DIVIDA: R$ {perfil['divida_atual']}

TRANSAÇÕES RECENTES:
{transacoes.to_string(index=False)}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}

PRODUTOS FINANCEIROS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""

# =============== System Prompt ================ 
system_prompt = """
Você é Ana, uma agente financeira inteligente especializada em planejamento de gastos domésticos, organização financeira familiar e renegociação de dívidas.

Objetivo Principal

Ajudar o cliente a:
- Organizar seu orçamento pessoal e familiar
- Avaliar e, se necessário, orientar sobre refinanciamento ou quitação de dívidas
- Planejar metas financeiras (curto, médio e longo prazo)
- Construir e acompanhar a reserva de emergência

Regras Obrigatórias de Comportamento

1. Base de Dados
- Sempre baseie suas respostas exclusivamente nos dados fornecidos pelo cliente (perfil, histórico ou informações informadas na conversa).
- Nunca crie, estime ou invente valores financeiros.

2. Limite de Conhecimento
- Caso não possua informações não minta, informe que não possui essas informações e mostre outras opções.
- Nunca responda perguntas fora do contexto de finanças pessoais.


3. Investimentos
- Nunca faça ofertas diretas ou recomendações fechadas de investimento.
- Apenas explique os tipos de investimentos disponíveis, suas características, riscos e para quais objetivos costumam ser indicados.

4. Segurança e Ética
- Nunca compartilhe dados sensíveis, senhas ou informações de outros clientes.
- Respeite totalmente a privacidade.

5. Didática e Confirmação
- Explique de forma clara, simples e educativa.
- Sempre pergunte ao final se o cliente entendeu a explicação ou se deseja aprofundar algum ponto.
"""

# =========================Chamar Ollama =============== 
def perguntar(msg):
    prompt = f"""
    {system_prompt}

    CONTEXTO DO CLIENTE:
    {contexto}

    Pergunta: {msg}"""

    r = requests.post(OLLAMA_URL, json={"model": MODELO, "prompt": prompt, "stream": False})
    return r.json().get('response', '')

# ========================== Interface ====================
st.title(" Ana, Sua Analista Financeira")

if pergunta := st.chat_input("Sua dúvida sobre finanças..."):
    st.chat_message("user").write(pergunta)
    with st.spinner("..."):
        st.chat_message("assistant").write(perguntar(pergunta))
