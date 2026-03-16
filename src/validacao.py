"""
Módulo de Validação Anti-Alucinação do IR Smart.

Este módulo implementa as 6 camadas de segurança para garantir
que as respostas do sistema sejam precisas e confiáveis.

Camadas de validação:
1. Separação de responsabilidades (LLM não faz cálculos)
2. Validação cruzada (dupla checagem)
3. Base de conhecimento estruturada
4. Respostas fundamentadas
5. Admissão de limitações
6. Testes automatizados
"""

import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional

from loguru import logger


class NivelConfianca(Enum):
    """Níveis de confiança das respostas."""
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAIXA = "BAIXA"
    REQUER_VALIDACAO = "REQUER_VALIDACAO"


class TipoValidacao(Enum):
    """Tipos de validação realizados."""
    CALCULO_NUMERICO = "CALCULO_NUMERICO"
    REGRA_TRIBUTARIA = "REGRA_TRIBUTARIA"
    ESCOPO_ATENDIMENTO = "ESCOPO_ATENDIMENTO"
    CONSISTENCIA_DADOS = "CONSISTENCIA_DADOS"


@dataclass
class ResultadoValidacao:
    """Resultado de uma validação."""
    valido: bool
    tipo: TipoValidacao
    nivel_confianca: NivelConfianca
    mensagem: str
    detalhes: Optional[dict] = None


class ValidadorAntiAlucinacao:
    """
    Validador para garantir precisão e segurança das respostas.
    
    Este validador implementa múltiplas camadas de verificação para
    evitar que o sistema forneça informações incorretas.
    """
    
    TOPICOS_FORA_ESCOPO = [
        "fii", "fiis", "fundo imobiliário", "fundos imobiliários",
        "etf", "etfs", "bdr", "bdrs",
        "opção", "opções", "derivativo", "derivativos",
        "cripto", "bitcoin", "criptomoeda", "criptomoedas",
        "forex", "dólar", "euro",
        "ação exterior", "ações exterior", "stock", "stocks",
        "herança", "doação", "permuta",
        "imposto de renda pessoa jurídica", "irpj",
        "mei", "simples nacional"
    ]
    
    TERMOS_SUSPEITOS = [
        "sonegar", "sonegação", "esconder", "ocultar",
        "não declarar", "fraudar", "fraude"
    ]
    
    ALIQUOTA_SWING_TRADE = Decimal("0.15")
    ALIQUOTA_DAY_TRADE = Decimal("0.20")
    LIMITE_ISENCAO = Decimal("20000.00")
    
    def __init__(self) -> None:
        """Inicializa o validador."""
        logger.info("Validador anti-alucinação inicializado")
    
    def validar_calculo_ir(
        self,
        lucro: float,
        aliquota: float,
        ir_calculado: float,
        tolerancia: float = 0.01
    ) -> ResultadoValidacao:
        """
        Valida se o cálculo de IR está correto.
        
        Args:
            lucro: Valor do lucro base.
            aliquota: Alíquota aplicada.
            ir_calculado: Valor do IR calculado pelo sistema.
            tolerancia: Margem de erro aceitável.
            
        Returns:
            Resultado da validação.
        """
        lucro_decimal = Decimal(str(lucro))
        aliquota_decimal = Decimal(str(aliquota))
        ir_calculado_decimal = Decimal(str(ir_calculado))
        
        ir_esperado = (lucro_decimal * aliquota_decimal).quantize(
            Decimal('0.01'), 
            rounding=ROUND_HALF_UP
        )
        
        diferenca = abs(ir_esperado - ir_calculado_decimal)
        tolerancia_decimal = Decimal(str(tolerancia))
        
        if diferenca <= tolerancia_decimal:
            return ResultadoValidacao(
                valido=True,
                tipo=TipoValidacao.CALCULO_NUMERICO,
                nivel_confianca=NivelConfianca.ALTA,
                mensagem="Cálculo de IR validado com sucesso.",
                detalhes={
                    "ir_esperado": float(ir_esperado),
                    "ir_calculado": float(ir_calculado_decimal),
                    "diferenca": float(diferenca)
                }
            )
        else:
            logger.warning(
                f"Divergência no cálculo de IR: esperado={ir_esperado}, "
                f"calculado={ir_calculado_decimal}, diferença={diferenca}"
            )
            return ResultadoValidacao(
                valido=False,
                tipo=TipoValidacao.CALCULO_NUMERICO,
                nivel_confianca=NivelConfianca.BAIXA,
                mensagem=f"Divergência detectada no cálculo. Diferença: R$ {diferenca}",
                detalhes={
                    "ir_esperado": float(ir_esperado),
                    "ir_calculado": float(ir_calculado_decimal),
                    "diferenca": float(diferenca)
                }
            )
    
    def validar_aliquota(
        self,
        tipo_operacao: str,
        aliquota_usada: float
    ) -> ResultadoValidacao:
        """
        Valida se a alíquota aplicada está correta para o tipo de operação.
        
        Args:
            tipo_operacao: 'DAY_TRADE' ou 'SWING_TRADE'.
            aliquota_usada: Alíquota que foi aplicada.
            
        Returns:
            Resultado da validação.
        """
        aliquota_decimal = Decimal(str(aliquota_usada))
        
        if tipo_operacao == "DAY_TRADE":
            aliquota_correta = self.ALIQUOTA_DAY_TRADE
        elif tipo_operacao == "SWING_TRADE":
            aliquota_correta = self.ALIQUOTA_SWING_TRADE
        else:
            return ResultadoValidacao(
                valido=False,
                tipo=TipoValidacao.REGRA_TRIBUTARIA,
                nivel_confianca=NivelConfianca.BAIXA,
                mensagem=f"Tipo de operação desconhecido: {tipo_operacao}"
            )
        
        if aliquota_decimal == aliquota_correta:
            return ResultadoValidacao(
                valido=True,
                tipo=TipoValidacao.REGRA_TRIBUTARIA,
                nivel_confianca=NivelConfianca.ALTA,
                mensagem=f"Alíquota de {aliquota_usada*100:.0f}% correta para {tipo_operacao}."
            )
        else:
            return ResultadoValidacao(
                valido=False,
                tipo=TipoValidacao.REGRA_TRIBUTARIA,
                nivel_confianca=NivelConfianca.BAIXA,
                mensagem=(
                    f"Alíquota incorreta! "
                    f"Esperado: {float(aliquota_correta)*100:.0f}%, "
                    f"Usado: {aliquota_usada*100:.0f}%"
                )
            )
    
    def validar_isencao(
        self,
        tipo_operacao: str,
        total_vendas_mes: float,
        isento: bool
    ) -> ResultadoValidacao:
        """
        Valida se o status de isenção está correto.
        
        Args:
            tipo_operacao: 'DAY_TRADE' ou 'SWING_TRADE'.
            total_vendas_mes: Total de vendas no mês.
            isento: Status de isenção informado.
            
        Returns:
            Resultado da validação.
        """
        total_decimal = Decimal(str(total_vendas_mes))
        
        if tipo_operacao == "DAY_TRADE":
            isento_esperado = False
        else:
            isento_esperado = total_decimal <= self.LIMITE_ISENCAO
        
        if isento == isento_esperado:
            return ResultadoValidacao(
                valido=True,
                tipo=TipoValidacao.REGRA_TRIBUTARIA,
                nivel_confianca=NivelConfianca.ALTA,
                mensagem="Status de isenção validado corretamente.",
                detalhes={
                    "total_vendas": float(total_decimal),
                    "limite": float(self.LIMITE_ISENCAO),
                    "isento": isento
                }
            )
        else:
            return ResultadoValidacao(
                valido=False,
                tipo=TipoValidacao.REGRA_TRIBUTARIA,
                nivel_confianca=NivelConfianca.BAIXA,
                mensagem=(
                    f"Status de isenção incorreto! "
                    f"Total vendas: R$ {total_vendas_mes:,.2f}, "
                    f"Deveria ser: {'ISENTO' if isento_esperado else 'TRIBUTÁVEL'}"
                )
            )
    
    def verificar_escopo(self, texto: str) -> ResultadoValidacao:
        """
        Verifica se a pergunta está dentro do escopo de atendimento.
        
        Args:
            texto: Texto da pergunta do usuário.
            
        Returns:
            Resultado da validação com nível de confiança.
        """
        texto_lower = texto.lower()
        
        topicos_encontrados = []
        for topico in self.TOPICOS_FORA_ESCOPO:
            if topico in texto_lower:
                topicos_encontrados.append(topico)
        
        if topicos_encontrados:
            return ResultadoValidacao(
                valido=False,
                tipo=TipoValidacao.ESCOPO_ATENDIMENTO,
                nivel_confianca=NivelConfianca.REQUER_VALIDACAO,
                mensagem=(
                    "Esta pergunta envolve tópicos fora do meu escopo de especialização. "
                    "Meu foco é em ações negociadas no mercado à vista da B3."
                ),
                detalhes={"topicos_detectados": topicos_encontrados}
            )
        
        termos_encontrados = []
        for termo in self.TERMOS_SUSPEITOS:
            if termo in texto_lower:
                termos_encontrados.append(termo)
        
        if termos_encontrados:
            return ResultadoValidacao(
                valido=False,
                tipo=TipoValidacao.ESCOPO_ATENDIMENTO,
                nivel_confianca=NivelConfianca.REQUER_VALIDACAO,
                mensagem=(
                    "Não posso ajudar com práticas ilegais. "
                    "Posso te mostrar formas LEGAIS de otimização tributária."
                ),
                detalhes={"termos_detectados": termos_encontrados}
            )
        
        return ResultadoValidacao(
            valido=True,
            tipo=TipoValidacao.ESCOPO_ATENDIMENTO,
            nivel_confianca=NivelConfianca.ALTA,
            mensagem="Pergunta dentro do escopo de atendimento."
        )
    
    def validar_consistencia_operacao(
        self,
        quantidade: int,
        preco_unitario: float,
        valor_total: float,
        tolerancia: float = 0.01
    ) -> ResultadoValidacao:
        """
        Valida se os dados da operação são consistentes.
        
        Args:
            quantidade: Quantidade de ações.
            preco_unitario: Preço por ação.
            valor_total: Valor total da operação.
            tolerancia: Margem de erro aceitável.
            
        Returns:
            Resultado da validação.
        """
        if quantidade <= 0:
            return ResultadoValidacao(
                valido=False,
                tipo=TipoValidacao.CONSISTENCIA_DADOS,
                nivel_confianca=NivelConfianca.BAIXA,
                mensagem="Quantidade deve ser maior que zero."
            )
        
        if preco_unitario <= 0:
            return ResultadoValidacao(
                valido=False,
                tipo=TipoValidacao.CONSISTENCIA_DADOS,
                nivel_confianca=NivelConfianca.BAIXA,
                mensagem="Preço unitário deve ser maior que zero."
            )
        
        valor_esperado = Decimal(str(quantidade)) * Decimal(str(preco_unitario))
        valor_informado = Decimal(str(valor_total))
        diferenca = abs(valor_esperado - valor_informado)
        
        if diferenca <= Decimal(str(tolerancia)):
            return ResultadoValidacao(
                valido=True,
                tipo=TipoValidacao.CONSISTENCIA_DADOS,
                nivel_confianca=NivelConfianca.ALTA,
                mensagem="Dados da operação consistentes."
            )
        else:
            return ResultadoValidacao(
                valido=False,
                tipo=TipoValidacao.CONSISTENCIA_DADOS,
                nivel_confianca=NivelConfianca.BAIXA,
                mensagem=(
                    f"Inconsistência nos dados! "
                    f"Esperado: R$ {valor_esperado:,.2f}, "
                    f"Informado: R$ {valor_total:,.2f}"
                )
            )
    
    def validar_resultado_completo(
        self,
        resultado_calculo: dict
    ) -> list[ResultadoValidacao]:
        """
        Realiza validação completa de um resultado de cálculo.
        
        Args:
            resultado_calculo: Dicionário com todos os dados do cálculo.
            
        Returns:
            Lista com todos os resultados de validação.
        """
        validacoes = []
        
        if resultado_calculo.get('base_calculo', 0) > 0:
            validacao_ir = self.validar_calculo_ir(
                lucro=resultado_calculo.get('base_calculo', 0),
                aliquota=resultado_calculo.get('aliquota', 0),
                ir_calculado=resultado_calculo.get('ir_devido', 0)
            )
            validacoes.append(validacao_ir)
        
        tipo_op = resultado_calculo.get('tipo_operacao', '')
        if isinstance(tipo_op, str):
            tipo_str = tipo_op
        else:
            tipo_str = tipo_op.value if hasattr(tipo_op, 'value') else str(tipo_op)
        
        validacao_aliquota = self.validar_aliquota(
            tipo_operacao=tipo_str,
            aliquota_usada=resultado_calculo.get('aliquota', 0)
        )
        validacoes.append(validacao_aliquota)
        
        validacao_isencao = self.validar_isencao(
            tipo_operacao=tipo_str,
            total_vendas_mes=resultado_calculo.get('total_vendas_mes', 0),
            isento=resultado_calculo.get('isento', False)
        )
        validacoes.append(validacao_isencao)
        
        validacao_consistencia = self.validar_consistencia_operacao(
            quantidade=resultado_calculo.get('quantidade', 0),
            preco_unitario=resultado_calculo.get('preco_venda', 0),
            valor_total=resultado_calculo.get('valor_venda', 0)
        )
        validacoes.append(validacao_consistencia)
        
        return validacoes
    
    def obter_nivel_confianca_geral(
        self,
        validacoes: list[ResultadoValidacao]
    ) -> NivelConfianca:
        """
        Determina o nível de confiança geral baseado em todas as validações.
        
        Args:
            validacoes: Lista de resultados de validação.
            
        Returns:
            Nível de confiança geral.
        """
        if not validacoes:
            return NivelConfianca.MEDIA
        
        invalidas = [v for v in validacoes if not v.valido]
        if invalidas:
            return NivelConfianca.BAIXA
        
        niveis = [v.nivel_confianca for v in validacoes]
        if NivelConfianca.REQUER_VALIDACAO in niveis:
            return NivelConfianca.REQUER_VALIDACAO
        if NivelConfianca.BAIXA in niveis:
            return NivelConfianca.BAIXA
        if NivelConfianca.MEDIA in niveis:
            return NivelConfianca.MEDIA
        
        return NivelConfianca.ALTA
    
    def extrair_numeros_da_resposta(self, texto: str) -> list[float]:
        """
        Extrai números monetários de um texto para validação.
        
        Args:
            texto: Texto para análise.
            
        Returns:
            Lista de valores numéricos encontrados.
        """
        padrao = r'R\$\s*([\d.,]+)'
        matches = re.findall(padrao, texto)
        
        valores = []
        for match in matches:
            try:
                valor_limpo = match.replace('.', '').replace(',', '.')
                valores.append(float(valor_limpo))
            except ValueError:
                continue
        
        return valores


validador: Optional[ValidadorAntiAlucinacao] = None


def get_validador() -> ValidadorAntiAlucinacao:
    """
    Obtém a instância global do validador.
    
    Returns:
        Instância do ValidadorAntiAlucinacao.
    """
    global validador
    if validador is None:
        validador = ValidadorAntiAlucinacao()
    return validador
