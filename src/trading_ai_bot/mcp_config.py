"""
MCP Server Configuration для Trading AI Bot Tools
"""
import json
from typing import Dict, Any
from .tools import ALL_MCP_TOOLS, MarketDataTool, TechnicalAnalysisTool


class MCPServerConfig:
    """Конфигурация MCP сервера для торговых инструментов"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.market_data_tool = MarketDataTool(config.get('exchange', {}))
        self.technical_analysis_tool = TechnicalAnalysisTool()
    
    def get_server_info(self) -> Dict[str, Any]:
        """Информация о MCP сервере"""
        return {
            "name": "trading-ai-bot",
            "version": "1.0.0",
            "description": "AI-powered trading bot with MCP tools for market data and technical analysis",
            "capabilities": {
                "tools": list(ALL_MCP_TOOLS.keys()),
                "resources": [],
                "prompts": []
            }
        }
    
    def get_tools_schema(self) -> Dict[str, Any]:
        """Схема всех доступных MCP инструментов"""
        return ALL_MCP_TOOLS
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Вызов MCP инструмента
        
        Args:
            tool_name: Имя инструмента (например, "market_data.get_current_price")
            arguments: Аргументы для инструмента
            
        Returns:
            Результат выполнения инструмента
        """
        try:
            # Разбираем имя инструмента
            if '.' not in tool_name:
                raise ValueError(f"Invalid tool name format: {tool_name}")
            
            module_name, method_name = tool_name.split('.', 1)
            
            # Маршрутизация к соответствующему инструменту
            if module_name == "market_data":
                result = await self._call_market_data_tool(method_name, arguments)
            elif module_name == "technical_analysis":
                result = await self._call_technical_analysis_tool(method_name, arguments)
            else:
                raise ValueError(f"Unknown tool module: {module_name}")
            
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _call_market_data_tool(self, method_name: str, arguments: Dict[str, Any]) -> Any:
        """Вызов методов инструмента рыночных данных"""
        async with self.market_data_tool:
            if method_name == "get_current_price":
                return await self.market_data_tool.get_current_price(arguments["symbol"])
            
            elif method_name == "get_klines":
                return await self.market_data_tool.get_klines(
                    arguments["symbol"],
                    arguments.get("interval", "15m"),
                    arguments.get("limit", 100)
                )
            
            elif method_name == "get_24hr_ticker":
                return await self.market_data_tool.get_24hr_ticker(arguments["symbol"])
            
            elif method_name == "get_multi_timeframe_data":
                return await self.market_data_tool.get_multi_timeframe_data(
                    arguments["symbol"],
                    arguments.get("timeframes", ["5m", "15m", "1h", "4h"])
                )
            
            elif method_name == "get_market_data":
                return await self.market_data_tool.get_market_data(
                    arguments["symbol"],
                    arguments.get("include_multi_timeframe", False)
                )
            
            else:
                raise ValueError(f"Unknown market data method: {method_name}")
    
    async def _call_technical_analysis_tool(self, method_name: str, arguments: Dict[str, Any]) -> Any:
        """Вызов методов инструмента технического анализа"""
        tool = self.technical_analysis_tool
        
        if method_name == "calculate_rsi":
            return tool.calculate_rsi(
                arguments["prices"],
                arguments.get("period", 14)
            )
        
        elif method_name == "calculate_macd":
            return tool.calculate_macd(arguments["prices"])
        
        elif method_name == "calculate_bollinger_bands":
            return tool.calculate_bollinger_bands(
                arguments["prices"],
                arguments.get("period", 20),
                arguments.get("std_dev", 2.0)
            )
        
        elif method_name == "calculate_volume_profile":
            return tool.calculate_volume_profile(arguments["klines"])
        
        elif method_name == "calculate_support_resistance":
            return tool.calculate_support_resistance(arguments["klines"])
        
        elif method_name == "analyze_multiple_timeframes":
            return tool.analyze_multiple_timeframes(arguments["klines_data"])
        
        elif method_name == "comprehensive_analysis":
            return tool.comprehensive_analysis(
                arguments["market_data"],
                arguments.get("multi_timeframe_data")
            )
        
        else:
            raise ValueError(f"Unknown technical analysis method: {method_name}")


def create_mcp_server_config(config_path: str = "config.json") -> MCPServerConfig:
    """Создать конфигурацию MCP сервера из файла"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return MCPServerConfig(config)
    except Exception as e:
        # Fallback конфигурация
        default_config = {
            "exchange": {
                "base_url": "https://fapi.binance.com"
            },
            "ai": {}
        }
        return MCPServerConfig(default_config)
