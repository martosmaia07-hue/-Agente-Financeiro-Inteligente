"""
Módulo de gerenciamento do banco de dados SQLite.

Este módulo é responsável por:
- Criar e gerenciar conexão com o banco SQLite
- Definir schemas das tabelas (operações, impostos, etc.)
- Operações CRUD para operações de compra/venda
- Consultas de histórico e relatórios
"""

import sqlite3
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from loguru import logger
from pydantic import BaseModel, Field


class Operacao(BaseModel):
    """Modelo de dados para uma operação de compra ou venda."""
    
    id: Optional[int] = None
    data: date
    ticker: str = Field(..., min_length=4, max_length=10)
    tipo: str = Field(..., pattern="^(COMPRA|VENDA)$")
    quantidade: int = Field(..., gt=0)
    preco_unitario: float = Field(..., gt=0)
    valor_total: float = Field(..., gt=0)
    corretagem: float = Field(default=0.0, ge=0)
    emolumentos: float = Field(default=0.0, ge=0)
    is_day_trade: bool = False
    created_at: Optional[datetime] = None


class ImpostoCalculado(BaseModel):
    """Modelo de dados para impostos calculados."""
    
    id: Optional[int] = None
    mes_referencia: date
    tipo_operacao: str = Field(..., pattern="^(DAY_TRADE|SWING_TRADE)$")
    lucro_bruto: float
    prejuizo_compensado: float = 0.0
    base_calculo: float
    aliquota: float
    imposto_devido: float
    total_vendas_mes: float
    isento: bool = False
    darf_gerada: bool = False
    pago: bool = False


class DatabaseManager:
    """
    Gerenciador do banco de dados SQLite para o IR Smart.
    
    Attributes:
        db_path: Caminho para o arquivo do banco de dados.
    """
    
    def __init__(self, db_path: str = "database/ir_smart.db") -> None:
        """
        Inicializa o gerenciador do banco de dados.
        
        Args:
            db_path: Caminho para o arquivo SQLite.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logger.info(f"Banco de dados inicializado em: {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Context manager para conexão com o banco."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro no banco de dados: {e}")
            raise
        finally:
            conn.close()
    
    def _init_database(self) -> None:
        """Cria as tabelas do banco de dados se não existirem."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS operacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data DATE NOT NULL,
                    ticker VARCHAR(10) NOT NULL,
                    tipo VARCHAR(6) NOT NULL CHECK (tipo IN ('COMPRA', 'VENDA')),
                    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                    preco_unitario DECIMAL(10,2) NOT NULL CHECK (preco_unitario > 0),
                    valor_total DECIMAL(12,2) NOT NULL CHECK (valor_total > 0),
                    corretagem DECIMAL(8,2) DEFAULT 0,
                    emolumentos DECIMAL(8,2) DEFAULT 0,
                    is_day_trade BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS impostos_calculados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mes_referencia DATE NOT NULL,
                    tipo_operacao VARCHAR(12) NOT NULL CHECK (tipo_operacao IN ('DAY_TRADE', 'SWING_TRADE')),
                    lucro_bruto DECIMAL(12,2),
                    prejuizo_compensado DECIMAL(12,2) DEFAULT 0,
                    base_calculo DECIMAL(12,2),
                    aliquota DECIMAL(5,4),
                    imposto_devido DECIMAL(10,2),
                    total_vendas_mes DECIMAL(12,2),
                    isento BOOLEAN DEFAULT FALSE,
                    darf_gerada BOOLEAN DEFAULT FALSE,
                    pago BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS precos_medios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker VARCHAR(10) NOT NULL UNIQUE,
                    quantidade_total INTEGER DEFAULT 0,
                    preco_medio DECIMAL(10,4) DEFAULT 0,
                    custo_total DECIMAL(12,2) DEFAULT 0,
                    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prejuizos_acumulados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_operacao VARCHAR(12) NOT NULL CHECK (tipo_operacao IN ('DAY_TRADE', 'SWING_TRADE')),
                    valor DECIMAL(12,2) DEFAULT 0,
                    mes_origem DATE,
                    valor_utilizado DECIMAL(12,2) DEFAULT 0,
                    saldo DECIMAL(12,2) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_conversas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sessao_id VARCHAR(50),
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_operacoes_data 
                ON operacoes(data)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_operacoes_ticker 
                ON operacoes(ticker)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_impostos_mes 
                ON impostos_calculados(mes_referencia)
            """)
            
            logger.debug("Tabelas do banco de dados criadas/verificadas")
    
    def inserir_operacao(self, operacao: Operacao) -> int:
        """
        Insere uma nova operação no banco de dados.
        
        Args:
            operacao: Dados da operação a ser inserida.
            
        Returns:
            ID da operação inserida.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO operacoes 
                (data, ticker, tipo, quantidade, preco_unitario, valor_total, 
                 corretagem, emolumentos, is_day_trade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                operacao.data.isoformat(),
                operacao.ticker.upper(),
                operacao.tipo,
                operacao.quantidade,
                operacao.preco_unitario,
                operacao.valor_total,
                operacao.corretagem,
                operacao.emolumentos,
                operacao.is_day_trade
            ))
            
            operacao_id = cursor.lastrowid
            logger.info(f"Operação inserida: ID={operacao_id}, {operacao.tipo} {operacao.quantidade}x {operacao.ticker}")
            
            if operacao.tipo == "COMPRA":
                self._atualizar_preco_medio(conn, operacao)
            
            return operacao_id
    
    def _atualizar_preco_medio(self, conn: sqlite3.Connection, operacao: Operacao) -> None:
        """Atualiza o preço médio de um ativo após uma compra."""
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT quantidade_total, preco_medio, custo_total 
            FROM precos_medios WHERE ticker = ?
        """, (operacao.ticker.upper(),))
        
        resultado = cursor.fetchone()
        
        custo_operacao = operacao.valor_total + operacao.corretagem + operacao.emolumentos
        
        if resultado:
            qtd_atual = resultado['quantidade_total']
            custo_atual = resultado['custo_total']
            
            nova_qtd = qtd_atual + operacao.quantidade
            novo_custo = custo_atual + custo_operacao
            novo_preco_medio = novo_custo / nova_qtd if nova_qtd > 0 else 0
            
            cursor.execute("""
                UPDATE precos_medios 
                SET quantidade_total = ?, preco_medio = ?, custo_total = ?,
                    ultima_atualizacao = CURRENT_TIMESTAMP
                WHERE ticker = ?
            """, (nova_qtd, novo_preco_medio, novo_custo, operacao.ticker.upper()))
        else:
            preco_medio = custo_operacao / operacao.quantidade
            cursor.execute("""
                INSERT INTO precos_medios (ticker, quantidade_total, preco_medio, custo_total)
                VALUES (?, ?, ?, ?)
            """, (operacao.ticker.upper(), operacao.quantidade, preco_medio, custo_operacao))
        
        logger.debug(f"Preço médio atualizado para {operacao.ticker}")
    
    def obter_preco_medio(self, ticker: str) -> Optional[dict]:
        """
        Obtém o preço médio de um ativo.
        
        Args:
            ticker: Código do ativo.
            
        Returns:
            Dicionário com quantidade_total, preco_medio e custo_total.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT quantidade_total, preco_medio, custo_total, ultima_atualizacao
                FROM precos_medios WHERE ticker = ?
            """, (ticker.upper(),))
            
            resultado = cursor.fetchone()
            if resultado:
                return dict(resultado)
            return None
    
    def obter_vendas_mes(self, ano: int, mes: int) -> float:
        """
        Obtém o total de vendas de um determinado mês.
        
        Args:
            ano: Ano de referência.
            mes: Mês de referência (1-12).
            
        Returns:
            Valor total das vendas no mês.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            data_inicio = f"{ano:04d}-{mes:02d}-01"
            if mes == 12:
                data_fim = f"{ano + 1:04d}-01-01"
            else:
                data_fim = f"{ano:04d}-{mes + 1:02d}-01"
            
            cursor.execute("""
                SELECT COALESCE(SUM(valor_total), 0) as total
                FROM operacoes 
                WHERE tipo = 'VENDA' 
                AND data >= ? AND data < ?
            """, (data_inicio, data_fim))
            
            resultado = cursor.fetchone()
            return float(resultado['total']) if resultado else 0.0
    
    def obter_operacoes_mes(self, ano: int, mes: int) -> list[dict]:
        """
        Obtém todas as operações de um determinado mês.
        
        Args:
            ano: Ano de referência.
            mes: Mês de referência (1-12).
            
        Returns:
            Lista de operações do mês.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            data_inicio = f"{ano:04d}-{mes:02d}-01"
            if mes == 12:
                data_fim = f"{ano + 1:04d}-01-01"
            else:
                data_fim = f"{ano:04d}-{mes + 1:02d}-01"
            
            cursor.execute("""
                SELECT * FROM operacoes 
                WHERE data >= ? AND data < ?
                ORDER BY data, id
            """, (data_inicio, data_fim))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def obter_prejuizo_acumulado(self, tipo_operacao: str) -> float:
        """
        Obtém o prejuízo acumulado de um tipo de operação.
        
        Args:
            tipo_operacao: 'DAY_TRADE' ou 'SWING_TRADE'.
            
        Returns:
            Valor do prejuízo acumulado.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(saldo), 0) as total
                FROM prejuizos_acumulados 
                WHERE tipo_operacao = ? AND saldo > 0
            """, (tipo_operacao,))
            
            resultado = cursor.fetchone()
            return float(resultado['total']) if resultado else 0.0
    
    def registrar_prejuizo(self, tipo_operacao: str, valor: float, mes_origem: date) -> int:
        """
        Registra um novo prejuízo acumulado.
        
        Args:
            tipo_operacao: 'DAY_TRADE' ou 'SWING_TRADE'.
            valor: Valor do prejuízo (positivo).
            mes_origem: Mês de origem do prejuízo.
            
        Returns:
            ID do registro.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO prejuizos_acumulados 
                (tipo_operacao, valor, mes_origem, saldo)
                VALUES (?, ?, ?, ?)
            """, (tipo_operacao, abs(valor), mes_origem.isoformat(), abs(valor)))
            
            logger.info(f"Prejuízo registrado: {tipo_operacao} R$ {valor:.2f}")
            return cursor.lastrowid
    
    def compensar_prejuizo(self, tipo_operacao: str, valor_lucro: float) -> float:
        """
        Compensa prejuízos acumulados com lucro obtido.
        
        Args:
            tipo_operacao: 'DAY_TRADE' ou 'SWING_TRADE'.
            valor_lucro: Valor do lucro a ser compensado.
            
        Returns:
            Valor efetivamente compensado.
        """
        prejuizo_disponivel = self.obter_prejuizo_acumulado(tipo_operacao)
        valor_compensar = min(prejuizo_disponivel, valor_lucro)
        
        if valor_compensar <= 0:
            return 0.0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, saldo FROM prejuizos_acumulados 
                WHERE tipo_operacao = ? AND saldo > 0
                ORDER BY mes_origem ASC
            """, (tipo_operacao,))
            
            prejuizos = cursor.fetchall()
            restante = valor_compensar
            
            for prejuizo in prejuizos:
                if restante <= 0:
                    break
                
                compensar = min(prejuizo['saldo'], restante)
                novo_saldo = prejuizo['saldo'] - compensar
                
                cursor.execute("""
                    UPDATE prejuizos_acumulados 
                    SET valor_utilizado = valor_utilizado + ?, saldo = ?
                    WHERE id = ?
                """, (compensar, novo_saldo, prejuizo['id']))
                
                restante -= compensar
            
            logger.info(f"Prejuízo compensado: {tipo_operacao} R$ {valor_compensar:.2f}")
            return valor_compensar
    
    def salvar_imposto_calculado(self, imposto: ImpostoCalculado) -> int:
        """
        Salva um cálculo de imposto no banco de dados.
        
        Args:
            imposto: Dados do imposto calculado.
            
        Returns:
            ID do registro.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO impostos_calculados 
                (mes_referencia, tipo_operacao, lucro_bruto, prejuizo_compensado,
                 base_calculo, aliquota, imposto_devido, total_vendas_mes, isento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                imposto.mes_referencia.isoformat(),
                imposto.tipo_operacao,
                imposto.lucro_bruto,
                imposto.prejuizo_compensado,
                imposto.base_calculo,
                imposto.aliquota,
                imposto.imposto_devido,
                imposto.total_vendas_mes,
                imposto.isento
            ))
            
            logger.info(f"Imposto salvo: {imposto.tipo_operacao} {imposto.mes_referencia} = R$ {imposto.imposto_devido:.2f}")
            return cursor.lastrowid
    
    def salvar_mensagem_conversa(self, sessao_id: str, role: str, content: str) -> int:
        """
        Salva uma mensagem do histórico de conversa.
        
        Args:
            sessao_id: Identificador da sessão.
            role: 'user', 'assistant' ou 'system'.
            content: Conteúdo da mensagem.
            
        Returns:
            ID do registro.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO historico_conversas (sessao_id, role, content)
                VALUES (?, ?, ?)
            """, (sessao_id, role, content))
            
            return cursor.lastrowid
    
    def obter_historico_conversa(self, sessao_id: str, limite: int = 20) -> list[dict]:
        """
        Obtém o histórico de conversa de uma sessão.
        
        Args:
            sessao_id: Identificador da sessão.
            limite: Número máximo de mensagens a retornar.
            
        Returns:
            Lista de mensagens ordenadas cronologicamente.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content, created_at 
                FROM historico_conversas 
                WHERE sessao_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (sessao_id, limite))
            
            mensagens = [dict(row) for row in cursor.fetchall()]
            return list(reversed(mensagens))
    
    def atualizar_quantidade_apos_venda(self, ticker: str, quantidade_vendida: int) -> None:
        """
        Atualiza a quantidade de um ativo após uma venda.
        
        Args:
            ticker: Código do ativo.
            quantidade_vendida: Quantidade vendida.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT quantidade_total, preco_medio 
                FROM precos_medios WHERE ticker = ?
            """, (ticker.upper(),))
            
            resultado = cursor.fetchone()
            if resultado:
                nova_qtd = max(0, resultado['quantidade_total'] - quantidade_vendida)
                novo_custo = nova_qtd * resultado['preco_medio']
                
                cursor.execute("""
                    UPDATE precos_medios 
                    SET quantidade_total = ?, custo_total = ?,
                        ultima_atualizacao = CURRENT_TIMESTAMP
                    WHERE ticker = ?
                """, (nova_qtd, novo_custo, ticker.upper()))
                
                logger.debug(f"Quantidade atualizada para {ticker}: {nova_qtd} ações")


db_manager: Optional[DatabaseManager] = None


def get_database() -> DatabaseManager:
    """
    Obtém a instância global do gerenciador de banco de dados.
    
    Returns:
        Instância do DatabaseManager.
    """
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
