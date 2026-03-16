"""
IR Smart - Assistente Tributário Inteligente.

Módulo principal do projeto IR Smart para cálculo de
Imposto de Renda sobre operações com ações.

Author: Gleison Mota
Date: Março 2026
Version: 1.0.0
"""

from src.motor_calculo import MotorCalculoIR, get_motor_calculo
from src.database import DatabaseManager, get_database
from src.chatgpt_client import ChatGPTClient, get_gpt_client
from src.validacao import ValidadorAntiAlucinacao, get_validador

__version__ = "1.0.0"
__author__ = "Gleison Mota"
__all__ = [
    "MotorCalculoIR",
    "DatabaseManager", 
    "ChatGPTClient",
    "ValidadorAntiAlucinacao",
    "get_motor_calculo",
    "get_database",
    "get_gpt_client",
    "get_validador"
]
