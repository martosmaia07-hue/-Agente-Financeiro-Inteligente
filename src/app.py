import os
import json
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

################### CONFIGURAÇÃO ########################
OLLAMA_BASE = "http://localhost:11434"
OLLAMA_URL = f"{OLLAMA_BASE}/api/generate"
MODELO = "llama3.2"

################### PROMPTS (MODO GUARDIÃO) ####################
SYSTEM_FINANCAS = """Você é o San, um educador financeiro amigável e didático.

OBJETIVO:
Ensinar conceitos de finanças pessoais de forma simples, usando os dados do cliente como exemplo prático.

REGRAS:
- NÃO recomendar investimentos específicos; apenas explique como funcionam e ajude na organização;
- Use os dados fornecidos para dar exemplos personalizados;
- Linguagem simples, como se explicasse para um amigo;
- Se não souber algo, diga: "Não tenho essa informação, mas posso explicar...";
- No máximo 3 parágrafos e sempre pergunte se o cliente entendeu.
"""

SYSTEM_GUARDIAO = """Você é o San no modo GUARDIÃO (anti-golpe) de um banco.

OBJETIVO:
Proteger o cliente contra golpes e transações suspeitas usando histórico e transações recentes.

REGRAS:
- Foque em identificar sinais de golpe (Pix noturno, favorecido novo, "taxa de liberação", pedidos de códigos/senhas).
- Nunca peça senha, token, códigos de verificação, foto de documento ou dados sensíveis.
- Se detectar alto risco, oriente ações seguras: validar no app oficial, limitar Pix, bloquear, contatar canal oficial.
- Seja direto: 1) risco, 2) por quê, 3) o que fazer agora.
- No máximo 3 parágrafos e pergunte se o cliente quer seguir com as ações recomendadas.
"""

SYSTEM_AUTOPILOTO = """Você é o San no modo AUTOPILOTO financeiro.

OBJETIVO:
Ajudar o cliente a organizar orçamento, prever saldo, reduzir juros/rotativo e montar reserva.

REGRAS:
- Use as transações para achar padrões (recorrências, gastos altos, cartão/juros, assinaturas).
- Proponha regras e planos simples (teto de gasto, checklist semanal, meta mensal de reserva).
- Não recomende investimentos específicos; foque em hábitos e planejamento.
- No máximo 3 parágrafos e pergunte se o plano faz sentido.
"""

AGENTES = {
    "guardiao": {"nome": "🛡️ Guardião", "system": SYSTEM_GUARDIAO},
    "financas": {"nome": "📚 Finanças", "system": SYSTEM_FINANCAS},
    "autopiloto": {"nome": "🧭 Autopiloto", "system": SYSTEM_AUTOPILOTO},
}


################### DADOS (PASTAS MOCK) ##################


BASE_DATA = Path(os.getenv(
    "BIA_DATA_DIR",
    r"D:\Pessoal\Secular\Machine Learning\protótipo_bia\dio-lab-bia-do-futuro\data"
))
if not BASE_DATA.exists():
    BASE_DATA = BASE_DATA / "dados_sinteticos"  # fallback


CENARIOS = {
    "guardiao": BASE_DATA / "cenario_guardiao" / "data",
    "autopiloto": BASE_DATA / "cenario_autopiloto" / "data",
    "misto": BASE_DATA / "cenario_misto" / "data",
}

#################### FUNÇÕES AUXILIARES ####################
def _ler_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(show_spinner=False)
def carregar_contexto(data_dir_str: str) -> str:
    """
    Cache com argumento simples (str) pra evitar qualquer treta de hash/Path entre versões.
    """
    data_dir = Path(data_dir_str)

    perfil = _ler_json(data_dir / "perfil_investidor.json")
    transacoes = pd.read_csv(data_dir / "transacoes.csv")
    historico = pd.read_csv(data_dir / "historico_atendimento.csv")
    produtos = _ler_json(data_dir / "produtos_financeiros.json")

    transacoes_rec = transacoes.tail(40)
    historico_rec = historico.tail(15)

    prod_resumo = [
        {"nome": p.get("nome"), "categoria": p.get("categoria"), "risco": p.get("risco")}
        for p in (produtos[:30] if isinstance(produtos, list) else [])
    ]

    contexto = f"""
CLIENTE: {perfil.get("nome", "N/A")}, {perfil.get("idade", "N/A")} anos, perfil {perfil.get("perfil_investidor", "N/A")}
OBJETIVO: {perfil.get("objetivo_principal", "N/A")}
PATRIMÔNIO: R${perfil.get("patrimonio_total", "N/A")} | RESERVA: R${perfil.get("reserva_emergencia_atual", "N/A")}

TRANSAÇÕES (últimas 40):
{transacoes_rec.to_string(index=False)}

ATENDIMENTOS (últimos 15):
{historico_rec.to_string(index=False)}

PRODUTOS (resumo):
{json.dumps(prod_resumo, ensure_ascii=False)}
""".strip()
    return contexto

def rotear_agente(msg: str) -> str:
    m = (msg or "").lower()

    if "@guardiao" in m:
        return "guardiao"
    if "@financas" in m:
        return "financas"
    if "@autopiloto" in m:
        return "autopiloto"

    palavras_guardiao = [
        "golpe", "fraude", "phishing", "pix", "não reconheço", "taxa", "liberação",
        "suporte", "ligação", "sms", "whatsapp", "conta invadida", "invadida",
        "suspeita", "suspeito", "bloquear", "bloqueio", "limite pix", "token", "código", "senha"
    ]
    if any(p in m for p in palavras_guardiao):
        return "guardiao"

    palavras_financas = [
        "o que é", "explica", "conceito", "entender", "como funciona", "cdi", "selic",
        "inflação", "juros", "juros compostos", "ipca", "renda fixa", "tesouro", "cdb","investimento"
    ]
    if any(p in m for p in palavras_financas):
        return "financas"

    palavras_autopiloto = [
        "orçamento", "planejar", "planejamento", "gastos", "economizar", "sobrou", "faltou",
        "cartão", "rotativo", "parcelado", "assinatura", "meta", "reserva", "controle", "organizar"
    ]
    if any(p in m for p in palavras_autopiloto):
        return "autopiloto"

    return "financas"


def montar_prompt(pergunta: str, data_dir: Path, agente_key: str) -> str:
    contexto = carregar_contexto(str(data_dir))
    system = AGENTES[agente_key]["system"]

    return f"""{system}

CONTEXTO DO CLIENTE:
{contexto}

Pergunta: {pergunta}
"""

def _parse_ndjson_line(line):
    if isinstance(line, (bytes, bytearray)):
        line = line.decode("utf-8", errors="ignore")

    line = line.strip()
    if not line:
        return None

    if line.startswith("data:"):
        line = line[len("data:"):].strip()

    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def chamar_ollama_stream(prompt: str):
    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": True,
        "keep_alive": "0",
        "options": {
            "num_predict": 220,
            "temperature": 0.2,
            "num_ctx": 4096
        }
    }

    with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=600) as r:
        if r.status_code != 200:
            raise RuntimeError(f"Ollama HTTP {r.status_code}: {r.text}")

        for raw in r.iter_lines(decode_unicode=False):
            if not raw:
                continue
            data = _parse_ndjson_line(raw)
            if not data:
                continue
            
            if "error" in data:
                raise RuntimeError(f"Ollama error: {data['error']}")

            yield data.get("response", "")

            if data.get("done"):
                break

######################## LangGraph ########################
def chamar_ollama_once(prompt: str) -> str:
    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "10m",
        "options": {
            "num_predict": 200,
            "temperature": 0.2,
            "num_ctx": 2048
        }
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=600)
    if r.status_code != 200:
        raise RuntimeError(f"Ollama HTTP {r.status_code}: {r.text}")
    data = r.json()
    return data.get("response", "")

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

AGENTES = {
    "guardiao": {"system": SYSTEM_GUARDIAO},
    "financas": {"system": SYSTEM_FINANCAS},
    "autopiloto": {"system": SYSTEM_AUTOPILOTO},
}

class ChatState(TypedDict):
    pergunta: str
    data_dir: str
    agente: Optional[str]
    prompt: Optional[str]
    resposta: Optional[str]

def router_node(state: ChatState) -> ChatState:
    agente = rotear_agente(state["pergunta"]) 
    state["agente"] = agente
    return state

def build_prompt_node(state: ChatState) -> ChatState:
    contexto = carregar_contexto(state["data_dir"])
    agente = state["agente"] or "financas"
    system = AGENTES[agente]["system"]

    if agente == "financas":
        contexto_filtrado = contexto.split("TRANSAÇÕES")[0].strip()
    elif agente == "guardiao":
        contexto_filtrado = contexto.split("PRODUTOS")[0].strip()
    else:
        contexto_filtrado = contexto.split("ATENDIMENTOS")[0].strip()

    state["prompt"] = f"""{system}

CONTEXTO DO CLIENTE:
{contexto_filtrado}

Pergunta: {state["pergunta"]}
"""
    return state

def llm_node(state: ChatState) -> ChatState:
    state["resposta"] = chamar_ollama_once(state["prompt"] or "")
    return state

def checker_node(state: ChatState) -> ChatState:
    """
    Checker bem simples e rápido:
    - garante até 3 parágrafos
    - remove qualquer pedido de senha/código/token (se o modelo vacilar)
    """
    resp = (state.get("resposta") or "").strip()

    paras = [p.strip() for p in resp.split("\n\n") if p.strip()]
    resp = "\n\n".join(paras[:3])

    proibidos = ["senha", "token", "código", "codigo", "sms", "verificação", "verificacao"]
    if any(w in resp.lower() for w in proibidos):
        resp += "\n\nObs.: Não compartilhe senha, token ou códigos de verificação com ninguém."
    state["resposta"] = resp
    return state

def build_graph():
    g = StateGraph(ChatState)
    g.add_node("router", router_node)
    g.add_node("build_prompt", build_prompt_node)
    g.add_node("llm", llm_node)
    g.add_node("checker", checker_node)

    g.set_entry_point("router")
    g.add_edge("router", "build_prompt")
    g.add_edge("build_prompt", "llm")
    g.add_edge("llm", "checker")
    g.add_edge("checker", END)
    return g.compile()

GRAPH = build_graph()

def responder(pergunta: str, data_dir: Path):
    out = GRAPH.invoke({"pergunta": pergunta, "data_dir": str(data_dir), "agente": None, "prompt": None, "resposta": None})
    return out["resposta"], out["agente"]


######################### INTERFACE #######################
st.set_page_config(page_title="San Guardião", page_icon="🛡️")

st.title("🛡️ San, agente Guardião (rápido)")

dataset_override = st.sidebar.selectbox(
    "Dataset (para teste)",
    ["guardiao", "autopiloto", "misto"],
    index=0
)

data_dir = CENARIOS[dataset_override]
st.sidebar.write("data_dir =", str(data_dir))
st.sidebar.write("existe?", data_dir.exists())
if not data_dir.exists():
    st.error(f"Não achei a pasta do dataset: {data_dir}")
    st.stop()

st.sidebar.caption(f"Lendo dados de: {data_dir}")

col1, col2 = st.sidebar.columns(2)
if col1.button("🧹 Limpar conversa"):
    st.session_state.pop("messages", None)
if col2.button("♻️ Limpar cache"):
    st.cache_data.clear()

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

pergunta = st.chat_input("Manda tua dúvida sobre segurança / golpes...")
if pergunta:
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.write(pergunta)

    resposta, agente_key = responder(pergunta, data_dir)
    agente_nome = {"guardiao":"🛡️ Guardião","financas":"📚 Finanças","autopiloto":"🧭 Autopiloto"}.get(agente_key, agente_key)

    with st.chat_message("assistant"):
        st.caption(f"Atendendo com: {agente_nome}")
        st.markdown(resposta)

    st.session_state.messages.append({"role": "assistant", "content": resposta})

