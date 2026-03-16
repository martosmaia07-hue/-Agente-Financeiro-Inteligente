"""
Funções utilitárias para o IR Smart.

Este módulo contém funções auxiliares utilizadas em todo o projeto:
- Formatação de valores monetários
- Parsing de datas
- Extração de dados de operações do texto
- Geração de DARF
- Helpers diversos
"""

import re
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from loguru import logger


def formatar_moeda(valor: float, simbolo: str = "R$") -> str:
    """
    Formata um valor numérico como moeda brasileira.
    
    Args:
        valor: Valor a ser formatado.
        simbolo: Símbolo da moeda (padrão: R$).
        
    Returns:
        String formatada (ex: "R$ 1.234,56").
    """
    valor_decimal = Decimal(str(valor)).quantize(
        Decimal('0.01'), 
        rounding=ROUND_HALF_UP
    )
    
    parte_inteira = int(abs(valor_decimal))
    parte_decimal = abs(valor_decimal) - parte_inteira
    
    inteiro_formatado = f"{parte_inteira:,}".replace(",", ".")
    decimal_formatado = str(parte_decimal)[2:4].ljust(2, '0')
    
    sinal = "-" if valor < 0 else ""
    
    return f"{sinal}{simbolo} {inteiro_formatado},{decimal_formatado}"


def formatar_percentual(valor: float, casas_decimais: int = 0) -> str:
    """
    Formata um valor decimal como percentual.
    
    Args:
        valor: Valor decimal (ex: 0.15 para 15%).
        casas_decimais: Número de casas decimais.
        
    Returns:
        String formatada (ex: "15%").
    """
    percentual = valor * 100
    return f"{percentual:.{casas_decimais}f}%"


def formatar_data(data: date, formato: str = "%d/%m/%Y") -> str:
    """
    Formata uma data para exibição.
    
    Args:
        data: Objeto date.
        formato: Formato de saída (padrão: DD/MM/YYYY).
        
    Returns:
        String da data formatada.
    """
    return data.strftime(formato)


def parse_data(texto: str) -> Optional[date]:
    """
    Converte uma string de data para objeto date.
    
    Formatos suportados:
    - DD/MM/YYYY
    - DD-MM-YYYY
    - YYYY-MM-DD
    - DD/MM/YY
    
    Args:
        texto: String com a data.
        
    Returns:
        Objeto date ou None se não conseguir parsear.
    """
    formatos = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d/%m/%y",
    ]
    
    texto = texto.strip()
    
    for formato in formatos:
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    
    logger.warning(f"Não foi possível parsear a data: {texto}")
    return None


def parse_valor_monetario(texto: str) -> Optional[float]:
    """
    Converte uma string de valor monetário para float.
    
    Formatos suportados:
    - R$ 1.234,56
    - 1.234,56
    - 1234.56
    - 1234,56
    
    Args:
        texto: String com o valor.
        
    Returns:
        Valor float ou None se não conseguir parsear.
    """
    texto = texto.strip().replace("R$", "").strip()
    
    if "." in texto and "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    
    try:
        return float(texto)
    except ValueError:
        logger.warning(f"Não foi possível parsear o valor: {texto}")
        return None


def extrair_ticker(texto: str) -> Optional[str]:
    """
    Extrai o código de um ticker de um texto.
    
    Args:
        texto: Texto contendo o ticker.
        
    Returns:
        Ticker em maiúsculas ou None.
    """
    padrao = r'\b([A-Za-z]{4}\d{1,2})\b'
    match = re.search(padrao, texto.upper())
    
    if match:
        return match.group(1)
    return None


def extrair_quantidade(texto: str) -> Optional[int]:
    """
    Extrai uma quantidade de ações de um texto.
    
    Args:
        texto: Texto contendo a quantidade.
        
    Returns:
        Quantidade como inteiro ou None.
    """
    padroes = [
        r'(\d+)\s*(?:ações?|papéis?|cotas?)',
        r'(?:comprei?|vendi?|vendeu|comprou)\s*(\d+)',
        r'quantidade[:\s]+(\d+)',
        r'\b(\d+)\s*(?:x|X)\s*[A-Za-z]{4}\d',
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    numeros = re.findall(r'\b(\d+)\b', texto)
    for num in numeros:
        valor = int(num)
        if 1 <= valor <= 100000:
            return valor
    
    return None


def extrair_preco(texto: str) -> Optional[float]:
    """
    Extrai um preço de um texto.
    
    Args:
        texto: Texto contendo o preço.
        
    Returns:
        Preço como float ou None.
    """
    padroes = [
        r'R\$\s*([\d.,]+)',
        r'(?:preço|valor|cotação)[:\s]*(?:R\$\s*)?([\d.,]+)',
        r'(?:por|a)\s*(?:R\$\s*)?([\d.,]+)',
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            valor = parse_valor_monetario(match.group(1))
            if valor is not None and 0.01 <= valor <= 10000:
                return valor
    
    return None


def identificar_tipo_operacao_texto(texto: str) -> Optional[str]:
    """
    Identifica se o texto descreve uma compra ou venda.
    
    Args:
        texto: Texto da mensagem.
        
    Returns:
        'COMPRA', 'VENDA' ou None.
    """
    texto_lower = texto.lower()
    
    palavras_venda = ['vendi', 'vendeu', 'vender', 'venda', 'vendendo']
    palavras_compra = ['comprei', 'comprou', 'comprar', 'compra', 'comprando']
    
    for palavra in palavras_venda:
        if palavra in texto_lower:
            return "VENDA"
    
    for palavra in palavras_compra:
        if palavra in texto_lower:
            return "COMPRA"
    
    return None


def extrair_dados_operacao(texto: str) -> dict:
    """
    Tenta extrair todos os dados de uma operação de um texto.
    
    Args:
        texto: Texto descrevendo a operação.
        
    Returns:
        Dicionário com os dados extraídos.
    """
    dados = {
        "ticker": extrair_ticker(texto),
        "quantidade": extrair_quantidade(texto),
        "tipo": identificar_tipo_operacao_texto(texto),
        "preco": extrair_preco(texto),
    }
    
    dados_preenchidos = {k: v for k, v in dados.items() if v is not None}
    
    logger.debug(f"Dados extraídos do texto: {dados_preenchidos}")
    
    return dados


def calcular_preco_medio(
    quantidade_atual: int,
    preco_medio_atual: float,
    quantidade_nova: int,
    preco_novo: float
) -> float:
    """
    Calcula o novo preço médio após uma compra.
    
    Args:
        quantidade_atual: Quantidade atual em carteira.
        preco_medio_atual: Preço médio atual.
        quantidade_nova: Quantidade sendo comprada.
        preco_novo: Preço da nova compra.
        
    Returns:
        Novo preço médio.
    """
    custo_atual = Decimal(str(quantidade_atual)) * Decimal(str(preco_medio_atual))
    custo_novo = Decimal(str(quantidade_nova)) * Decimal(str(preco_novo))
    quantidade_total = quantidade_atual + quantidade_nova
    
    if quantidade_total == 0:
        return 0.0
    
    preco_medio = (custo_atual + custo_novo) / Decimal(str(quantidade_total))
    
    return float(preco_medio.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP))


def gerar_codigo_darf() -> dict:
    """
    Retorna informações sobre o código DARF para IR sobre ações.
    
    Returns:
        Dicionário com informações da DARF.
    """
    return {
        "codigo": "6015",
        "descricao": "IRPF - Ganhos líquidos em operações em bolsa",
        "periodo_apuracao": "Mensal",
        "vencimento": "Último dia útil do mês seguinte",
        "cnpj_favorecido": "Receita Federal do Brasil",
        "instrucoes": [
            "Preencher com o valor do imposto devido no mês",
            "Período de apuração: mês/ano das operações",
            "Não esquecer de incluir prejuízos compensados se houver"
        ]
    }


def obter_mes_referencia(data: date) -> str:
    """
    Obtém a string de referência do mês para DARF.
    
    Args:
        data: Data de referência.
        
    Returns:
        String no formato "MM/YYYY".
    """
    return f"{data.month:02d}/{data.year}"


def calcular_dias_para_vencimento(data_operacao: date) -> int:
    """
    Calcula quantos dias faltam para o vencimento da DARF.
    
    Args:
        data_operacao: Data da operação.
        
    Returns:
        Número de dias até o vencimento.
    """
    from src.motor_calculo import get_motor_calculo
    
    motor = get_motor_calculo()
    vencimento = motor.calcular_vencimento_darf(data_operacao)
    
    dias = (vencimento - date.today()).days
    return dias


def validar_ticker(ticker: str) -> bool:
    """
    Valida se um ticker está no formato correto.
    
    Args:
        ticker: Código do ativo.
        
    Returns:
        True se válido, False caso contrário.
    """
    padrao = r'^[A-Za-z]{4}\d{1,2}$'
    return bool(re.match(padrao, ticker))


def formatar_operacao_resumo(operacao: dict) -> str:
    """
    Formata uma operação para exibição resumida.
    
    Args:
        operacao: Dicionário com dados da operação.
        
    Returns:
        String formatada.
    """
    tipo = operacao.get('tipo', 'N/A')
    ticker = operacao.get('ticker', 'N/A')
    quantidade = operacao.get('quantidade', 0)
    preco = operacao.get('preco_unitario', 0)
    valor_total = operacao.get('valor_total', quantidade * preco)
    
    emoji = "🔴" if tipo == "VENDA" else "🟢"
    
    return (
        f"{emoji} {tipo} | {quantidade}x {ticker} "
        f"@ {formatar_moeda(preco)} = {formatar_moeda(valor_total)}"
    )


def gerar_id_sessao() -> str:
    """
    Gera um ID único para uma sessão de conversa.
    
    Returns:
        String com ID da sessão.
    """
    import uuid
    return str(uuid.uuid4())[:8]


def truncar_texto(texto: str, max_chars: int = 100) -> str:
    """
    Trunca um texto mantendo palavras completas.
    
    Args:
        texto: Texto a ser truncado.
        max_chars: Número máximo de caracteres.
        
    Returns:
        Texto truncado com "..." se necessário.
    """
    if len(texto) <= max_chars:
        return texto
    
    texto_cortado = texto[:max_chars]
    ultimo_espaco = texto_cortado.rfind(' ')
    
    if ultimo_espaco > 0:
        texto_cortado = texto_cortado[:ultimo_espaco]
    
    return texto_cortado + "..."
