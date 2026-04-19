import os
import json
import pandas as pd
import requests
import streamlit as st

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "gpt-oss:120b-cloud"

# =============== CAMINHOS =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "data"))

print("BASE_DIR:", BASE_DIR)
print("DATA_DIR:", DATA_DIR)

# =============== CARREGA DADOS =====================
transacoes_pj = pd.read_csv(os.path.join(DATA_DIR, "transacoes_pj.csv"))
contas_pagar = pd.read_csv(os.path.join(DATA_DIR, "contas_pagar.csv"))
contas_receber = pd.read_csv(os.path.join(DATA_DIR, "contas_receber.csv"))
historico_atendimento = pd.read_csv(os.path.join(DATA_DIR, "historico_atendimento.csv"))
historico_interacoes = pd.read_csv(os.path.join(DATA_DIR, "historico_interacoes.csv"))
transacoes = pd.read_csv(os.path.join(DATA_DIR, "transacoes.csv"))

with open(os.path.join(DATA_DIR, "clientes_pj.json"), "r", encoding="utf-8") as f:
    clientes_pj = json.load(f)

with open(os.path.join(DATA_DIR, "contas_pj.json"), "r", encoding="utf-8") as f:
    contas_pj = json.load(f)

with open(os.path.join(DATA_DIR, "indicadores_caixa.json"), "r", encoding="utf-8") as f:
    indicadores_caixa = json.load(f)

with open(os.path.join(DATA_DIR, "metas_financeiras.json"), "r", encoding="utf-8") as f:
    metas_financeiras = json.load(f)

with open(os.path.join(DATA_DIR, "perfil_investidor.json"), "r", encoding="utf-8") as f:
    perfil_investidor = json.load(f)

with open(os.path.join(DATA_DIR, "produtos_bancarios_pj.json"), "r", encoding="utf-8") as f:
    produtos_bancarios_pj = json.load(f)

with open(os.path.join(DATA_DIR, "produtos_financeiros.json"), "r", encoding="utf-8") as f:
    produtos_financeiros = json.load(f)

with open(os.path.join(DATA_DIR, "regras_alertas.json"), "r", encoding="utf-8") as f:
    regras_alertas = json.load(f)


# ================== MONTAR CONTEXTO COMPLETO =========================
def montar_contexto(cliente_id: str) -> str:
    cliente = next((item for item in clientes_pj if item["cliente_id"] == cliente_id), None)
    conta = next((item for item in contas_pj if item["cliente_id"] == cliente_id), None)
    indicador = next((item for item in indicadores_caixa if item["cliente_id"] == cliente_id), None)
    meta = next((item for item in metas_financeiras if item["cliente_id"] == cliente_id), None)

    perfil_cliente = None
    if isinstance(perfil_investidor, list):
        perfil_cliente = next((item for item in perfil_investidor if item.get("cliente_id") == cliente_id), None)

    transacoes_pj_cliente = transacoes_pj[transacoes_pj["cliente_id"] == cliente_id].copy()
    contas_pagar_cliente = contas_pagar[contas_pagar["cliente_id"] == cliente_id].copy()
    contas_receber_cliente = contas_receber[contas_receber["cliente_id"] == cliente_id].copy()
    historico_interacoes_cliente = historico_interacoes[historico_interacoes["cliente_id"] == cliente_id].copy()

    historico_atendimento_cliente = pd.DataFrame()
    if "cliente_id" in historico_atendimento.columns:
        historico_atendimento_cliente = historico_atendimento[
            historico_atendimento["cliente_id"] == cliente_id
        ].copy()

    transacoes_cliente = pd.DataFrame()
    if "cliente_id" in transacoes.columns:
        transacoes_cliente = transacoes[transacoes["cliente_id"] == cliente_id].copy()

    if not transacoes_pj_cliente.empty and "data" in transacoes_pj_cliente.columns:
        transacoes_pj_cliente = transacoes_pj_cliente.sort_values(by="data", ascending=False).head(5)

    if not contas_pagar_cliente.empty and "data_vencimento" in contas_pagar_cliente.columns:
        contas_pagar_cliente = contas_pagar_cliente.sort_values(by="data_vencimento", ascending=True).head(5)

    if not contas_receber_cliente.empty and "data_prevista" in contas_receber_cliente.columns:
        contas_receber_cliente = contas_receber_cliente.sort_values(by="data_prevista", ascending=True).head(5)

    if not historico_interacoes_cliente.empty and "data" in historico_interacoes_cliente.columns:
        historico_interacoes_cliente = historico_interacoes_cliente.sort_values(by="data", ascending=False).head(3)

    if not historico_atendimento_cliente.empty and "data" in historico_atendimento_cliente.columns:
        historico_atendimento_cliente = historico_atendimento_cliente.sort_values(by="data", ascending=False).head(3)

    if not transacoes_cliente.empty and "data" in transacoes_cliente.columns:
        transacoes_cliente = transacoes_cliente.sort_values(by="data", ascending=False).head(5)

    if cliente is None:
        return f"Não foi possível montar o contexto: cliente_id '{cliente_id}' não encontrado em clientes_pj.json."

    nome_fantasia = cliente.get("nome_fantasia", "Não informado")
    razao_social = cliente.get("razao_social", "Não informado")
    tipo_empresa = cliente.get("tipo_empresa", "Não informado")
    segmento = cliente.get("segmento", "Não informado")
    cidade = cliente.get("cidade", "Não informado")
    estado = cliente.get("estado", "Não informado")
    tempo_empresa_meses = cliente.get("tempo_empresa_meses", "Não informado")
    perfil_financeiro = cliente.get("perfil_financeiro", "Não informado")

    banco = conta.get("banco", "Não informado") if conta else "Não informado"
    agencia = conta.get("agencia", "Não informado") if conta else "Não informado"
    numero_conta = conta.get("conta", "Não informado") if conta else "Não informado"
    saldo_atual = conta.get("saldo_atual", 0) if conta else 0
    limite_disponivel = conta.get("limite_disponivel", 0) if conta else 0
    reserva_minima = conta.get("reserva_minima_recomendada", 0) if conta else 0
    status_caixa = conta.get("status_caixa", "Não informado") if conta else "Não informado"

    media_entradas = indicador.get("media_entradas_mensais", 0) if indicador else 0
    media_saidas = indicador.get("media_saidas_mensais", 0) if indicador else 0
    percentual_retirada = indicador.get("percentual_retirada_pessoal_mes", 0) if indicador else 0
    ticket_medio = indicador.get("ticket_medio_entrada", 0) if indicador else 0
    dias_pressao = indicador.get("dias_com_maior_pressao_caixa", []) if indicador else []
    situacao_atual = indicador.get("situacao_atual", "Não informado") if indicador else "Não informado"

    tipo_meta = meta.get("tipo", "Não informado") if meta else "Não informado"
    descricao_meta = meta.get("descricao", "Não informado") if meta else "Não informado"
    valor_meta = meta.get("valor_meta", 0) if meta else 0
    valor_atual_meta = meta.get("valor_atual", 0) if meta else 0
    status_meta = meta.get("status", "Não informado") if meta else "Não informado"

    perfil_investidor_txt = "Não informado"
    if perfil_cliente:
        perfil_investidor_txt = perfil_cliente.get("perfil_investidor", "Não informado")

    produtos_pj_resumidos = [
        {
            "nome": item.get("nome", ""),
            "categoria": item.get("categoria", ""),
            "descricao": item.get("descricao", "")
        }
        for item in produtos_bancarios_pj
    ]

    regras_resumidas = [
        {
            "nome": item.get("nome", ""),
            "descricao": item.get("descricao", ""),
            "mensagem": item.get("mensagem", "")
        }
        for item in regras_alertas
    ]

    produtos_financeiros_resumidos = []
    if isinstance(produtos_financeiros, list):
        produtos_financeiros_resumidos = [
            {
                "nome": item.get("nome", ""),
                "categoria": item.get("categoria", ""),
                "descricao": item.get("descricao", "")
            }
            for item in produtos_financeiros
        ]

    transacoes_pj_txt = transacoes_pj_cliente.to_string(index=False) if not transacoes_pj_cliente.empty else "Nenhuma transação PJ encontrada."
    contas_pagar_txt = contas_pagar_cliente.to_string(index=False) if not contas_pagar_cliente.empty else "Nenhuma conta a pagar encontrada."
    contas_receber_txt = contas_receber_cliente.to_string(index=False) if not contas_receber_cliente.empty else "Nenhuma conta a receber encontrada."
    historico_interacoes_txt = historico_interacoes_cliente.to_string(index=False) if not historico_interacoes_cliente.empty else "Nenhuma interação anterior encontrada."
    historico_atendimento_txt = historico_atendimento_cliente.to_string(index=False) if not historico_atendimento_cliente.empty else "Nenhum atendimento anterior encontrado."
    transacoes_txt = transacoes_cliente.to_string(index=False) if not transacoes_cliente.empty else "Nenhuma transação adicional encontrada."

    contexto = f"""
CLIENTE:
- Nome fantasia: {nome_fantasia}
- Razão social: {razao_social}
- Tipo de empresa: {tipo_empresa}
- Segmento: {segmento}
- Cidade/UF: {cidade}/{estado}
- Tempo de empresa: {tempo_empresa_meses} meses
- Perfil financeiro: {perfil_financeiro}
- Perfil investidor: {perfil_investidor_txt}

CONTA PJ:
- Banco: {banco}
- Agência: {agencia}
- Conta: {numero_conta}
- Saldo atual: R$ {saldo_atual:.2f}
- Limite disponível: R$ {limite_disponivel:.2f}
- Reserva mínima recomendada: R$ {reserva_minima:.2f}
- Status do caixa: {status_caixa}

INDICADORES FINANCEIROS:
- Média de entradas mensais: R$ {media_entradas:.2f}
- Média de saídas mensais: R$ {media_saidas:.2f}
- Percentual de retirada pessoal no mês: {percentual_retirada * 100:.0f}%
- Ticket médio de entrada: R$ {ticket_medio:.2f}
- Dias de maior pressão de caixa: {", ".join(dias_pressao) if dias_pressao else "Não informado"}
- Situação atual: {situacao_atual}

META FINANCEIRA:
- Tipo: {tipo_meta}
- Descrição: {descricao_meta}
- Valor da meta: R$ {valor_meta:.2f}
- Valor atual: R$ {valor_atual_meta:.2f}
- Status: {status_meta}

TRANSAÇÕES PJ RECENTES:
{transacoes_pj_txt}

CONTAS A PAGAR:
{contas_pagar_txt}

CONTAS A RECEBER:
{contas_receber_txt}

HISTÓRICO DE INTERAÇÕES:
{historico_interacoes_txt}

HISTÓRICO DE ATENDIMENTO:
{historico_atendimento_txt}

TRANSAÇÕES ADICIONAIS:
{transacoes_txt}

PRODUTOS BANCÁRIOS PJ DISPONÍVEIS:
{json.dumps(produtos_pj_resumidos, indent=2, ensure_ascii=False)}

PRODUTOS FINANCEIROS DISPONÍVEIS:
{json.dumps(produtos_financeiros_resumidos, indent=2, ensure_ascii=False)}

REGRAS DE ALERTA:
{json.dumps(regras_resumidas, indent=2, ensure_ascii=False)}
"""
    return contexto


def montar_contexto_compacto(cliente_id: str) -> str:
    cliente = next((item for item in clientes_pj if item["cliente_id"] == cliente_id), None)
    conta = next((item for item in contas_pj if item["cliente_id"] == cliente_id), None)
    indicador = next((item for item in indicadores_caixa if item["cliente_id"] == cliente_id), None)

    if cliente is None:
        return f"Cliente com ID '{cliente_id}' não encontrado."
    if conta is None:
        return f"Conta do cliente '{cliente_id}' não encontrada."
    if indicador is None:
        return f"Indicadores do cliente '{cliente_id}' não encontrados."

    transacoes_pj_cliente = transacoes_pj[transacoes_pj["cliente_id"] == cliente_id].copy()
    contas_pagar_cliente = contas_pagar[contas_pagar["cliente_id"] == cliente_id].copy()
    contas_receber_cliente = contas_receber[contas_receber["cliente_id"] == cliente_id].copy()
    historico_interacoes_cliente = historico_interacoes[historico_interacoes["cliente_id"] == cliente_id].copy()

    if not transacoes_pj_cliente.empty and "data" in transacoes_pj_cliente.columns:
        transacoes_pj_cliente = transacoes_pj_cliente.sort_values(by="data", ascending=False).head(5)

    if not contas_pagar_cliente.empty and "data_vencimento" in contas_pagar_cliente.columns:
        contas_pagar_cliente = contas_pagar_cliente.sort_values(by="data_vencimento", ascending=True).head(5)

    if not contas_receber_cliente.empty and "data_prevista" in contas_receber_cliente.columns:
        contas_receber_cliente = contas_receber_cliente.sort_values(by="data_prevista", ascending=True).head(5)

    if not historico_interacoes_cliente.empty and "data" in historico_interacoes_cliente.columns:
        historico_interacoes_cliente = historico_interacoes_cliente.sort_values(by="data", ascending=False).head(3)

    contexto = f"""
CLIENTE: {cliente.get('nome_fantasia', 'Não informado')} | TIPO: {cliente.get('tipo_empresa', 'Não informado')} | SEGMENTO: {cliente.get('segmento', 'Não informado')}
PERFIL FINANCEIRO: {cliente.get('perfil_financeiro', 'Não informado')}
SALDO ATUAL: R$ {conta.get('saldo_atual', 0):.2f} | RESERVA MÍNIMA: R$ {conta.get('reserva_minima_recomendada', 0):.2f} | STATUS: {conta.get('status_caixa', 'Não informado')}
MÉDIA ENTRADAS: R$ {indicador.get('media_entradas_mensais', 0):.2f} | MÉDIA SAÍDAS: R$ {indicador.get('media_saidas_mensais', 0):.2f}
RETIRADA PESSOAL NO MÊS: {indicador.get('percentual_retirada_pessoal_mes', 0) * 100:.0f}%

TRANSAÇÕES RECENTES:
{transacoes_pj_cliente.to_string(index=False) if not transacoes_pj_cliente.empty else "Nenhuma transação encontrada."}

CONTAS A PAGAR:
{contas_pagar_cliente.to_string(index=False) if not contas_pagar_cliente.empty else "Nenhuma conta a pagar encontrada."}

CONTAS A RECEBER:
{contas_receber_cliente.to_string(index=False) if not contas_receber_cliente.empty else "Nenhuma conta a receber encontrada."}

ATENDIMENTOS ANTERIORES:
{historico_interacoes_cliente.to_string(index=False) if not historico_interacoes_cliente.empty else "Nenhuma interação anterior encontrada."}

PRODUTOS DISPONÍVEIS:
{json.dumps(produtos_bancarios_pj, indent=2, ensure_ascii=False)}

REGRAS DE ALERTA:
{json.dumps(regras_alertas, indent=2, ensure_ascii=False)}
"""
    return contexto


SYSTEM_PROMPT = """Você é o Guardião de Caixa, um agente financeiro inteligente especializado em gestão de caixa para pequenos negócios, MEIs, autônomos e microempresas.

OBJETIVO:
Ajudar o cliente a entender a saúde financeira do negócio, acompanhar entradas e saídas, identificar riscos de aperto de caixa, priorizar compromissos financeiros e apoiar decisões com base exclusivamente nos dados disponíveis no sistema.

PAPEL:
Você atua como um CFO digital consultivo, preventivo, educativo e objetivo. Sua função é orientar com clareza, sem julgamentos, usando linguagem acessível e profissional.

MISSÃO PRINCIPAL:
- analisar dados financeiros do cliente com foco em fluxo de caixa;
- explicar a situação atual do negócio em linguagem simples;
- alertar proativamente sobre riscos financeiros;
- sugerir próximos passos práticos e coerentes;
- apoiar a organização financeira do cliente;
- limitar suas respostas ao escopo dos dados fornecidos.

ESCOPO DE ATUAÇÃO:
Você pode ajudar com:
- saldo atual e situação do caixa;
- análise de entradas e saídas;
- contas a pagar e contas a receber;
- vencimentos próximos;
- risco de caixa insuficiente;
- impacto de retiradas pessoais no negócio;
- organização financeira do fluxo operacional;
- alertas preventivos e explicações financeiras básicas;
- sugestões de ação com base em regras e dados disponíveis;
- explicação de produtos bancários PJ, quando estiverem presentes na base.

Você não deve:
- inventar dados;
- responder com base em suposições não suportadas;
- aprovar crédito;
- prometer resultados financeiros;
- substituir contador, consultor tributário ou gerente humano;
- fornecer aconselhamento jurídico, contábil oficial ou tributário formal;
- recomendar investimentos complexos sem contexto apropriado;
- tomar decisões em nome do cliente.

REGRAS:
- Sempre baseie suas respostas apenas nos dados fornecidos no contexto.
- Nunca invente movimentações, saldos, vencimentos, recebimentos ou produtos.
- Quando não houver dados suficientes, diga isso explicitamente.
- Se a pergunta do usuário extrapolar o escopo do agente, informe a limitação com educação e redirecione para o escopo financeiro do negócio.
- Ao analisar a situação do cliente, explique de forma objetiva quais dados sustentam sua conclusão.
- Sempre que possível, organize a resposta em:
  1. resumo da situação;
  2. pontos de atenção;
  3. próxima ação sugerida.
- Quando houver risco financeiro identificado, priorize clareza e prevenção.
- Não use linguagem alarmista. Seja firme, útil e profissional.
- Não trate estimativas como certezas.
- Se houver conflito ou ausência de informação, assuma a postura mais conservadora e transparente.

COMPORTAMENTO PROATIVO:
Quando os dados permitirem, você pode:
- alertar sobre caixa abaixo da reserva mínima;
- destacar vencimentos próximos;
- apontar concentração de despesas;
- sinalizar retiradas pessoais elevadas;
- mostrar risco de insuficiência de caixa;
- sugerir organização por prioridade;
- explicar impacto potencial de uma decisão financeira.

Mas você só deve fazer isso se houver dados no contexto que sustentem a observação.

TOM DE VOZ:
- acessível;
- profissional;
- direto;
- consultivo;
- educativo.

Evite:
- excesso de jargão técnico;
- respostas frias ou robóticas;
- julgamentos sobre a gestão do cliente;
- frases vagas sem explicar o motivo.

FORMATO DE RESPOSTA PREFERENCIAL:
Sempre que fizer sentido, responda seguindo esta estrutura:

Resumo:
Apresente de forma clara e simples a situação financeira atual do cliente, com base nos dados disponíveis.

Pontos de atenção:
- Destaque riscos, vencimentos próximos, excesso de despesas ou qualquer sinal de pressão no caixa.
- Aponte fatores que podem comprometer a operação do negócio ou exigir acompanhamento mais próximo.

Próxima ação sugerida:
Indique uma ação prática e objetiva que o cliente pode tomar naquele momento, com foco em organização, prevenção ou priorização financeira.

Se não houver pontos de atenção relevantes, você pode responder de forma mais direta, mantendo clareza e objetividade.

TRATAMENTO DE INCERTEZA:
Se não houver dados suficientes, use respostas como:
- "Não tenho dados suficientes para afirmar isso com segurança."
- "Com as informações disponíveis, consigo apenas indicar uma estimativa."
- "Esse ponto não aparece claramente na base atual."

SEGURANÇA E PRIVACIDADE:
- Nunca forneça informações de outros clientes.
- Nunca revele credenciais, senhas ou dados sigilosos.
- Nunca simule acesso a sistemas externos se isso não estiver no contexto.
- Se o usuário pedir algo sensível, negue com firmeza e educação.
"""


def montar_historico_conversa(historico, limite=6):
    mensagens_recentes = historico[-limite:]

    linhas = []
    for msg in mensagens_recentes:
        papel = "Usuário" if msg["role"] == "user" else "Assistente"
        linhas.append(f"{papel}: {msg['content']}")

    return "\n".join(linhas) if linhas else "Sem histórico anterior."


def perguntar(cliente_id, msg, historico):
    contexto = montar_contexto_compacto(cliente_id)
    historico_texto = montar_historico_conversa(historico)

    prompt = f"""
{SYSTEM_PROMPT}

CONTEXTO DO CLIENTE:
{contexto}

HISTÓRICO DA CONVERSA:
{historico_texto}

PERGUNTA ATUAL DO USUÁRIO:
{msg}
"""

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False
            }
        )
        r.raise_for_status()
        return r.json()["response"]
    except Exception as e:
        return f"Erro ao consultar o modelo: {e}"


# ========== INTERFACE ==========
st.set_page_config(page_title="Guardião de Caixa", page_icon="💼", layout="centered")

st.title("💼 Guardião de Caixa")
st.caption("Seu agente financeiro para pequenos negócios")

opcoes_clientes = {
    "Mariana Souza Studio": "cli_001",
    "Oficina Rota Certa": "cli_002",
}

cliente_escolhido = st.selectbox(
    "Selecione o cliente para análise:",
    list(opcoes_clientes.keys())
)

cliente_id = opcoes_clientes[cliente_escolhido]

st.info(f"Cliente selecionado: {cliente_escolhido}")

if "historico_chats" not in st.session_state:
    st.session_state.historico_chats = {}

if cliente_id not in st.session_state.historico_chats:
    st.session_state.historico_chats[cliente_id] = []

historico_atual = st.session_state.historico_chats[cliente_id]

if st.button("Limpar conversa deste cliente"):
    st.session_state.historico_chats[cliente_id] = []
    st.rerun()

for msg in historico_atual:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if pergunta_usuario := st.chat_input("Digite sua dúvida sobre o caixa do negócio..."):
    with st.chat_message("user"):
        st.write(pergunta_usuario)

    with st.spinner("Analisando a situação do caixa..."):
        resposta = perguntar(cliente_id, pergunta_usuario, historico_atual)

    historico_atual.append({"role": "user", "content": pergunta_usuario})
    historico_atual.append({"role": "assistant", "content": resposta})

    with st.chat_message("assistant"):
        st.write(resposta)