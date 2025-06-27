"""
Основные компоненты торговой системы
"""

from .trading_agent import TradingAgent
# from .data_provider import BinanceDataProvider  # Временно отключено
from .claude_analyzer import ClaudeMarketAnalyzer
from .risk_manager import RiskManager
# from .technical_analyzer import TechnicalAnalyzer  # Временно отключено

__all__ = [
    'TradingAgent',
    # 'BinanceDataProvider',  # Временно отключено
    'ClaudeMarketAnalyzer',
    'RiskManager',
    # 'TechnicalAnalyzer'  # Временно отключено
    'TechnicalAnalyzer'
]
