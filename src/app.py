"""
IR Smart - Assistente Tributário Inteligente.

Interface Streamlit principal do aplicativo.
"""

import sys
from datetime import date, datetime
from pathlib import Path

import streamlit as st
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import DatabaseManager, Operacao, get_database
from src.motor_calculo import DadosOperacao, get_motor_calculo
from src.chatgpt_client import get_gpt_client
from src.validacao import get_validador, NivelConfianca
from src.cache import get_cache
from src.utils import (
    formatar_moeda,
    formatar_percentual,
    formatar_data,
    extrair_dados_operacao,
    gerar_id_sessao
)

logger.add(
    "logs/ir_smart_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO"
)

st.set_page_config(
    page_title="IR Smart - Assistente Tributário",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

PRIMARY_COLOR = "#10b981"
PRIMARY_LIGHT = "#34d399"
PRIMARY_DARK = "#059669"
BG_DARK = "#0f172a"
BG_CARD = "#1e293b"
TEXT_PRIMARY = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"

CUSTOM_CSS = """
<style>
    /* ========== TEMA ESCURO PROFISSIONAL ========== */
    
    /* Fundo principal escuro */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    }
    
    /* Texto geral da área principal */
    .main .stMarkdown p,
    .main .stMarkdown span,
    .main .stMarkdown li {
        color: #e2e8f0 !important;
    }
    
    .main .stMarkdown h1,
    .main .stMarkdown h2,
    .main .stMarkdown h3 {
        color: #10b981 !important;
    }
    
    /* Labels de inputs */
    .main label,
    .main .stTextInput label,
    .main .stSelectbox label,
    .main .stNumberInput label,
    .main .stDateInput label,
    .main .stCheckbox label,
    .main .stRadio label {
        color: #cbd5e1 !important;
    }
    
    /* Labels dentro de formulários */
    .stForm label,
    .stForm .stTextInput label,
    .stForm .stSelectbox label,
    .stForm .stNumberInput label,
    .stForm .stDateInput label,
    .stForm .stCheckbox label span,
    .stForm p {
        color: #cbd5e1 !important;
    }
    
    /* Títulos na área principal */
    .main h1, .main h2, .main h3, .main h4,
    .main [data-testid="stMarkdownContainer"] h1,
    .main [data-testid="stMarkdownContainer"] h2,
    .main [data-testid="stMarkdownContainer"] h3,
    .main [data-testid="stMarkdownContainer"] h4,
    section[data-testid="stMain"] h1,
    section[data-testid="stMain"] h2,
    section[data-testid="stMain"] h3,
    section[data-testid="stMain"] h4 {
        color: #10b981 !important;
    }
    
    /* Expander header com texto visível */
    .streamlit-expanderHeader p,
    .streamlit-expanderHeader span,
    [data-testid="stExpander"] summary span {
        color: #e2e8f0 !important;
    }
    
    /* Texto dentro de dataframes/tabelas */
    .main .stDataFrame,
    .main table,
    .main th,
    .main td {
        color: #e2e8f0 !important;
    }
    
    /* Caption e textos pequenos */
    .main .stCaption,
    .main small,
    .main figcaption {
        color: #94a3b8 !important;
    }
    
    /* Header com degradê */
    .app-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #1e293b 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #334155;
    }
    
    /* ========== SIDEBAR ESCURA ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #10b981 !important;
    }
    
    [data-testid="stSidebar"] p {
        color: #cbd5e1 !important;
    }
    
    [data-testid="stSidebar"] .stMetric label {
        color: #94a3b8 !important;
    }
    
    [data-testid="stSidebar"] .stMetric [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
    }
    
    [data-testid="stSidebar"] .stMetric [data-testid="stMetricDelta"] {
        color: #10b981 !important;
    }
    
    /* Alertas na Sidebar */
    [data-testid="stSidebar"] .stSuccess,
    [data-testid="stSidebar"] .stError,
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid #334155 !important;
    }
    
    [data-testid="stSidebar"] .stSuccess p,
    [data-testid="stSidebar"] .stSuccess span,
    [data-testid="stSidebar"] .stError p,
    [data-testid="stSidebar"] .stError span,
    [data-testid="stSidebar"] [data-testid="stAlert"] p,
    [data-testid="stSidebar"] [data-testid="stAlert"] span {
        color: #f1f5f9 !important;
        font-weight: bold !important;
    }
    
    /* Caption na Sidebar */
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] span {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
    }
    
    /* ========== INPUTS - TEMA ESCURO ========== */
    
    /* Remove bordas e sombras dos containers */
    .stTextInput > div,
    .stTextInput > div > div,
    .stNumberInput > div,
    .stNumberInput > div > div,
    .stDateInput > div,
    .stDateInput > div > div,
    .stSelectbox > div,
    .stSelectbox > div > div {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        background: transparent !important;
    }
    
    /* Text Input */
    .stTextInput input {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #f1f5f9 !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Number Input */
    .stNumberInput input {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #f1f5f9 !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Date Input */
    .stDateInput input {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #f1f5f9 !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Select Box */
    .stSelectbox [data-baseweb="select"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        border: none !important;
    }
    
    /* Focus state */
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stDateInput input:focus,
    .stSelectbox [data-baseweb="select"]:focus-within {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 1px #10b981 !important;
    }
    
    /* Botões + e - do Number Input */
    .stNumberInput button {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    .stNumberInput button:hover {
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%) !important;
    }
    
    /* Dropdown do Select */
    [data-baseweb="popover"] [data-baseweb="menu"],
    [data-baseweb="popover"] ul {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
    }
    
    [data-baseweb="popover"] li,
    [data-baseweb="popover"] [role="option"] {
        color: #f1f5f9 !important;
        background-color: #1e293b !important;
    }
    
    [data-baseweb="popover"] li:hover,
    [data-baseweb="popover"] [role="option"]:hover {
        background-color: #334155 !important;
    }
    
    /* Checkbox */
    .stCheckbox label span,
    .stCheckbox span {
        color: #cbd5e1 !important;
    }
    
    /* Chat Input */
    .stChatInput > div {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 25px !important;
    }
    
    .stChatInput > div:focus-within {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 1px #10b981 !important;
    }
    
    .stChatInput textarea,
    .stChatInput input {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
    }
    
    /* Inputs dentro de forms */
    .stForm input,
    .stForm textarea,
    .stForm select {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
    }
    
    /* ========== BOTÕES ========== */
    .stButton > button,
    .stForm .stButton > button,
    button[kind="secondary"],
    button[kind="primary"],
    .stForm button {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        font-weight: bold !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
        opacity: 1 !important;
    }
    
    /* Texto dos botões */
    .stButton > button span,
    .stButton > button p,
    .stButton > button div,
    .stForm .stButton > button span,
    .stForm .stButton > button p,
    .stForm button span,
    .stForm button p,
    [data-testid="stForm"] button span,
    [data-testid="stForm"] button p {
        color: white !important;
    }
    
    .stButton > button:hover,
    .stForm .stButton > button:hover,
    .stForm button:hover {
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4) !important;
    }
    
    /* Botões do formulário específicos */
    [data-testid="stForm"] button,
    [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%) !important;
        color: white !important;
        border: none !important;
        opacity: 1 !important;
    }
    
    /* ========== MÉTRICAS ========== */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: bold !important;
    }
    
    /* ========== ALERTAS ========== */
    .stSuccess {
        background-color: rgba(16, 185, 129, 0.15) !important;
        border-left: 4px solid #10b981 !important;
    }
    
    .stWarning {
        background-color: rgba(245, 158, 11, 0.15) !important;
        border-left: 4px solid #f59e0b !important;
    }
    
    .stError {
        background-color: rgba(239, 68, 68, 0.15) !important;
        border-left: 4px solid #ef4444 !important;
    }
    
    .stInfo {
        background-color: rgba(59, 130, 246, 0.15) !important;
        border-left: 4px solid #3b82f6 !important;
    }
    
    /* ========== CHAT MESSAGES ========== */
    [data-testid="stChatMessage"] {
        background-color: #1e293b !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin: 10px 0 !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2) !important;
        border: 1px solid #334155 !important;
    }
    
    /* Texto das mensagens do chat */
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] .stMarkdown,
    [data-testid="stChatMessage"] .stMarkdown p,
    [data-testid="stChatMessage"] .stMarkdown span {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stChatMessage"] strong,
    [data-testid="stChatMessage"] b {
        color: #f1f5f9 !important;
    }
    
    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3,
    [data-testid="stChatMessage"] h4 {
        color: #10b981 !important;
    }
    
    /* Mensagem do assistente */
    [data-testid="stChatMessage"][data-testid*="assistant"] {
        border-left: 4px solid #10b981 !important;
    }
    
    /* ========== PROGRESS BAR ========== */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #10b981 0%, #34d399 100%) !important;
    }
    
    /* ========== DIVIDERS ========== */
    .app-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #334155, transparent);
        margin: 15px 0;
    }
    
    /* ========== FORMS ========== */
    .stForm {
        background-color: #1e293b !important;
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
        border: 1px solid #334155 !important;
    }
    
    /* ========== EXPANDER ========== */
    .streamlit-expanderHeader {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }
    
    /* Texto do expander visível */
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary:hover,
    [data-testid="stExpander"] summary:hover span,
    [data-testid="stExpander"] summary:hover p,
    [data-testid="stExpander"] summary:focus,
    [data-testid="stExpander"] summary:focus span,
    [data-testid="stExpander"] > div:first-child,
    [data-testid="stExpander"] > div:first-child span,
    [data-testid="stExpander"] > div:first-child p,
    .streamlit-expanderHeader,
    .streamlit-expanderHeader span,
    .streamlit-expanderHeader p,
    .streamlit-expanderHeader:hover,
    .streamlit-expanderHeader:hover span {
        color: #e2e8f0 !important;
        background-color: #1e293b !important;
    }
    
    /* Força cor do texto no expander header */
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"],
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] * {
        color: #e2e8f0 !important;
    }
    
    /* Conteúdo dentro do expander */
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stExpander"] .stWrite,
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stExpander"] div {
        color: #e2e8f0 !important;
    }
    
    /* Info/Alert box texto visível */
    .stAlert p,
    .stAlert span,
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span {
        color: #e2e8f0 !important;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state():
    """Inicializa o estado da sessão."""
    if "sessao_id" not in st.session_state:
        st.session_state.sessao_id = gerar_id_sessao()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "db" not in st.session_state:
        st.session_state.db = get_database()
    
    if "motor" not in st.session_state:
        st.session_state.motor = get_motor_calculo()
    
    if "gpt" not in st.session_state:
        st.session_state.gpt = get_gpt_client()
    
    if "validador" not in st.session_state:
        st.session_state.validador = get_validador()
    
    if "total_vendas_mes" not in st.session_state:
        hoje = date.today()
        st.session_state.total_vendas_mes = st.session_state.db.obter_vendas_mes(
            hoje.year, hoje.month
        )


def render_sidebar():
    """Renderiza a barra lateral com informações e controles."""
    import base64
    
    with st.sidebar:
        logo_path = Path("assets/logo.png")
        if logo_path.exists():
            logo_base64 = base64.b64encode(logo_path.read_bytes()).decode()
            st.markdown(f"""
                <div style="
                    display: flex; 
                    align-items: center; 
                    gap: 12px; 
                    padding: 10px 0;
                    margin-bottom: 5px;
                ">
                    <img src="data:image/png;base64,{logo_base64}" width="45" height="45" 
                         style="object-fit: contain;">
                    <div>
                        <p style="font-size: 1.3rem; font-weight: bold; margin: 0; line-height: 1.2;">
                            <span style="color: #ffffff;">IR</span> <span style="color: #10b981;">Smart</span>
                        </p>
                        <p style="color: #94a3b8; font-size: 0.75rem; margin: 0;">
                            Assistente Tributário
                        </p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="
                    display: flex; 
                    align-items: center; 
                    gap: 12px; 
                    padding: 10px 0;
                    margin-bottom: 5px;
                ">
                    <span style="font-size: 2.2rem;">💹</span>
                    <div>
                        <p style="font-size: 1.3rem; font-weight: bold; margin: 0; line-height: 1.2;">
                            <span style="color: #ffffff;">IR</span> <span style="color: #10b981;">Smart</span>
                        </p>
                        <p style="color: #94a3b8; font-size: 0.75rem; margin: 0;">
                            Assistente Tributário
                        </p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="app-divider"></div>', unsafe_allow_html=True)

        st.markdown("### 📊 Resumo do Mês")
        
        hoje = date.today()
        total_vendas = st.session_state.db.obter_vendas_mes(hoje.year, hoje.month)
        limite_isencao = 20000.00
        margem = max(0, limite_isencao - total_vendas)
        percentual_usado = min(100, (total_vendas / limite_isencao) * 100)
        
        st.metric(
            label="Total Vendido",
            value=formatar_moeda(total_vendas),
            delta=f"Margem: {formatar_moeda(margem)}"
        )
        
        if total_vendas <= limite_isencao:
            st.success(f"✅ Status: ISENTO")
        else:
            st.error(f"❌ Status: TRIBUTÁVEL")
        
        st.progress(percentual_usado / 100)
        st.caption(f"{percentual_usado:.1f}% do limite de isenção")
        
        st.markdown("---")
        
        st.markdown("### 📉 Prejuízos Acumulados")
        
        prejuizo_swing = st.session_state.db.obter_prejuizo_acumulado("SWING_TRADE")
        prejuizo_day = st.session_state.db.obter_prejuizo_acumulado("DAY_TRADE")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Swing Trade", formatar_moeda(prejuizo_swing))
        with col2:
            st.metric("Day Trade", formatar_moeda(prejuizo_day))
        
        st.markdown("---")
        
        st.markdown("### ⚙️ Ações")
        
        if st.button("📝 Registrar Operação", use_container_width=True):
            st.session_state.show_operacao_form = True
        
        if st.button("📊 Ver Histórico", use_container_width=True):
            st.session_state.show_historico = True
        
        if st.button("🗑️ Limpar Conversa", use_container_width=True):
            st.session_state.messages = []
            st.session_state.gpt.limpar_historico()
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📦 Cache de Respostas")
        
        cache = get_cache()
        stats = cache.obter_estatisticas()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Itens", stats['total_itens'])
        with col2:
            st.metric("Hits", stats['total_hits'])
        
        if stats['total_hits'] > 0:
            st.caption(f"💰 Economia estimada: ${stats['economia_estimada']:.3f}")
        
        st.markdown("---")
        
        st.markdown("### ℹ️ Informações")
        st.caption(f"Sessão: {st.session_state.sessao_id}")
        st.caption(f"Data: {formatar_data(hoje)}")
        st.markdown("""
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #334155;">
                <p style="font-size: 0.75rem; margin: 0;">
                    <span style="color: #ffffff;">IR</span> <span style="color: #10b981;">Smart</span> 
                    <span style="color: #94a3b8;">v1.0.0</span>
                </p>
                <p style="color: #94a3b8; font-size: 0.7rem; margin: 0;">© 2026 Gleison Mota</p>
            </div>
        """, unsafe_allow_html=True)


def render_operacao_form():
    """Renderiza o formulário de registro de operação."""
    st.markdown("### 📝 Registrar Nova Operação")
    
    with st.form("form_operacao"):
        col1, col2 = st.columns(2)
        
        with col1:
            ticker = st.text_input(
                "Ticker",
                placeholder="Ex: PETR4",
                max_chars=6
            ).upper()
            
            tipo = st.selectbox(
                "Tipo de Operação",
                options=["COMPRA", "VENDA"]
            )
            
            quantidade = st.number_input(
                "Quantidade",
                min_value=1,
                value=100,
                step=1
            )
        
        with col2:
            preco_unitario = st.number_input(
                "Preço Unitário (R$)",
                min_value=0.01,
                value=30.00,
                step=0.01,
                format="%.2f"
            )
            
            data_operacao = st.date_input(
                "Data da Operação",
                value=date.today(),
                max_value=date.today()
            )
            
            is_day_trade = st.checkbox("É Day Trade?")
        
        valor_total = quantidade * preco_unitario
        st.info(f"💵 Valor Total: {formatar_moeda(valor_total)}")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            submitted = st.form_submit_button(
                "✅ Registrar",
                use_container_width=True
            )
        
        with col_btn2:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                st.session_state.show_operacao_form = False
                st.rerun()
        
        if submitted:
            if not ticker or len(ticker) < 4:
                st.error("⚠️ Ticker inválido!")
            else:
                operacao = Operacao(
                    data=data_operacao,
                    ticker=ticker,
                    tipo=tipo,
                    quantidade=quantidade,
                    preco_unitario=preco_unitario,
                    valor_total=valor_total,
                    is_day_trade=is_day_trade
                )
                
                try:
                    operacao_id = st.session_state.db.inserir_operacao(operacao)
                    st.success(f"✅ Operação registrada com sucesso! (ID: {operacao_id})")
                    
                    if tipo == "VENDA":
                        preco_medio_info = st.session_state.db.obter_preco_medio(ticker)
                        preco_compra = preco_medio_info['preco_medio'] if preco_medio_info else preco_unitario * 0.9
                        
                        dados_calculo = DadosOperacao(
                            ticker=ticker,
                            quantidade=quantidade,
                            preco_venda=preco_unitario,
                            preco_compra=preco_compra,
                            data_compra=date(2020, 1, 1) if not is_day_trade else data_operacao,
                            data_venda=data_operacao
                        )
                        
                        hoje = date.today()
                        vendas_anteriores = st.session_state.db.obter_vendas_mes(
                            hoje.year, hoje.month
                        ) - valor_total
                        
                        resultado = st.session_state.motor.calcular_ir(
                            dados_calculo,
                            total_vendas_mes_anterior=vendas_anteriores
                        )
                        
                        st.markdown("---")
                        st.markdown("### 📊 Resultado do Cálculo")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Lucro/Prejuízo", formatar_moeda(resultado.lucro_bruto))
                        with col2:
                            st.metric("Tipo", resultado.tipo_operacao.value.replace("_", " "))
                        with col3:
                            if resultado.isento:
                                st.metric("IR Devido", "ISENTO ✅")
                            else:
                                st.metric("IR Devido", formatar_moeda(resultado.ir_devido))
                        
                        st.info(resultado.mensagem)
                        
                        for alerta in resultado.alertas:
                            st.warning(alerta)
                    
                    st.session_state.show_operacao_form = False
                    
                except Exception as e:
                    st.error(f"❌ Erro ao registrar operação: {e}")
                    logger.error(f"Erro ao registrar operação: {e}")


def render_historico():
    """Renderiza o histórico de operações."""
    st.markdown("### 📊 Histórico de Operações")
    
    hoje = date.today()
    operacoes = st.session_state.db.obter_operacoes_mes(hoje.year, hoje.month)
    
    if not operacoes:
        st.info("📭 Nenhuma operação registrada este mês.")
    else:
        for op in reversed(operacoes):
            emoji = "🔴" if op['tipo'] == "VENDA" else "🟢"
            day_trade = "⚡ Day Trade" if op.get('is_day_trade') else ""
            
            with st.expander(
                f"{emoji} {op['data']} | {op['tipo']} {op['quantidade']}x {op['ticker']} {day_trade}"
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Preço:** {formatar_moeda(op['preco_unitario'])}")
                    st.write(f"**Quantidade:** {op['quantidade']}")
                with col2:
                    st.write(f"**Valor Total:** {formatar_moeda(op['valor_total'])}")
                    st.write(f"**Data:** {op['data']}")
    
    if st.button("⬅️ Voltar", use_container_width=True):
        st.session_state.show_historico = False
        st.rerun()


def processar_mensagem(mensagem: str) -> str:
    """
    Processa uma mensagem do usuário e retorna a resposta.
    
    Args:
        mensagem: Mensagem do usuário.
        
    Returns:
        Resposta do assistente.
    """
    validacao_escopo = st.session_state.validador.verificar_escopo(mensagem)
    
    if not validacao_escopo.valido:
        return validacao_escopo.mensagem
    
    dados_extraidos = extrair_dados_operacao(mensagem)
    
    hoje = date.today()
    total_vendas = st.session_state.db.obter_vendas_mes(hoje.year, hoje.month)
    prejuizo_swing = st.session_state.db.obter_prejuizo_acumulado("SWING_TRADE")
    prejuizo_day = st.session_state.db.obter_prejuizo_acumulado("DAY_TRADE")
    
    contexto = st.session_state.gpt.montar_contexto_usuario(
        total_vendas_mes=total_vendas,
        prejuizo_swing=prejuizo_swing,
        prejuizo_day_trade=prejuizo_day
    )
    
    tem_dados_calculo = False
    
    if dados_extraidos.get('tipo') == 'VENDA' and dados_extraidos.get('ticker') and dados_extraidos.get('quantidade') and dados_extraidos.get('preco'):
        tem_dados_calculo = True
        preco_medio_info = st.session_state.db.obter_preco_medio(dados_extraidos['ticker'])
        preco_compra = preco_medio_info['preco_medio'] if preco_medio_info else dados_extraidos['preco'] * 0.9
        
        dados_calculo = DadosOperacao(
            ticker=dados_extraidos['ticker'],
            quantidade=dados_extraidos['quantidade'],
            preco_venda=dados_extraidos['preco'],
            preco_compra=preco_compra,
            data_compra=date(2020, 1, 1),
            data_venda=hoje
        )
        
        resultado = st.session_state.motor.calcular_ir(
            dados_calculo,
            total_vendas_mes_anterior=total_vendas
        )
        
        resultado_dict = {
            'ticker': resultado.ticker,
            'quantidade': resultado.quantidade,
            'preco_compra': resultado.preco_compra,
            'preco_venda': resultado.preco_venda,
            'valor_venda': resultado.valor_venda,
            'lucro_bruto': resultado.lucro_bruto,
            'tipo_operacao': resultado.tipo_operacao.value,
            'aliquota': resultado.aliquota,
            'total_vendas_mes': resultado.total_vendas_mes,
            'isento': resultado.isento,
            'prejuizo_compensado': resultado.prejuizo_compensado,
            'base_calculo': resultado.base_calculo,
            'ir_devido': resultado.ir_devido
        }
        
        validacoes = st.session_state.validador.validar_resultado_completo(resultado_dict)
        nivel_confianca = st.session_state.validador.obter_nivel_confianca_geral(validacoes)
        
        contexto_calculo = st.session_state.gpt.montar_contexto_calculo(resultado_dict)
        contexto += "\n" + contexto_calculo
        
        if nivel_confianca != NivelConfianca.ALTA:
            contexto += "\n⚠️ AVISO: Verificar resultado - confiança não máxima."
    
    if tem_dados_calculo:
        resposta = st.session_state.gpt.enviar_mensagem(mensagem, contexto, usar_cache=False)
    else:
        resposta = st.session_state.gpt.enviar_mensagem(mensagem, contexto, usar_cache=True)
    
    st.session_state.db.salvar_mensagem_conversa(
        st.session_state.sessao_id,
        "user",
        mensagem
    )
    st.session_state.db.salvar_mensagem_conversa(
        st.session_state.sessao_id,
        "assistant",
        resposta
    )
    
    return resposta


def render_chat():
    """Renderiza a interface de chat."""
    import base64
    
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        logo_base64 = base64.b64encode(logo_path.read_bytes()).decode()
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #1e293b 100%);
                padding: 30px 20px;
                border-radius: 15px;
                margin-bottom: 25px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
                border: 1px solid #334155;
            ">
                <div style="display: flex; align-items: center; justify-content: center; gap: 20px;">
                    <img src="data:image/png;base64,{logo_base64}" width="80" height="80" 
                         style="object-fit: contain;">
                    <span style="font-size: 2.8rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                        <span style="color: #ffffff;">IR</span> <span style="color: #10b981;">Smart</span>
                    </span>
                </div>
                <p style="color: #cbd5e1; font-size: 1.15rem; margin-top: 15px; text-align: center;">
                    Seu assistente inteligente para cálculo de Imposto de Renda sobre ações
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #1e293b 100%);
                padding: 30px 20px;
                border-radius: 15px;
                margin-bottom: 25px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
                border: 1px solid #334155;
            ">
                <div style="display: flex; align-items: center; justify-content: center; gap: 20px;">
                    <span style="font-size: 3.5rem;">💹</span>
                    <span style="font-size: 2.8rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                        <span style="color: #ffffff;">IR</span> <span style="color: #10b981;">Smart</span>
                    </span>
                </div>
                <p style="color: #cbd5e1; font-size: 1.15rem; margin-top: 15px; text-align: center;">
                    Seu assistente inteligente para cálculo de Imposto de Renda sobre ações
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "Olá! 👋 Sou o **IR Smart**, seu assistente inteligente para cálculo de impostos sobre ações.\n\n"
                "Posso te ajudar com:\n"
                "- 📊 **Cálculo de IR** sobre vendas de ações\n"
                "- 💰 **Verificação de isenção** mensal (R$ 20.000)\n"
                "- 📉 **Compensação de prejuízos**\n"
                "- 📝 **Geração de DARF**\n"
                "- ❓ **Dúvidas** sobre regras tributárias\n\n"
                "Como posso te ajudar hoje?"
            )
        })
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Digite sua mensagem..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Processando..."):
                resposta = processar_mensagem(prompt)
                st.markdown(resposta)
        
        st.session_state.messages.append({"role": "assistant", "content": resposta})


def main():
    """Função principal do aplicativo."""
    init_session_state()
    
    render_sidebar()
    
    if st.session_state.get("show_operacao_form", False):
        render_operacao_form()
    elif st.session_state.get("show_historico", False):
        render_historico()
    else:
        render_chat()


if __name__ == "__main__":
    main()
