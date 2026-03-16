"""
Cliente OpenAI GPT-4 para o IR Smart.

Este módulo é responsável por:
- Gerenciar comunicação com a API da OpenAI
- Processar linguagem natural das perguntas dos usuários
- Gerar respostas humanizadas com base nos cálculos do motor
- Manter contexto da conversa
"""

import os
from datetime import date
from typing import Optional

from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI

from src.cache import get_cache

load_dotenv()

SYSTEM_PROMPT = """Você é o IR Smart, um assistente inteligente especializado em cálculo de Imposto de Renda sobre operações com ações no mercado brasileiro.

IDENTIDADE:
- Nome: IR Smart
- Função: Assistente tributário para investidores pessoa física
- Especialização: Cálculo de IR sobre ganho de capital em ações (mercado à vista, B3)
- Tom: Profissional-acessível, educativo, confiável

OBJETIVO PRINCIPAL:
Ajudar investidores a calcular corretamente o Imposto de Renda sobre suas operações com ações, 
garantindo conformidade fiscal e tranquilidade tributária.

═══════════════════════════════════════════════════════════════════════

REGRAS FUNDAMENTAIS DE SEGURANÇA:

1. NUNCA INVENTE INFORMAÇÕES TRIBUTÁRIAS
   - Use APENAS as regras oficiais da Receita Federal fornecidas
   - Se não tiver certeza sobre algo, admita e sugira consultar um contador
   - Não especule sobre mudanças legislativas futuras

2. CÁLCULOS SÃO FEITOS PELO SISTEMA, NÃO POR VOCÊ
   - Você recebe os resultados já calculados pelo motor tributário
   - Sua função é EXPLICAR os cálculos, não executá-los
   - Se houver divergência, sempre confie no cálculo programático

3. SEMPRE FUNDAMENTE SUAS RESPOSTAS
   - Cite a base legal (ex: "Conforme IN RFB 1.585/2015, art. 59...")
   - Explique o passo a passo do raciocínio
   - Inclua links para documentação oficial quando relevante

4. ADMITA LIMITAÇÕES
   - Se a pergunta for sobre FIIs, opções, ETFs ou outros ativos → redirecione
   - Se a situação for complexa demais → sugira consultar contador
   - Se não souber → diga "Não tenho essa informação"

5. SEJA EDUCATIVO
   - Explique termos técnicos de forma simples
   - Use exemplos práticos
   - Ensine o "porquê" das regras, não apenas o "como"

═══════════════════════════════════════════════════════════════════════

ESCOPO DE ATUAÇÃO:

✅ O QUE VOCÊ COBRE:
- Cálculo de IR sobre ações no mercado à vista (B3)
- Day trade (20%) e swing trade (15%)
- Isenção para vendas até R$ 20.000/mês (swing trade)
- Compensação de prejuízos
- Geração de DARF (código 6015)
- Controle de preço médio de compra
- Explicação das regras tributárias

❌ O QUE VOCÊ NÃO COBRE:
- Fundos Imobiliários (FIIs)
- ETFs e BDRs
- Opções e derivativos
- Criptomoedas
- Ações no exterior
- Planejamento tributário complexo
- Defesa em fiscalização

═══════════════════════════════════════════════════════════════════════

FORMATO DE RESPOSTA:

Para CÁLCULOS, use esta estrutura:

💰 **Resumo da Operação:**
- [Detalhes da operação]

📊 **Cálculo do Imposto:**
1. [Passo 1]
2. [Passo 2]
3. [Resultado]

⚖️ **Base Legal:**
- [Citação da legislação]

💡 **Dica:**
- [Orientação adicional se aplicável]

═══════════════════════════════════════════════════════════════════════

Para PERGUNTAS GERAIS, seja direto e educativo:

📚 **Resposta:**
[Explicação clara e objetiva]

📖 **Saiba mais:**
[Link ou referência para aprofundamento]

═══════════════════════════════════════════════════════════════════════

ALERTAS PROATIVOS:

Você deve SEMPRE alertar quando:
- Vendas se aproximam de R$ 20.000 no mês (avisar faltando R$ 2.000)
- Usuário tem prejuízos acumulados que pode compensar
- Há risco de perder isenção
- DARF está próxima do vencimento
- Detecção de possível day trade não identificado

═══════════════════════════════════════════════════════════════════════

LINGUAGEM E TOM:

✅ USE:
- "Você está isento" (não "Está isento")
- "Deixa eu calcular..." (conversacional)
- "Importante:" (não "IMPORTANTE!!!")
- Emojis com moderação (💰 📊 ⚠️ ✅)

❌ EVITE:
- Juridiquês excessivo
- ALL CAPS (exceto siglas)
- Emojis em excesso
- Tom alarmista
- Linguagem muito informal

═══════════════════════════════════════════════════════════════════════

LEMBRE-SE:
- Você é um ASSISTENTE, não um substituto de contador
- Priorize SEGURANÇA e CONFORMIDADE sobre conveniência
- Seja TRANSPARENTE sobre suas limitações
- EDUQUE enquanto responde
- Mantenha TOM PROFISSIONAL mas ACESSÍVEL
"""


class ChatGPTClient:
    """
    Cliente para comunicação com a API OpenAI GPT-4.
    
    Esta classe gerencia:
    - Configuração e autenticação com a API
    - Envio de mensagens e recebimento de respostas
    - Gerenciamento do histórico de conversa
    - Injeção de contexto (dados do usuário, cálculos)
    
    Attributes:
        client: Instância do cliente OpenAI.
        model: Modelo GPT a ser utilizado.
        historico: Histórico de mensagens da conversa.
    """
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Inicializa o cliente GPT.
        
        Args:
            api_key: Chave da API OpenAI. Se não fornecida, busca da variável de ambiente.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY não configurada. O cliente funcionará em modo simulado.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.historico: list[dict] = []
        self._inicializar_conversa()
        
        logger.info(f"Cliente GPT inicializado | Modelo: {self.model}")
    
    def _inicializar_conversa(self) -> None:
        """Inicializa a conversa com o system prompt."""
        self.historico = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
    def adicionar_contexto(self, contexto: str) -> None:
        """
        Adiciona contexto adicional à conversa (dados do usuário, cálculos, etc.).
        
        Args:
            contexto: Texto com informações contextuais.
        """
        mensagem_contexto = {
            "role": "system",
            "content": f"CONTEXTO ATUALIZADO:\n{contexto}"
        }
        
        if len(self.historico) > 1 and self.historico[1].get("role") == "system":
            self.historico[1] = mensagem_contexto
        else:
            self.historico.insert(1, mensagem_contexto)
        
        logger.debug("Contexto adicionado à conversa")
    
    def montar_contexto_usuario(
        self,
        total_vendas_mes: float = 0.0,
        prejuizo_swing: float = 0.0,
        prejuizo_day_trade: float = 0.0,
        operacoes_recentes: Optional[list] = None
    ) -> str:
        """
        Monta o contexto do usuário para injetar na conversa.
        
        Args:
            total_vendas_mes: Total de vendas no mês atual.
            prejuizo_swing: Prejuízo acumulado em swing trade.
            prejuizo_day_trade: Prejuízo acumulado em day trade.
            operacoes_recentes: Lista de operações recentes.
            
        Returns:
            String formatada com o contexto.
        """
        limite_isencao = 20000.00
        margem_isencao = max(0, limite_isencao - total_vendas_mes)
        status = "ISENTO" if total_vendas_mes <= limite_isencao else "TRIBUTÁVEL"
        
        contexto = f"""
SITUAÇÃO ATUAL DO USUÁRIO (Data: {date.today().strftime('%d/%m/%Y')}):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 VENDAS DO MÊS:
- Total vendido: R$ {total_vendas_mes:,.2f}
- Limite de isenção: R$ {limite_isencao:,.2f}
- Margem restante: R$ {margem_isencao:,.2f}
- Status: {status}

📉 PREJUÍZOS ACUMULADOS:
- Swing Trade: R$ {prejuizo_swing:,.2f}
- Day Trade: R$ {prejuizo_day_trade:,.2f}
"""
        
        if operacoes_recentes:
            contexto += "\n📋 ÚLTIMAS OPERAÇÕES:\n"
            for op in operacoes_recentes[-5:]:
                contexto += f"- {op.get('data', 'N/A')}: {op.get('tipo', 'N/A')} {op.get('quantidade', 0)}x {op.get('ticker', 'N/A')} @ R$ {op.get('preco_unitario', 0):,.2f}\n"
        
        contexto += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        return contexto
    
    def montar_contexto_calculo(self, resultado_calculo: dict) -> str:
        """
        Monta contexto com resultado de um cálculo para a resposta.
        
        Args:
            resultado_calculo: Dicionário com resultado do motor de cálculo.
            
        Returns:
            String formatada com o contexto do cálculo.
        """
        contexto = f"""
RESULTADO DO CÁLCULO (Motor IR Smart):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 OPERAÇÃO:
- Ativo: {resultado_calculo.get('ticker', 'N/A')}
- Quantidade: {resultado_calculo.get('quantidade', 0)} ações
- Preço de compra: R$ {resultado_calculo.get('preco_compra', 0):,.2f}
- Preço de venda: R$ {resultado_calculo.get('preco_venda', 0):,.2f}
- Valor da venda: R$ {resultado_calculo.get('valor_venda', 0):,.2f}

💰 RESULTADO:
- Lucro/Prejuízo: R$ {resultado_calculo.get('lucro_bruto', 0):,.2f}
- Tipo: {resultado_calculo.get('tipo_operacao', 'N/A')}
- Alíquota: {resultado_calculo.get('aliquota', 0)*100:.0f}%

🎯 TRIBUTAÇÃO:
- Total vendas no mês: R$ {resultado_calculo.get('total_vendas_mes', 0):,.2f}
- Status: {'ISENTO' if resultado_calculo.get('isento', False) else 'TRIBUTÁVEL'}
- Prejuízo compensado: R$ {resultado_calculo.get('prejuizo_compensado', 0):,.2f}
- Base de cálculo: R$ {resultado_calculo.get('base_calculo', 0):,.2f}
- IR DEVIDO: R$ {resultado_calculo.get('ir_devido', 0):,.2f}

IMPORTANTE: Use estes dados calculados pelo motor. NÃO refaça os cálculos.
Explique o resultado de forma clara e educativa para o usuário.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return contexto
    
    def enviar_mensagem(
        self,
        mensagem: str,
        contexto_adicional: Optional[str] = None,
        usar_cache: bool = True
    ) -> str:
        """
        Envia uma mensagem para o GPT e obtém a resposta.
        
        Args:
            mensagem: Mensagem do usuário.
            contexto_adicional: Contexto extra a ser injetado (ex: resultado de cálculo).
            usar_cache: Se True, verifica cache antes de chamar API.
            
        Returns:
            Resposta do GPT.
        """
        cache = get_cache()
        
        if usar_cache:
            resposta_cache = cache.buscar(mensagem)
            if resposta_cache:
                self.historico.append({"role": "user", "content": mensagem})
                self.historico.append({"role": "assistant", "content": resposta_cache})
                logger.info("✅ Resposta servida do cache")
                return resposta_cache + "\n\n_📦 (resposta do cache)_"
        
        if contexto_adicional:
            self.adicionar_contexto(contexto_adicional)
        
        self.historico.append({
            "role": "user",
            "content": mensagem
        })
        
        if self.client is None:
            resposta = self._resposta_simulada(mensagem)
            logger.warning("Usando resposta simulada (API não configurada)")
        else:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.historico,
                    temperature=0.7,
                    max_tokens=1500
                )
                resposta = response.choices[0].message.content
                logger.debug(f"Resposta recebida do GPT ({len(resposta)} caracteres)")
                
                if usar_cache:
                    cache.salvar(mensagem, resposta)
                    
            except Exception as e:
                logger.error(f"Erro na comunicação com GPT: {e}")
                resposta = self._resposta_erro()
        
        self.historico.append({
            "role": "assistant",
            "content": resposta
        })
        
        if len(self.historico) > 20:
            self.historico = [self.historico[0]] + self.historico[-18:]
        
        return resposta
    
    def _resposta_simulada(self, mensagem: str) -> str:
        """Gera uma resposta simulada quando a API não está disponível."""
        mensagem_lower = mensagem.lower()
        
        if any(word in mensagem_lower for word in ['olá', 'oi', 'bom dia', 'boa tarde', 'boa noite']):
            return (
                "Olá! 👋 Sou o **IR Smart**, seu assistente inteligente para cálculo de impostos sobre ações.\n\n"
                "Posso te ajudar com:\n"
                "- 📊 Cálculo de IR sobre vendas de ações\n"
                "- 💰 Verificação de isenção mensal (R$ 20.000)\n"
                "- 📉 Compensação de prejuízos\n"
                "- 📝 Geração de DARF\n\n"
                "Como posso te ajudar hoje?"
            )
        
        if any(word in mensagem_lower for word in ['day trade', 'daytrade', 'swing trade']):
            return (
                "📚 **Day Trade vs Swing Trade:**\n\n"
                "**Day Trade:**\n"
                "- Compra e venda no MESMO dia\n"
                "- Alíquota: **20%**\n"
                "- ❌ Não tem isenção mensal\n\n"
                "**Swing Trade:**\n"
                "- Compra e venda em dias DIFERENTES\n"
                "- Alíquota: **15%**\n"
                "- ✅ Isenção para vendas até R$ 20.000/mês\n\n"
                "⚖️ *Base Legal: Lei nº 8.981/1995, art. 21*"
            )
        
        if 'isenção' in mensagem_lower or 'isento' in mensagem_lower:
            return (
                "📚 **Isenção de IR sobre Ações:**\n\n"
                "Você está **isento** de pagar IR quando:\n"
                "- Operações de **Swing Trade** (dias diferentes)\n"
                "- Total de **vendas no mês** ≤ R$ 20.000,00\n\n"
                "⚠️ **Importante:**\n"
                "Se ultrapassar R$ 20.000 em vendas, você paga IR sobre **todo** o lucro do mês!\n\n"
                "💡 **Dica:** Planeje suas vendas para aproveitar a isenção mensal.\n\n"
                "⚖️ *Base Legal: IN RFB nº 1.585/2015, art. 61*"
            )
        
        return (
            "Entendi sua pergunta! 🤔\n\n"
            "⚠️ **Nota:** A API do GPT não está configurada no momento.\n\n"
            "Para usar todas as funcionalidades do IR Smart:\n"
            "1. Configure sua `OPENAI_API_KEY` no arquivo `.env`\n"
            "2. Reinicie a aplicação\n\n"
            "Enquanto isso, posso te ajudar com:\n"
            "- Cálculos de IR (funciona normalmente)\n"
            "- Registro de operações\n"
            "- Consulta de histórico\n\n"
            "O que você gostaria de fazer?"
        )
    
    def _resposta_erro(self) -> str:
        """Retorna mensagem de erro padrão."""
        return (
            "⚠️ Desculpe, ocorreu um erro ao processar sua solicitação.\n\n"
            "Possíveis causas:\n"
            "- Problema de conexão com a API\n"
            "- Limite de requisições atingido\n"
            "- Erro temporário\n\n"
            "Por favor, tente novamente em alguns instantes.\n"
            "Se o problema persistir, verifique suas configurações de API."
        )
    
    def limpar_historico(self) -> None:
        """Limpa o histórico de conversa, mantendo apenas o system prompt."""
        self._inicializar_conversa()
        logger.info("Histórico de conversa limpo")
    
    def obter_historico(self) -> list[dict]:
        """
        Retorna o histórico de conversa (sem o system prompt).
        
        Returns:
            Lista de mensagens (role, content).
        """
        return [msg for msg in self.historico if msg["role"] != "system"]


gpt_client: Optional[ChatGPTClient] = None


def get_gpt_client() -> ChatGPTClient:
    """
    Obtém a instância global do cliente GPT.
    
    Returns:
        Instância do ChatGPTClient.
    """
    global gpt_client
    if gpt_client is None:
        gpt_client = ChatGPTClient()
    return gpt_client
