import json
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv
import streamlit as st


load_dotenv()
cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open('./data/perfil_investidor.json', 'r', encoding='utf-8') as f:
    perfil = json.load(f)

with open('./data/produtos_financeiros.json', 'r', encoding='utf-8') as f:
    produtos = json.load(f)

transacao = pd.read_csv('./data/transacoes.csv')
historico = pd.read_csv('./data/historico_atendimento.csv')


contexto = f"""

[PERFIL DO CLIENTE]
{json.dumps(perfil, indent=2, ensure_ascii=False)}

[ÚLTIMAS TRANSAÇÕES]
{transacao.to_string(index=False)}

[HISTÓRICO DE CONVERSAS ANTERIORES]
{historico.to_string(index=False)}

[PRODUTOS FINANCEIROS DISPONÍVEIS NO MERCADO]
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""

SYSTEM_PROMPT="""
Você é o Atlas, um estrategista financeiro proativo e radicalmente honesto.
Seu objetivo é garantir que as metas financeiras do cliente sejam atingidas no prazo estipulado.

TOM DE VOZ:
Formal-moderno, polido, técnico (mas acessível) e extremamente objetivo. Aja com a confiança de um mentor financeiro que não faz rodeios.

REGRAS ESTABELECIDAS:
1. FOCO NA VIABILIDADE: Avalie matematicamente se as metas são possíveis. Se o plano for inviável com os aportes e prazos atuais, avise o cliente imediatamente e sugira um recálculo.
2. ADESÃO AO PERFIL: Nunca recomende ativos fora do perfil de risco do cliente estabelecido no contexto.
3. PROATIVIDADE COM CAIXA: Baseie suas análises estritamente nas [ÚLTIMAS TRANSAÇÕES]. Se notar sobras no orçamento, sugira proativamente um aporte para antecipar uma meta.
4. LIMITAÇÃO DE PRODUTOS: Se o cliente perguntar onde investir, cruze o perfil de risco dele e recomende APENAS opções listadas na sessão [PRODUTOS FINANCEIROS DISPONÍVEIS NO MERCADO].
5. PREVENÇÃO DE ALUCINAÇÃO: Se faltarem dados sobre um ativo ou se o cliente perguntar algo fora do universo financeiro, admita que não tem essa informação.
"""

def perguntar(msm):
    mensagens_api = [{"role": "system", "content": str(SYSTEM_PROMPT + contexto)}]
    
    for msg in msm:
        conteudo = msg["content"]
        if isinstance(conteudo, list):
            conteudo = conteudo[0] if len(conteudo) > 0 else ""
            
        texto_seguro = str(conteudo)
        mensagens_api.append({"role": str(msg["role"]), "content": texto_seguro})

    resposta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=mensagens_api
    )
    return resposta.choices[0].message.content


st.title("🏛️ ATLAS: Estrategista Financeiro")
st.markdown("Seu navegador rumo à liberdade financeira.")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Olá, João. Sou o Atlas. Analisei suas últimas transações e suas metas ativas. Como posso otimizar seu plano hoje?"
    })

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua mensagem para o Atlas..."):
    
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Analisando portfólio..."):
            resposta = perguntar(st.session_state.messages)
            st.markdown(resposta)
            
    st.session_state.messages.append({"role": "assistant", "content": resposta})