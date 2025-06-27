"""
Trading AI Bot Tools

Модульная структура инструментов для MCP сервера
"""

from .market_data import MarketDataTool
from .market_data import MCP_TOOLS as MARKET_DATA_TOOLS
from .technical_analysis import TechnicalAnalysisTool
from .technical_analysis import MCP_TOOLS as TECHNICAL_ANALYSIS_TOOLS
from .analysis_formatter import AnalysisFormatterTool
from .analysis_validator import AnalysisValidatorTool
from .mock_analyzer import MockAnalyzerTool
from .prompt_builder import PromptBuilderTool
from .historical_data import HistoricalDataTool

# Объединяем все MCP tools для экспорта
ALL_MCP_TOOLS = {
    **{f"market_data.{name}": tool for name, tool in MARKET_DATA_TOOLS.items()},
    **{f"technical_analysis.{name}": tool for name, tool in TECHNICAL_ANALYSIS_TOOLS.items()}
}

__all__ = [
    "MarketDataTool",
    "TechnicalAnalysisTool",
    "AnalysisFormatterTool",
    "AnalysisValidatorTool", 
    "MockAnalyzerTool",
    "PromptBuilderTool", 
    "HistoricalDataTool",
    "ALL_MCP_TOOLS"
]
