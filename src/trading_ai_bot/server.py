#!/usr/bin/env python3
"""
Простой API сервер для ИИ агента торговли на фьючерсных рынках
(будет заменен на MCP после установки зависимостей)
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional
import json
from datetime import datetime

from .core.trading_agent import TradingAgent
from .tools.market_data import MarketDataTool
from .core.claude_analyzer import ClaudeMarketAnalyzer
from .core.risk_manager import RiskManager
from .tools.technical_analysis import TechnicalAnalysisTool

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trading_ai_server")

class TradingAIServer:
    """Простой сервер для торгового ИИ агента"""
    
    def __init__(self):
        self.config: Optional[Dict] = None
        self.trading_agent: Optional[TradingAgent] = None
        self.data_provider: Optional[MarketDataTool] = None
        self.claude_analyzer: Optional[ClaudeMarketAnalyzer] = None
        self.risk_manager: Optional[RiskManager] = None
        self.technical_analyzer: Optional[TechnicalAnalysisTool] = None
    
    async def initialize(self):
        """Инициализация сервера"""
        # Загружаем конфигурацию
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "trading": {
                    "initial_balance": 10000,
                    "max_risk_per_trade": 0.02,
                    "trading_pairs": ["BTCUSDT", "ETHUSDT"]
                },
                "exchange": {},
                "ai": {}
            }
        
        # Инициализируем компоненты
        await self._initialize_components()
        logger.info("Сервер торговой системы инициализирован")
    
    async def _initialize_components(self):
        """Инициализация компонентов системы"""
        if not self.config:
            return
            
        try:
            self.data_provider = MarketDataTool(self.config.get('exchange', {}))
            self.claude_analyzer = ClaudeMarketAnalyzer(self.config.get('ai', {}))
            self.risk_manager = RiskManager(self.config)
            self.technical_analyzer = TechnicalAnalysisTool()
            
            # Создаем торгового агента
            agent_config = {
                **self.config.get('trading', {}),
                'exchange': self.config.get('exchange', {}),
                'ai': self.config.get('ai', {})
            }
            self.trading_agent = TradingAgent(agent_config)
            
            logger.info("Компоненты торговой системы инициализированы")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации компонентов: {e}")
            raise
    
    async def get_market_data(self, symbol: str) -> Dict:
        """Получить данные рынка"""
        if not self.data_provider:
            raise Exception("Поставщик данных не инициализирован")
        
        try:
            async with self.data_provider:
                market_data = await self.data_provider.get_market_data(symbol)
                return market_data
        except Exception as e:
            raise Exception(f"Ошибка получения данных рынка: {e}")
    
    async def analyze_market(self, symbol: str) -> Dict:
        """Анализ рынка с помощью ИИ"""
        if not self.data_provider or not self.claude_analyzer:
            raise Exception("Анализаторы не инициализированы")
        
        try:
            # Получаем данные рынка
            async with self.data_provider:
                market_data = await self.data_provider.get_market_data(symbol)
            
            # Получаем технический анализ
            technical_analysis = await self.technical_analyzer.analyze(market_data)
            
            # Анализируем с помощью Claude
            analysis = await self.claude_analyzer.analyze_market(market_data, technical_analysis)
            
            return analysis
        except Exception as e:
            raise Exception(f"Ошибка анализа рынка: {e}")
    
    async def get_technical_analysis(self, symbol: str) -> Dict:
        """Получить технический анализ"""
        if not self.data_provider or not self.technical_analyzer:
            raise Exception("Анализаторы не инициализированы")
        
        try:
            # Получаем данные рынка
            async with self.data_provider:
                market_data = await self.data_provider.get_market_data(symbol)
            
            # Проводим технический анализ
            technical_analysis = await self.technical_analyzer.analyze(market_data)
            
            return technical_analysis
        except Exception as e:
            raise Exception(f"Ошибка технического анализа: {e}")
    
    async def calculate_position_size(self, symbol: str, entry_price: float, 
                                    stop_loss: float, confidence: float) -> Dict:
        """Рассчитать размер позиции"""
        if not self.risk_manager:
            raise Exception("Менеджер рисков не инициализирован")
        
        try:
            analysis = {
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "confidence": confidence
            }
            
            market_data = {"symbol": symbol}
            
            position_calc = self.risk_manager.calculate_position_size(analysis, market_data)
            
            return position_calc
        except Exception as e:
            raise Exception(f"Ошибка расчета размера позиции: {e}")
    
    async def get_portfolio_summary(self) -> Dict:
        """Получить сводку портфеля"""
        if not self.risk_manager:
            raise Exception("Менеджер рисков не инициализирован")
        
        try:
            portfolio = self.risk_manager.get_portfolio_summary()
            return portfolio
        except Exception as e:
            raise Exception(f"Ошибка получения сводки портфеля: {e}")
    
    async def execute_trade_decision(self, symbol: str, action: str, size: float,
                                   entry_price: float, stop_loss: float, 
                                   take_profit: float) -> Dict:
        """Выполнить торговое решение"""
        if not self.trading_agent:
            raise Exception("Торговый агент не инициализирован")
        
        try:
            decision = {
                "symbol": symbol,
                "action": action,
                "size": size,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit
            }
            
            # Добавляем дополнительные поля
            risk_amount = abs(entry_price - stop_loss) * size
            potential_profit = abs(take_profit - entry_price) * size
            
            decision.update({
                "risk_amount": risk_amount,
                "potential_profit": potential_profit,
                "risk_reward_ratio": potential_profit / risk_amount if risk_amount > 0 else 0
            })
            
            # Выполняем сделку
            await self.trading_agent.execute_trade(decision)
            
            result = {
                "status": "executed",
                "decision": decision,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
        except Exception as e:
            raise Exception(f"Ошибка выполнения торгового решения: {e}")
    
    async def configure_system(self, config: Dict) -> str:
        """Настроить систему"""
        try:
            self.config = config
            await self._initialize_components()
            return "Система успешно настроена"
        except Exception as e:
            raise Exception(f"Ошибка настройки системы: {e}")

async def main():
    """Запуск простого сервера"""
    server_instance = TradingAIServer()
    
    try:
        await server_instance.initialize()
        logger.info("🚀 Торговый ИИ сервер запущен")
        
        # Простая демонстрация работы
        print("📊 Тестирование функций сервера:")
        
        # Получаем данные рынка
        market_data = await server_instance.get_market_data("BTCUSDT")
        print(f"✅ Данные рынка получены: цена ${market_data.get('current_price', 'N/A')}")
        
        # Анализируем рынок
        analysis = await server_instance.analyze_market("BTCUSDT")
        print(f"✅ Анализ завершен: {analysis.get('market_sentiment', 'N/A')} настроение")
        
        # Сводка портфеля
        portfolio = await server_instance.get_portfolio_summary()
        print(f"✅ Портфель: баланс ${portfolio.get('balance', 'N/A')}")
        
        print("\n🔄 Сервер работает в демо-режиме. Нажмите Ctrl+C для остановки.")
        
        # Бесконечный цикл для поддержания работы сервера
        while True:
            await asyncio.sleep(60)  # Ждем минуту
            logger.info("Сервер активен...")
            
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Ошибка в работе сервера: {e}")
    finally:
        print("🏁 Сервер остановлен")

if __name__ == "__main__":
    asyncio.run(main())
