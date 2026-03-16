"""
Sistema de Cache para respostas do GPT.

Este módulo implementa cache para evitar chamadas repetidas à API da OpenAI,
economizando custos e melhorando a performance.

Estratégias implementadas:
1. Cache exato - perguntas idênticas
2. Cache semântico - perguntas similares (usando normalização de texto)
"""

import hashlib
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from loguru import logger


class CacheManager:
    """
    Gerenciador de cache para respostas do GPT.
    
    Attributes:
        db_path: Caminho para o banco de dados.
        ttl_hours: Tempo de vida do cache em horas.
    """
    
    def __init__(
        self, 
        db_path: str = "database/ir_smart.db",
        ttl_hours: int = 24 * 7  # 7 dias por padrão
    ) -> None:
        """
        Inicializa o gerenciador de cache.
        
        Args:
            db_path: Caminho para o banco SQLite.
            ttl_hours: Tempo de vida do cache em horas.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
        self._init_cache_table()
        logger.info(f"Cache inicializado | TTL: {ttl_hours}h")
    
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
            logger.error(f"Erro no cache: {e}")
            raise
        finally:
            conn.close()
    
    def _init_cache_table(self) -> None:
        """Cria a tabela de cache se não existir."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache_respostas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pergunta_hash VARCHAR(64) UNIQUE NOT NULL,
                    pergunta_original TEXT NOT NULL,
                    pergunta_normalizada TEXT NOT NULL,
                    resposta TEXT NOT NULL,
                    hits INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_hash 
                ON cache_respostas(pergunta_hash)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_normalizada 
                ON cache_respostas(pergunta_normalizada)
            """)
            
            logger.debug("Tabela de cache criada/verificada")
    
    def _normalizar_texto(self, texto: str) -> str:
        """
        Normaliza o texto para comparação.
        
        Remove acentos, pontuação, converte para minúsculas,
        e remove espaços extras.
        
        Args:
            texto: Texto a ser normalizado.
            
        Returns:
            Texto normalizado.
        """
        texto = texto.lower().strip()
        
        acentos = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
            'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n'
        }
        for acentuado, normal in acentos.items():
            texto = texto.replace(acentuado, normal)
        
        texto = re.sub(r'[^\w\s]', ' ', texto)
        
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    
    def _gerar_hash(self, texto: str) -> str:
        """
        Gera um hash SHA-256 do texto normalizado.
        
        Args:
            texto: Texto para gerar hash.
            
        Returns:
            Hash em hexadecimal.
        """
        texto_normalizado = self._normalizar_texto(texto)
        return hashlib.sha256(texto_normalizado.encode()).hexdigest()
    
    def _is_pergunta_generica(self, texto: str) -> bool:
        """
        Verifica se a pergunta é genérica (pode ser cacheada).
        
        Perguntas com dados específicos do usuário não devem ser cacheadas.
        
        Args:
            texto: Texto da pergunta.
            
        Returns:
            True se genérica, False se específica.
        """
        texto_lower = texto.lower()
        
        perguntas_especificas_usuario = [
            "estou isento", "sou isento", "meu imposto", "minha isenção",
            "quanto pago", "quanto devo", "meu prejuízo", "meu prejuizo",
            "minhas vendas", "minha margem", "quanto posso vender",
            "se eu vender", "posso vender", "minha situação", "minha situacao"
        ]
        
        for termo in perguntas_especificas_usuario:
            if termo in texto_lower:
                return False
        
        perguntas_genericas = [
            "o que é", "o que sao", "qual a diferença", "como funciona",
            "me explica", "explique", "o que significa", "quando vence",
            "day trade", "swing trade", "isencao", "isenção", 
            "prejuizo", "prejuízo", "compensar", "compensação",
            "darf", "aliquota", "alíquota", "imposto de renda",
            "como declarar", "como calcular"
        ]
        
        for termo in perguntas_genericas:
            if termo in texto_lower:
                return True
        
        tem_ticker = bool(re.search(r'\b[A-Z]{4}\d{1,2}\b', texto.upper()))
        tem_valor = bool(re.search(r'R\$\s*[\d.,]+', texto))
        tem_quantidade = bool(re.search(r'\b\d+\s*(ações?|acoes?)\b', texto_lower))
        
        if tem_ticker or tem_valor or tem_quantidade:
            return False
        
        return True
    
    def buscar(self, pergunta: str) -> Optional[str]:
        """
        Busca uma resposta no cache.
        
        Args:
            pergunta: Pergunta do usuário.
            
        Returns:
            Resposta cacheada ou None se não encontrada.
        """
        if not self._is_pergunta_generica(pergunta):
            logger.debug("Pergunta específica - ignorando cache")
            return None
        
        pergunta_hash = self._gerar_hash(pergunta)
        pergunta_normalizada = self._normalizar_texto(pergunta)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT resposta, created_at, hits
                FROM cache_respostas
                WHERE pergunta_hash = ?
            """, (pergunta_hash,))
            
            resultado = cursor.fetchone()
            
            if resultado:
                created_at = datetime.fromisoformat(resultado['created_at'])
                idade = datetime.now() - created_at
                
                if idade.total_seconds() / 3600 > self.ttl_hours:
                    logger.debug(f"Cache expirado para: {pergunta[:50]}...")
                    self._remover_expirado(pergunta_hash)
                    return None
                
                cursor.execute("""
                    UPDATE cache_respostas 
                    SET hits = hits + 1, last_accessed = CURRENT_TIMESTAMP
                    WHERE pergunta_hash = ?
                """, (pergunta_hash,))
                
                logger.info(f"✅ Cache HIT! Hits: {resultado['hits'] + 1}")
                return resultado['resposta']
            
            cursor.execute("""
                SELECT resposta, pergunta_hash, hits
                FROM cache_respostas
                WHERE pergunta_normalizada = ?
            """, (pergunta_normalizada,))
            
            resultado = cursor.fetchone()
            
            if resultado:
                cursor.execute("""
                    UPDATE cache_respostas 
                    SET hits = hits + 1, last_accessed = CURRENT_TIMESTAMP
                    WHERE pergunta_hash = ?
                """, (resultado['pergunta_hash'],))
                
                logger.info(f"✅ Cache HIT (normalizado)! Hits: {resultado['hits'] + 1}")
                return resultado['resposta']
        
        logger.debug(f"Cache MISS para: {pergunta[:50]}...")
        return None
    
    def salvar(self, pergunta: str, resposta: str) -> None:
        """
        Salva uma resposta no cache.
        
        Args:
            pergunta: Pergunta original.
            resposta: Resposta do GPT.
        """
        if not self._is_pergunta_generica(pergunta):
            logger.debug("Pergunta específica - não salvando no cache")
            return
        
        pergunta_hash = self._gerar_hash(pergunta)
        pergunta_normalizada = self._normalizar_texto(pergunta)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO cache_respostas 
                (pergunta_hash, pergunta_original, pergunta_normalizada, resposta)
                VALUES (?, ?, ?, ?)
            """, (pergunta_hash, pergunta, pergunta_normalizada, resposta))
            
            logger.info(f"💾 Resposta salva no cache: {pergunta[:50]}...")
    
    def _remover_expirado(self, pergunta_hash: str) -> None:
        """Remove um item expirado do cache."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM cache_respostas WHERE pergunta_hash = ?
            """, (pergunta_hash,))
    
    def limpar_expirados(self) -> int:
        """
        Remove todos os itens expirados do cache.
        
        Returns:
            Número de itens removidos.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            data_limite = datetime.now() - timedelta(hours=self.ttl_hours)
            
            cursor.execute("""
                DELETE FROM cache_respostas 
                WHERE created_at < ?
            """, (data_limite.isoformat(),))
            
            removidos = cursor.rowcount
            
            if removidos > 0:
                logger.info(f"🧹 Cache limpo: {removidos} itens expirados removidos")
            
            return removidos
    
    def obter_estatisticas(self) -> dict:
        """
        Retorna estatísticas do cache.
        
        Returns:
            Dicionário com estatísticas.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as total FROM cache_respostas")
            total = cursor.fetchone()['total']
            
            cursor.execute("SELECT SUM(hits) as total_hits FROM cache_respostas")
            resultado = cursor.fetchone()
            total_hits = resultado['total_hits'] or 0
            
            cursor.execute("""
                SELECT pergunta_original, hits 
                FROM cache_respostas 
                ORDER BY hits DESC 
                LIMIT 5
            """)
            mais_acessadas = [
                {"pergunta": row['pergunta_original'][:50], "hits": row['hits']}
                for row in cursor.fetchall()
            ]
            
            return {
                "total_itens": total,
                "total_hits": total_hits,
                "economia_estimada": total_hits * 0.002,  # ~$0.002 por request
                "mais_acessadas": mais_acessadas
            }
    
    def limpar_tudo(self) -> None:
        """Remove todos os itens do cache."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cache_respostas")
            logger.info("🗑️ Cache completamente limpo")


cache_manager: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """
    Obtém a instância global do cache.
    
    Returns:
        Instância do CacheManager.
    """
    global cache_manager
    if cache_manager is None:
        cache_manager = CacheManager()
    return cache_manager
