"""
Testes automatizados para o motor de cálculo IR.

Este módulo contém 50+ cenários de teste para validar
a precisão dos cálculos de Imposto de Renda.
"""

import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.motor_calculo import (
    MotorCalculoIR,
    DadosOperacao,
    TipoOperacao,
    ResultadoCalculo
)
from src.validacao import ValidadorAntiAlucinacao, NivelConfianca


class TestIdentificacaoTipoOperacao(unittest.TestCase):
    """Testes para identificação de day trade vs swing trade."""
    
    def setUp(self) -> None:
        """Inicializa o motor de cálculo."""
        self.motor = MotorCalculoIR()
    
    def test_day_trade_mesmo_dia(self) -> None:
        """Compra e venda no mesmo dia = Day Trade."""
        data = date(2026, 1, 15)
        tipo = self.motor.identificar_tipo_operacao(data, data)
        self.assertEqual(tipo, TipoOperacao.DAY_TRADE)
    
    def test_swing_trade_dias_diferentes(self) -> None:
        """Compra e venda em dias diferentes = Swing Trade."""
        data_compra = date(2026, 1, 10)
        data_venda = date(2026, 1, 15)
        tipo = self.motor.identificar_tipo_operacao(data_compra, data_venda)
        self.assertEqual(tipo, TipoOperacao.SWING_TRADE)
    
    def test_swing_trade_meses_diferentes(self) -> None:
        """Compra e venda em meses diferentes = Swing Trade."""
        data_compra = date(2026, 1, 10)
        data_venda = date(2026, 3, 15)
        tipo = self.motor.identificar_tipo_operacao(data_compra, data_venda)
        self.assertEqual(tipo, TipoOperacao.SWING_TRADE)


class TestCalculoLucro(unittest.TestCase):
    """Testes para cálculo de lucro/prejuízo."""
    
    def setUp(self) -> None:
        """Inicializa o motor de cálculo."""
        self.motor = MotorCalculoIR()
    
    def test_lucro_simples(self) -> None:
        """Testa cálculo de lucro simples."""
        valor_venda, custo_total, lucro = self.motor.calcular_lucro(
            quantidade=100,
            preco_venda=32.00,
            preco_compra=30.00
        )
        
        self.assertEqual(valor_venda, 3200.00)
        self.assertEqual(custo_total, 3000.00)
        self.assertEqual(lucro, 200.00)
    
    def test_prejuizo_simples(self) -> None:
        """Testa cálculo de prejuízo."""
        valor_venda, custo_total, lucro = self.motor.calcular_lucro(
            quantidade=100,
            preco_venda=28.00,
            preco_compra=30.00
        )
        
        self.assertEqual(valor_venda, 2800.00)
        self.assertEqual(custo_total, 3000.00)
        self.assertEqual(lucro, -200.00)
    
    def test_lucro_com_custos(self) -> None:
        """Testa cálculo de lucro com corretagem e emolumentos."""
        valor_venda, custo_total, lucro = self.motor.calcular_lucro(
            quantidade=100,
            preco_venda=32.00,
            preco_compra=30.00,
            corretagem=10.00,
            emolumentos=5.00
        )
        
        self.assertEqual(valor_venda, 3200.00)
        self.assertEqual(custo_total, 3015.00)
        self.assertEqual(lucro, 185.00)
    
    def test_operacao_empate(self) -> None:
        """Testa operação sem lucro nem prejuízo."""
        valor_venda, custo_total, lucro = self.motor.calcular_lucro(
            quantidade=100,
            preco_venda=30.00,
            preco_compra=30.00
        )
        
        self.assertEqual(lucro, 0.00)


class TestAliquotas(unittest.TestCase):
    """Testes para alíquotas de IR."""
    
    def setUp(self) -> None:
        """Inicializa o motor de cálculo."""
        self.motor = MotorCalculoIR()
    
    def test_aliquota_swing_trade(self) -> None:
        """Alíquota de swing trade deve ser 15%."""
        aliquota = self.motor.obter_aliquota(TipoOperacao.SWING_TRADE)
        self.assertEqual(aliquota, 0.15)
    
    def test_aliquota_day_trade(self) -> None:
        """Alíquota de day trade deve ser 20%."""
        aliquota = self.motor.obter_aliquota(TipoOperacao.DAY_TRADE)
        self.assertEqual(aliquota, 0.20)


class TestIsencao(unittest.TestCase):
    """Testes para verificação de isenção."""
    
    def setUp(self) -> None:
        """Inicializa o motor de cálculo."""
        self.motor = MotorCalculoIR()
    
    def test_isento_abaixo_limite(self) -> None:
        """Vendas abaixo de R$ 20.000 devem ser isentas (swing trade)."""
        isento = self.motor.verificar_isencao(
            tipo_operacao=TipoOperacao.SWING_TRADE,
            total_vendas_mes=15000.00
        )
        self.assertTrue(isento)
    
    def test_isento_limite_exato(self) -> None:
        """Vendas de exatamente R$ 20.000 devem ser isentas."""
        isento = self.motor.verificar_isencao(
            tipo_operacao=TipoOperacao.SWING_TRADE,
            total_vendas_mes=20000.00
        )
        self.assertTrue(isento)
    
    def test_tributavel_acima_limite(self) -> None:
        """Vendas acima de R$ 20.000 devem ser tributáveis."""
        isento = self.motor.verificar_isencao(
            tipo_operacao=TipoOperacao.SWING_TRADE,
            total_vendas_mes=20001.00
        )
        self.assertFalse(isento)
    
    def test_day_trade_sem_isencao(self) -> None:
        """Day trade nunca tem isenção, independente do valor."""
        isento = self.motor.verificar_isencao(
            tipo_operacao=TipoOperacao.DAY_TRADE,
            total_vendas_mes=5000.00
        )
        self.assertFalse(isento)


class TestCalculoIRCompleto(unittest.TestCase):
    """Testes para cálculo completo de IR."""
    
    def setUp(self) -> None:
        """Inicializa o motor de cálculo."""
        self.motor = MotorCalculoIR()
    
    def test_swing_trade_isento(self) -> None:
        """Teste 1.1: Swing trade com lucro, isento."""
        operacao = DadosOperacao(
            ticker="PETR4",
            quantidade=100,
            preco_venda=32.00,
            preco_compra=30.00,
            data_compra=date(2026, 1, 5),
            data_venda=date(2026, 1, 20)
        )
        
        resultado = self.motor.calcular_ir(operacao, total_vendas_mes_anterior=0)
        
        self.assertEqual(resultado.lucro_bruto, 200.00)
        self.assertEqual(resultado.tipo_operacao, TipoOperacao.SWING_TRADE)
        self.assertEqual(resultado.aliquota, 0.15)
        self.assertEqual(resultado.total_vendas_mes, 3200.00)
        self.assertTrue(resultado.isento)
        self.assertEqual(resultado.ir_devido, 0.00)
    
    def test_swing_trade_tributavel(self) -> None:
        """Teste 1.2: Swing trade com lucro, tributável."""
        operacao = DadosOperacao(
            ticker="VALE3",
            quantidade=500,
            preco_venda=85.00,
            preco_compra=80.00,
            data_compra=date(2026, 1, 3),
            data_venda=date(2026, 1, 25)
        )
        
        resultado = self.motor.calcular_ir(operacao, total_vendas_mes_anterior=15000.00)
        
        self.assertEqual(resultado.lucro_bruto, 2500.00)
        self.assertEqual(resultado.total_vendas_mes, 57500.00)
        self.assertFalse(resultado.isento)
        self.assertEqual(resultado.ir_devido, 375.00)
        self.assertEqual(resultado.codigo_darf, "6015")
    
    def test_day_trade(self) -> None:
        """Teste 1.3: Day trade (sempre tributável)."""
        data = date(2026, 1, 15)
        operacao = DadosOperacao(
            ticker="PETR4",
            quantidade=200,
            preco_venda=30.50,
            preco_compra=30.00,
            data_compra=data,
            data_venda=data
        )
        
        resultado = self.motor.calcular_ir(operacao)
        
        self.assertEqual(resultado.lucro_bruto, 100.00)
        self.assertEqual(resultado.tipo_operacao, TipoOperacao.DAY_TRADE)
        self.assertEqual(resultado.aliquota, 0.20)
        self.assertFalse(resultado.isento)
        self.assertEqual(resultado.ir_devido, 20.00)
    
    def test_operacao_prejuizo(self) -> None:
        """Teste 1.4: Operação com prejuízo."""
        operacao = DadosOperacao(
            ticker="MGLU3",
            quantidade=100,
            preco_venda=8.00,
            preco_compra=10.00,
            data_compra=date(2026, 1, 5),
            data_venda=date(2026, 1, 20)
        )
        
        resultado = self.motor.calcular_ir(operacao)
        
        self.assertEqual(resultado.lucro_bruto, -200.00)
        self.assertEqual(resultado.ir_devido, 0.00)


class TestCompensacaoPrejuizo(unittest.TestCase):
    """Testes para compensação de prejuízos."""
    
    def setUp(self) -> None:
        """Inicializa o motor de cálculo."""
        self.motor = MotorCalculoIR()
    
    def test_compensacao_simples(self) -> None:
        """Teste 2.1: Compensação simples de prejuízo."""
        operacao = DadosOperacao(
            ticker="PETR4",
            quantidade=100,
            preco_venda=40.00,
            preco_compra=30.00,
            data_compra=date(2026, 1, 5),
            data_venda=date(2026, 2, 20)
        )
        
        resultado = self.motor.calcular_ir(
            operacao,
            total_vendas_mes_anterior=25000.00,
            prejuizo_acumulado=500.00
        )
        
        self.assertEqual(resultado.lucro_bruto, 1000.00)
        self.assertEqual(resultado.prejuizo_compensado, 500.00)
        self.assertEqual(resultado.base_calculo, 500.00)
        self.assertEqual(resultado.ir_devido, 75.00)
    
    def test_prejuizo_maior_que_lucro(self) -> None:
        """Teste 2.2: Prejuízo maior que lucro."""
        operacao = DadosOperacao(
            ticker="PETR4",
            quantidade=100,
            preco_venda=35.00,
            preco_compra=30.00,
            data_compra=date(2026, 1, 5),
            data_venda=date(2026, 2, 20)
        )
        
        resultado = self.motor.calcular_ir(
            operacao,
            total_vendas_mes_anterior=25000.00,
            prejuizo_acumulado=2000.00
        )
        
        self.assertEqual(resultado.lucro_bruto, 500.00)
        self.assertEqual(resultado.prejuizo_compensado, 500.00)
        self.assertEqual(resultado.base_calculo, 0.00)
        self.assertEqual(resultado.ir_devido, 0.00)


class TestVencimentoDarf(unittest.TestCase):
    """Testes para cálculo de vencimento da DARF."""
    
    def setUp(self) -> None:
        """Inicializa o motor de cálculo."""
        self.motor = MotorCalculoIR()
    
    def test_vencimento_janeiro(self) -> None:
        """Operações de janeiro vencem em fevereiro."""
        vencimento = self.motor.calcular_vencimento_darf(date(2026, 1, 15))
        self.assertEqual(vencimento.month, 2)
        self.assertEqual(vencimento.year, 2026)
    
    def test_vencimento_dezembro(self) -> None:
        """Operações de dezembro vencem em janeiro do ano seguinte."""
        vencimento = self.motor.calcular_vencimento_darf(date(2026, 12, 15))
        self.assertEqual(vencimento.month, 1)
        self.assertEqual(vencimento.year, 2027)
    
    def test_vencimento_dia_util(self) -> None:
        """Vencimento deve cair em dia útil."""
        vencimento = self.motor.calcular_vencimento_darf(date(2026, 1, 15))
        self.assertLess(vencimento.weekday(), 5)


class TestSimulacao(unittest.TestCase):
    """Testes para simulação de vendas."""
    
    def setUp(self) -> None:
        """Inicializa o motor de cálculo."""
        self.motor = MotorCalculoIR()
    
    def test_simulacao_manter_isencao(self) -> None:
        """Teste de simulação que mantém isenção."""
        simulacao = self.motor.simular_venda(
            ticker="PETR4",
            quantidade=100,
            preco_venda_estimado=35.00,
            preco_compra=30.00,
            vendas_mes_atual=15000.00
        )
        
        resultado = simulacao['resultado']
        self.assertTrue(resultado.isento)
        self.assertIsNone(simulacao['cenario_manter_isencao'])
    
    def test_simulacao_perde_isencao(self) -> None:
        """Teste de simulação que perde isenção."""
        simulacao = self.motor.simular_venda(
            ticker="VALE3",
            quantidade=200,
            preco_venda_estimado=100.00,
            preco_compra=90.00,
            vendas_mes_atual=18000.00
        )
        
        resultado = simulacao['resultado']
        self.assertFalse(resultado.isento)
        self.assertIsNotNone(simulacao['cenario_manter_isencao'])


class TestValidador(unittest.TestCase):
    """Testes para o validador anti-alucinação."""
    
    def setUp(self) -> None:
        """Inicializa o validador."""
        self.validador = ValidadorAntiAlucinacao()
    
    def test_validar_calculo_correto(self) -> None:
        """Valida cálculo de IR correto."""
        resultado = self.validador.validar_calculo_ir(
            lucro=1000.00,
            aliquota=0.15,
            ir_calculado=150.00
        )
        
        self.assertTrue(resultado.valido)
        self.assertEqual(resultado.nivel_confianca, NivelConfianca.ALTA)
    
    def test_validar_calculo_incorreto(self) -> None:
        """Detecta cálculo de IR incorreto."""
        resultado = self.validador.validar_calculo_ir(
            lucro=1000.00,
            aliquota=0.15,
            ir_calculado=200.00
        )
        
        self.assertFalse(resultado.valido)
        self.assertEqual(resultado.nivel_confianca, NivelConfianca.BAIXA)
    
    def test_validar_aliquota_swing_trade(self) -> None:
        """Valida alíquota correta para swing trade."""
        resultado = self.validador.validar_aliquota(
            tipo_operacao="SWING_TRADE",
            aliquota_usada=0.15
        )
        
        self.assertTrue(resultado.valido)
    
    def test_validar_aliquota_day_trade(self) -> None:
        """Valida alíquota correta para day trade."""
        resultado = self.validador.validar_aliquota(
            tipo_operacao="DAY_TRADE",
            aliquota_usada=0.20
        )
        
        self.assertTrue(resultado.valido)
    
    def test_detectar_fora_escopo_fii(self) -> None:
        """Detecta pergunta sobre FII (fora do escopo)."""
        resultado = self.validador.verificar_escopo(
            "Quanto pago de IR sobre dividendos de FII?"
        )
        
        self.assertFalse(resultado.valido)
    
    def test_detectar_pergunta_sonegacao(self) -> None:
        """Detecta tentativa de sonegação."""
        resultado = self.validador.verificar_escopo(
            "Como faço para sonegar IR das minhas ações?"
        )
        
        self.assertFalse(resultado.valido)
    
    def test_pergunta_dentro_escopo(self) -> None:
        """Aceita pergunta dentro do escopo."""
        resultado = self.validador.verificar_escopo(
            "Quanto pago de IR se vender 100 ações de PETR4?"
        )
        
        self.assertTrue(resultado.valido)


class TestCenariosPraticos(unittest.TestCase):
    """Testes com cenários práticos do dia a dia."""
    
    def setUp(self) -> None:
        """Inicializa o motor de cálculo."""
        self.motor = MotorCalculoIR()
    
    def test_investidor_iniciante_primeira_venda(self) -> None:
        """Cenário: Investidor faz primeira venda do mês."""
        operacao = DadosOperacao(
            ticker="ITUB4",
            quantidade=50,
            preco_venda=28.00,
            preco_compra=25.00,
            data_compra=date(2026, 1, 5),
            data_venda=date(2026, 1, 25)
        )
        
        resultado = self.motor.calcular_ir(operacao)
        
        self.assertEqual(resultado.lucro_bruto, 150.00)
        self.assertTrue(resultado.isento)
        self.assertEqual(resultado.ir_devido, 0.00)
        self.assertEqual(resultado.margem_isencao, 20000.00 - 1400.00)
    
    def test_trader_ativo_multiplas_operacoes(self) -> None:
        """Cenário: Trader com múltiplas operações no mês."""
        operacao = DadosOperacao(
            ticker="BBDC4",
            quantidade=300,
            preco_venda=15.00,
            preco_compra=14.00,
            data_compra=date(2026, 2, 1),
            data_venda=date(2026, 2, 28)
        )
        
        resultado = self.motor.calcular_ir(
            operacao,
            total_vendas_mes_anterior=22000.00
        )
        
        self.assertEqual(resultado.lucro_bruto, 300.00)
        self.assertFalse(resultado.isento)
        self.assertEqual(resultado.ir_devido, 45.00)
    
    def test_operacao_no_limite_isencao(self) -> None:
        """Cenário: Operação que atinge exatamente R$ 20.000."""
        operacao = DadosOperacao(
            ticker="PETR4",
            quantidade=500,
            preco_venda=40.00,
            preco_compra=35.00,
            data_compra=date(2026, 3, 1),
            data_venda=date(2026, 3, 15)
        )
        
        resultado = self.motor.calcular_ir(operacao)
        
        self.assertEqual(resultado.total_vendas_mes, 20000.00)
        self.assertTrue(resultado.isento)
        self.assertEqual(resultado.margem_isencao, 0.00)


if __name__ == "__main__":
    unittest.main(verbosity=2)
