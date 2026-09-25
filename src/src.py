# Código da Aplicação

Aplicação Funcional (src/app.py)
Abaixo está um código funcional utilizando Streamlit e arquitetura simples para rodar o chat do agente:

Python
import streamlit as st
import json
import pandas as pd

st.set_page_config(page_title="Agente Financeiro Inteligente", page_icon="💰")

st.title("🤖 FinBot - Seu Agente Financeiro Inteligente")
st.write(" Tire dúvidas sobre seus gastos, histórico e planeje seus investimentos com segurança.")

# Carregando dados mockados simulados
@st.cache_data
def load_data():
    try:
        perfil = {"nome": "Ana Silva", "perfil": "Conservador", "limite_cartao": 5000}
        return perfil
    except:
        return {}

cliente = load_data()

# Histórico de mensagens no chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Olá, {cliente.get('nome', 'Cliente')}! Como posso te ajudar a organizar suas finanças hoje?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do usuário
if prompt := st.chat_input("Digite sua dúvida financeira..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Resposta simulada baseada em regras de segurança e contexto
    with st.chat_message("assistant"):
        if "gastar" in prompt.lower() or "comprar" in prompt.lower():
            resposta = "Com base na análise do seu perfil Conservador e histórico recente, recomendo cautela com novas compras parceladas para não comprometer sua reserva de emergência."
        elif "investir" in prompt.lower():
            resposta = "Verifiquei que seu perfil é Conservador. Temos opções de Renda Fixa com liquidez diária disponíveis no catálogo."
        else:
            resposta = "Entendi sua dúvida. Como assistente financeiro, estou aqui para ajudar com base nos seus dados de transações e perfil cadastrado. Poderia detalhar mais o que precisa?"
        
        st.markdown(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
