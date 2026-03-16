"""
Motor de Cálculo de Imposto de Renda sobre Ações.

Este módulo é responsável por:
- Calcular IR sobre operações de compra/venda de ações
- Diferenciar entre day trade (20%) e swing trade (15%)
- Aplicar isenção mensal de R$ 20.000 para swing trade
- Gerenciar compensação de prejuízos
- Gerar dados para DARF
"""

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Optional

from loguru import logger


class TipoOperacao(Enum):
    """Tipos de operação no mercado de ações."""
    DAY_TRADE = "DAY_TRADE"
    SWING_TRADE = "SWING_TRADE"


@dataclass
class DadosOperacao:
    """Dados de entrada para cálculo de IR."""
    ticker: str
    quantidade: int
    preco_venda: float
    preco_compra: float
    data_compra: date
    data_venda: date
    corretagem: float = 0.0
    emolumentos: float = 0.0


@dataclass
class ResultadoCalculo:
    """Resultado do cálculo de IR sobre uma operação."""
    ticker: str
    quantidade: int
    preco_compra: float
    preco_venda: float
    valor_venda: float
    custo_total: float
    lucro_bruto: float
    tipo_operacao: TipoOperacao
    aliquota: float
    total_vendas_mes: float
    isento: bool
    prejuizo_compensado: float = 0.0
    base_calculo: float = 0.0
    ir_devido: float = 0.0
    margem_isencao: float = 0.0
    vencimento_darf: Optional[date] = None
    codigo_darf: str = "6015"
    mensagem: str = ""
    alertas: list[str] = field(default_factory=list)


class RegrasTributarias:
    """Carrega e gerencia as regras tributárias do arquivo JSON."""
    
    def __init__(self, path: str = "data/regras_tributarias.json") -> None:
        """
        Inicializa as regras tributárias.
        
        Args:
            path: Caminho para o arquivo de regras.
        """
        self.path = Path(path)
        self._regras = self._carregar_regras()
    
    def _carregar_regras(self) -> dict:
        """Carrega as regras do arquivo JSON."""
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                regras = json.load(f)
                logger.debug(f"Regras tributárias carregadas de {self.path}")
                return regras
        except FileNotFoundError:
            logger.warning(f"Arquivo de regras não encontrado: {self.path}. Usando regras padrão.")
            return self._regras_padrao()
    
    def _regras_padrao(self) -> dict:
        """Retorna regras tributárias padrão caso o arquivo não exista."""
        return {
            "swing_trade": {
                "aliquota": 0.15,
                "isencao_mensal": 20000.00,
                "codigo_darf": "6015"
            },
            "day_trade": {
                "aliquota": 0.20,
                "isencao_mensal": 0.00,
                "codigo_darf": "6015"
            }
        }
    
    @property
    def aliquota_swing_trade(self) -> float:
        """Alíquota para operações swing trade (15%)."""
        return self._regras.get("swing_trade", {}).get("aliquota", 0.15)
    
    @property
    def aliquota_day_trade(self) -> float:
        """Alíquota para operações day trade (20%)."""
        return self._regras.get("day_trade", {}).get("aliquota", 0.20)
    
    @property
    def isencao_mensal(self) -> float:
        """Limite de isenção mensal para swing trade (R$ 20.000)."""
        return self._regras.get("swing_trade", {}).get("isencao_mensal", 20000.00)
    
    @property
    def codigo_darf(self) -> str:
        """Código da DARF para IR sobre ações."""
        return self._regras.get("swing_trade", {}).get("codigo_darf", "6015")


class MotorCalculoIR:
    """
    Motor de cálculo de Imposto de Renda sobre operações com ações.
    
    Este motor é determinístico e segue estritamente as regras da
    Receita Federal (IN RFB nº 1.585/2015).
    
    Attributes:
        regras: Instância das regras tributárias.
    """
    
    def __init__(self) -> None:
        """Inicializa o motor de cálculo."""
        self.regras = RegrasTributarias()
        logger.info("Motor de cálculo IR inicializado")
    
    def identificar_tipo_operacao(
        self, 
        data_compra: date, 
        data_venda: date
    ) -> TipoOperacao:
        """
        Identifica se a operação é day trade ou swing trade.
        
        Args:
            data_compra: Data da compra.
            data_venda: Data da venda.
            
        Returns:
            Tipo da operação (DAY_TRADE ou SWING_TRADE).
        """
        if data_compra == data_venda:
            return TipoOperacao.DAY_TRADE
        return TipoOperacao.SWING_TRADE
    
    def calcular_lucro(
        self,
        quantidade: int,
        preco_venda: float,
        preco_compra: float,
        corretagem: float = 0.0,
        emolumentos: float = 0.0
    ) -> tuple[float, float, float]:
        """
        Calcula o lucro/prejuízo de uma operação.
        
        Args:
            quantidade: Quantidade de ações.
            preco_venda: Preço unitário de venda.
            preco_compra: Preço médio de compra.
            corretagem: Valor da corretagem.
            emolumentos: Valor dos emolumentos.
            
        Returns:
            Tupla com (valor_venda, custo_total, lucro_bruto).
        """
        valor_venda = Decimal(str(quantidade)) * Decimal(str(preco_venda))
        custo_aquisicao = Decimal(str(quantidade)) * Decimal(str(preco_compra))
        custos_operacionais = Decimal(str(corretagem)) + Decimal(str(emolumentos))
        
        custo_total = custo_aquisicao + custos_operacionais
        lucro_bruto = valor_venda - custo_total
        
        return (
            float(valor_venda.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            float(custo_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            float(lucro_bruto.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        )
    
    def verificar_isencao(
        self,
        tipo_operacao: TipoOperacao,
        total_vendas_mes: float
    ) -> bool:
        """
        Verifica se a operação está isenta de IR.
        
        Args:
            tipo_operacao: Tipo da operação.
            total_vendas_mes: Total de vendas no mês.
            
        Returns:
            True se isento, False caso contrário.
        """
        if tipo_operacao == TipoOperacao.DAY_TRADE:
            return False
        
        return total_vendas_mes <= self.regras.isencao_mensal
    
    def obter_aliquota(self, tipo_operacao: TipoOperacao) -> float:
        """
        Obtém a alíquota de IR conforme o tipo de operação.
        
        Args:
            tipo_operacao: Tipo da operação.
            
        Returns:
            Alíquota aplicável (0.15 ou 0.20).
        """
        if tipo_operacao == TipoOperacao.DAY_TRADE:
            return self.regras.aliquota_day_trade
        return self.regras.aliquota_swing_trade
    
    def calcular_vencimento_darf(self, mes_operacao: date) -> date:
        """
        Calcula a data de vencimento da DARF.
        
        Args:
            mes_operacao: Mês de referência da operação.
            
        Returns:
            Data de vencimento (último dia útil do mês seguinte).
        """
        ano = mes_operacao.year
        mes = mes_operacao.month
        
        if mes == 12:
            proximo_ano = ano + 1
            proximo_mes = 1
        else:
            proximo_ano = ano
            proximo_mes = mes + 1
        
        if proximo_mes == 12:
            ultimo_dia = 31
        elif proximo_mes in [4, 6, 9, 11]:
            ultimo_dia = 30
        elif proximo_mes == 2:
            if (proximo_ano % 4 == 0 and proximo_ano % 100 != 0) or (proximo_ano % 400 == 0):
                ultimo_dia = 29
            else:
                ultimo_dia = 28
        else:
            ultimo_dia = 31
        
        vencimento = date(proximo_ano, proximo_mes, ultimo_dia)
        
        while vencimento.weekday() >= 5:
            vencimento = vencimento.replace(day=vencimento.day - 1)
        
        return vencimento
    
    def calcular_ir(
        self,
        operacao: DadosOperacao,
        total_vendas_mes_anterior: float = 0.0,
        prejuizo_acumulado: float = 0.0
    ) -> ResultadoCalculo:
        """
        Calcula o Imposto de Renda sobre uma operação de venda.
        
        Este é o método principal do motor de cálculo.
        
        Args:
            operacao: Dados da operação.
            total_vendas_mes_anterior: Total de vendas já realizadas no mês.
            prejuizo_acumulado: Prejuízo acumulado para compensação.
            
        Returns:
            Resultado completo do cálculo.
        """
        tipo_operacao = self.identificar_tipo_operacao(
            operacao.data_compra, 
            operacao.data_venda
        )
        
        valor_venda, custo_total, lucro_bruto = self.calcular_lucro(
            operacao.quantidade,
            operacao.preco_venda,
            operacao.preco_compra,
            operacao.corretagem,
            operacao.emolumentos
        )
        
        total_vendas_mes = total_vendas_mes_anterior + valor_venda
        
        isento = self.verificar_isencao(tipo_operacao, total_vendas_mes)
        
        aliquota = self.obter_aliquota(tipo_operacao)
        
        alertas = []
        margem_isencao = 0.0
        
        if tipo_operacao == TipoOperacao.SWING_TRADE:
            margem_isencao = self.regras.isencao_mensal - total_vendas_mes
            
            if margem_isencao > 0 and margem_isencao < 2000:
                alertas.append(
                    f"⚠️ Você está próximo do limite de isenção! "
                    f"Restam apenas R$ {margem_isencao:,.2f} para manter a isenção."
                )
            elif margem_isencao <= 0 and total_vendas_mes_anterior <= self.regras.isencao_mensal:
                alertas.append(
                    "⚠️ ATENÇÃO: Esta operação ultrapassou o limite de isenção de R$ 20.000,00. "
                    "Você deverá pagar IR sobre TODO o lucro do mês."
                )
        
        if tipo_operacao == TipoOperacao.DAY_TRADE:
            alertas.append(
                "💡 Operação identificada como Day Trade (20%). "
                "Não há isenção mensal para day trade."
            )
        
        ir_devido = 0.0
        prejuizo_compensado = 0.0
        base_calculo = 0.0
        
        if lucro_bruto > 0 and not isento:
            if prejuizo_acumulado > 0:
                prejuizo_compensado = min(prejuizo_acumulado, lucro_bruto)
                base_calculo = lucro_bruto - prejuizo_compensado
                
                if prejuizo_compensado > 0:
                    alertas.append(
                        f"✅ Compensação de prejuízo aplicada: R$ {prejuizo_compensado:,.2f}"
                    )
            else:
                base_calculo = lucro_bruto
            
            if base_calculo > 0:
                ir_decimal = Decimal(str(base_calculo)) * Decimal(str(aliquota))
                ir_devido = float(ir_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        
        elif lucro_bruto < 0:
            alertas.append(
                f"📝 Prejuízo de R$ {abs(lucro_bruto):,.2f} registrado. "
                "Pode ser compensado em operações futuras do mesmo tipo."
            )
        
        vencimento_darf = None
        if ir_devido > 0:
            vencimento_darf = self.calcular_vencimento_darf(operacao.data_venda)
        
        if isento:
            mensagem = (
                f"✅ Operação ISENTA de IR! "
                f"Suas vendas do mês totalizam R$ {total_vendas_mes:,.2f}, "
                f"abaixo do limite de R$ {self.regras.isencao_mensal:,.2f}."
            )
        elif ir_devido > 0:
            mensagem = (
                f"💰 IR devido: R$ {ir_devido:,.2f} "
                f"({tipo_operacao.value.replace('_', ' ').title()} - {aliquota*100:.0f}%)"
            )
        elif lucro_bruto < 0:
            mensagem = f"📉 Operação com prejuízo de R$ {abs(lucro_bruto):,.2f}. Sem IR a pagar."
        else:
            mensagem = "✅ Sem IR a pagar nesta operação."
        
        resultado = ResultadoCalculo(
            ticker=operacao.ticker.upper(),
            quantidade=operacao.quantidade,
            preco_compra=operacao.preco_compra,
            preco_venda=operacao.preco_venda,
            valor_venda=valor_venda,
            custo_total=custo_total,
            lucro_bruto=lucro_bruto,
            tipo_operacao=tipo_operacao,
            aliquota=aliquota,
            total_vendas_mes=total_vendas_mes,
            isento=isento,
            prejuizo_compensado=prejuizo_compensado,
            base_calculo=base_calculo,
            ir_devido=ir_devido,
            margem_isencao=max(0, margem_isencao),
            vencimento_darf=vencimento_darf,
            codigo_darf=self.regras.codigo_darf,
            mensagem=mensagem,
            alertas=alertas
        )
        
        logger.info(
            f"Cálculo IR: {operacao.ticker} | "
            f"Lucro: R$ {lucro_bruto:,.2f} | "
            f"Tipo: {tipo_operacao.value} | "
            f"Isento: {isento} | "
            f"IR: R$ {ir_devido:,.2f}"
        )
        
        return resultado
    
    def simular_venda(
        self,
        ticker: str,
        quantidade: int,
        preco_venda_estimado: float,
        preco_compra: float,
        vendas_mes_atual: float = 0.0,
        prejuizo_acumulado: float = 0.0
    ) -> dict:
        """
        Simula uma venda para estimar o impacto tributário.
        
        Args:
            ticker: Código do ativo.
            quantidade: Quantidade a vender.
            preco_venda_estimado: Preço estimado de venda.
            preco_compra: Preço médio de compra.
            vendas_mes_atual: Total de vendas já realizadas no mês.
            prejuizo_acumulado: Prejuízo acumulado.
            
        Returns:
            Dicionário com detalhes da simulação.
        """
        operacao = DadosOperacao(
            ticker=ticker,
            quantidade=quantidade,
            preco_venda=preco_venda_estimado,
            preco_compra=preco_compra,
            data_compra=date.today(),
            data_venda=date.today()
        )
        operacao.data_compra = date(2000, 1, 1)
        
        resultado = self.calcular_ir(operacao, vendas_mes_atual, prejuizo_acumulado)
        
        cenario_manter_isencao = None
        if resultado.total_vendas_mes > self.regras.isencao_mensal:
            margem_disponivel = self.regras.isencao_mensal - vendas_mes_atual
            if margem_disponivel > 0:
                qtd_maxima = int(margem_disponivel / preco_venda_estimado)
                if qtd_maxima > 0:
                    cenario_manter_isencao = {
                        "quantidade_maxima": qtd_maxima,
                        "valor_venda_maximo": qtd_maxima * preco_venda_estimado,
                        "economia_ir_estimada": resultado.ir_devido
                    }
        
        return {
            "resultado": resultado,
            "cenario_manter_isencao": cenario_manter_isencao,
            "recomendacao": self._gerar_recomendacao(resultado, cenario_manter_isencao)
        }
    
    def _gerar_recomendacao(
        self, 
        resultado: ResultadoCalculo, 
        cenario_isencao: Optional[dict]
    ) -> str:
        """Gera uma recomendação baseada no resultado da simulação."""
        if resultado.isento:
            return (
                f"✅ Você pode realizar esta venda mantendo a isenção. "
                f"Margem restante: R$ {resultado.margem_isencao:,.2f}"
            )
        
        if cenario_isencao:
            return (
                f"💡 SUGESTÃO: Venda apenas {cenario_isencao['quantidade_maxima']} ações "
                f"(R$ {cenario_isencao['valor_venda_maximo']:,.2f}) para manter a isenção. "
                f"Deixe o restante para o próximo mês e economize "
                f"R$ {cenario_isencao['economia_ir_estimada']:,.2f} de IR."
            )
        
        if resultado.ir_devido > 0:
            return (
                f"💰 Esta venda gerará IR de R$ {resultado.ir_devido:,.2f}. "
                f"DARF deve ser paga até {resultado.vencimento_darf.strftime('%d/%m/%Y') if resultado.vencimento_darf else 'N/A'}."
            )
        
        return "✅ Operação analisada com sucesso."


motor_ir: Optional[MotorCalculoIR] = None


def get_motor_calculo() -> MotorCalculoIR:
    """
    Obtém a instância global do motor de cálculo.
    
    Returns:
        Instância do MotorCalculoIR.
    """
    global motor_ir
    if motor_ir is None:
        motor_ir = MotorCalculoIR()
    return motor_ir
